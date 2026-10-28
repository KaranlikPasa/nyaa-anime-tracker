"""
Config and State Management for Nyaa Anime Tracker
"""
import os
import sys
import json
import uuid
from typing import List, Dict, Any, Optional

if getattr(sys, "frozen", False):
    PROJECT_DIR = os.path.dirname(sys.executable)
    BUNDLE_DIR = getattr(sys, "_MEIPASS", PROJECT_DIR)
else:
    PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
    BUNDLE_DIR = PROJECT_DIR

if sys.platform != "win32" and not os.access(PROJECT_DIR, os.W_OK):
    xdg_data = os.environ.get("XDG_DATA_HOME", os.path.expanduser("~/.local/share"))
    DATA_DIR = os.path.join(xdg_data, "nyaa-anime-tracker")
else:
    DATA_DIR = os.path.join(PROJECT_DIR, "data")
SETTINGS_FILE = os.path.join(DATA_DIR, "settings.json")
HISTORY_FILE = os.path.join(DATA_DIR, "history.json")

def get_asset_path(filename: str) -> str:
    """Finds an asset file both in regular execution and inside a PyInstaller bundle."""
    p1 = os.path.join(BUNDLE_DIR, filename)
    if os.path.exists(p1):
        return p1
    return os.path.join(PROJECT_DIR, filename)

DEFAULT_SETTINGS = {
    "check_interval": 60,               # seconds between checks
    "category": "1_0",                  # 1_0: All Anime (Raw + English-translated + Other)
    "english_only": False,              # legacy flag
    "start_with_windows": False,        # auto-start on Windows boot
    "close_to_tray": True,              # minimize to tray when closed
    "play_sound": True,                 # sound on toast notification
    "theme": "dark",                    # UI theme: dark or light
    "max_history": 200,                 # max records in history
}

DEFAULT_ANIME = [
    # A few popular examples if empty
    {
        "id": "sample-1",
        "name": "Dandadan",
        "enabled": True,
        "resolution": "Tümü",
        "group": "",
        "exclude": "Dub"
    }
]

class ConfigManager:
    def __init__(self):
        os.makedirs(DATA_DIR, exist_ok=True)
        self.settings: Dict[str, Any] = {}
        self.tracked_anime: List[Dict[str, Any]] = []
        self.seen_guids: set = set()
        self.history: List[Dict[str, Any]] = []
        
        self.load_settings()
        self.load_history()

    def load_settings(self):
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.settings = {**DEFAULT_SETTINGS, **data.get("settings", {})}
                    # Migrate old settings
                    if "category" not in data.get("settings", {}):
                        self.settings["category"] = "1_0"
                    self.tracked_anime = data.get("tracked_anime", [])
            except Exception as e:
                print(f"[Config] Error loading settings: {e}")
                self.settings = DEFAULT_SETTINGS.copy()
                self.tracked_anime = DEFAULT_ANIME.copy()
        else:
            self.settings = DEFAULT_SETTINGS.copy()
            self.tracked_anime = DEFAULT_ANIME.copy()
            self.save_settings()

    def save_settings(self):
        try:
            with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
                json.dump({
                    "settings": self.settings,
                    "tracked_anime": self.tracked_anime
                }, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"[Config] Error saving settings: {e}")

    def load_history(self):
        if os.path.exists(HISTORY_FILE):
            try:
                with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.seen_guids = set(data.get("seen_guids", []))
                    self.history = data.get("history", [])
            except Exception as e:
                print(f"[Config] Error loading history: {e}")
                self.seen_guids = set()
                self.history = []
        else:
            self.seen_guids = set()
            self.history = []

    def save_history(self):
        try:
            # Keep history bounded
            max_hist = self.settings.get("max_history", 200)
            trimmed_history = self.history[:max_hist]
            with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                json.dump({
                    "seen_guids": list(self.seen_guids)[-2000:],  # keep last 2000 seen IDs
                    "history": trimmed_history
                }, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[Config] Error saving history: {e}")

    # --- Anime List Operations ---

    def add_anime(self, name: str, resolution: str = "Tümü", group: str = "", exclude: str = "", category: str = "1_0") -> Optional[Dict[str, Any]]:
        name = name.strip()
        if not name:
            return None
            
        # Check if already exists (case-insensitive)
        for anime in self.tracked_anime:
            if anime["name"].strip().lower() == name.lower():
                return None  # Already in list

        item = {
            "id": str(uuid.uuid4()),
            "name": name,
            "enabled": True,
            "resolution": resolution,
            "group": group.strip(),
            "exclude": exclude.strip(),
            "category": category
        }
        self.tracked_anime.append(item)
        self.save_settings()
        return item

    def remove_anime(self, anime_id: str) -> bool:
        initial_len = len(self.tracked_anime)
        self.tracked_anime = [a for a in self.tracked_anime if a["id"] != anime_id]
        if len(self.tracked_anime) != initial_len:
            self.save_settings()
            return True
        return False

    def toggle_anime(self, anime_id: str, enabled: bool):
        for anime in self.tracked_anime:
            if anime["id"] == anime_id:
                anime["enabled"] = enabled
                self.save_settings()
                break

    def get_setting(self, key: str, default=None):
        return self.settings.get(key, default)

    def set_setting(self, key: str, value: Any):
        self.settings[key] = value
        self.save_settings()

    # --- History & Seen Check ---

    def is_seen(self, guid: str) -> bool:
        return guid in self.seen_guids

    def mark_seen(self, guid: str):
        self.seen_guids.add(guid)

    def add_history_entry(self, entry: Dict[str, Any]):
        self.history.insert(0, entry)
        self.save_history()

    def clear_history(self):
        self.history.clear()
        self.save_history()

config = ConfigManager()
