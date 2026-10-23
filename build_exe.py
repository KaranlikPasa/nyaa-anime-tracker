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
        f"--name=NyaaAnimeTakipcisi",
        f"--icon={os.path.join(PROJECT_DIR, 'icon.ico')}",
        f"--add-data={os.path.join(PROJECT_DIR, 'icon.ico')};.",
        f"--add-data={os.path.join(PROJECT_DIR, 'icon.png')};.",
        os.path.join(PROJECT_DIR, "main.py")
    ]
    result = subprocess.run(cmd, cwd=PROJECT_DIR)
    if result.returncode == 0:
        print("\n[SUCCESS] Executable built in: dist\\NyaaAnimeTakipcisi.exe")
    else:
        print("\n[ERROR] Build failed with code:", result.returncode)

if __name__ == "__main__":
    build()
