# toast.py
# 自製通知視窗，掛在主視窗下避免 Tk 根視窗問題

import tkinter as tk
import os
import sys

try:
    import ctypes
    def _round_corners(hwnd):
        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            hwnd, 33, ctypes.byref(ctypes.c_int(2)), ctypes.sizeof(ctypes.c_int))
except Exception:
    def _round_corners(_): pass

TOAST_W        = 300
TOAST_H        = 84
TOAST_DURATION = 5000
FADE_STEPS     = 15
FADE_MS        = 25

_root = None
_slots = [False, False, False]
_icon_cache = None   # PhotoImage 快取（必須保持參照避免 GC）


def _get_base_dir() -> str:
    return os.path.dirname(sys.executable) if getattr(sys, "frozen", False) \
           else os.path.dirname(os.path.abspath(__file__))


def _get_data_dir() -> str:
    base = _get_base_dir()
    data = os.path.join(base, "Data")
    return data if os.path.isdir(data) else base


def _try_load_icon(parent, bg: str, accent: str):
    """在 title_row 左側加上 16x16 icon，找不到就用 accent 色小方塊"""
    global _icon_cache
    # 優先找 Data/ 資料夾，再找程式目錄
    search_dirs = [_get_data_dir(), _get_base_dir()]
    for base in search_dirs:
        for name in ("icon.ico", "icon.png"):
            path = os.path.join(base, name)
            if os.path.exists(path):
                try:
                    from PIL import Image, ImageTk
                    img = Image.open(path).convert("RGBA").resize((16, 16))
                    _icon_cache = ImageTk.PhotoImage(img)
                    tk.Label(parent, image=_icon_cache, bg=bg, bd=0
                             ).pack(side="left", padx=(0, 4))
                    return
                except Exception:
                    pass
    # Fallback：accent 色小圓點
    canvas = tk.Canvas(parent, width=10, height=10, bg=bg,
                       highlightthickness=0, bd=0)
    canvas.create_oval(1, 1, 9, 9, fill=accent, outline="")
    canvas.pack(side="left", padx=(0, 4))


def set_root(root):
    """main.py 啟動後呼叫，傳入主視窗的 root"""
    global _root
    _root = root


def _taskbar_top() -> int:
    try:
        import ctypes as ct
        class RECT(ct.Structure):
            _fields_ = [("left",ct.c_long),("top",ct.c_long),
                        ("right",ct.c_long),("bottom",ct.c_long)]
        class ABD(ct.Structure):
            _fields_ = [("cbSize",ct.c_uint),("hWnd",ct.c_void_p),
                        ("uCallbackMessage",ct.c_uint),("uEdge",ct.c_uint),
                        ("rc",RECT),("lParam",ct.c_long)]
        abd = ABD(); abd.cbSize = ct.sizeof(abd)
        ct.windll.shell32.SHAppBarMessage(5, ct.byref(abd))
        return abd.rc.top
    except Exception:
        if _root:
            return _root.winfo_screenheight() - 48
        return 1000


def show(title: str, message: str,
         bg: str = "#1e1030", accent: str = "#9d4edd",
         text_color: str = "#e8d5b7"):
    """從任意執行緒安全地呼叫，在主執行緒建立通知視窗"""
    if _root is None:
        return
    _root.after(0, lambda: _create_toast(title, message, bg, accent, text_color))


def _get_slot() -> int:
    for i, used in enumerate(_slots):
        if not used:
            return i
    return 0


def _create_toast(title, message, bg, accent, text_color):
    if _root is None:
        return

    slot = _get_slot()
    _slots[slot] = True

    sw = _root.winfo_screenwidth()
    tb = _taskbar_top()
    margin = 12
    x = sw - TOAST_W - margin
    y = tb - TOAST_H - margin - slot * (TOAST_H + 8)

    win = tk.Toplevel(_root)
    win.overrideredirect(True)
    win.attributes("-topmost", True)
    win.attributes("-alpha", 0.0)
    win.geometry(f"{TOAST_W}x{TOAST_H}+{x}+{y}")
    win.configure(bg=accent)

    try:
        _round_corners(win.winfo_id())
    except Exception:
        pass

    # 內框
    inner = tk.Frame(win, bg=bg, bd=0)
    inner.place(x=2, y=2, width=TOAST_W - 4, height=TOAST_H - 4)

    # 左色條
    tk.Frame(inner, bg=accent, width=4).pack(side="left", fill="y")

    content = tk.Frame(inner, bg=bg)
    content.pack(side="left", fill="both", expand=True, padx=8, pady=6)

    # 標題列（圖示 + 文字）
    title_row = tk.Frame(content, bg=bg)
    title_row.pack(fill="x")

    # 嘗試載入 icon
    _try_load_icon(title_row, bg, accent)

    tk.Label(title_row, text=title,
             font=("Microsoft JhengHei UI", 11, "bold"),
             fg=accent, bg=bg, anchor="w").pack(side="left", fill="x", expand=True)

    tk.Label(content, text=message,
             font=("Microsoft JhengHei UI", 10),
             fg=text_color, bg=bg, anchor="w",
             wraplength=TOAST_W - 46, justify="left").pack(fill="x")

    # 關閉按鈕
    def close():
        _fade_out(win, slot)

    tk.Button(win, text="✕", font=("Segoe UI", 9),
              fg=text_color, bg=bg, bd=0, cursor="hand2",
              activeforeground=accent, activebackground=bg,
              command=close).place(x=TOAST_W - 22, y=4, width=18, height=18)

    for w in (win, inner, content):
        w.bind("<Button-1>", lambda _: close())

    _fade_in(win, step=0,
             on_done=lambda: win.after(TOAST_DURATION, lambda: _fade_out(win, slot)))


def _fade_in(win, step, on_done):
    try:
        win.attributes("-alpha", min(step / FADE_STEPS * 0.95, 0.95))
    except Exception:
        return
    if step < FADE_STEPS:
        win.after(FADE_MS, lambda: _fade_in(win, step + 1, on_done))
    else:
        on_done()


def _fade_out(win, slot, step=0):
    try:
        alpha = 0.95 * (1 - step / FADE_STEPS)
        win.attributes("-alpha", max(alpha, 0.0))
    except Exception:
        _slots[slot] = False
        return
    if step < FADE_STEPS:
        win.after(FADE_MS, lambda: _fade_out(win, slot, step + 1))
    else:
        _slots[slot] = False
        try:
            win.destroy()
        except Exception:
            pass