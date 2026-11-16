"""
XBrowser Features Hub:
- Interactive Bookmark Bar with full Context Menu (Open, Open in New Tab, Copy URL, Delete Bookmark)
- History Viewer Dialog with item deletion and complete history clear
- Clear Browsing Data Dialog with clean profile cache/cookie/history purge
- Tab Search Dialog and Media Sniffer Dialog
"""
import os
from typing import Optional

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QFrame, QHBoxLayout, QVBoxLayout, QPushButton, QLabel, QLineEdit,
    QListWidget, QListWidgetItem, QDialog, QMessageBox, QMenu, QCheckBox,
    QApplication, QWidget
)
from PyQt6.QtWebEngineCore import QWebEngineProfile

from .icons import get_icon
from .settings import SettingsManager

# Import complementary dialogs from original bytecode
from . import _features_hub_orig as _orig
TabSearchDialog = _orig.TabSearchDialog
MediaSnifferDialog = _orig.MediaSnifferDialog
MEDIA_SNIFFER_JS = getattr(_orig, "MEDIA_SNIFFER_JS", "")


class BookmarkBar(QFrame):
    open_url = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(30)
        self.is_dark = True
        self.settings = SettingsManager()
        self._build_ui()
        self.refresh_theme(True)

    def _build_ui(self):
        self.bar_layout = QHBoxLayout(self)
        self.bar_layout.setContentsMargins(8, 0, 8, 0)
        self.bar_layout.setSpacing(4)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_bar_context_menu)

    def refresh_bookmarks(self):
        if not hasattr(self, "bar_layout"):
            return

        # Clear existing buttons
        while self.bar_layout.count():
            item = self.bar_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        bms = self.settings.get("bookmarks") or []
        icon_col = "#94a3b8" if self.is_dark else "#475569"

        for bm in bms[:30]:
            title = bm.get("title", "Bookmark")
            url = bm.get("url", "#")
            btn = QPushButton(title)
            btn.setIcon(get_icon("globe", icon_col, 12))
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setToolTip(f"{title}\n{url}\n(Klik kanan untuk opsi / hapus)")
            btn.clicked.connect(lambda _, u=url: self.open_url.emit(u))

            # Enable custom context menu on each button
            btn.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            btn.customContextMenuRequested.connect(
                lambda pos, b=bm, b_btn=btn: self._show_bookmark_menu(pos, b, b_btn)
            )
            self.bar_layout.addWidget(btn)

        self.bar_layout.addStretch()

    def _show_bookmark_menu(self, pos, bm, btn_widget):
        menu = QMenu(self)
        self._apply_menu_style(menu)

        act_open = menu.addAction("Buka")
        act_new_tab = menu.addAction("Buka di Tab Baru")
        act_copy = menu.addAction("Salin Alamat Tautan")
        menu.addSeparator()
        act_delete = menu.addAction("Hapus Bookmark")

        global_pos = btn_widget.mapToGlobal(pos)
        selected = menu.exec(global_pos)

        url = bm.get("url", "")
        if selected == act_open and url:
            self.open_url.emit(url)
        elif selected == act_new_tab and url:
            parent = self.parent()
            if hasattr(parent, "tab_widget"):
                parent.tab_widget.add_new_tab(url)
            elif hasattr(parent, "_navigate_url"):
                parent._navigate_url(url, new_tab=True)
            else:
                self.open_url.emit(url)
        elif selected == act_copy and url:
            QApplication.clipboard().setText(url)
        elif selected == act_delete:
            self.settings.delete_bookmark(url)
            self.refresh_bookmarks()

            # Synchronize active speed dial startpage if open
            parent = self.parent()
            if hasattr(parent, "_active_view"):
                av = parent._active_view()
                if av and hasattr(av, "url") and av.url().toString().startswith("xbrowser://speeddial"):
                    av.load_start_page()

    def _show_bar_context_menu(self, pos):
        menu = QMenu(self)
        self._apply_menu_style(menu)

        act_add = menu.addAction("Tambah Halaman Ini ke Bookmark")
        menu.addSeparator()
        act_clear_all = menu.addAction("Hapus Semua Bookmark")

        global_pos = self.mapToGlobal(pos)
        selected = menu.exec(global_pos)

        if selected == act_add:
            parent = self.parent()
            if hasattr(parent, "_active_view"):
                view = parent._active_view()
                if view:
                    title = view.title() or "New Bookmark"
                    url = view.url().toString()
                    if url and not url.startswith("data:") and not url.startswith("about:"):
                        self.settings.add_bookmark(title, url)
                        self.refresh_bookmarks()
        elif selected == act_clear_all:
            reply = QMessageBox.question(
                self,
                "Hapus Semua Bookmark",
                "Apakah Anda yakin ingin menghapus seluruh bookmark pada bilah bookmark?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.settings.set("bookmarks", [])
                self.refresh_bookmarks()

    def _apply_menu_style(self, menu):
        if self.is_dark:
            menu.setStyleSheet('''
                QMenu {
                    background-color: #1e293b;
                    color: #f8fafc;
                    border: 1px solid #334155;
                    border-radius: 6px;
                    padding: 4px;
                }
                QMenu::item {
                    padding: 6px 14px;
                    border-radius: 4px;
                }
                QMenu::item:selected {
                    background-color: #0284c7;
                    color: #ffffff;
                }
                QMenu::separator {
                    height: 1px;
                    background: #334155;
                    margin: 4px 6px;
                }
            ''')
        else:
            menu.setStyleSheet('''
                QMenu {
                    background-color: #ffffff;
                    color: #0f172a;
                    border: 1px solid #cbd5e1;
                    border-radius: 6px;
                    padding: 4px;
                }
                QMenu::item {
                    padding: 6px 14px;
                    border-radius: 4px;
                }
                QMenu::item:selected {
                    background-color: #e0f2fe;
                    color: #0369a1;
                }
                QMenu::separator {
                    height: 1px;
                    background: #e2e8f0;
                    margin: 4px 6px;
                }
            ''')

    def refresh_theme(self, is_dark: bool):
        self.is_dark = is_dark
        bg = "#0b1120" if is_dark else "#f8fafc"
        border = "#1e293b" if is_dark else "#cbd5e1"
        col = "#cbd5e1" if is_dark else "#1e293b"
        hover_bg = "#1e293b" if is_dark else "#e2e8f0"
        hover_col = "#f8fafc" if is_dark else "#0f172a"

        self.setStyleSheet(f'''
            BookmarkBar {{
                background-color: {bg};
                border-bottom: 1px solid {border};
                padding: 0 8px;
            }}
            QPushButton {{
                background: transparent;
                border: none;
                border-radius: 4px;
                color: {col};
                font-size: 11px;
                padding: 2px 8px;
            }}
            QPushButton:hover {{
                background-color: {hover_bg};
                color: {hover_col};
            }}
        ''')
        self.refresh_bookmarks()


class HistoryViewerDialog(QDialog):
    open_url = pyqtSignal(str)

    def __init__(self, parent=None, is_dark=None):
        super().__init__(parent)
        if is_dark is None:
            self.is_dark = getattr(parent, "theme_manager", None) and parent.theme_manager.is_dark if parent else True
        else:
            self.is_dark = is_dark

        self.setWindowTitle("Riwayat Penjelajahan")
        self.resize(720, 500)
        self.settings = SettingsManager()

        bg = "#0f172a" if self.is_dark else "#ffffff"
        fg = "#f8fafc" if self.is_dark else "#0f172a"
        card_bg = "#1e293b" if self.is_dark else "#f8fafc"
        border = "#334155" if self.is_dark else "#cbd5e1"
        btn_bg = "#334155" if self.is_dark else "#e2e8f0"
        btn_fg = "white" if self.is_dark else "#0f172a"

        self.setStyleSheet(f'''
            QDialog {{
                background-color: {bg};
                color: {fg};
                font-family: 'Segoe UI', sans-serif;
            }}
            QLineEdit {{
                background-color: {card_bg};
                border: 1px solid {border};
                border-radius: 6px;
                padding: 6px 12px;
                color: {fg};
                font-size: 13px;
            }}
            QListWidget {{
                background-color: {card_bg};
                border: 1px solid {border};
                border-radius: 6px;
                color: {fg};
                font-size: 12px;
                outline: none;
            }}
            QListWidget::item {{
                padding: 8px 10px;
                border-bottom: 1px solid {border};
            }}
            QListWidget::item:selected {{
                background-color: #0284c7;
                color: white;
            }}
            QPushButton {{
                background-color: {btn_bg};
                color: {btn_fg};
                border: 1px solid {border};
                border-radius: 6px;
                padding: 6px 14px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: #0284c7;
                color: white;
            }}
        ''')
        self._build_ui()
        self._populate_history()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        header = QHBoxLayout()
        title_lbl = QLabel("Riwayat Penjelajahan")
        title_lbl.setStyleSheet("font-size: 16px; font-weight: bold; color: #38bdf8;")
        header.addWidget(title_lbl)
        header.addStretch()

        clear_btn = QPushButton("Hapus Seluruh Riwayat")
        clear_btn.setStyleSheet("background-color: #ef4444; color: white; border: none; font-weight: bold;")
        clear_btn.clicked.connect(self._clear_all)
        header.addWidget(clear_btn)
        layout.addLayout(header)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Cari judul atau URL...")
        self.search_input.textChanged.connect(self._filter_history)
        layout.addWidget(self.search_input)

        self.history_list = QListWidget()
        self.history_list.itemDoubleClicked.connect(self._on_item_clicked)
        self.history_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.history_list.customContextMenuRequested.connect(self._show_item_context_menu)
        layout.addWidget(self.history_list)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        close_btn = QPushButton("Tutup")
        close_btn.clicked.connect(self.accept)
        btn_row.addWidget(close_btn)
        layout.addLayout(btn_row)

    def _populate_history(self, filter_text=""):
        self.history_list.clear()
        hist = self.settings.get("history") or []
        ft = filter_text.strip().lower()

        for item in reversed(hist):
            title = item.get("title", "Untitled Page")
            url = item.get("url", "")
            time_str = item.get("timestamp", "")

            if ft and ft not in title.lower() and ft not in url.lower():
                continue

            display = f"[{time_str}]  {title} - {url}" if time_str else f"{title} - {url}"
            li = QListWidgetItem(display)
            li.setData(Qt.ItemDataRole.UserRole, url)
            li.setIcon(get_icon("globe", "#94a3b8", 14))
            self.history_list.addItem(li)

    def _filter_history(self, text):
        self._populate_history(text)

    def _on_item_clicked(self, item):
        url = item.data(Qt.ItemDataRole.UserRole)
        if url:
            self.open_url.emit(url)
            self.accept()

    def _show_item_context_menu(self, pos):
        item = self.history_list.itemAt(pos)
        if not item:
            return

        url = item.data(Qt.ItemDataRole.UserRole)
        menu = QMenu(self)
        menu.setStyleSheet('''
            QMenu {
                background-color: #1e293b;
                color: #f8fafc;
                border: 1px solid #334155;
                border-radius: 6px;
                padding: 4px;
            }
            QMenu::item:selected {
                background-color: #0284c7;
            }
        ''')
        act_open = menu.addAction("Buka")
        act_copy = menu.addAction("Salin Alamat URL")
        menu.addSeparator()
        act_delete = menu.addAction("Hapus dari Riwayat")

        selected = menu.exec(self.history_list.mapToGlobal(pos))
        if selected == act_open and url:
            self.open_url.emit(url)
            self.accept()
        elif selected == act_copy and url:
            QApplication.clipboard().setText(url)
        elif selected == act_delete and url:
            hist = self.settings.get("history") or []
            new_hist = [h for h in hist if h.get("url") != url]
            self.settings.set("history", new_hist)
            self._populate_history(self.search_input.text())

    def _clear_all(self):
        reply = QMessageBox.question(
            self,
            "Hapus Seluruh Riwayat",
            "Apakah Anda yakin ingin menghapus seluruh riwayat penelusuran?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.settings.clear_history()
            self._populate_history()


class ClearBrowsingDataDialog(QDialog):
    def __init__(self, profile: QWebEngineProfile, parent=None, is_dark=None):
        super().__init__(parent)
        self.profile = profile
        if is_dark is None:
            self.is_dark = getattr(parent, "theme_manager", None) and parent.theme_manager.is_dark if parent else True
        else:
            self.is_dark = is_dark

        self.setWindowTitle("Hapus Data Penjelajahan")
        self.setFixedSize(420, 320)
        self.settings = SettingsManager()

        bg = "#0f172a" if self.is_dark else "#ffffff"
        fg = "#f8fafc" if self.is_dark else "#0f172a"
        cb_fg = "#cbd5e1" if self.is_dark else "#334155"

        self.setStyleSheet(f'''
            QDialog {{
                background-color: {bg};
                color: {fg};
                font-family: 'Segoe UI', sans-serif;
            }}
            QCheckBox {{
                color: {cb_fg};
                font-size: 13px;
                spacing: 8px;
            }}
            QPushButton {{
                background-color: #ef4444;
                color: white;
                font-weight: bold;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
            }}
            QPushButton:hover {{
                background-color: #dc2626;
            }}
        ''')
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        title = QLabel("Hapus Data Penjelajahan")
        title.setStyleSheet("font-size: 15px; font-weight: bold; color: #38bdf8;")
        layout.addWidget(title)

        desc = QLabel("Pilih komponen data yang ingin dibersihkan dari penyimpanan:")
        desc.setStyleSheet("color: #94a3b8; font-size: 12px;")
        desc.setWordWrap(True)
        layout.addWidget(desc)

        self.cb_history = QCheckBox("Riwayat Penjelajahan (History)")
        self.cb_history.setChecked(True)
        layout.addWidget(self.cb_history)

        self.cb_cache = QCheckBox("Cache Gambar dan File Sementara")
        self.cb_cache.setChecked(True)
        layout.addWidget(self.cb_cache)

        self.cb_cookies = QCheckBox("Cookie dan Data Situs Lokal")
        self.cb_cookies.setChecked(True)
        layout.addWidget(self.cb_cookies)

        layout.addStretch()

        btn_row = QHBoxLayout()
        clear_btn = QPushButton("Hapus Data Sekarang")
        clear_btn.clicked.connect(self._clear_data)

        cancel_btn = QPushButton("Batal")
        cancel_btn.setStyleSheet("background-color: #334155;")
        cancel_btn.clicked.connect(self.reject)

        btn_row.addWidget(clear_btn)
        btn_row.addWidget(cancel_btn)
        layout.addLayout(btn_row)

    def _clear_data(self):
        if self.cb_history.isChecked():
            self.settings.clear_history()

        if self.cb_cache.isChecked() and self.profile:
            self.profile.clearHttpCache()

        if self.cb_cookies.isChecked() and self.profile:
            self.profile.cookieStore().deleteAllCookies()

        QMessageBox.information(self, "Data Dibersihkan", "Data penjelajahan yang dipilih berhasil dihapus!")
        self.accept()
