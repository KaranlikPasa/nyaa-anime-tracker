"""
Build Standalone Windows Executable using PyInstaller
"""
import subprocess
import sys
import os

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))

def build():
    print("Building standalone executable...")
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconsole",
        "--onefile",
        "--clean",
        "--name=NyaaAnimeTakipcisi",
        f"--icon={os.path.join(PROJECT_DIR, 'icon.ico')}",
        f"--add-data={os.path.join(PROJECT_DIR, 'icon.ico')};.",
        f"--add-data={os.path.join(PROJECT_DIR, 'icon.png')};.",
        "--collect-all=customtkinter",
        "--collect-all=winotify",
        "--collect-all=pystray",
        os.path.join(PROJECT_DIR, "main.py")
    ]
    print("Running PyInstaller...")
    result = subprocess.run(cmd, cwd=PROJECT_DIR)
    if result.returncode == 0:
        exe_path = os.path.join(PROJECT_DIR, "dist", "NyaaAnimeTakipcisi.exe")
        if os.path.exists(exe_path):
            size_mb = os.path.getsize(exe_path) / (1024 * 1024)
            print(f"\n[SUCCESS] Executable built successfully: {exe_path} ({size_mb:.2f} MB)")
    else:
        print("\n[ERROR] Build failed with code:", result.returncode)

if __name__ == "__main__":
    build()
