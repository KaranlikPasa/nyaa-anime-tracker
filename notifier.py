"""
Windows Notification Manager with Winotify and Pystray Fallback
"""
import os
import sys
import webbrowser

try:
    from winotify import Notification, audio
    HAS_WINOTIFY = True
except ImportError:
    HAS_WINOTIFY = False

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
ICON_PNG = os.path.join(PROJECT_DIR, "icon.png")
ICON_ICO = os.path.join(PROJECT_DIR, "icon.ico")

class Notifier:
    def __init__(self, tray_icon=None):
        self.tray_icon = tray_icon

    def set_tray_icon(self, tray_icon):
        self.tray_icon = tray_icon

    def notify_release(self, anime_name: str, release_title: str, guid: str, link: str, size: str = "", seeders: str = "", play_sound: bool = True):
        """
        Sends a Windows toast notification for a newly detected release.
        """
        title = f"🎬 {anime_name} - Yeni Bölüm!"
        details = []
        if size:
            details.append(f"📦 {size}")
        if seeders:
            details.append(f"🌱 {seeders} seed")
            
        details_str = f" ({' | '.join(details)})" if details else ""
        msg = f"{release_title}{details_str}"

        # Try winotify first
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

                # Primary click on toast opens web page
                if guid:
                    toast.launch = guid

                # Action buttons
                if guid:
                    toast.add_actions(label="🌐 Nyaa'da Aç", launch=guid)
                if link:
                    toast.add_actions(label="📥 Torrent İndir", launch=link)

                toast.show()
                return
            except Exception as e:
                print(f"[Notifier] winotify failed: {e}, falling back to tray notification.")

        # Fallback to tray balloon notification
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
