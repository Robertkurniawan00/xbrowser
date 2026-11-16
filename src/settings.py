"""
Settings Manager and Configuration Store for XBrowser.
Provides thread-safe persistence, default configurations, and atomic disk writes.
"""
import os
import json
import threading
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

CONFIG_DIR = os.path.expanduser(r"~/.xbrowser")
CONFIG_PATH = os.path.join(CONFIG_DIR, "config.json")

SEARCH_ENGINES = {
    "Brave Search": "https://search.brave.com/search?q={query}",
    "DuckDuckGo": "https://duckduckgo.com/?q={query}",
    "Startpage": "https://www.startpage.com/sp/search?query={query}",
    "SearXNG": "https://searx.be/search?q={query}",
    "Google": "https://www.google.com/search?q={query}",
    "Bing": "https://www.bing.com/search?q={query}",
}

DEFAULT_CONFIG: Dict[str, Any] = {
    "general": {
        "search_engine": "Google",
        "homepage": "xbrowser://speeddial",
        "dark_mode": True,
        "restore_session": True,
        "zoom_factor": 1.0,
    },
    "tor": {
        "enabled": False,
        "proxy_host": "127.0.0.1",
        "proxy_port": 9050,
        "control_port": 9051,
        "security_level": "Standard",
        "anti_fingerprinting": True,
        "auto_route_onion": True,
    },
    "shields": {
        "enabled": True,
        "block_ads": True,
        "block_youtube_ads": True,
        "block_trackers": True,
        "block_scripts": False,
        "block_fingerprinting": True,
        "https_first_mode": True,
        "block_webrtc_leak": True,
        "block_third_party_cookies": True,
        "whitelisted_domains": [],
        "stats": {
            "total_blocked": 0,
            "bytes_saved": 0,
            "time_saved_ms": 0,
        },
    },
    "vpn": {
        "enabled": False,
        "location": "Optimal",
        "auto_connect": False,
    },
    "workspaces": {
        "active": "Personal",
        "list": [
            "Personal",
            "Tor Privacy",
            "Work & Tools",
        ],
    },
    "extensions": {
        "developer_mode": True,
        "installed": [],
    },
    "appearance": {
        "wallpaper": "Cyberpunk",
        "custom_wallpaper_path": "",
        "selected_category": "all",
        "minimalist_toolbar": True,
    },
    "performance": {
        "memory_saver_enabled": True,
        "inactive_timeout_minutes": 15,
        "auto_trim_ram": True,
        "low_ram_mode": True,
        "ultra_light_mode": True,
    },
    "bookmarks": [
        {"title": "DuckDuckGo", "url": "https://duckduckgo.com", "icon": "search", "category": "favorites"},
        {"title": "Brave Search", "url": "https://search.brave.com", "icon": "shield", "category": "favorites"},
        {"title": "Tor Project", "url": "https://www.torproject.org", "icon": "lock", "category": "dev"},
        {"title": "YouTube", "url": "https://www.youtube.com", "icon": "video", "category": "social"},
        {"title": "GitHub", "url": "https://github.com", "icon": "code", "category": "dev"},
        {"title": "Wikipedia", "url": "https://www.wikipedia.org", "icon": "book", "category": "work"},
        {"title": "Reddit", "url": "https://www.reddit.com", "icon": "forum", "category": "social"},
    ],
    "profile": {
        "username": "",
        "avatar_color": "#15803d",
    },
    "history": [],
}


class SettingsManager:
    _instance: Optional["SettingsManager"] = None
    _lock = threading.RLock()

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    instance = super().__new__(cls)
                    instance._pending_shield_updates = 0
                    instance._last_shield_save = 0.0
                    instance.data = {}
                    instance._load()
                    cls._instance = instance
        return cls._instance

    def _load(self):
        with self._lock:
            try:
                os.makedirs(CONFIG_DIR, exist_ok=True)
                if os.path.exists(CONFIG_PATH):
                    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                        self.data = json.load(f)

                    # Ensure standard top-level sections exist
                    for section, values in DEFAULT_CONFIG.items():
                        if section not in self.data:
                            if isinstance(values, list):
                                self.data[section] = list(values)
                            elif isinstance(values, dict):
                                self.data[section] = dict(values)
                            else:
                                self.data[section] = values
                        elif isinstance(values, dict) and isinstance(self.data[section], dict):
                            for k, v in values.items():
                                if k not in self.data[section]:
                                    self.data[section][k] = v

                    # Filter out garbage in history (data: URIs, xbrowser://, empty URLs)
                    if "history" in self.data and isinstance(self.data["history"], list):
                        cleaned_hist = []
                        for h in self.data["history"]:
                            if isinstance(h, dict):
                                u = str(h.get("url", "")).strip()
                                if u and not u.startswith("data:") and not u.startswith("about:blank") and not u.startswith("xbrowser://speeddial"):
                                    cleaned_hist.append(h)
                        self.data["history"] = cleaned_hist[-1000:]
                else:
                    self.data = json.loads(json.dumps(DEFAULT_CONFIG))
                    self.save()
            except Exception as e:
                print(f"[!] Config load error: {e}")
                self.data = json.loads(json.dumps(DEFAULT_CONFIG))
                self.save()

    def save(self):
        with self._lock:
            try:
                os.makedirs(CONFIG_DIR, exist_ok=True)
                tmp_path = CONFIG_PATH + ".tmp"
                with open(tmp_path, "w", encoding="utf-8") as f:
                    json.dump(self.data, f, indent=2, ensure_ascii=False)
                os.replace(tmp_path, CONFIG_PATH)
            except Exception as e:
                print(f"[!] Config save error: {e}")

    def flush(self):
        self.save()

    def get(self, section: str, key: Optional[str] = None, default: Any = None) -> Any:
        with self._lock:
            if section not in self.data:
                return default
            val = self.data[section]
            if key is None:
                return val
            if isinstance(val, dict):
                return val.get(key, default)
            return val

    def set(self, section: str, key_or_val: Any = None, val: Any = None):
        """
        Flexible setter supporting both:
        - set(section, value) -> sets self.data[section] = value
        - set(section, key, value) -> sets self.data[section][key] = value
        """
        with self._lock:
            if val is None:
                self.data[section] = key_or_val
            else:
                if section not in self.data or not isinstance(self.data[section], dict):
                    self.data[section] = {}
                self.data[section][key_or_val] = val
            self.save()

    def get_bookmarks(self) -> List[Dict[str, Any]]:
        with self._lock:
            return list(self.data.get("bookmarks", []))

    def add_bookmark(self, title: str, url: str, category: str = "favorites", icon: str = "globe"):
        with self._lock:
            bms = self.data.setdefault("bookmarks", [])
            clean_url = str(url).strip().rstrip("/")
            for b in bms:
                if str(b.get("url", "")).strip().rstrip("/") == clean_url:
                    b["title"] = title.strip()
                    b["category"] = category
                    self.save()
                    return
            bms.append({
                "title": title.strip(),
                "url": url.strip(),
                "icon": icon,
                "category": category,
            })
            self.save()

    def delete_bookmark(self, target: Any) -> bool:
        """
        Deletes a bookmark by index (int) or by matching URL / title (str) or dict.
        """
        with self._lock:
            bms = self.data.get("bookmarks", [])
            if not bms:
                return False

            deleted = False
            if isinstance(target, int):
                if 0 <= target < len(bms):
                    bms.pop(target)
                    deleted = True
            elif isinstance(target, str):
                target_str = target.strip().rstrip("/").lower()
                new_bms = [b for b in bms if str(b.get("url", "")).strip().rstrip("/").lower() != target_str]
                if len(new_bms) != len(bms):
                    self.data["bookmarks"] = new_bms
                    deleted = True
                else:
                    new_bms = [b for b in bms if str(b.get("title", "")).strip().lower() != target_str]
                    if len(new_bms) != len(bms):
                        self.data["bookmarks"] = new_bms
                        deleted = True
            elif isinstance(target, dict):
                target_url = str(target.get("url", "")).strip().rstrip("/").lower()
                new_bms = [b for b in bms if str(b.get("url", "")).strip().rstrip("/").lower() != target_url]
                if len(new_bms) != len(bms):
                    self.data["bookmarks"] = new_bms
                    deleted = True

            if deleted:
                self.save()
            return deleted

    def add_history(self, title: str, url: str):
        if not url:
            return
        clean_url = str(url).strip()
        if clean_url.startswith("data:") or clean_url.startswith("about:blank") or clean_url == "xbrowser://speeddial":
            return

        with self._lock:
            hist = self.data.setdefault("history", [])
            item = {
                "title": str(title).strip() if title else clean_url,
                "url": clean_url,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
            }
            if hist and hist[-1].get("url") == clean_url:
                hist[-1] = item
            else:
                hist.append(item)

            if len(hist) > 1000:
                self.data["history"] = hist[-1000:]

            threading.Thread(target=self.save, daemon=True).start()

    def clear_history(self):
        """Safely and completely clear browsing history."""
        with self._lock:
            self.data["history"] = []
            self.save()

    def update_shield_stats(self, count: int = 1, bytes_saved: int = 0, time_ms: int = 0):
        should_flush = False
        with self._lock:
            stats = self.data.setdefault("shields", {}).setdefault("stats", {})
            stats["total_blocked"] = stats.get("total_blocked", 0) + count
            stats["bytes_saved"] = stats.get("bytes_saved", 0) + (bytes_saved * count)
            stats["time_saved_ms"] = stats.get("time_saved_ms", 0) + (time_ms * count)

            self._pending_shield_updates += count
            now = time.time()
            if self._pending_shield_updates >= 10 or (now - self._last_shield_save >= 5.0):
                should_flush = True
                self._pending_shield_updates = 0
                self._last_shield_save = now

        if should_flush:
            self.save()
