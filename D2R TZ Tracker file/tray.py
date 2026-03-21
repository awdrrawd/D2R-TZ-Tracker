# tray.py
import os, sys, threading
import pystray
from PIL import Image, ImageDraw


def _get_icon_image():
    import os, sys
    base = os.path.dirname(sys.executable) if getattr(sys, "frozen", False) \
           else os.path.dirname(os.path.abspath(__file__))
    data = os.path.join(base, "Data")
    search_dirs = [data, base] if os.path.isdir(data) else [base]
    for d in search_dirs:
        for name in ("icon.ico", "icon.png"):
            path = os.path.join(d, name)
            if os.path.exists(path):
                try:
                    img = Image.open(path).convert("RGBA").resize((64, 64), Image.LANCZOS)
                    return img
                except Exception:
                    pass
    img  = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.ellipse([4, 4, 60, 60], fill="#9d4edd")
    draw.text((16, 18), "TZ", fill="white")
    return img


class TrayIcon:
    def __init__(self, on_show, on_quit,
                 on_settings=None, get_strings=None, get_states=None,
                 on_toggle_compact=None,
                 on_toggle_notify5=None, on_toggle_notifyfav=None,
                 on_set_topmost=None, on_reset_pos=None,
                 on_refresh=None, on_toggle_lock=None, on_about=None,
                 on_toggle_transparent=None):
        self.on_show             = on_show
        self.on_quit             = on_quit
        self.on_settings         = on_settings
        self.get_strings         = get_strings
        self.get_states          = get_states
        self.on_toggle_notify5   = on_toggle_notify5
        self.on_toggle_notifyfav = on_toggle_notifyfav
        self.on_set_topmost      = on_set_topmost
        self.on_reset_pos        = on_reset_pos
        self.on_toggle_compact   = on_toggle_compact
        self.on_refresh          = on_refresh
        self.on_toggle_lock      = on_toggle_lock
        self.on_about            = on_about
        self.on_toggle_transparent = on_toggle_transparent
        self._icon  = None
        self._thread = None

    def start(self):
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        if self._icon:
            try:
                self._icon.stop()
            except Exception:
                pass

    def update_tooltip(self, text: str):
        if self._icon:
            try:
                self._icon.title = text
            except Exception:
                pass

    def refresh_menu(self):
        if self._icon:
            try:
                self._icon.update_menu()
            except Exception:
                pass

    def _s(self, key: str, default: str = "") -> str:
        if self.get_strings:
            try:
                return self.get_strings().get(key, default)
            except Exception:
                pass
        return default

    def _st(self, key, default=None):
        if self.get_states:
            try:
                return self.get_states().get(key, default)
            except Exception:
                pass
        return default

    def _run(self):
        img = _get_icon_image()

        def topmost_lbl(item):
            on = self._st("topmost_mode", "hard") == "hard"
            return ("✓ " if on else "  ") + self._s("topmost_hard", "Topmost")

        def toggle_topmost(i, it):
            cur = self._st("topmost_mode", "hard")
            if self.on_set_topmost:
                self.on_set_topmost("off" if cur == "hard" else "hard")

        def show_lbl(item):
            vis = self._st("visible", True)
            return ("✓ " if vis else "  ") + self._s("tray_show", "Show / Hide")

        def compact_lbl(item):
            return ("✓ " if self._st("is_compact", False) else "  ") + self._s("tray_compact", "Compact Mode")

        def notify5_lbl(item):
            return ("✓ " if self._st("notify5", True) else "  ") + self._s("tray_notify5", "Zone-end Alert")

        def notifyfav_lbl(item):
            return ("✓ " if self._st("notifyfav", True) else "  ") + self._s("tray_notifyfav", "Fav Alert")

        def lock_lbl(item):
            return ("✓ " if self._st("position_locked", False) else "  ") + self._s("tray_lock_pos", "Lock Position")

        def transparent_lbl(item):
            return ("✓ " if self._st("text_only_mode", False) else "  ") + self._s("tray_transparent", "Transparent Background")

        menu = pystray.Menu(
            pystray.MenuItem(lambda i: self._s("tray_name", "D2R TZ Tracker"),
                             None, enabled=False),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(show_lbl,
                             lambda i, it: self.on_show(), default=True),
            pystray.MenuItem(compact_lbl,
                             lambda i, it: self.on_toggle_compact and self.on_toggle_compact()),
            pystray.MenuItem(lambda i: self._s("tray_settings", "Settings"),
                             lambda i, it: self.on_settings and self.on_settings()),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(topmost_lbl, toggle_topmost),
            pystray.MenuItem(notify5_lbl,
                             lambda i, it: self.on_toggle_notify5 and self.on_toggle_notify5()),
            pystray.MenuItem(notifyfav_lbl,
                             lambda i, it: self.on_toggle_notifyfav and self.on_toggle_notifyfav()),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(lambda i: self._s("tray_refresh", "Refresh Now"),
                             lambda i, it: self.on_refresh and self.on_refresh()),
            pystray.MenuItem(lock_lbl,
                             lambda i, it: self.on_toggle_lock and self.on_toggle_lock()),
            pystray.MenuItem(transparent_lbl,
                             lambda i, it: self.on_toggle_transparent and self.on_toggle_transparent()),
            pystray.MenuItem(lambda i: self._s("tray_reset_pos", "Reset Position"),
                             lambda i, it: self.on_reset_pos and self.on_reset_pos()),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(lambda i: self._s("tray_about", "About"),
                             lambda i, it: self.on_about and self.on_about()),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(lambda i: self._s("tray_quit", "Quit"),
                             lambda i, it: self.on_quit()),
        )

        self._icon = pystray.Icon(
            name="D2R TZ Tracker", icon=img,
            title="D2R TZ Tracker", menu=menu)
        self._icon.run()