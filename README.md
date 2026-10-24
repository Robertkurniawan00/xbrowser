# XBrowser

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![GUI Framework](https://img.shields.io/badge/GUI-PyQt6%20%2F%20Qt6-green.svg)](https://riverbankcomputing.com/software/pyqt/)
[![Engine](https://img.shields.io/badge/Engine-QtWebEngine%20(Chromium)-orange.svg)](https://wiki.qt.io/QtWebEngine)
[![Platform](https://img.shields.io/badge/Platform-Windows%2010%20%2F%2011-0078D6.svg)](https://www.microsoft.com/windows)
[![License](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)

**XBrowser** is a fast, ultra-lightweight, and privacy-focused desktop browser built with Python and QtWebEngine (Chromium). It unites the best capabilities of three pioneering browsers into a cohesive desktop experience:

* 🧅 **Tor Browser**: SOCKS5 onion routing, `.onion` domain resolution, visual circuit inspector, anti-fingerprinting canvas/WebGL farbling, and security level controls.
* 🛡️ **Brave Shields**: Native ad and tracker blocking, omnibox shields popover, per-site toggles, bandwidth/time savings metrics, and privacy DNS-over-HTTPS (DoH).
* 🎭 **Opera Workspaces**: Docked left sidebar, isolated multi-session workspaces (Personal, Tor Privacy, Work & Tools), flyout web panels (AI Assistant, WhatsApp, Quick Notes, History), and Dual-Tab Split View.
* 🧩 **Chrome & Opera Extension Engine**: Full support for Manifest V2 and V3 extensions, runtime polyfills (`chrome.*` and `browser.*`), automatic content script injection, and popup frames.
* ⚡ **Resource Limiter & ProBalance**: Auto-trims memory working sets, snoozes inactive background tabs, and caps renderer memory usage for smooth multitasking on low-RAM machines.

---

## Key Features

| Category | Capabilities |
| :--- | :--- |
| **Privacy & Security** | Built-in Tor proxy integration, WebRTC IP leak guard, DNS-over-HTTPS presets (Cloudflare, AdGuard, Quad9, Google), phishing/malware domain interceptor, anti-fingerprint canvas farbling. |
| **Productivity** | Isolated workspaces with separate cookies/cache, Dual-Tab Split View, quick sidebar notes, full browsing history drawer, speed dial dashboard. |
| **Media & Display** | Native YouTube adblocker & error-recovery engine, picture-in-picture (PiP) window, hardware-accelerated video decoding with sRGB profile locking, native dark mode support. |
| **Extensions** | Load unpacked extensions (`manifest.json`), install `.crx`/`.zip` archives, toolbar action icons, and extension manager. |
| **Efficiency** | Dynamic Chromium flag tuning, aggressive memory pruning via Win32 working set trim, background CPU throttling. |

---

## Keyboard Shortcuts

| Shortcut | Action |
| :--- | :--- |
| `Ctrl + T` | Open new tab |
| `Ctrl + W` | Close current tab |
| `Ctrl + Shift + T` | Reopen last closed tab |
| `Ctrl + Tab` / `Ctrl + Shift + Tab` | Next / previous tab |
| `Ctrl + H` | Open history panel |
| `Ctrl + Shift + P` | Open Command Palette |
| `Alt + A` | Open AI Page Summarizer |
| `Ctrl + U` | View page source in new tab |
| `F11` | Toggle fullscreen mode |
| `F12` | Inspect Element / DevTools |
| `Ctrl + +` / `Ctrl + -` / `Ctrl + 0` | Zoom in / Zoom out / Reset zoom |

---

## Installation & Running

1. Clone or download this repository.

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Launch the browser:
   ```bash
   python main.py
   ```

**Optional command-line flags:**
```bash
# Open specific URL
python main.py https://duckduckgo.com

# Start directly with Tor Network enabled
python main.py --tor

# Start in a specific workspace
python main.py --workspace="Tor Privacy"
```

---

## License

This project is licensed under the [MIT License](LICENSE).
