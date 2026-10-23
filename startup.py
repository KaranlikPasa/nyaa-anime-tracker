"""
Windows Startup Manager using HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run
"""
import sys
import os
import winreg

APP_NAME = "NyaaAnimeTracker"

def get_launch_command(start_minimized: bool = True) -> str:
    """Returns the proper command line to run this app in the background."""
    project_dir = os.path.dirname(os.path.abspath(__file__))
    main_py = os.path.join(project_dir, "main.py")
    
    # Check if running as compiled executable (PyInstaller)
    if getattr(sys, "frozen", False):
        exe_path = sys.executable
        arg = " --minimized" if start_minimized else ""
        return f'"{exe_path}"{arg}'
    
    # Running from python script
    python_dir = os.path.dirname(sys.executable)
    pythonw = os.path.join(python_dir, "pythonw.exe")
    if not os.path.exists(pythonw):
        pythonw = sys.executable  # fallback
        
    arg = " --minimized" if start_minimized else ""
    return f'"{pythonw}" "{main_py}"{arg}'

def is_startup_enabled() -> bool:
    """Checks whether the application is registered to run on Windows startup."""
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
    """Enables or disables auto-start on Windows boot."""
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
