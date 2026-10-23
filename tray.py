"""
System Tray Manager using pystray
"""
import os
import threading
from typing import Callable, Optional
from PIL import Image
import pystray
from pystray import MenuItem as item

from config import get_asset_path

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
ICON_PNG = get_asset_path("icon.png")

class TrayManager:
    def __init__(self, on_show_window: Callable, on_exit: Callable, on_check_now: Callable, on_toggle_pause: Callable, get_is_paused: Callable):
        self.on_show_window = on_show_window
        self.on_exit = on_exit
        self.on_check_now = on_check_now
        self.on_toggle_pause = on_toggle_pause
        self.get_is_paused = get_is_paused
        
        self.icon: Optional[pystray.Icon] = None
        self._thread: Optional[threading.Thread] = None

    def _create_image(self) -> Image.Image:
        if os.path.exists(ICON_PNG):
            return Image.open(ICON_PNG)
        # Fallback image if file not found
        img = Image.new("RGBA", (64, 64), color=(30, 41, 59, 255))
        return img

    def _get_pause_label(self, item) -> str:
        return "▶️ Devam Et" if self.get_is_paused() else "⏸️ Duraklat"

    def _create_menu(self):
        return pystray.Menu(
            item("🖥️ Arayüzü Göster", lambda: self.on_show_window(), default=True),
            item("🔍 Şimdi Kontrol Et", lambda: self.on_check_now()),
            item(self._get_pause_label, lambda: self.on_toggle_pause()),
            pystray.Menu.SEPARATOR,
            item("🚪 Çıkış", lambda: self.on_exit())
        )

    def start(self):
        if self.icon is not None:
            return
        
        image = self._create_image()
        self.icon = pystray.Icon(
            "nyaa_anime_tracker",
            image,
            "Nyaa Anime Çeviri Takipçisi",
            menu=self._create_menu()
        )
        
        self._thread = threading.Thread(target=self.icon.run, name="NyaaTrayThread", daemon=True)
        self._thread.start()
        print("[Tray] System tray icon initialized.")

    def notify(self, message: str, title: str = "Nyaa Takipçisi"):
        if self.icon:
            try:
                self.icon.notify(message, title)
            except Exception as e:
                print(f"[Tray] Notify error: {e}")

    def stop(self):
        if self.icon:
            try:
                self.icon.stop()
            except Exception as e:
                print(f"[Tray] Error stopping tray: {e}")
            self.icon = None
