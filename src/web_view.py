"""
XBrowser Web View & Web Page Architecture
Provides:
- Secure Chromium page runtime with hardened sandboxing
- HTTPS-First navigation upgrades & threat filtering
- WebRTC IP leak guard & DNS prefetch prevention
- Chrome DevTools inspection & view-source integrations
- Tor network onion routing hooks
- Guaranteed extension script & cosmetic styling injection
"""

import os
import sys
from typing import Optional

from PyQt6.QtCore import Qt, QUrl, QTimer, pyqtSignal
from PyQt6.QtWidgets import QMessageBox, QInputDialog, QWidget
from PyQt6.QtGui import QColor, QAction
from PyQt6.QtWebEngineCore import (
    QWebEnginePage, QWebEngineProfile, QWebEngineSettings,
    QWebEngineFullScreenRequest
)
from PyQt6.QtWebEngineWidgets import QWebEngineView

from src.icons import get_icon
from src.speed_dial import generate_speed_dial_html
from src.extensions import ExtensionEngine
from src.tor_engine import TorEngine
from src.devtools import DevToolsManager


class BrowserWebPage(QWebEnginePage):
    """
    Hardened QWebEnginePage with strict security policies,
    credential leak protection, and phishing detection.
    """
    internal_scheme_requested = pyqtSignal(str)

    def __init__(self, profile: Optional[QWebEngineProfile] = None, parent: Optional[QWidget] = None):
        super().__init__(profile, parent)
        self.setBackgroundColor(QColor('#0b1120'))

        # Security hardening: Prevent common Chromium-based attack vectors
        ws = self.settings()
        ws.setAttribute(QWebEngineSettings.WebAttribute.AllowRunningInsecureContent, False)
        ws.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, False)
        ws.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, False)
        ws.setAttribute(QWebEngineSettings.WebAttribute.WebRTCPublicInterfacesOnly, True)
        ws.setAttribute(QWebEngineSettings.WebAttribute.DnsPrefetchEnabled, False)
        ws.setAttribute(QWebEngineSettings.WebAttribute.HyperlinkAuditingEnabled, False)

    def acceptNavigationRequest(self, url: QUrl, nav_type: QWebEnginePage.NavigationType, is_main_frame: bool) -> bool:
        url_str = url.toString()

        # Handle internal xbrowser:// scheme navigation
        if url.scheme() == 'xbrowser':
            cur_url_str = self.url().toString()
            cur_scheme = self.url().scheme()
            opener_url = getattr(self, '_opener_url', None)
            opener_scheme = opener_url.scheme() if (opener_url and opener_url.isValid()) else ''

            is_untrusted_origin = (
                (cur_scheme and cur_scheme not in ('xbrowser', 'about', '') and cur_url_str not in ('', 'about:blank'))
                or (opener_scheme and opener_scheme not in ('xbrowser', 'about', ''))
            )

            if is_untrusted_origin:
                # Prevent untrusted web pages from triggering local media execution
                if url_str.startswith('xbrowser://play-media'):
                    low = url_str.lower()
                    if 'url=file' in low or 'file%3a' in low or 'file://' in low:
                        return False
                elif not url_str.startswith('xbrowser://speeddial'):
                    return False

            if url_str.startswith('xbrowser://threat-blocked'):
                return True

            QTimer.singleShot(0, lambda u=url_str: self.internal_scheme_requested.emit(u))
            return False

        # Main frame checks: Phishing & Malicious domain filter
        if is_main_frame and not url_str.startswith(('about:', 'view-source:', 'chrome://')):
            from src.phishing_detector import get_phishing_detector, generate_threat_warning_html
            report = get_phishing_detector().check_url(url_str)
            if report.is_threat:
                html = generate_threat_warning_html(report, url_str)
                QTimer.singleShot(0, lambda h=html: self.setHtml(h, QUrl('xbrowser://threat-blocked')))
                return False

            # HTTPS-First: Auto-upgrade public HTTP navigations to HTTPS
            if url.scheme() == 'http':
                host = url.host().lower()
                is_local = (
                    host in ('localhost', '127.0.0.1', '::1')
                    or host.endswith('.onion')
                    or host.startswith(('192.168.', '10.', '172.16.', '172.17.', '172.18.', '172.19.',
                                       '172.20.', '172.21.', '172.22.', '172.23.', '172.24.', '172.25.',
                                       '172.26.', '172.27.', '172.28.', '172.29.', '172.30.', '172.31.'))
                )
                if not is_local:
                    upgraded_url = QUrl(url)
                    upgraded_url.setScheme('https')
                    QTimer.singleShot(0, lambda u=upgraded_url: self.setUrl(u))
                    return False

        return super().acceptNavigationRequest(url, nav_type, is_main_frame)

    def javaScriptAlert(self, securityOrigin: QUrl, msg: str):
        host = securityOrigin.host()
        title = f"Pemberitahuan - {host}" if (host and not host.startswith('xbrowser')) else "Pemberitahuan"
        dlg = QMessageBox(self.view())
        dlg.setIcon(QMessageBox.Icon.Information)
        dlg.setWindowTitle(title)
        dlg.setText(msg)
        dlg.setStandardButtons(QMessageBox.StandardButton.Ok)
        ok_btn = dlg.button(QMessageBox.StandardButton.Ok)
        if ok_btn:
            ok_btn.setText("OK")
        dlg.exec()

    def javaScriptConfirm(self, securityOrigin: QUrl, msg: str) -> bool:
        host = securityOrigin.host()
        title = f"Konfirmasi - {host}" if (host and not host.startswith('xbrowser')) else "Konfirmasi"
        dlg = QMessageBox(self.view())
        dlg.setIcon(QMessageBox.Icon.Question)
        dlg.setWindowTitle(title)
        dlg.setText(msg)
        dlg.setStandardButtons(QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
        ok_btn = dlg.button(QMessageBox.StandardButton.Ok)
        if ok_btn:
            ok_btn.setText("Hapus" if "hapus" in msg.lower() else "Lanjutkan")
        cancel_btn = dlg.button(QMessageBox.StandardButton.Cancel)
        if cancel_btn:
            cancel_btn.setText("Batal")
        return dlg.exec() == QMessageBox.StandardButton.Ok

    def javaScriptPrompt(self, securityOrigin: QUrl, msg: str, defaultValue: str) -> tuple:
        host = securityOrigin.host()
        title = f"Masukan - {host}" if (host and not host.startswith('xbrowser')) else "Masukan"
        val, ok = QInputDialog.getText(self.view(), title, msg, text=defaultValue)
        return (val, ok)

    def certificateError(self, error) -> bool:
        host = error.url().host()
        is_local = (
            host in ('localhost', '127.0.0.1', '::1')
            or host.startswith(('192.168.', '10.', '172.16.', '172.17.', '172.18.', '172.19.',
                               '172.20.', '172.21.', '172.22.', '172.23.', '172.24.', '172.25.',
                               '172.26.', '172.27.', '172.28.', '172.29.', '172.30.', '172.31.'))
        )
        if is_local:
            error.acceptCertificate()
            return True
        return super().certificateError(error)


class BrowserWebView(QWebEngineView):
    """
    Core interactive browser view supporting zoom controls,
    injected extension scripts, YouTube adblocking, and Tor routing.
    """
    internal_scheme_requested = pyqtSignal(str)
    onion_detected = pyqtSignal(str)
    new_tab_requested = pyqtSignal(QUrl)
    fullscreen_requested = pyqtSignal(bool)
    audio_state_changed = pyqtSignal(bool)

    def __init__(self, profile: Optional[QWebEngineProfile] = None, tor_engine: Optional[TorEngine] = None, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.profile = profile
        self.tor_engine = tor_engine
        self.ext_engine = ExtensionEngine()
        self.tab_widget = parent if (parent and hasattr(parent, 'add_new_tab')) else None

        page = BrowserWebPage(profile, self)
        page.internal_scheme_requested.connect(self.internal_scheme_requested.emit)
        self.setPage(page)
        self.setZoomFactor(1.0)

        self.loadFinished.connect(self._on_load_finished)
        self.urlChanged.connect(self._on_url_changed)
        page.fullScreenRequested.connect(self._on_fullscreen_requested)
        page.audioMutedChanged.connect(lambda: self.audio_state_changed.emit(self.page().recentlyAudible()))
        page.recentlyAudibleChanged.connect(self.audio_state_changed.emit)

    def load_start_page(self):
        self.page().setBackgroundColor(QColor('#0b1120'))
        html = generate_speed_dial_html()
        self.setHtml(html, QUrl('xbrowser://speeddial'))
        self.setZoomFactor(1.0)

    def zoom_in(self):
        cur = round(self.zoomFactor(), 2)
        if cur < 3.0:
            self.setZoomFactor(round(cur + 0.1, 2))

    def zoom_out(self):
        cur = round(self.zoomFactor(), 2)
        if cur > 0.4:
            self.setZoomFactor(round(cur - 0.1, 2))

    def reset_zoom(self):
        self.setZoomFactor(1.0)

    def get_zoom_percent(self) -> int:
        return int(round(self.zoomFactor() * 100))

    def _on_url_changed(self, qurl: QUrl):
        url_str = qurl.toString()
        self.page().setBackgroundColor(QColor('#0b1120'))

        if '.onion' in url_str:
            self.onion_detected.emit(url_str)
            if self.tor_engine and not self.tor_engine.is_connected:
                self.tor_engine.apply_to_profile(self.profile, True)

        self.ext_engine.inject_scripts_for_page(self.page(), url_str, is_start=True)

    def _on_load_finished(self, success: bool):
        if not success:
            return

        cur_url = self.url().toString()
        self.ext_engine.inject_scripts_for_page(self.page(), cur_url, is_start=False)

        if 'youtube.com' in cur_url:
            from src.youtube_adblock import YOUTUBE_ADBLOCK_JS
            self.page().runJavaScript(YOUTUBE_ADBLOCK_JS)

        from src.resource_limiter import ResourceLimiter
        QTimer.singleShot(2500, lambda: ResourceLimiter.get_instance().trim_memory())

    def _on_fullscreen_requested(self, request: QWebEngineFullScreenRequest):
        request.accept()
        self.fullscreen_requested.emit(request.toggleOn())

    def createWindow(self, window_type: QWebEnginePage.WebWindowType):
        if hasattr(self, 'tab_widget') and self.tab_widget:
            new_view = self.tab_widget.add_new_tab(load_start=False)
            if new_view and hasattr(new_view, 'page'):
                new_view.page()._opener_url = self.url()
            return new_view
        return super().createWindow(window_type)

    def contextMenuEvent(self, event):
        menu = self.createStandardContextMenu()
        menu.addSeparator()

        act_inspect = QAction(get_icon('inspect', '#38bdf8', 14), 'Inspeksi Elemen (Inspect Element)', self)
        act_inspect.setShortcut('F12')
        act_inspect.triggered.connect(self._inspect_element)
        menu.addAction(act_inspect)

        act_source = QAction(get_icon('code', '#94a3b8', 14), 'Lihat Sumber Halaman (View Source)', self)
        act_source.setShortcut('Ctrl+U')
        act_source.triggered.connect(self._view_page_source)
        menu.addAction(act_source)

        act_onion = QAction(get_icon('onion', '#a78bfa', 14), 'Rute Ulang via Tor Sirkuit Baru', self)
        act_onion.triggered.connect(lambda: self.tor_engine.request_new_identity(self.profile) if self.tor_engine else None)
        menu.addAction(act_onion)

        menu.exec(event.globalPos())

    def _inspect_element(self):
        DevToolsManager.get_instance().inspect_element(self)

    def _view_page_source(self):
        cur = self.url().toString()
        if cur and not cur.startswith('view-source:'):
            self.new_tab_requested.emit(QUrl(f'view-source:{cur}'))
