"""
XBrowser Minimalist Modern Speed Dial (Start Page)
Provides:
- High-contrast responsive layout for Dark Mode and Light Mode
- Interactive Speed Dial Tiles with authentic Brand Icons
- Search bar with quick search engine integration
- Custom bear mascot branding
"""
import sys
import os
import re
import base64

# Import original bytecode implementation
from . import _speed_dial_orig as _orig

# Re-export module globals
BRAND_ICONS_DATA_URI = _orig.BRAND_ICONS_DATA_URI
SEARCH_ENGINES = _orig.SEARCH_ENGINES
TILE_SVGS = _orig.TILE_SVGS
WALLPAPER_STYLES = _orig.WALLPAPER_STYLES
SettingsManager = _orig.SettingsManager
categorize_bookmark = _orig.categorize_bookmark

# Prepare bear logo
_app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_logo_candidates = [
    os.path.join(_app_dir, "assets", "xbrowser_logo.png"),
    os.path.join(_app_dir, "_internal", "assets", "xbrowser_logo.png"),
    r"C:\Users\Roku\AppData\Local\Programs\XBrowser\_internal\assets\xbrowser_logo.png",
]

_b64_logo = ""
for lp in _logo_candidates:
    if os.path.exists(lp):
        try:
            with open(lp, "rb") as f:
                _b64_logo = base64.b64encode(f.read()).decode("ascii")
            if _b64_logo:
                break
        except Exception:
            pass

_NEW_BRAND_HTML = f'''<div class="brand-icon">
                <img src="data:image/png;base64,{_b64_logo}" width="42" height="42" alt="XBrowser Bear Mascot" style="object-fit:contain; display:block; filter: drop-shadow(0 2px 8px rgba(0,0,0,0.3));" />
            </div>'''

_BRAND_SVG_PATTERN = re.compile(r'<div class="brand-icon">\s*<svg[^>]*>.*?</svg>\s*</div>', re.DOTALL)

SPEED_DIAL_HTML_TEMPLATE = _BRAND_SVG_PATTERN.sub(_NEW_BRAND_HTML, _orig.SPEED_DIAL_HTML_TEMPLATE)


def generate_speed_dial_html() -> str:
    html = _orig.generate_speed_dial_html()
    if _b64_logo:
        html = _BRAND_SVG_PATTERN.sub(_NEW_BRAND_HTML, html)
    return html
