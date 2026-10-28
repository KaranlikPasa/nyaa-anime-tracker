"""
Startup Manager for Windows (Registry) and Linux (XDG Autostart .desktop)
"""
import sys
import os

APP_NAME = "NyaaAnimeTracker"

if sys.platform == "win32":
    try:
        import winreg
    except ImportError:
        winreg = None
else:
    winreg = None


def get_launch_command(start_minimized: bool = True) -> str:
    """Returns the proper command line to run this app in the background."""
    if sys.platform != "win32":
        arg = " --minimized" if start_minimized else ""
        if os.path.exists("/usr/bin/nyaa-anime-tracker"):
            return f"/usr/bin/nyaa-anime-tracker{arg}"
        project_dir = os.path.dirname(os.path.abspath(__file__))
        return f"{os.path.join(project_dir, 'nyaa-anime-tracker')}{arg}"

    project_dir = os.path.dirname(os.path.abspath(__file__))
    main_py = os.path.join(project_dir, "main.py")
    
    if getattr(sys, "frozen", False):
        exe_path = sys.executable
        arg = " --minimized" if start_minimized else ""
        return f'"{exe_path}"{arg}'
    
    python_dir = os.path.dirname(sys.executable)
    pythonw = os.path.join(python_dir, "pythonw.exe")
    if not os.path.exists(pythonw):
        pythonw = sys.executable
        
    arg = " --minimized" if start_minimized else ""
    return f'"{pythonw}" "{main_py}"{arg}'


def is_startup_enabled() -> bool:
    """Checks whether the application is registered to run on system startup."""
    if sys.platform != "win32":
        autostart_dir = os.path.expanduser("~/.config/autostart")
        desktop_file = os.path.join(autostart_dir, "nyaa-anime-tracker.desktop")
        return os.path.exists(desktop_file)

    if not winreg:
        return False

    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0,
            winreg.KEY_READ
        )
        try:
            val, _ = winreg.QueryValueEx(key, APP_NAME)
            winreg.CloseKey(key)
            return bool(val)
        except FileNotFoundError:
            winreg.CloseKey(key)
            return False
    except Exception as e:
        print(f"[Startup] Error reading registry: {e}")
        return False


def set_startup(enable: bool, start_minimized: bool = True) -> bool:
    """Enables or disables auto-start on boot."""
    if sys.platform != "win32":
        autostart_dir = os.path.expanduser("~/.config/autostart")
        desktop_file = os.path.join(autostart_dir, "nyaa-anime-tracker.desktop")
        if not enable:
            if os.path.exists(desktop_file):
                try:
                    os.remove(desktop_file)
                    print("[Startup] Removed Linux autostart desktop file.")
                except Exception as e:
                    print(f"[Startup] Error removing autostart file: {e}")
            return True

        try:
            os.makedirs(autostart_dir, exist_ok=True)
            cmd = get_launch_command(start_minimized=start_minimized)
            content = f"""[Desktop Entry]
Type=Application
Name=Nyaa Anime Çeviri Takipçisi
Comment=Yeni Nyaa.si bölümlerini arka planda takip eden masaüstü uygulaması
Exec={cmd}
Icon=nyaa-anime-tracker
Terminal=false
Categories=Utility;Network;
X-GNOME-Autostart-enabled=true
"""
            with open(desktop_file, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"[Startup] Created Linux autostart file: {desktop_file}")
            return True
        except Exception as e:
            print(f"[Startup] Error creating autostart file: {e}")
            return False

    if not winreg:
        return False

    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0,
            winreg.KEY_SET_VALUE | winreg.KEY_READ
        )
        if enable:
            cmd = get_launch_command(start_minimized=start_minimized)
            winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, cmd)
            print(f"[Startup] Enabled auto-start: {cmd}")
        else:
            try:
                winreg.DeleteValue(key, APP_NAME)
                print("[Startup] Disabled auto-start.")
            except FileNotFoundError:
                pass
        winreg.CloseKey(key)
        return True
    except Exception as e:
        print(f"[Startup] Error setting registry: {e}")
        return False


if __name__ == "__main__":
    print("Startup enabled:", is_startup_enabled())
    print("Launch command:", get_launch_command())
