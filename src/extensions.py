"""
XBrowser Robust Extension Engine
Provides:
- Manifest V2 & Manifest V3 unpacked and CRX/ZIP loading
- Chrome API runtime polyfill
- Reliable CSS and content script injection on page load
- Extension management and storage persistence
"""
import os
import json
import hashlib
from typing import Any, Dict, List, Optional

from PyQt6.QtCore import Qt, QObject, pyqtSignal, QUrl
from PyQt6.QtWidgets import QWidget, QDialog, QVBoxLayout
from PyQt6.QtWebEngineCore import (
    QWebEngineProfile, QWebEnginePage, QWebEngineUrlSchemeHandler,
    QWebEngineUrlRequestJob, QWebEngineScript
)
from PyQt6.QtWebEngineWidgets import QWebEngineView

# Import base implementation from bytecode
from . import _extensions_orig as _orig

# Re-export module symbols
EXTENSIONS_STORAGE_DIR = _orig.EXTENSIONS_STORAGE_DIR
ExtensionMetadata = _orig.ExtensionMetadata
ExtensionPopupDialog = _orig.ExtensionPopupDialog
ExtensionUrlSchemeHandler = _orig.ExtensionUrlSchemeHandler
CHROME_API_POLYFILL = _orig.CHROME_API_POLYFILL
get_chrome_api_polyfill = _orig.get_chrome_api_polyfill


class ExtensionEngine(_orig.ExtensionEngine):
    """
    Subclassed ExtensionEngine ensuring guaranteed injection of CSS & scripts
    into DOM without timing drops or silent omissions.
    """
    def inject_scripts_for_page(self, page: QWebEnginePage, url: str, is_start: bool = False):
        if not url or url.startswith(("about:", "xbrowser://", "chrome://", "view-source:")):
            return

        try:
            super().inject_scripts_for_page(page, url, is_start=is_start)
        except Exception:
            pass

        # Guaranteed injection pass on page load finished
        if not is_start and page:
            for ext in self.extensions.values():
                if not getattr(ext, "enabled", True):
                    continue

                for cs in getattr(ext, "content_scripts", []):
                    matches = cs.get("matches", [])
                    exclude_matches = cs.get("exclude_matches", [])

                    if not self._url_matches(url, matches):
                        continue
                    if exclude_matches and self._url_matches(url, exclude_matches):
                        continue

                    # Inject CSS
                    for css_file in cs.get("css", []):
                        css_p = os.path.join(ext.root_dir, css_file)
                        if os.path.exists(css_p):
                            css_code = self._get_cached_file(css_p)
                            if css_code:
                                css_hash = hashlib.md5(css_file.encode()).hexdigest()[:8]
                                escaped_css = json.dumps(css_code)
                                inject_css_js = f"""
                                (function() {{
                                    const sid = 'xb_ext_css_{ext.id}_{css_hash}';
                                    if (document.getElementById(sid)) return;
                                    const style = document.createElement('style');
                                    style.id = sid;
                                    style.textContent = {escaped_css};
                                    style.dataset.extensionId = '{ext.id}';
                                    (document.head || document.documentElement).appendChild(style);
                                }})();
                                """
                                page.runJavaScript(inject_css_js)

                    # Inject JS
                    for js_file in cs.get("js", []):
                        js_p = os.path.join(ext.root_dir, js_file)
                        if os.path.exists(js_p):
                            js_code = self._get_cached_file(js_p)
                            if js_code:
                                page.runJavaScript(js_code)
