# taskbar_widget.py
# 工作列釘選小視窗：顯示當前/下個 TZ，固定在工作列上方

import tkinter as tk
import customtkinter as ctk
import os
import sys
import ctypes

from tz_data import get_group_name

# 固定字體大小（不跟隨 font_size 設定）
_WIDGET_FONT_FAMILY = "Microsoft JhengHei UI"
_FONT_LBL  = 9    # 標籤
_FONT_NAME = 11   # TZ 名稱

WIDGET_W = 280
WIDGET_H = 48


def _font(size: int, bold: bool = False):
    return ctk.CTkFont(
        family=_WIDGET_FONT_FAMILY,
        size=size,
        weight="bold" if bold else "normal",
    )


def _dim(hex_color: str, factor: float = 0.4) -> str:
    h = hex_color.lstrip("#")
    if len(h) != 6:
        return hex_color
    r = min(255, int(int(h[0:2], 16) * factor))
    g = min(255, int(int(h[2:4], 16) * factor))
    b = min(255, int(int(h[4:6], 16) * factor))
    return f"#{r:02x}{g:02x}{b:02x}"


class TaskbarWidget:
    """
    獨立的小視窗，固定顯示在工作列正上方。
    顯示：當前 TZ | 下個 TZ
    可拖曳左右移動（固定在工作列高度）。
    """

    def __init__(self, settings: dict):
        self.settings = settings
        self._visible = False

        self.cur_group = None
        self.nxt_group = None
        self.status    = "idle"

        self.win = tk.Toplevel()
        self.win.title("D2R TZ Bar")
        self.win.overrideredirect(True)
        self.win.resizable(False, False)

        self._setup()
        self._build()
        self._position()

        # 預設隱藏
        self.win.withdraw()

    def _taskbar_height(self) -> int:
        """取得 Windows 工作列高度"""
        try:
            from ctypes import wintypes
            class RECT(ctypes.Structure):
                _fields_ = [("left",ctypes.c_long),("top",ctypes.c_long),
                             ("right",ctypes.c_long),("bottom",ctypes.c_long)]
            rect = RECT()
            # ABM_GETTASKBARPOS = 5
            class APPBARDATA(ctypes.Structure):
                _fields_ = [
                    ("cbSize",    ctypes.c_uint),
                    ("hWnd",      ctypes.c_void_p),
                    ("uCallbackMessage", ctypes.c_uint),
                    ("uEdge",     ctypes.c_uint),
                    ("rc",        RECT),
                    ("lParam",    ctypes.c_long),
                ]
            abd = APPBARDATA()
            abd.cbSize = ctypes.sizeof(abd)
            ctypes.windll.shell32.SHAppBarMessage(5, ctypes.byref(abd))
            sh = self.win.winfo_screenheight()
            return sh - abd.rc.top
        except Exception:
            return 40   # 預設工作列高度

    def _setup(self):
        s  = self.settings
        bg = s.get("bg_color", "#120d1f")
        self.win.configure(bg=bg)
        self.win.attributes("-topmost", True)
        self.win.attributes("-alpha", s.get("opacity", 0.93))
        # DWM 圓角
        try:
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                self.win.winfo_id(), 33,
                ctypes.byref(ctypes.c_int(2)),
                ctypes.sizeof(ctypes.c_int),
            )
        except Exception:
            pass

    def _position(self):
        """固定在工作列正上方，水平位置由設定決定"""
        self.win.update_idletasks()
        sw  = self.win.winfo_screenwidth()
        sh  = self.win.winfo_screenheight()
        tbh = self._taskbar_height()
        y   = sh - tbh - WIDGET_H - 4
        # taskbar_x 若為 None/-1/未設定，置中
        tx  = self.settings.get("taskbar_x")
        if tx is None or tx < 0:
            x = (sw - WIDGET_W) // 2
        else:
            x = int(tx)
        x   = max(0, min(x, sw - WIDGET_W))
        self.win.geometry(f"{WIDGET_W}x{WIDGET_H}+{x}+{y}")

    def _build(self):
        s      = self.settings
        bg     = s.get("bg_color",     "#120d1f")
        ac     = s.get("accent_color", "#9d4edd")
        tc     = s.get("text_color",   "#e8d5b7")
        sub    = s.get("sub_color",    "#7b6a9a")
        favs   = s.get("favorites",    [])
        lang   = s.get("lang",         "en-us")

        # 清空
        for w in self.win.winfo_children():
            w.destroy()

        frame = ctk.CTkFrame(self.win, fg_color=_dim(ac, 0.20),
                             corner_radius=8)
        frame.pack(fill="both", expand=True)

        # 拖曳
        frame.bind("<ButtonPress-1>",   self._drag_start)
        frame.bind("<B1-Motion>",       self._drag_move)
        frame.bind("<ButtonRelease-1>", self._drag_end)

        # 左半：當前 TZ
        left = ctk.CTkFrame(frame, fg_color="transparent")
        left.pack(side="left", fill="both", expand=True, padx=(8, 2), pady=4)
        left.bind("<ButtonPress-1>",   self._drag_start)
        left.bind("<B1-Motion>",       self._drag_move)
        left.bind("<ButtonRelease-1>", self._drag_end)

        lang_i18n = {
            "zh-tw": ("當前", "下個"),
            "zh-cn": ("当前", "下个"),
        }.get(lang, ("Now", "Next"))

        ctk.CTkLabel(left, text=lang_i18n[0],
                     font=_font(_FONT_LBL), text_color=sub, anchor="w").pack(anchor="w")

        cur_name, cur_col = self._resolve(self.cur_group, lang, favs, s, tc, sub)
        ctk.CTkLabel(left, text=cur_name,
                     font=_font(_FONT_NAME, True), text_color=cur_col,
                     anchor="w", wraplength=120).pack(anchor="w")

        # 分隔線
        ctk.CTkFrame(frame, width=1, fg_color=_dim(ac, 0.5)).pack(
            side="left", fill="y", pady=6)

        # 右半：下個 TZ
        right = ctk.CTkFrame(frame, fg_color="transparent")
        right.pack(side="left", fill="both", expand=True, padx=(2, 8), pady=4)
        right.bind("<ButtonPress-1>",   self._drag_start)
        right.bind("<B1-Motion>",       self._drag_move)
        right.bind("<ButtonRelease-1>", self._drag_end)

        ctk.CTkLabel(right, text=lang_i18n[1],
                     font=_font(_FONT_LBL), text_color=sub, anchor="w").pack(anchor="w")

        if self.status == "waiting":
            nxt_name, nxt_col = "…", sub
        else:
            nxt_name, nxt_col = self._resolve(self.nxt_group, lang, favs, s, tc, sub)
        ctk.CTkLabel(right, text=nxt_name,
                     font=_font(_FONT_NAME, True), text_color=nxt_col,
                     anchor="w", wraplength=120).pack(anchor="w")

    def _resolve(self, group, lang, favs, s, tc, sub):
        if group is None:
            return "—", sub
        name   = get_group_name(group, lang)
        is_fav = group["id"] in favs
        col    = s.get("fav_color", "#ffd700") \
                 if is_fav and s.get("fav_color_enabled", True) else tc
        return name, col

    # ── 拖曳（水平方向，垂直固定在工作列上方）────────────────────────────────

    def _drag_start(self, e):
        self._ox = e.x_root - self.win.winfo_x()

    def _drag_move(self, e):
        sw = self.win.winfo_screenwidth()
        x  = max(0, min(e.x_root - self._ox, sw - WIDGET_W))
        sh = self.win.winfo_screenheight()
        tbh = self._taskbar_height()
        y   = sh - tbh - WIDGET_H - 4
        self.win.geometry(f"+{x}+{y}")

    def _drag_end(self, _e):
        self.settings["taskbar_x"] = self.win.winfo_x()

    # ── 公開方法 ──────────────────────────────────────────────────────────────

    def show(self):
        self._visible = True
        self._position()
        self.win.deiconify()
        self.win.lift()

    def hide(self):
        self._visible = False
        self.win.withdraw()

    def toggle(self):
        if self._visible:
            self.hide()
        else:
            self.show()

    def update_tz(self, cur_group, nxt_group, status):
        """由主視窗 update_tz 呼叫後轉發過來"""
        self.cur_group = cur_group
        self.nxt_group = nxt_group
        self.status    = status
        if self._visible:
            self._build()

    def apply_settings(self, settings: dict):
        """設定改變時重新套用顏色"""
        self.settings = settings
        self._setup()
        if self._visible:
            self._build()