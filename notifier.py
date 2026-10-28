"""
Cross-Platform Notification Manager:
- Windows: Winotify (Toast with action buttons)
- Linux: notify-send (libnotify)
- Fallback: Pystray system tray notification
"""
import os
import sys
import shutil
import subprocess
import webbrowser

try:
    from winotify import Notification, audio
    HAS_WINOTIFY = (sys.platform == "win32")
except ImportError:
    HAS_WINOTIFY = False

from config import get_asset_path

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
ICON_PNG = get_asset_path("icon.png")
ICON_ICO = get_asset_path("icon.ico")

class Notifier:
    def __init__(self, tray_icon=None):
        self.tray_icon = tray_icon

    def set_tray_icon(self, tray_icon):
        self.tray_icon = tray_icon

    def notify_release(self, anime_name: str, release_title: str, guid: str, link: str, size: str = "", seeders: str = "", play_sound: bool = True):
        """
        Sends a desktop notification for a newly detected release.
        """
        title = f"🎬 {anime_name} - Yeni Bölüm!"
        details = []
        if size:
            details.append(f"📦 {size}")
        if seeders:
            details.append(f"🌱 {seeders} seed")
            
        details_str = f" ({' | '.join(details)})" if details else ""
        msg = f"{release_title}{details_str}"

        # 1. Windows: Try winotify
        if HAS_WINOTIFY:
            try:
                toast = Notification(
                    app_id="Nyaa Anime Çeviri Takipçisi",
                    title=title,
                    msg=msg,
                    duration="short",
                    icon=ICON_PNG if os.path.exists(ICON_PNG) else ""
                )
                
                if play_sound:
                    toast.set_audio(audio.Reminder, loop=False)
                else:
                    toast.set_audio(audio.Silent, loop=False)

                if guid:
                    toast.launch = guid
                    toast.add_actions(label="🌐 Nyaa'da Aç", launch=guid)
                if link:
                    toast.add_actions(label="📥 Torrent İndir", launch=link)

                toast.show()
                return
            except Exception as e:
                print(f"[Notifier] winotify failed: {e}, falling back.")

        # 2. Linux / Arch: Try notify-send
        if sys.platform != "win32" and shutil.which("notify-send"):
            try:
                cmd = ["notify-send", "-a", "Nyaa Anime Tracker", "-u", "normal"]
                if os.path.exists(ICON_PNG):
                    cmd.extend(["-i", ICON_PNG])
                cmd.extend([title, msg])
                subprocess.Popen(cmd)
                return
            except Exception as e:
                print(f"[Notifier] notify-send failed: {e}")

        # 3. Fallback to tray balloon notification
        if self.tray_icon:
            try:
                self.tray_icon.notify(msg, title)
                return
            except Exception as e:
                print(f"[Notifier] tray notify failed: {e}")

        print(f"[Notifier fallback] {title}: {msg}")

    def test_notification(self, play_sound: bool = True):
        """Sends a test notification."""
        self.notify_release(
            anime_name="Test Animesi",
            release_title="[SubsPlease] Test Anime - 01 (1080p) [1080p].mkv",
            guid="https://nyaa.si",
            link="https://nyaa.si",
            size="1.4 GiB",
            seeders="128",
            play_sound=play_sound
        )

notifier = Notifier()
