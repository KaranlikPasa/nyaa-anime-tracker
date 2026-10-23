"""
Main Application Entry Point for Nyaa Anime Tracker
"""
import sys
import os

# Ensure the project directory is in the module search path
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

from config import config
from tracker import tracker
from tray import TrayManager
from notifier import notifier
from gui import AnimeTrackerApp

def main():
    start_minimized = "--minimized" in sys.argv

    # Initialize the GUI application
    app = AnimeTrackerApp(start_minimized=start_minimized)

    # Initialize System Tray Manager
    tray = TrayManager(
        on_show_window=lambda: app.after(0, app.show_from_tray),
        on_exit=lambda: app.after(0, app.full_exit),
        on_check_now=tracker.trigger_check_now,
        on_toggle_pause=lambda: app.after(0, app.action_toggle_pause),
        get_is_paused=lambda: tracker.is_paused
    )

    app.set_tray_manager(tray)
    notifier.set_tray_icon(tray)

    # Start system tray
    tray.start()

    # Start background tracker
    tracker.start()

    # Run the Tkinter main event loop
    try:
        app.mainloop()
    except KeyboardInterrupt:
        app.full_exit()

if __name__ == "__main__":
    main()
