"""
Background Tracking Service for Nyaa.si Anime Releases
"""
import time
import threading
from datetime import datetime
from typing import Callable, Optional, Dict, Any, List

from config import config
from nyaa_client import nyaa_client
from matcher import match_anime
from notifier import notifier

class AnimeTracker:
    def __init__(self):
        self.is_running = False
        self.is_paused = False
        self.thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._manual_trigger = threading.Event()
        
        # State indicators
        self.last_check_time: Optional[datetime] = None
        self.last_status: str = "Hazır"
        self.total_checks: int = 0
        self.total_matches: int = 0

        # UI Callbacks
        self.on_status_change: Optional[Callable[[str], None]] = None
        self.on_match_found: Optional[Callable[[Dict[str, Any]], None]] = None
        self.on_check_finished: Optional[Callable[[datetime, int], None]] = None

    def _set_status(self, status: str):
        self.last_status = status
        if self.on_status_change:
            try:
                self.on_status_change(status)
            except Exception as e:
                print(f"[Tracker] Error in on_status_change callback: {e}")

    def start(self):
        if self.is_running:
            return
        self.is_running = True
        self.is_paused = False
        self._stop_event.clear()
        self._manual_trigger.clear()
        
        self.thread = threading.Thread(target=self._run_loop, name="NyaaTrackerWorker", daemon=True)
        self.thread.start()
        print("[Tracker] Background tracker started.")

    def stop(self):
        if not self.is_running:
            return
        self.is_running = False
        self._stop_event.set()
        self._manual_trigger.set()
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=2.0)
        self._set_status("Durduruldu")
        print("[Tracker] Background tracker stopped.")

    def pause(self):
        self.is_paused = True
        self._set_status("Duraklatıldı")

    def resume(self):
        self.is_paused = False
        self._set_status("Çalışıyor")
        self.trigger_check_now()

    def trigger_check_now(self):
        """Triggers an immediate check without waiting for sleep."""
        self._manual_trigger.set()

    def _run_loop(self):
        self._set_status("Çalışıyor")
        
        # Check if first run ever (baseline initialization)
        is_first_run = len(config.seen_guids) == 0

        while self.is_running and not self._stop_event.is_set():
            if not self.is_paused:
                try:
                    self._perform_check(suppress_notifications=is_first_run)
                    if is_first_run:
                        is_first_run = False
                except Exception as e:
                    print(f"[Tracker] Check exception: {e}")
                    self._set_status(f"Hata: {e}")

            # Sleep in small increments or wait for manual trigger
            interval = max(15, config.get_setting("check_interval", 60))
            wait_step = 1.0
            elapsed = 0.0

            while elapsed < interval and not self._stop_event.is_set():
                if self._manual_trigger.is_set():
                    self._manual_trigger.clear()
                    break
                time.sleep(wait_step)
                elapsed += wait_step

    def _perform_check(self, suppress_notifications: bool = False):
        active_anime = [a for a in config.tracked_anime if a.get("enabled", True)]
        if not active_anime:
            self._set_status("Takip listesi boş")
            self.last_check_time = datetime.now()
            if self.on_check_finished:
                self.on_check_finished(self.last_check_time, 0)
            return

        self._set_status("Nyaa kontrol ediliyor...")
        english_only = config.get_setting("english_only", True)
        feed_items = nyaa_client.fetch_feed(english_only=english_only)
        
        self.total_checks += 1
        self.last_check_time = datetime.now()
        new_matches_count = 0

        # Process from oldest to newest in feed if possible
        for item in reversed(feed_items):
            guid = item.get("guid") or item.get("link")
            if not guid:
                continue

            # If already processed, skip
            if config.is_seen(guid):
                continue

            # Check matches across all active anime rules
            matched_anime_name = None
            for anime_rule in active_anime:
                is_match, name = match_anime(item["title"], anime_rule)
                if is_match:
                    matched_anime_name = name
                    break

            if matched_anime_name:
                # We found a match!
                new_matches_count += 1
                self.total_matches += 1

                history_entry = {
                    "anime_name": matched_anime_name,
                    "title": item["title"],
                    "link": item["link"],
                    "guid": item["guid"],
                    "size": item["size"],
                    "pubDate": item["pubDate"],
                    "seeders": item["seeders"],
                    "magnet": item.get("magnet", ""),
                    "detected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                config.add_history_entry(history_entry)

                if not suppress_notifications:
                    play_sound = config.get_setting("play_sound", True)
                    notifier.notify_release(
                        anime_name=matched_anime_name,
                        release_title=item["title"],
                        guid=item["guid"],
                        link=item["link"],
                        size=item["size"],
                        seeders=item["seeders"],
                        play_sound=play_sound
                    )

                if self.on_match_found:
                    try:
                        self.on_match_found(history_entry)
                    except Exception as e:
                        print(f"[Tracker] Error in on_match_found callback: {e}")

            # Mark as seen so we don't process it again
            config.mark_seen(guid)

        config.save_history()
        
        status_msg = f"Çalışıyor (Son kontrol: {self.last_check_time.strftime('%H:%M:%S')})"
        if new_matches_count > 0:
            status_msg += f" - {new_matches_count} yeni bölüm yakalandı!"
        self._set_status(status_msg)

        if self.on_check_finished:
            try:
                self.on_check_finished(self.last_check_time, new_matches_count)
            except Exception as e:
                print(f"[Tracker] Error in on_check_finished callback: {e}")

    def search_recent_for_anime(self, anime_rule: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Actively queries Nyaa for this specific anime to discover recent releases immediately.
        """
        anime_name = anime_rule.get("name", "")
        english_only = config.get_setting("english_only", True)
        items = nyaa_client.fetch_feed(english_only=english_only, query=anime_name)

        matches = []
        for item in items:
            is_match, name = match_anime(item["title"], anime_rule)
            if is_match:
                entry = {
                    "anime_name": name,
                    "title": item["title"],
                    "link": item["link"],
                    "guid": item["guid"],
                    "size": item["size"],
                    "pubDate": item["pubDate"],
                    "seeders": item["seeders"],
                    "magnet": item.get("magnet", ""),
                    "detected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                matches.append(entry)
                # Ensure marked as seen so future background poll doesn't duplicate toast
                config.mark_seen(item["guid"])
        
        return matches

tracker = AnimeTracker()
