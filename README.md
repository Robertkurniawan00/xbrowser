<div align="center">

  <img src="assets/xbrowser_logo.png" width="120" alt="XBrowser Logo" />

  # XBrowser

  <p>Privacy-hardened desktop browser built with Python, PyQt6, and QtWebEngine (Chromium).</p>

  [![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
  [![GUI](https://img.shields.io/badge/GUI-PyQt6%20%2F%20Qt6-green.svg)](https://riverbankcomputing.com/software/pyqt/)
  [![Engine](https://img.shields.io/badge/Engine-QtWebEngine%20Chromium-orange.svg)](https://wiki.qt.io/QtWebEngine)
  [![Platform](https://img.shields.io/badge/Platform-Windows%2010%20%7C%2011-0078D6.svg)](https://www.microsoft.com/windows)
  [![License](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)

</div>

---

XBrowser is a lightweight desktop web browser designed for local privacy control, multi-session compartmentalization, and minimal resource usage.

### Core Capabilities

- **Tor Proxy Routing**: Built-in SOCKS5 proxy integration for anonymous browsing and direct `.onion` hidden service resolution with circuit status monitoring.
- **Content Shields**: Local ad blocking, tracker interception, WebRTC IP leak protection, and customizable DNS-over-HTTPS (DoH) providers (Cloudflare, Quad9, AdGuard, Google).
- **Workspace Isolation**: Multi-session containers (Personal, Tor Privacy, Work) with isolated cookie stores, browser caches, and local storage instances.
- **Extension Engine**: Supports loading unpacked Manifest V2 and V3 extensions with `chrome.*` and `browser.*` runtime APIs.
- **Resource Management**: Dynamic Chromium flag optimization, active memory working-set trimming, and background process management for low-RAM systems.

---

## Key Features

| Area | Functionality |
| :--- | :--- |
| **Privacy & Security** | Integrated Tor network proxy, WebRTC IP leak prevention, phishing domain blocker, encrypted password vault. |
| **Workspaces & Tabs** | Isolated workspace containers, dual-tab split view, speed dial dashboard, full-text history search. |
| **Media Playback** | Native YouTube ad blocking, picture-in-picture (PiP) window, GPU-accelerated video decoding. |
| **Extensions** | Manifest V2/V3 extension loader, custom content script injection, toolbar action popup support. |
| **Performance** | Memory footprint trimming via Win32 APIs, renderer process limits, background tab throttling. |

---

## Keyboard Shortcuts

| Shortcut | Action |
| :--- | :--- |
| `Ctrl + T` | Open new tab |
| `Ctrl + W` | Close current tab |
| `Ctrl + Shift + T` | Reopen last closed tab |
| `Ctrl + Tab` / `Ctrl + Shift + Tab` | Next / previous tab |
| `Ctrl + H` | Toggle history drawer |
| `Ctrl + Shift + P` | Open Command Palette |
| `Ctrl + U` | View page source in new tab |
| `F11` | Toggle fullscreen mode |
| `F12` | Inspect Element / Developer Tools |
| `Ctrl + +` / `Ctrl + -` / `Ctrl + 0` | Zoom in / Zoom out / Reset zoom level |

---

## Installation & Running

### Requirements
- Python 3.10 or later
- Windows 10 / 11

### Setup
```bash
git clone https://github.com/Robertkurniawan00/xbrowser.git
cd xbrowser
pip install -r requirements.txt
python main.py
```

### Command Line Options
```bash
# Open specific URL
python main.py https://duckduckgo.com

# Launch with Tor Network routing enabled
python main.py --tor

# Launch in a specific workspace container
python main.py --workspace="Tor Privacy"
```

---

## Building Executable

To compile a standalone Windows executable (`dist/XBrowser/XBrowser.exe`):

```bash
python build_exe.py
```

The script builds the standalone application with PyInstaller, bundles the Tor runtime and icon assets, and updates Windows shortcut associations.

---

## License

This project is licensed under the [MIT License](LICENSE).
