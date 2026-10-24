"""
XBrowser - The Hybrid Browser combining Tor Browser, Brave, and Opera
Main Entry Point
"""

import sys
import os
import argparse

# Enable high DPI scaling
os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"

def _configure_chromium_flags():
    """Configure smart Chromium flags dynamically tailored to hardware memory capacity."""
    ram_gb = 8.0
    avail_gb = 4.0
    mem_load = 50
    try:
        import ctypes
        class MEMORYSTATUSEX(ctypes.Structure):
            _fields_ = [('dwLength', ctypes.c_ulong), ('dwMemoryLoad', ctypes.c_ulong),
                        ('ullTotalPhys', ctypes.c_ulonglong), ('ullAvailPhys', ctypes.c_ulonglong),
                        ('ullTotalPageFile', ctypes.c_ulonglong), ('ullAvailPageFile', ctypes.c_ulonglong),
                        ('ullTotalVirtual', ctypes.c_ulonglong), ('ullAvailVirtual', ctypes.c_ulonglong),
                        ('sullAvailExtendedVirtual', ctypes.c_ulonglong)]
        stat = MEMORYSTATUSEX()
        stat.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
        if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(stat)):
            ram_gb = stat.ullTotalPhys / (1024 ** 3)
            avail_gb = stat.ullAvailPhys / (1024 ** 3)
            mem_load = stat.dwMemoryLoad
    except Exception:
        pass

    # Check user dark mode preference (defaults to True)
    is_dark = True
    try:
        import json
        cfg_p = os.path.join(os.path.expanduser("~"), ".xbrowser", "config.json")
        if os.path.exists(cfg_p):
            with open(cfg_p, "r", encoding="utf-8") as f:
                cfg = json.load(f)
                is_dark = cfg.get("general", {}).get("dark_mode", True)
    except Exception:
        pass

    flags = [
        "--autoplay-policy=no-user-gesture-required",
        "--ignore-gpu-blocklist",
        "--enable-gpu-rasterization",
        "--enable-accelerated-2d-canvas",
        "--force-color-profile=srgb",
        "--disable-direct-composition-video-overlays",
        "--enable-features=SmoothScrolling,ParallelDownloading,WebAssemblyLazyCompilation,PaintHolding",
        "--disable-features=AudioServiceOutOfProcess,TranslateUI,OptimizationHints,MediaRouter,DirectCompositionVideoOverlays",
        "--blink-settings=preferredColorScheme=1",
        "--force-webrtc-ip-handling-policy=default_public_interface_only",
    ]

    if is_dark:
        flags.append("--force-dark-mode")

    # Ultra-lightweight & Minimalist Low-RAM Profile
    # Automatically activates when available RAM <= 2GB or memory load >= 75% or total RAM <= 6.5GB
    if ram_gb <= 4.0 or avail_gb <= 2.0 or mem_load >= 75 or ram_gb <= 6.5:
        flags.extend([
            "--renderer-process-limit=2",
            "--enable-low-end-device-mode",
            "--js-flags=--max-old-space-size=128 --optimize-for-size --expose-gc",
            "--disk-cache-size=33554432",
            "--media-cache-size=16777216",
            "--num-raster-threads=2",
            "--enable-accelerated-video-decode",
            "--disable-site-isolation-trials",
            "--disable-background-networking",
            "--disable-component-update",
            "--disable-domain-reliability",
            "--disable-dev-shm-usage",
            "--disable-speech-api",
            "--disable-speech-synthesis-api",
            "--disable-sync",
            "--disable-breakpad",
            "--disable-hang-monitor",
            "--disable-cloud-import",
            "--disable-default-apps",
            "--no-pings",
            "--enable-features=SmoothScrolling,ParallelDownloading,WebAssemblyLazyCompilation,PaintHolding,LowEndDeviceMode",
            "--disable-features=AudioServiceOutOfProcess,TranslateUI,OptimizationHints,MediaRouter,DirectCompositionVideoOverlays,BackForwardCache,CalculateNativeWinOcclusion,InterestFeedContentSuggestions,SubresourceRedirect,NotificationTriggers"
        ])
    elif ram_gb <= 8.0:
        flags.extend([
            "--renderer-process-limit=3",
            "--enable-low-end-device-mode",
            "--js-flags=--max-old-space-size=256 --optimize-for-size",
            "--disk-cache-size=33554432",
            "--media-cache-size=16777216",
            "--num-raster-threads=2",
            "--disable-background-networking",
            "--disable-dev-shm-usage",
            "--enable-features=SmoothScrolling,ParallelDownloading,WebAssemblyLazyCompilation,PaintHolding,LowEndDeviceMode",
            "--disable-features=AudioServiceOutOfProcess,TranslateUI,OptimizationHints,MediaRouter,DirectCompositionVideoOverlays,BackForwardCache"
        ])
    else:
        flags.extend([
            "--renderer-process-limit=4",
            "--js-flags=--max-old-space-size=768",
            "--num-raster-threads=2",
        ])

    os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = " ".join(flags)

_configure_chromium_flags()

def _register_chrome_widevine_cdm():
    """Auto-detect and register Widevine CDM from Google Chrome for protected media playback."""
    # Note: Disabled by default to prevent ABI mismatches between Chrome 155 and QtWebEngine Chrome 140
    pass

# _register_chrome_widevine_cdm()


def get_app_dir():
    if getattr(sys, "frozen", False):
        return getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.dirname(os.path.abspath(__file__))

app_dir = get_app_dir()

# Add project root / extracted bundle to sys.path
sys.path.insert(0, app_dir)

# CRITICAL: Configure QtWebEngine paths for frozen environment before importing QWebEngineView
if getattr(sys, "frozen", False):
    candidates = [
        os.path.join(app_dir, "PyQt6", "Qt6", "bin", "QtWebEngineProcess.exe"),
        os.path.join(app_dir, "QtWebEngineProcess.exe"),
        os.path.join(app_dir, "PyQt6", "QtWebEngineProcess.exe"),
    ]
    for c in candidates:
        if os.path.exists(c):
            os.environ["QTWEBENGINEPROCESS_PATH"] = c
            break

    res_candidates = [
        os.path.join(app_dir, "PyQt6", "Qt6", "resources"),
        os.path.join(app_dir, "resources"),
    ]
    for r in res_candidates:
        if os.path.exists(r):
            os.environ["QTWEBENGINE_RESOURCES_PATH"] = r
            break

    loc_candidates = [
        os.path.join(app_dir, "PyQt6", "Qt6", "translations", "qtwebengine_locales"),
        os.path.join(app_dir, "translations", "qtwebengine_locales"),
    ]
    for l in loc_candidates:
        if os.path.exists(l):
            os.environ["QTWEBENGINE_LOCALES_PATH"] = l
            break

# CRITICAL: Import QtWebEngineWidgets BEFORE creating QApplication instance
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineUrlScheme
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt

# Register xbrowser custom scheme so Chromium recognizes it as a valid local scheme
_xb_scheme = QWebEngineUrlScheme(b"xbrowser")
_xb_scheme.setFlags(
    QWebEngineUrlScheme.Flag.LocalScheme |
    QWebEngineUrlScheme.Flag.LocalAccessAllowed |
    QWebEngineUrlScheme.Flag.SecureScheme
)
QWebEngineUrlScheme.registerScheme(_xb_scheme)

from src.main_window import MainWindow
from src.extensions import ExtensionEngine


def parse_args():
    parser = argparse.ArgumentParser(description="XBrowser: Tor + Brave + Opera Hybrid Browser")
    parser.add_argument("url", nargs="?", default="", help="Initial URL or search query to open")
    parser.add_argument("--tor", action="store_true", help="Force Tor Network routing on launch")
    parser.add_argument("--workspace", default="", help="Initial workspace to activate (Personal, Tor Privacy, Work)")
    return parser.parse_args()


def load_default_extensions():
    """Auto-loads built-in sample extensions if not already present."""
    engine = ExtensionEngine()
    base_dir = os.path.join(get_app_dir(), "assets", "default_extensions")
    for sub in ["dark_mode_mini", "privacy_shield_helper"]:
        p = os.path.join(base_dir, sub)
        if os.path.isdir(p):
            # Demo extensions like dark_mode_mini should not be enabled by default
            is_dark_mini = (sub == "dark_mode_mini")
            engine.load_unpacked(p, initial_enabled=(not is_dark_mini))


def safe_excepthook(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    import traceback
    err_str = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    print(f"[XBrowser Caught Unhandled Exception]\n{err_str}", file=sys.stderr)


sys.excepthook = safe_excepthook


def main():
    args = parse_args()

    app = QApplication(sys.argv)
    app.setApplicationName("XBrowser")
    app.setApplicationDisplayName("")

    # Set Application Icon
    icon_path = os.path.join(get_app_dir(), "assets", "xbrowser_icon.ico")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    # Preload default extensions
    load_default_extensions()

    # Launch Main Window
    window = MainWindow(start_url=args.url)
    if os.path.exists(icon_path):
        window.setWindowIcon(QIcon(icon_path))

    if args.tor:
        window.tor_engine.enable_tor(True)

    if args.workspace:
        window.ws_manager.set_active_workspace(args.workspace)

    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
