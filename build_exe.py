"""
XBrowser - Build & Packaging Automation Script
Produces:
1. Standalone Application Folder (dist/XBrowser/XBrowser.exe) with portable runtime.
2. Bundled assets, Tor engine binaries, and PyQt6-WebEngine resources.
3. Automatically synchronized Desktop & Start Menu shortcuts with the new bear mascot icon.
"""

import os
import sys
import shutil
import subprocess

def build():
    project_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_dir)

    icon_path = os.path.join(project_dir, "assets", "xbrowser_icon.ico")
    main_py = os.path.join(project_dir, "main.py")

    print("=" * 70)
    print("      XBROWSER DESKTOP BUILD AUTOMATION (WINDOWS 10 / 11)")
    print("=" * 70)
    print(f"[*] Project Directory : {project_dir}")
    print(f"[*] Main entry        : {main_py}")
    print(f"[*] App Icon          : {icon_path}")

    # Step 0: Terminate running instances to prevent file lock
    try:
        subprocess.run(["taskkill", "/F", "/IM", "XBrowser.exe"], capture_output=True)
    except Exception:
        pass

    # Step 1: Run PyInstaller
    print("\n[1/3] Packaging XBrowser with PyInstaller...")
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name=XBrowser",
        "--windowed",
        "--noconfirm",
        "--clean",
        f"--icon={icon_path}",
        f"--add-data=assets{os.pathsep}assets",
        f"--add-data=bin{os.pathsep}bin",
        "--hidden-import=PyQt6.QtWidgets",
        "--hidden-import=PyQt6.QtCore",
        "--hidden-import=PyQt6.QtGui",
        "--hidden-import=PyQt6.QtWebEngineWidgets",
        "--hidden-import=PyQt6.QtWebEngineCore",
        "--hidden-import=PyQt6.QtNetwork",
        "--hidden-import=stem",
        "--hidden-import=cryptography",
        "--hidden-import=src",
        main_py
    ]

    res = subprocess.run(cmd)
    if res.returncode != 0:
        print("[!] PyInstaller build failed!")
        return False

    dist_dir = os.path.join(project_dir, "dist", "XBrowser")
    dist_exe = os.path.join(dist_dir, "XBrowser.exe")

    # Step 2: Deploy to local installation directory
    print("\n[2/3] Synchronizing with local installation...")
    local_app_dir = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs", "XBrowser")
    if os.path.exists(dist_exe):
        try:
            os.makedirs(local_app_dir, exist_ok=True)
            # Sync files
            shutil.copy2(dist_exe, os.path.join(local_app_dir, "XBrowser.exe"))
            dist_internal = os.path.join(dist_dir, "_internal")
            target_internal = os.path.join(local_app_dir, "_internal")
            if os.path.exists(dist_internal):
                # Copy updated assets & binaries into target _internal
                shutil.copytree(dist_internal, target_internal, dirs_exist_ok=True)
            print(f"[*] Local installation updated: {local_app_dir}")
        except Exception as e:
            print(f"[!] Warning syncing to local app dir: {e}")

    # Step 3: Update shortcuts
    print("\n[3/3] Updating Windows Shortcuts...")
    try:
        import win32com.client
        sh = win32com.client.Dispatch("WScript.Shell")
        
        # Desktop
        desktop = os.path.join(os.environ["USERPROFILE"], "Desktop")
        dt_lnk = os.path.join(desktop, "XBrowser.lnk")
        s = sh.CreateShortcut(dt_lnk)
        s.TargetPath = os.path.join(local_app_dir, "XBrowser.exe")
        s.WorkingDirectory = local_app_dir
        s.IconLocation = f"{icon_path},0"
        s.Description = "XBrowser - Privacy-Hardened Desktop Browser"
        s.Save()

        # Start Menu
        programs_dir = os.path.join(os.environ["APPDATA"], "Microsoft", "Windows", "Start Menu", "Programs")
        sm_lnk = os.path.join(programs_dir, "XBrowser.lnk")
        s2 = sh.CreateShortcut(sm_lnk)
        s2.TargetPath = os.path.join(local_app_dir, "XBrowser.exe")
        s2.WorkingDirectory = local_app_dir
        s2.IconLocation = f"{icon_path},0"
        s2.Description = "XBrowser - Privacy-Hardened Desktop Browser"
        s2.Save()
        print("[*] Desktop and Start Menu shortcuts successfully configured!")
    except Exception as e:
        print(f"[!] Warning creating shortcuts: {e}")

    print("\n" + "=" * 70)
    print("      BUILD COMPLETED SUCCESSFULLY!")
    print("=" * 70)
    return True

if __name__ == "__main__":
    build()
