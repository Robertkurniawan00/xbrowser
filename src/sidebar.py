"""
XBrowser Sidebar & Drawer Subsystem
Features:
- Expandable & resizable Web Panel Drawer (drag border or toggle expand button)
- Responsive WhatsApp Web viewport with auto QR code fit-to-screen
- Quick Notes with persistent markdown storage
- History viewer panel with working history clearing
"""
import os
from typing import Optional, Union

from PyQt6.QtCore import Qt, pyqtSignal, QUrl, QTimer, QSize, QPoint
from PyQt6.QtWidgets import (
    QFrame, QHBoxLayout, QVBoxLayout, QPushButton, QLabel, QLineEdit,
    QListWidget, QListWidgetItem, QStackedWidget, QTextEdit, QWidget,
    QMessageBox, QMenu, QApplication
)
from PyQt6.QtGui import QIcon
from PyQt6.QtWebEngineWidgets import QWebEngineView

from . import _sidebar_orig as _orig

# Re-export unchanged symbols
NOTES_FILE = _orig.NOTES_FILE
SidebarButton = _orig.SidebarButton
QuickNotesWidget = _orig.QuickNotesWidget
HistoryPanelWidget = _orig.HistoryPanelWidget
WorkspaceManager = _orig.WorkspaceManager
get_icon = _orig.get_icon


class WebPanelDrawer(_orig.WebPanelDrawer):
    """
    Enhanced WebPanelDrawer supporting:
    - Width expansion / shrinkage toggle button
    - Interactive edge resizing by dragging the right border
    - Responsive WhatsApp Web viewport with QR-code fit
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.normal_width = 540
        self.expanded_width = 820
        self.is_expanded = False
        self._dragging_edge = False
        self._drag_start_x = 0
        self._drag_start_w = self.normal_width

        self.setFixedWidth(self.normal_width)
        self.setMinimumWidth(380)
        self.setMaximumWidth(1100)
        self.setMouseTracking(True)

        self._enhance_header_ui()

    def _enhance_header_ui(self):
        if hasattr(self, "hdr") and self.hdr.layout():
            h_layout = self.hdr.layout()

            self.expand_btn = QPushButton("⤢")
            self.expand_btn.setFixedSize(26, 26)
            self.expand_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            self.expand_btn.setToolTip("Perluas / Perkecil Jendela Panel (Toggle Width)")
            self.expand_btn.setStyleSheet('''
                QPushButton {
                    background: transparent;
                    border: none;
                    color: #94a3b8;
                    font-size: 15px;
                    font-weight: bold;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #334155;
                    color: #f8fafc;
                }
            ''')
            self.expand_btn.clicked.connect(self.toggle_expanded)

            idx = max(0, h_layout.count() - 1)
            h_layout.insertWidget(idx, self.expand_btn)

    def toggle_expanded(self):
        if self.is_expanded:
            self.setFixedWidth(self.normal_width)
            self.expand_btn.setText("⤢")
            self.expand_btn.setToolTip("Perluas Jendela Panel")
            self.is_expanded = False
        else:
            self.setFixedWidth(self.expanded_width)
            self.expand_btn.setText("⤡")
            self.expand_btn.setToolTip("Perkecil Jendela Panel")
            self.is_expanded = True

    def show_panel(self, panel_id: str):
        super().show_panel(panel_id)

        # Specialized handling for WhatsApp Web
        if panel_id == "wa":
            if self.width() < 540:
                self.setFixedWidth(self.normal_width)

            if hasattr(self, "wa_view") and self.wa_view:
                self.wa_view.setZoomFactor(0.85)

                def _inject_wa_fit():
                    fit_script = """
                    (function() {
                        const styleId = 'xb_wa_responsive_style';
                        if (document.getElementById(styleId)) return;
                        const style = document.createElement('style');
                        style.id = styleId;
                        style.textContent = `
                            /* WhatsApp Web Landing QR Fit */
                            div[data-testid="qrcode"], canvas[aria-label*="Scan"], canvas {
                                max-width: 100% !important;
                                height: auto !important;
                                display: block !important;
                                margin: 0 auto !important;
                            }
                            body {
                                overflow-x: hidden !important;
                            }
                            ._1jJ70, ._2A5aO, .landing-window, .landing-wrapper {
                                min-width: auto !important;
                                width: 100% !important;
                                padding: 12px !important;
                            }
                        `;
                        (document.head || document.documentElement).appendChild(style);
                    })();
                    """
                    self.wa_view.page().runJavaScript(fit_script)

                try:
                    self.wa_view.loadFinished.disconnect(_inject_wa_fit)
                except Exception:
                    pass
                self.wa_view.loadFinished.connect(_inject_wa_fit)
                _inject_wa_fit()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and event.pos().x() >= self.width() - 8:
            self._dragging_edge = True
            self._drag_start_x = event.globalPosition().x()
            self._drag_start_w = self.width()
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._dragging_edge:
            delta = event.globalPosition().x() - self._drag_start_x
            new_w = int(max(380, min(1050, self._drag_start_w + delta)))
            self.setFixedWidth(new_w)
            self.normal_width = new_w
            event.accept()
            return

        if event.pos().x() >= self.width() - 8:
            self.setCursor(Qt.CursorShape.SizeHorCursor)
        else:
            self.unsetCursor()
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self._dragging_edge:
            self._dragging_edge = False
            self.unsetCursor()
            event.accept()
            return
        super().mouseReleaseEvent(event)


class SidebarWidget(_orig.SidebarWidget):
    pass
