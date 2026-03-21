# ui.py
# 主視窗：純 tkinter（支援透明背景）
# 設定頁：customtkinter Toplevel（獨立視窗，不透明）

import tkinter as tk
from tkinter import colorchooser, simpledialog, messagebox
import customtkinter as ctk
import ctypes
import webbrowser
import os
import sys

import config
import notifier
from tz_data import TZ_GROUPS, LANG_MAP, get_group_name, get_zone_name

# ── 視窗尺寸基準 ─────────────────────────────────────────────────────────────
WIN_W_MAIN    = 260
WIN_W_COMPACT = 220
BAR_H         = 28
BOT_H         = 22
COMPACT_BAR_H = 18
WIN_W_SETTINGS = 310
WIN_H_SETTINGS = 620
SETTINGS_SCALE = 1.3

# ── i18n ──────────────────────────────────────────────────────────────────────
_I18N = {
    "zh-tw": {
        "current":"當前 TZ","next":"下個 TZ","waiting":"等待更新中…","fetching":"抓取中…",
        "error":"抓取失敗","no_data":"—","next_in":"換場倒數","by":"by d2tz.info",
        "source":"資料：d2tz.info","settings":"設定","back":"← 返回","refresh":"重新整理",
        "compact":"收納","language":"語言","theme":"主題","theme_dark":"暗色","theme_light":"亮色",
        "save_theme":"儲存目前主題","delete_theme":"刪除主題","theme_name_prompt":"請輸入主題名稱：",
        "theme_saved":"主題已儲存","theme_deleted":"主題已刪除","opacity":"透明度","scale":"縮放",
        "font_size":"字體大小","colors":"顏色設定","bg_color":"背景","text_color":"文字",
        "accent_color":"強調","fav_color":"最愛","btn_color":"按鈕色","always_on_top":"視窗置頂",
        "notif_section":"通知設定","notify_5min":"換場前提醒","notify_fav":"下個 TZ 是最愛時提醒",
        "notify_minutes":"提前幾分鐘提醒","fav_color_enabled":"最愛場景使用專屬顏色",
        "display_section":"顯示設定","show_tier_exp":"顯示 EXP 評級","show_tier_loot":"顯示 LOOT 評級",
        "text_only_mode":"純文字模式（背景透明）","position_locked":"鎖定位置（點擊穿透）",
        "sound_5min":"換場提醒音效","sound_fav":"最愛提醒音效","sound_mute":"靜音",
        "sound_default":"預設（sound.wav）","sound_custom":"自訂音效","sound_browse":"瀏覽…",
        "favorites":"最愛群組","fav_hint":"勾選後當下個 TZ 為此群組時發送通知",
        "api_token_section":"API Token","api_token_hint":"輸入你的 d2tz.info Token（選填）",
        "tray_show":"顯示／隱藏","tray_compact":"迷你模式","tray_settings":"設定",
        "tray_quit":"結束","tray_name":"D2R TZ Tracker","tray_notify5":"換場提醒",
        "tray_notifyfav":"最愛提醒","tray_reset_pos":"還原位置","tray_refresh":"立即刷新",
        "tray_lock_pos":"鎖定位置","tray_about":"關於","tray_transparent":"透明背景",
        "tray_sound":"通知音效","tray_sound_mute":"靜音","tray_sound_default":"預設",
        "tray_sound_custom":"自訂","tray_sound_not_set":"(需設定音效)",
        "topmost_off":"關閉置頂","topmost_hard":"置頂",
        "notif_5min_msg":"{zone}等地區於 {n} 分鐘後換場",
        "notif_5min_single":"{zone} 於 {n} 分鐘後換場",
        "notif_fav_msg":"下個恐懼區域為 {zone} 等場景","notif_fav_single":"下個恐懼區域為 {zone}",
        "etc":"等","about_title":"關於 D2R TZ Tracker",
        "about_msg":"D2R TZ Tracker\n\nTZ API 與場景翻譯由 d2tz.info 提供\n\n本工具完全免費，開源分享\n感謝 D2TZ 團隊提供社區資源\n瀧月瀨使用 AI 製作",
        "exp":"EXP","loot":"Loot",
    },
    "zh-cn": {
        "current":"当前 TZ","next":"下个 TZ","waiting":"等待更新中…","fetching":"抓取中…",
        "error":"抓取失败","no_data":"—","next_in":"换场倒数","by":"by d2tz.info",
        "source":"数据：d2tz.info","settings":"设置","back":"← 返回","refresh":"刷新",
        "compact":"收纳","language":"语言","theme":"主题","theme_dark":"暗色","theme_light":"亮色",
        "save_theme":"保存当前主题","delete_theme":"删除主题","theme_name_prompt":"请输入主题名称：",
        "theme_saved":"主题已保存","theme_deleted":"主题已删除","opacity":"透明度","scale":"缩放",
        "font_size":"字体大小","colors":"颜色设置","bg_color":"背景","text_color":"文字",
        "accent_color":"强调","fav_color":"收藏","btn_color":"按钮色","always_on_top":"窗口置顶",
        "notif_section":"通知设置","notify_5min":"换场前提醒","notify_fav":"下个 TZ 是收藏时提醒",
        "notify_minutes":"提前几分钟提醒","fav_color_enabled":"收藏场景使用专属颜色",
        "display_section":"显示设置","show_tier_exp":"显示 EXP 评级","show_tier_loot":"显示 LOOT 评级",
        "text_only_mode":"纯文字模式（背景透明）","position_locked":"锁定位置（点击穿透）",
        "sound_5min":"换场提醒音效","sound_fav":"收藏提醒音效","sound_mute":"静音",
        "sound_default":"默认（sound.wav）","sound_custom":"自定义音效","sound_browse":"浏览…",
        "favorites":"收藏群组","fav_hint":"勾选后当下个 TZ 为此群组时发送通知",
        "api_token_section":"API Token","api_token_hint":"输入你的 d2tz.info Token（选填）",
        "tray_show":"显示／隐藏","tray_compact":"迷你模式","tray_settings":"设置",
        "tray_quit":"退出","tray_name":"D2R TZ Tracker","tray_notify5":"换场提醒",
        "tray_notifyfav":"收藏提醒","tray_reset_pos":"还原位置","tray_refresh":"立即刷新",
        "tray_lock_pos":"锁定位置","tray_about":"关于","tray_transparent":"透明背景",
        "tray_sound":"通知音效","tray_sound_mute":"静音","tray_sound_default":"默认",
        "tray_sound_custom":"自定义","tray_sound_not_set":"(需设定音效)",
        "topmost_off":"关闭置顶","topmost_hard":"置顶",
        "notif_5min_msg":"{zone}等地区于 {n} 分钟后换场",
        "notif_5min_single":"{zone} 于 {n} 分钟后换场",
        "notif_fav_msg":"下个恐惧区域为 {zone} 等场景","notif_fav_single":"下个恐惧区域为 {zone}",
        "etc":"等","about_title":"关于 D2R TZ Tracker",
        "about_msg":"D2R TZ Tracker\n\nTZ API 与场景翻译由 d2tz.info 提供\n\n本工具完全免费，开源分享\n感谢 D2TZ 团队提供社区资源\n瀧月濑使用 AI 制作",
        "exp":"EXP","loot":"Loot",
    },
    "en-us": {
        "current":"Current TZ","next":"Next TZ","waiting":"Waiting for update…","fetching":"Fetching…",
        "error":"Fetch failed","no_data":"—","next_in":"Next in","by":"by d2tz.info",
        "source":"Data: d2tz.info","settings":"Settings","back":"← Back","refresh":"Refresh",
        "compact":"Compact","language":"Language","theme":"Theme","theme_dark":"Dark","theme_light":"Light",
        "save_theme":"Save current theme","delete_theme":"Delete theme","theme_name_prompt":"Enter theme name:",
        "theme_saved":"Theme saved","theme_deleted":"Theme deleted","opacity":"Opacity","scale":"Scale",
        "font_size":"Font Size","colors":"Colors","bg_color":"Background","text_color":"Text",
        "accent_color":"Accent","fav_color":"Favorite","btn_color":"Button Color","always_on_top":"Always on Top",
        "notif_section":"Notifications","notify_5min":"Alert before zone ends",
        "notify_fav":"Notify when next TZ is a favorite","notify_minutes":"Minutes before alert",
        "fav_color_enabled":"Use favorite color for favorite zones",
        "display_section":"Display","show_tier_exp":"Show EXP tier","show_tier_loot":"Show LOOT tier",
        "text_only_mode":"Text-only mode (transparent background)",
        "position_locked":"Lock position (click-through)",
        "sound_5min":"Zone-end alert sound","sound_fav":"Favorite alert sound",
        "sound_mute":"Mute","sound_default":"Default (sound.wav)","sound_custom":"Custom","sound_browse":"Browse…",
        "favorites":"Favorite Groups","fav_hint":"Notify when next TZ matches this group",
        "api_token_section":"API Token","api_token_hint":"Enter your d2tz.info Token (optional)",
        "tray_show":"Show / Hide","tray_compact":"Compact Mode","tray_settings":"Settings",
        "tray_quit":"Quit","tray_name":"D2R TZ Tracker","tray_notify5":"Zone-end Alert",
        "tray_notifyfav":"Fav Alert","tray_reset_pos":"Reset Position","tray_refresh":"Refresh Now",
        "tray_lock_pos":"Lock Position","tray_about":"About","tray_transparent":"Transparent Background",
        "tray_sound":"Sound","tray_sound_mute":"Mute","tray_sound_default":"Default",
        "tray_sound_custom":"Custom","tray_sound_not_set":"(file not set)",
        "topmost_off":"Off","topmost_hard":"Topmost",
        "notif_5min_msg":"{zone} and more zones end in {n} min",
        "notif_5min_single":"{zone} ends in {n} min",
        "notif_fav_msg":"Next TZ: {zone} and more","notif_fav_single":"Next TZ: {zone}",
        "etc":"","about_title":"About D2R TZ Tracker",
        "about_msg":"D2R TZ Tracker\n\nTZ API and area translations provided by d2tz.info\n\nFree and open source.\nThanks to the D2TZ team.\nCreated by 瀧月瀨 with AI.",
        "exp":"EXP","loot":"Loot",
    },
}

_OVERRIDES = {
    "ko":{"current":"현재 TZ","next":"다음 TZ","settings":"설정","back":"← 뒤로","tray_show":"표시 / 숨기기","tray_quit":"종료","tray_about":"정보","tray_transparent":"투명 배경","topmost_hard":"항상 위에","about_title":"D2R TZ Tracker 정보","about_msg":"D2R TZ Tracker\n\nTZ 데이터: d2tz.info\n\n무료 오픈소스","etc":" 외"},
    "ja":{"current":"現在 TZ","next":"次の TZ","settings":"設定","back":"← 戻る","tray_show":"表示 / 非表示","tray_quit":"終了","tray_about":"バージョン情報","tray_transparent":"背景を透明にする","topmost_hard":"常に最前面","about_title":"D2R TZ Tracker について","about_msg":"D2R TZ Tracker\n\nTZ データ: d2tz.info\n\n無料オープンソース","etc":"など"},
    "de":{"current":"Aktuell TZ","next":"Nächste TZ","settings":"Einstellungen","back":"← Zurück","tray_show":"Anzeigen / Verstecken","tray_quit":"Beenden","tray_about":"Über","tray_transparent":"Transparenter Hintergrund","topmost_hard":"Immer oben","about_title":"Über D2R TZ Tracker","about_msg":"D2R TZ Tracker\n\nDaten: d2tz.info\n\nKostenlos, Open Source","etc":" usw."},
    "es":{"current":"TZ Actual","next":"Siguiente TZ","settings":"Configuración","back":"← Volver","tray_show":"Mostrar / Ocultar","tray_quit":"Salir","tray_about":"Acerca de","tray_transparent":"Fondo transparente","topmost_hard":"Siempre arriba","about_title":"Acerca de D2R TZ Tracker","about_msg":"D2R TZ Tracker\n\nDatos: d2tz.info\n\nGratuito, Open Source"},
    "fr":{"current":"TZ Actuelle","next":"TZ Suivante","settings":"Paramètres","back":"← Retour","tray_show":"Afficher / Masquer","tray_quit":"Quitter","tray_about":"À propos","tray_transparent":"Fond transparent","topmost_hard":"Toujours au premier plan","about_title":"À propos de D2R TZ Tracker","about_msg":"D2R TZ Tracker\n\nDonnées: d2tz.info\n\nGratuit, Open Source"},
    "it":{"current":"TZ Corrente","next":"Prossima TZ","settings":"Impostazioni","back":"← Indietro","tray_show":"Mostra / Nascondi","tray_quit":"Esci","tray_about":"Informazioni","tray_transparent":"Sfondo trasparente","topmost_hard":"Sempre in primo piano","about_title":"Informazioni su D2R TZ Tracker","about_msg":"D2R TZ Tracker\n\nDati: d2tz.info\n\nGratuito, Open Source"},
    "pl":{"current":"Obecna TZ","next":"Następna TZ","settings":"Ustawienia","back":"← Wróć","tray_show":"Pokaż / Ukryj","tray_quit":"Wyjdź","tray_about":"O programie","tray_transparent":"Przezroczyste tło","topmost_hard":"Zawsze na wierzchu","about_title":"O D2R TZ Tracker","about_msg":"D2R TZ Tracker\n\nDane: d2tz.info\n\nBezpłatne, Open Source"},
    "pt-br":{"current":"TZ Atual","next":"Próxima TZ","settings":"Configurações","back":"← Voltar","tray_show":"Mostrar / Ocultar","tray_quit":"Sair","tray_about":"Sobre","tray_transparent":"Fundo transparente","topmost_hard":"Sempre no topo","about_title":"Sobre D2R TZ Tracker","about_msg":"D2R TZ Tracker\n\nDados: d2tz.info\n\nGratuito, Open Source"},
    "ru":{"current":"Текущая TZ","next":"Следующая TZ","settings":"Настройки","back":"← Назад","tray_show":"Показать / Скрыть","tray_quit":"Выход","tray_about":"О программе","tray_transparent":"Прозрачный фон","topmost_hard":"Всегда сверху","about_title":"О D2R TZ Tracker","about_msg":"D2R TZ Tracker\n\nДанные: d2tz.info\n\nБесплатно, Open Source"},
}
for _lk, _ov in _OVERRIDES.items():
    _I18N[_lk] = {**_I18N["en-us"], **_ov}


def _t(s: dict, key: str) -> str:
    lang = s.get("lang", "en-us")
    return _I18N.get(lang, _I18N["en-us"]).get(key, key)


# ── 顏色工具 ──────────────────────────────────────────────────────────────────
def _dim(hex_color: str, factor: float = 0.4) -> str:
    h = hex_color.lstrip("#")
    if len(h) != 6:
        return hex_color
    r = min(255, int(int(h[0:2], 16) * factor))
    g = min(255, int(int(h[2:4], 16) * factor))
    b = min(255, int(int(h[4:6], 16) * factor))
    return f"#{r:02x}{g:02x}{b:02x}"


def _is_dark(hex_color: str) -> bool:
    h = hex_color.lstrip("#")
    if len(h) != 6:
        return True
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return (0.299 * r + 0.587 * g + 0.114 * b) < 128


def _entry_bg(bg: str) -> str:
    return _dim(bg, 1.5) if _is_dark(bg) else _dim(bg, 0.88)


# ── Data 資料夾 ───────────────────────────────────────────────────────────────
def _get_data_dir() -> str:
    base = os.path.dirname(sys.executable) if getattr(sys, "frozen", False) \
           else os.path.dirname(os.path.abspath(__file__))
    data = os.path.join(base, "Data")
    return data if os.path.isdir(data) else base


_icon_cache: dict = {}


def _load_tk_img(filename: str, size: int):
    """載入 PNG 為 tk.PhotoImage，找不到回傳 None"""
    key = (filename, size)
    if key in _icon_cache:
        return _icon_cache[key]
    path = os.path.join(_get_data_dir(), filename)
    if not os.path.exists(path):
        return None
    try:
        from PIL import Image as PILImage, ImageTk
        img   = PILImage.open(path).convert("RGBA").resize((size, size))
        photo = ImageTk.PhotoImage(img)
        _icon_cache[key] = photo
        return photo
    except Exception as e:
        print(f"[UI] 載入圖示失敗 {filename}: {e}")
        return None


# ── Windows API ───────────────────────────────────────────────────────────────
def _round_corners(hwnd):
    try:
        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            hwnd, 33, ctypes.byref(ctypes.c_int(2)), ctypes.sizeof(ctypes.c_int))
    except Exception:
        pass


def _set_layered(hwnd, enable: bool):
    GWL_EXSTYLE   = -20
    WS_EX_LAYERED = 0x00080000
    try:
        style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        style = (style | WS_EX_LAYERED) if enable else (style & ~WS_EX_LAYERED)
        ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style)
    except Exception:
        pass


def _set_click_through(hwnd, enable: bool):
    GWL_EXSTYLE       = -20
    WS_EX_TRANSPARENT = 0x00000020
    try:
        style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        style = (style | WS_EX_TRANSPARENT) if enable else (style & ~WS_EX_TRANSPARENT)
        ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style)
    except Exception:
        pass


def _set_appwindow(hwnd):
    GWL_EXSTYLE      = -20
    WS_EX_APPWINDOW  = 0x00040000
    WS_EX_TOOLWINDOW = 0x00000080
    try:
        style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        style = (style | WS_EX_APPWINDOW) & ~WS_EX_TOOLWINDOW
        ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style)
    except Exception:
        pass


def _usable_height() -> int:
    try:
        import ctypes as _ct
        class RECT(_ct.Structure):
            _fields_ = [("left",_ct.c_long),("top",_ct.c_long),
                        ("right",_ct.c_long),("bottom",_ct.c_long)]
        rc = RECT()
        _ct.windll.user32.SystemParametersInfoW(48, 0, _ct.byref(rc), 0)
        return rc.bottom
    except Exception:
        return 1040


def _countdown() -> str:
    import datetime
    now = datetime.datetime.now()
    m, s = now.minute, now.second
    nxt  = next((x for x in (0, 30, 60) if x > m), 60)
    ds   = (nxt - m) * 60 - s
    return f"{ds // 60}:{ds % 60:02d}"


def _truncate_text(text: str, font_spec: tuple, max_px: int) -> str:
    """
    用 tkinter font 測量實際像素寬度，超過 max_px 就截斷加「…」。
    font_spec：(family, size, weight) tuple。
    """
    try:
        import tkinter.font as tkfont
        fam, sz, wt = font_spec
        f = tkfont.Font(family=fam, size=sz, weight=wt)
        if f.measure(text) <= max_px:
            return text
        # 二分搜尋最長可放下的字元數
        lo, hi = 0, len(text)
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if f.measure(text[:mid] + "…") <= max_px:
                lo = mid
            else:
                hi = mid - 1
        return text[:lo] + "…"
    except Exception:
        # fallback：按字元數截斷
        limit = max(4, max_px // 14)
        return text if len(text) <= limit else text[:limit-1] + "…"


def _group_display_name(group: dict, lang: str, settings: dict) -> str:
    """群組顯示名稱，直接連接所有場景名稱（截斷由呼叫端處理）"""
    return get_group_name(group, lang)


def _short_group_name(group: dict, lang: str, settings: dict) -> str:
    """迷你模式用：第一個場景 + 等"""
    zones = group.get("zones", [])
    if not zones:
        return "—"
    first = get_zone_name(zones[0], lang)
    if len(zones) == 1:
        return first
    etc = _t(settings, "etc")
    return f"{first}{etc}" if etc else f"{first}…"


# ═════════════════════════════════════════════════════════════════════════════
class TZWindow:

    FONT_FAMILY = "Microsoft JhengHei UI"

    def __init__(self, settings: dict, scheduler=None):
        self.settings      = settings
        self.scheduler     = scheduler
        self.page          = settings.get("page", "main")
        self._visible      = True
        self._settings_win = None

        self.cur_group = None
        self.nxt_group = None
        self.status    = "idle"

        self.root = tk.Tk()
        self.root.title("D2R TZ Tracker")
        self.root.resizable(False, False)
        self.root.overrideredirect(True)

        self.root.update_idletasks()
        _set_appwindow(self.root.winfo_id())

        # 基本設定
        bg = settings.get("bg_color", "#120d1f")
        self.root.configure(bg=bg)
        self.root.attributes("-topmost", settings.get("always_on_top", True))
        self.root.attributes("-alpha", settings.get("opacity", 0.93))

        # 建立所有 widget
        self._rebuild()
        self._set_pos()
        self.root.update_idletasks()
        _round_corners(self.root.winfo_id())

        if settings.get("position_locked", False):
            self.root.after(200, lambda: _set_click_through(self.root.winfo_id(), True))

        self._tick()

    # ── 字體/縮放 ─────────────────────────────────────────────────────────────

    def _f(self, size: int, bold: bool = False) -> tuple:
        sc = self.settings.get("scale", 1.0)
        fs = self.settings.get("font_size", 13)
        sz = max(6, int(size * sc * fs / 13))
        return (self.FONT_FAMILY, sz, "bold" if bold else "normal")

    def _px(self, n: int) -> int:
        return max(1, int(n * self.settings.get("scale", 1.0)))

    def _c(self, key: str) -> str:
        return self.settings.get(key, "#888888")

    # ── 樣式 ──────────────────────────────────────────────────────────────────

    def _apply_style(self):
        s  = self.settings
        bg = s.get("bg_color", "#120d1f")
        self.root.attributes("-topmost", s.get("always_on_top", True))
        self.root.configure(bg=bg)

        if s.get("text_only_mode", False):
            # 透明背景：用 after 延遲設定，確保視窗已完全顯示
            self.root.attributes("-alpha", 1.0)
            self.root.after(50, lambda: self._apply_transparent(bg))
        else:
            # 一般模式：先清除透明色，再設 alpha
            try:
                self.root.wm_attributes("-transparentcolor", "")
            except Exception:
                pass
            self.root.attributes("-alpha", s.get("opacity", 0.93))

    def _apply_transparent(self, bg: str):
        """延遲套用透明色，確保視窗已完全渲染"""
        try:
            self.root.wm_attributes("-transparentcolor", bg)
        except Exception as e:
            print(f"[UI] transparentcolor 失敗: {e}")

    # ── 視窗大小（精確符合實際 widget 高度）──────────────────────────────────

    def _win_size(self) -> tuple[int, int | None]:
        """
        回傳 (寬, 高)。
        完整版高度回傳 None，讓 tkinter 根據內容自動撐開後再讀取實際高度。
        """
        s  = self.settings
        sc = s.get("scale", 1.0)
        fs = s.get("font_size", 13)

        if self.page == "compact":
            row_h = int((fs + 8) * sc)
            h = COMPACT_BAR_H + row_h * 2 + int(14 * sc)
            return int(WIN_W_COMPACT * sc), h

        return int(WIN_W_MAIN * sc), None

    # ── 位置 ──────────────────────────────────────────────────────────────────

    def _set_pos(self):
        s  = self.settings
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        w, h = self._win_size()

        if h is None:
            # 完整版：先設寬度讓 tkinter 計算內容高度，再讀取實際高度
            self.root.geometry(f"{w}x1")
            self.root.update_idletasks()
            h = self.root.winfo_reqheight()
            # reqheight 有時偏小，加上底列保護
            h = max(h, BAR_H + BOT_H + 80)

        if "win_x" not in s or "win_y" not in s:
            uh = _usable_height()
            s["win_x"] = max(0, sw - w - s.get("pos_x", 50))
            s["win_y"] = max(0, uh - h - s.get("pos_y", 50))

        x = max(-w + 20, min(s["win_x"], sw - 20))
        y = max(-h + 20, min(s["win_y"], sh - 20))
        s["win_x"], s["win_y"] = x, y
        self.root.geometry(f"{w}x{h}+{x}+{y}")

    # ── Rebuild ───────────────────────────────────────────────────────────────

    def _rebuild(self):
        keep = self._settings_win
        for w in list(self.root.winfo_children()):
            if keep is not None and w == keep:
                continue
            try:
                w.destroy()
            except Exception:
                pass
        bg = self.settings.get("bg_color", "#120d1f")
        self.root.configure(bg=bg)
        if self.page == "compact":
            self._build_compact()
        else:
            self._build_main()
        # widget 建立後才算位置（完整版需要 reqheight）
        self._set_pos()
        # 最後套用樣式（transparentcolor 必須在 widget 存在後才設）
        self._apply_style()

    def _switch_page(self, page: str):
        self.page = page
        self.settings["page"] = page
        config.save(self.settings)
        self.root.after(10, self._rebuild)

    # ── 拖曳 ──────────────────────────────────────────────────────────────────

    def _bind_drag(self, w):
        if self.settings.get("position_locked", False):
            return
        w.bind("<ButtonPress-1>",   self._ds)
        w.bind("<B1-Motion>",       self._dm)
        w.bind("<ButtonRelease-1>", self._de)

    def _ds(self, e):
        self._ox = e.x_root - self.root.winfo_x()
        self._oy = e.y_root - self.root.winfo_y()

    def _dm(self, e):
        self.root.geometry(f"+{e.x_root-self._ox}+{e.y_root-self._oy}")

    def _de(self, _e):
        self.settings["win_x"] = self.root.winfo_x()
        self.settings["win_y"] = self.root.winfo_y()
        config.save(self.settings)

    # ── 右鍵選單 ──────────────────────────────────────────────────────────────

    def _bind_rc(self, w):
        w.bind("<Button-3>", self._menu)

    def _menu(self, event):
        s  = self.settings
        bg = self._c("bg_color")
        tc = self._c("text_color")
        ac = self._c("accent_color")
        eb = _entry_bg(bg)

        m = tk.Menu(self.root, tearoff=0, bg=eb, fg=tc,
                    activebackground=_dim(ac, 0.4), activeforeground=tc,
                    relief="flat", bd=0)
        ck = lambda v: "✓ " if v else "  "

        m.add_command(label=ck(self._visible)+_t(s,"tray_show"),
                      command=self.hide if self._visible else self.show)
        m.add_command(label=ck(self.page=="compact")+_t(s,"tray_compact"),
                      command=self._to_main if self.page=="compact" else self._to_compact)
        m.add_command(label=_t(s,"tray_settings"), command=self._to_settings)
        m.add_separator()
        on_top = s.get("topmost_mode","hard") == "hard"
        m.add_command(label=ck(on_top)+_t(s,"topmost_hard"),
                      command=lambda: self._set_topmost("off" if on_top else "hard"))
        m.add_command(label=ck(s.get("notify_5min",True))+_t(s,"tray_notify5"),
                      command=lambda: self._toggle("notify_5min"))
        m.add_command(label=ck(s.get("notify_fav",True))+_t(s,"tray_notifyfav"),
                      command=lambda: self._toggle("notify_fav"))
        m.add_separator()
        m.add_command(label=_t(s,"tray_refresh"), command=self._on_refresh)
        m.add_command(label=ck(s.get("position_locked",False))+_t(s,"tray_lock_pos"),
                      command=self._toggle_lock)
        m.add_command(label=ck(s.get("text_only_mode",False))+_t(s,"tray_transparent"),
                      command=self._toggle_transparent)
        m.add_command(label=_t(s,"tray_reset_pos"), command=self.reset_position)
        m.add_separator()
        m.add_command(label=_t(s,"tray_about"), command=self._show_about)
        m.add_separator()
        m.add_command(label=_t(s,"tray_quit"), command=self._quit)
        try:
            m.tk_popup(event.x_root, event.y_root)
        finally:
            m.grab_release()

    # ── Hover 已移除（純文字模式下 hover 會中斷透明效果）────────────────────

    def _bind_hover(self, w):
        pass  # no-op，保留所有呼叫點不需改動

    # ── 主頁 ──────────────────────────────────────────────────────────────────

    def _build_main(self):
        s   = self.settings
        bg  = self._c("bg_color")
        ac  = self._c("accent_color")
        tc  = self._c("text_color")
        sub = self._c("sub_color")
        tom = s.get("text_only_mode", False)
        lkd = s.get("position_locked", False)

        bar_bg = bg if tom else _dim(ac, 0.22)
        bot_bg = bg if tom else _dim(ac, 0.22)
        sep_c  = bg if tom else _dim(ac, 0.5)

        # 底列先 pack（佔位），body 後 pack（expand）
        bot = tk.Frame(self.root, bg=bot_bg, height=BOT_H)
        bot.pack(side="bottom", fill="x")
        bot.pack_propagate(False)
        if not lkd: self._bind_drag(bot)
        self._bind_rc(bot); self._bind_hover(bot)

        src = tk.Label(bot, text=_t(s,"source"), bg=bot_bg, fg=ac,
                       font=self._f(9), cursor="hand2")
        src.pack(side="left", padx=6)
        src.bind("<Button-1>", lambda _: webbrowser.open("https://www.d2tz.info/"))
        tk.Label(bot, text=_t(s,"by"), bg=bot_bg, fg=sub, font=self._f(9)).pack(side="right", padx=6)

        cd_f = tk.Frame(bot, bg=bot_bg); cd_f.pack(side="right")
        tk.Label(cd_f, text=_t(s,"next_in")+"  ", bg=bot_bg, fg=sub, font=self._f(9)).pack(side="left")
        self._cd_lbl = tk.Label(cd_f, text=_countdown(), bg=bot_bg, fg=ac, font=self._f(11, True))
        self._cd_lbl.pack(side="left")

        # 標題列
        bar = tk.Frame(self.root, bg=bar_bg, height=BAR_H)
        bar.pack(side="top", fill="x")
        bar.pack_propagate(False)
        if not lkd: self._bind_drag(bar)
        self._bind_rc(bar); self._bind_hover(bar)

        tk.Label(bar, text="TZ Tracker", bg=bar_bg, fg=self._c("title_color"),
                 font=self._f(12, True)).pack(side="left", padx=8)

        for sym, cmd in [("□", self._to_compact), ("↻", self._on_refresh), ("⚙", self._to_settings)]:
            b = tk.Label(bar, text=sym, bg=bar_bg, fg=ac, font=self._f(12), cursor="hand2")
            b.pack(side="right", padx=3)
            b.bind("<Button-1>", lambda _e, c=cmd: c())
            b.bind("<Enter>",    lambda _e, lb=b: lb.configure(fg=self._c("title_color")))
            b.bind("<Leave>",    lambda _e, lb=b: lb.configure(fg=self._c("accent_color")))

        # 內容區
        body = tk.Frame(self.root, bg=bg)
        body.pack(side="top", fill="both", expand=True)
        if not lkd: self._bind_drag(body)
        self._bind_rc(body); self._bind_hover(body)

        self._tz_block(body, "current", self.cur_group)

        sep = tk.Frame(body, bg=sep_c, height=1)
        sep.pack(fill="x", padx=10, pady=4)
        self._bind_hover(sep)

        waiting = self.status == "waiting"
        self._tz_block(body, "next", None if waiting else self.nxt_group, waiting=waiting)

    def _tz_block(self, parent, row_type: str, group, waiting: bool = False):
        """
        一個 TZ 區塊（三個獨立子 Frame）：
          [lbl_row]  當前 TZ              ★
          [name_lbl] 場景名稱（最多兩行）
          [tier_row] EXP B   Loot C
        """
        s    = self.settings
        bg   = self._c("bg_color")
        ac   = self._c("accent_color")
        tc   = self._c("text_color")
        sub  = self._c("sub_color")
        favs = s.get("favorites", [])
        lang = s.get("lang", "en-us")
        px   = self._px

        block = tk.Frame(parent, bg=bg)
        block.pack(fill="x", padx=8, pady=(2, 0))
        self._bind_hover(block)

        # 決定顯示內容
        if waiting:
            display, nc, group = _t(s,"waiting"), sub, None
        elif self.status == "fetching" and group is None:
            display, nc = _t(s,"fetching"), sub
        elif group is None:
            display, nc = _t(s,"no_data"), sub
        else:
            display = _group_display_name(group, lang, s)
            gid    = group.get("id","")
            is_fav = gid in favs
            nc     = (self._c("fav_color") if is_fav and s.get("fav_color_enabled",True) else tc)

        # 標籤行
        lbl_row = tk.Frame(block, bg=bg)
        lbl_row.pack(fill="x")
        self._bind_hover(lbl_row)
        tk.Label(lbl_row, text=_t(s, row_type), bg=bg, fg=sub, font=self._f(9)).pack(side="left")

        if group is not None:
            gid    = group.get("id","")
            is_fav = gid in favs
            star_c = self._c("fav_color") if is_fav else sub
            star = tk.Label(lbl_row, text="★", bg=bg, fg=star_c, font=self._f(14), cursor="hand2")
            star.pack(side="right", padx=(0, 4))
            star.bind("<Button-1>", lambda _e, g=group: self._toggle_fav(g))

        # 場景名稱（單行，超過寬度截斷加…）
        w_px   = int(WIN_W_MAIN * s.get("scale",1.0)) - 48
        display = _truncate_text(display, self._f(13, True), w_px)
        name_lbl = tk.Label(block, text=display, bg=bg, fg=nc,
                            font=self._f(13, True),
                            anchor="center")
        name_lbl.pack(fill="x", padx=4, pady=1)
        self._bind_hover(name_lbl)

        # EXP / LOOT tier 行
        if group is not None:
            show_exp  = s.get("show_tier_exp",  True)
            show_loot = s.get("show_tier_loot", True)
            if show_exp or show_loot:
                tier_row = tk.Frame(block, bg=bg)
                tier_row.pack(fill="x", padx=px(8), pady=(0, 2))
                self._bind_hover(tier_row)

                ico_sz = max(8, int(12 * s.get("scale",1.0)))

                # 靠右排列：先 pack Loot（最右），再 pack EXP（Loot 左邊）
                # 視覺效果：[EXP圖] E值   [Loot圖] L值
                if show_loot:
                    val = group.get("tier_loot","?")
                    img = _load_tk_img("loot.png", ico_sz)
                    lf  = tk.Frame(tier_row, bg=bg)
                    lf.pack(side="right", padx=(0, px(4)))
                    tk.Label(lf, text=val, bg=bg, fg=tc, font=self._f(10, True)).pack(side="right")
                    if img:
                        tk.Label(lf, image=img, bg=bg).pack(side="right", padx=(0,2))

                if show_exp:
                    val = group.get("tier_exp","?")
                    img = _load_tk_img("exp.png", ico_sz)
                    ef  = tk.Frame(tier_row, bg=bg)
                    ef.pack(side="right", padx=(0, px(10)))
                    tk.Label(ef, text=val, bg=bg, fg=tc, font=self._f(10, True)).pack(side="right")
                    if img:
                        tk.Label(ef, image=img, bg=bg).pack(side="right", padx=(0,2))

    # ── 迷你模式（兩個獨立 Frame）─────────────────────────────────────────────

    def _build_compact(self):
        s   = self.settings
        bg  = self._c("bg_color")
        ac  = self._c("accent_color")
        tc  = self._c("text_color")
        sub = self._c("sub_color")
        lang = s.get("lang","en-us")
        favs = s.get("favorites",[])
        tom  = s.get("text_only_mode", False)
        lkd  = s.get("position_locked", False)

        bar_bg = bg if tom else _dim(ac, 0.22)

        # 標題列：透明模式 = bg（被消），一般模式 = dim_ac 深色條
        bar = tk.Frame(self.root, bg=bar_bg, height=COMPACT_BAR_H)
        bar.pack(side="top", fill="x")
        bar.pack_propagate(False)
        if not lkd: self._bind_drag(bar)
        self._bind_rc(bar); self._bind_hover(bar)

        tk.Label(bar, text="TZ Tracker", bg=bar_bg, fg=sub, font=self._f(8)).pack(side="left", padx=5)
        exp_btn = tk.Label(bar, text="⊞", bg=bar_bg, fg=ac, font=self._f(11), cursor="hand2")
        exp_btn.pack(side="right", padx=2)
        exp_btn.bind("<Button-1>", lambda _: self._to_main())

        # 內容區：透明模式 = bg（被消），只剩文字浮著
        body = tk.Frame(self.root, bg=bg)
        body.pack(side="top", fill="both", expand=True)
        if not lkd: self._bind_drag(body)
        self._bind_rc(body); self._bind_hover(body)

        def _col(g):
            if g and g.get("id","") in favs and s.get("fav_color_enabled",True):
                return self._c("fav_color")
            return tc

        rows = [
            (_t(s,"current"), _short_group_name(self.cur_group, lang, s) if self.cur_group else "—", _col(self.cur_group)),
            (_t(s,"next"),
             _t(s,"waiting") if self.status=="waiting" else
             (_short_group_name(self.nxt_group, lang, s) if self.nxt_group else "—"),
             sub if (self.status=="waiting" or not self.nxt_group) else _col(self.nxt_group)),
        ]

        for lbl, name, col in rows:
            row = tk.Frame(body, bg=bg)
            row.pack(fill="x", padx=6, pady=2)
            if not lkd: self._bind_drag(row)
            self._bind_rc(row)
            lbl_widget = tk.Label(row, text=lbl+"  ", bg=bg, fg=sub, font=self._f(8),
                     anchor="e")
            lbl_widget.pack(side="left")
            # 名稱可用寬度 = 視窗寬 - 標籤實際寬 - padding
            lbl_w = int(WIN_W_COMPACT * s.get("scale",1.0))
            name_max_px = lbl_w - 60
            name_trunc  = _truncate_text(name, self._f(10, True), name_max_px)
            tk.Label(row, text=name_trunc, bg=bg, fg=col, font=self._f(10, True),
                     anchor="w").pack(side="left")

    # ── 頁面切換 ──────────────────────────────────────────────────────────────

    def _to_main(self):    self._switch_page("main")
    def _to_compact(self): self._switch_page("compact")

    def _to_settings(self):
        if self._settings_win is not None:
            try: self._settings_win.lift(); return
            except Exception: self._settings_win = None
        self._open_settings_win()

    def _close_settings_win(self):
        if self._settings_win is not None:
            try: self._settings_win.destroy()
            except Exception: pass
            self._settings_win = None

    # ── 設定視窗（CTk Toplevel，永遠不透明）─────────────────────────────────

    def _open_settings_win(self):
        sc   = SETTINGS_SCALE
        sw_w = int(WIN_W_SETTINGS * sc)
        sw_h = int(WIN_H_SETTINGS * sc)

        ctk.set_appearance_mode("dark")
        win = ctk.CTkToplevel(self.root)
        win.title("D2R TZ Tracker — " + _t(self.settings, "settings"))
        win.resizable(False, False)
        win.overrideredirect(True)
        self._settings_win = win

        s  = self.settings
        bg = s.get("bg_color","#120d1f")
        ac = s.get("accent_color","#9d4edd")
        tc = s.get("text_color","#e8d5b7")
        eb = _entry_bg(bg)

        win.configure(fg_color=bg)
        win.attributes("-topmost", s.get("always_on_top", True))
        win.attributes("-alpha", 1.0)

        self.root.update_idletasks()
        rx, ry = self.root.winfo_x(), self.root.winfo_y()
        rw     = self.root.winfo_width()
        scw, sch = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        sx = rx - sw_w - 8
        if sx < 0: sx = rx + rw + 8
        sy = max(0, min(ry, sch - sw_h))
        win.geometry(f"{sw_w}x{sw_h}+{sx}+{sy}")

        try: _round_corners(win.winfo_id())
        except Exception: pass

        win.protocol("WM_DELETE_WINDOW", self._close_settings_win)

        _ox, _oy = [0], [0]
        def _ds(e): _ox[0]=e.x_root-win.winfo_x(); _oy[0]=e.y_root-win.winfo_y()
        def _dm(e): win.geometry(f"+{e.x_root-_ox[0]}+{e.y_root-_oy[0]}")

        def fct(size, bold=False):
            return ctk.CTkFont(family=self.FONT_FAMILY, size=int(size*sc),
                               weight="bold" if bold else "normal")

        def px(n): return max(1, int(n*sc))

        dim_ac = _dim(ac, 0.22)
        frame  = ctk.CTkFrame(win, fg_color=bg, corner_radius=10)
        frame.pack(fill="both", expand=True)

        bar = ctk.CTkFrame(frame, fg_color=dim_ac, height=px(32), corner_radius=0)
        bar.pack(fill="x"); bar.pack_propagate(False)
        bar.bind("<ButtonPress-1>",_ds); bar.bind("<B1-Motion>",_dm)
        bi = ctk.CTkFrame(bar, fg_color="transparent")
        bi.pack(fill="both",expand=True,padx=px(8),pady=px(4))
        bi.bind("<ButtonPress-1>",_ds); bi.bind("<B1-Motion>",_dm)
        ctk.CTkButton(bi,text=_t(s,"back"),width=px(60),height=px(22),
                      fg_color="transparent",hover_color=_dim(ac,0.4),
                      text_color=ac,font=fct(12,True),
                      command=self._close_settings_win).pack(side="left")
        ctk.CTkLabel(bi,text=_t(s,"settings"),font=fct(13,True),
                     text_color=s.get("title_color","#c77dff")).pack(side="left",padx=px(8))

        scroll = ctk.CTkScrollableFrame(frame,fg_color=bg,
                                        scrollbar_button_color=_dim(ac,0.45),
                                        scrollbar_button_hover_color=ac,corner_radius=0)
        scroll.pack(fill="both",expand=True)
        self._build_settings_content(scroll, sc, eb, fct, px)

    def _build_settings_content(self, scroll, sc, eb, fct, px):
        s   = self.settings
        ac  = self._c("accent_color")
        tc  = self._c("text_color")
        bg  = self._c("bg_color")
        sub = self._c("sub_color")

        def sep(text):
            ctk.CTkLabel(scroll,text=text,font=fct(12,True),text_color=ac,anchor="w").pack(fill="x",padx=px(6),pady=(px(10),px(2)))
            ctk.CTkFrame(scroll,height=1,fg_color=_dim(ac,0.5)).pack(fill="x",padx=px(6))

        def mk_opt(parent,values,var,cmd):
            return ctk.CTkOptionMenu(parent,values=values,variable=var,fg_color=eb,button_color=ac,
                button_hover_color=ac,text_color=tc,dropdown_fg_color=eb,dropdown_text_color=tc,
                dropdown_hover_color=_dim(ac,0.35),font=fct(12),dropdown_font=fct(12),command=cmd)

        sep(_t(s,"language"))
        lk=list(LANG_MAP.keys()); ln=list(LANG_MAP.values())
        lv=ctk.StringVar(value=LANG_MAP.get(s.get("lang","en-us"),"English"))
        mk_opt(scroll,ln,lv,lambda v:self._set_lang(lk[ln.index(v)])).pack(fill="x",padx=px(8),pady=px(4))

        sep(_t(s,"theme"))
        tl=config.get_all_theme_names(s); tids=[t[0] for t in tl]
        tdsp=[_t(s,t[1].strip("_")) if t[1].startswith("__") else t[1] for t in tl]
        cur_t=tdsp[tids.index(s.get("theme","dark"))] if s.get("theme","dark") in tids else tdsp[0]
        tv=ctk.StringVar(value=cur_t)
        mk_opt(scroll,tdsp,tv,lambda v:self._set_theme(tids[tdsp.index(v)])).pack(fill="x",padx=px(8),pady=(px(4),px(2)))
        tbr=ctk.CTkFrame(scroll,fg_color="transparent"); tbr.pack(fill="x",padx=px(8),pady=px(2))
        bc=s.get("btn_color") or ac
        for txt,cmd in [(_t(s,"save_theme"),self._save_theme),(_t(s,"delete_theme"),self._delete_theme)]:
            ctk.CTkButton(tbr,text=txt,height=px(26),fg_color=bc,
                hover_color=_dim(bc,1.6) if _is_dark(bc) else _dim(bc,0.8),
                text_color=tc,font=fct(11),command=cmd).pack(side="left",expand=True,fill="x",padx=(0,px(2)))

        sep(_t(s,"colors"))
        cdefs=[("bg_color",_t(s,"bg_color")),("text_color",_t(s,"text_color")),
               ("accent_color",_t(s,"accent_color")),("fav_color",_t(s,"fav_color")),("btn_color",_t(s,"btn_color"))]
        cg=ctk.CTkFrame(scroll,fg_color="transparent"); cg.pack(fill="x",padx=px(8),pady=px(4))
        for i,(key,lbl) in enumerate(cdefs):
            cf=ctk.CTkFrame(cg,fg_color="transparent"); cf.grid(row=0,column=i,padx=px(2),sticky="ew")
            cg.columnconfigure(i,weight=1)
            ctk.CTkLabel(cf,text=lbl,font=fct(9),text_color=sub).pack()
            ctk.CTkButton(cf,text="",height=px(24),fg_color=s.get(key,"#888"),
                hover_color=s.get(key,"#888"),command=lambda k=key:self._pick_color(k)).pack(fill="x")

        sep(_t(s,"opacity")+" / "+_t(s,"scale")+" / "+_t(s,"font_size"))
        for key,lk2,mn,mx,steps,dflt in [("opacity","opacity",0.2,1.0,16,0.93),("scale","scale",0.6,2.0,14,1.0),("font_size","font_size",8,20,12,13)]:
            row=ctk.CTkFrame(scroll,fg_color="transparent"); row.pack(fill="x",padx=px(8),pady=px(2))
            ctk.CTkLabel(row,text=_t(s,lk2),font=fct(11),text_color=tc,width=px(70)).pack(side="left")
            lv2=tk.StringVar(value=str(round(s.get(key,dflt),1)))
            ctk.CTkLabel(row,textvariable=lv2,font=fct(11),text_color=ac,width=px(36)).pack(side="right")
            def _cmd(k=key,lv=lv2):
                def _inner(v):
                    rv=round(float(v),1); lv.set(str(rv)); self.settings[k]=rv
                    self._rebuild(); config.save(self.settings)
                return _inner
            ctk.CTkSlider(row,from_=mn,to=mx,number_of_steps=steps,progress_color=ac,button_color=ac,
                variable=tk.DoubleVar(value=s.get(key,dflt)),command=_cmd()).pack(side="left",fill="x",expand=True,padx=px(4))

        sep(_t(s,"display_section"))
        topv=ctk.BooleanVar(value=s.get("topmost_mode","hard")=="hard")
        ctk.CTkSwitch(scroll,text=_t(s,"topmost_hard"),variable=topv,onvalue=True,offvalue=False,
            progress_color=ac,button_color=ac,text_color=tc,font=fct(12),
            command=lambda:self._set_topmost("hard" if topv.get() else "off")).pack(anchor="w",padx=px(14),pady=px(2))
        for key,lk2 in [("show_tier_exp","show_tier_exp"),("show_tier_loot","show_tier_loot"),
                        ("text_only_mode","text_only_mode"),("position_locked","position_locked")]:
            dv=True if key.startswith("show") else False
            bv=ctk.BooleanVar(value=s.get(key,dv))
            sw=ctk.CTkSwitch(scroll,text=_t(s,lk2),variable=bv,onvalue=True,offvalue=False,
                             progress_color=ac,button_color=ac,text_color=tc,font=fct(11))
            if key in ("show_tier_exp","show_tier_loot"):
                sw.configure(command=lambda k=key,v=bv:(self.settings.update({k:v.get()}),config.save(self.settings),self._rebuild()))
            elif key=="text_only_mode":
                sw.configure(command=lambda v=bv:self._set_text_only(v.get()))
            elif key=="position_locked":
                sw.configure(command=lambda v=bv:self._set_lock_pos(v.get()))
            sw.pack(anchor="w",padx=px(14),pady=px(1))

        sep(_t(s,"notif_section"))
        for key,lk2 in [("notify_5min","notify_5min"),("notify_fav","notify_fav"),("fav_color_enabled","fav_color_enabled")]:
            bv=ctk.BooleanVar(value=s.get(key,True))
            ctk.CTkSwitch(scroll,text=_t(s,lk2),variable=bv,onvalue=True,offvalue=False,
                progress_color=ac,button_color=ac,text_color=tc,font=fct(11),
                command=lambda k=key,v=bv:(self.settings.update({k:v.get()}),config.save(self.settings))
                ).pack(anchor="w",padx=px(14),pady=px(1))
        nm_row=ctk.CTkFrame(scroll,fg_color="transparent"); nm_row.pack(fill="x",padx=px(8),pady=px(4))
        ctk.CTkLabel(nm_row,text=_t(s,"notify_minutes"),font=fct(11),text_color=tc,width=px(110)).pack(side="left")
        nm_lbl=tk.StringVar(value=str(s.get("notify_minutes",5)))
        ctk.CTkLabel(nm_row,textvariable=nm_lbl,font=fct(11),text_color=ac,width=px(28)).pack(side="right")
        def _nm(v):
            rv=max(1,min(29,int(float(v)))); nm_lbl.set(str(rv)); self.settings["notify_minutes"]=rv; config.save(self.settings)
        ctk.CTkSlider(nm_row,from_=1,to=29,number_of_steps=28,progress_color=ac,button_color=ac,
            variable=tk.DoubleVar(value=s.get("notify_minutes",5)),command=_nm).pack(side="left",fill="x",expand=True,padx=px(4))

        # 音量滑桿
        vol_lbl = "音量" if s.get("lang","en-us") in ("zh-tw","zh-cn") else "Volume"
        sep(vol_lbl)
        vol_row = ctk.CTkFrame(scroll, fg_color="transparent")
        vol_row.pack(fill="x", padx=px(8), pady=px(4))
        vol_var = tk.StringVar(value=str(int(s.get("sound_volume", 1.0) * 100)) + "%")
        ctk.CTkLabel(vol_row, textvariable=vol_var, font=fct(11),
                     text_color=ac, width=px(40)).pack(side="right")
        def _vol_cmd(v):
            rv = round(float(v), 2)
            vol_var.set(f"{int(rv*100)}%")
            self.settings["sound_volume"] = rv
            config.save(self.settings)
        ctk.CTkSlider(vol_row, from_=0.0, to=1.0, number_of_steps=20,
                      progress_color=ac, button_color=ac,
                      variable=tk.DoubleVar(value=s.get("sound_volume", 1.0)),
                      command=_vol_cmd).pack(side="left", fill="x", expand=True, padx=(0, px(4)))

        for sk,lk2 in [("sound_url_5min","sound_5min"),("sound_url_fav","sound_fav")]:
            sep(_t(s,lk2)); self._sound_row(scroll,sk,px,ac,tc,sub,eb,fct,mk_opt)

        sep(_t(s,"favorites"))
        ctk.CTkLabel(scroll,text=_t(s,"fav_hint"),font=fct(11),text_color=sub,anchor="w",
            wraplength=int(WIN_W_SETTINGS*sc-20),justify="left").pack(fill="x",padx=px(8),pady=(0,px(3)))
        lang=s.get("lang","en-us"); favs=s.get("favorites",[]); self._fav_vars={}
        cur_act=None
        for g in TZ_GROUPS:
            an={"A":"1","B":"2","C":"3","D":"4","E":"5"}.get(g["id"][0],g["id"][0])
            al=f"ACT {an}"
            if al!=cur_act:
                cur_act=al
                ctk.CTkLabel(scroll,text=f"── {al} ──",font=fct(10,True),text_color=ac,anchor="center").pack(fill="x",padx=px(8),pady=(px(5),px(1)))
            var=ctk.BooleanVar(value=g["id"] in favs); self._fav_vars[g["id"]]=var
            ctk.CTkCheckBox(scroll,text=get_group_name(g,lang),variable=var,onvalue=True,offvalue=False,
                fg_color=ac,hover_color=ac,checkmark_color=bg,text_color=tc,font=fct(11),
                command=self._update_favs).pack(anchor="w",padx=px(18),pady=px(1))

        sep(_t(s,"api_token_section"))

        # 欄位列（輸入框 + 設定/確定按鈕）
        is_zh = s.get("lang","en-us") in ("zh-tw","zh-cn")
        cur_api = s.get("api_url","") or s.get("api_token","")

        # 欄位列（輸入框 + 設定/確定按鈕）
        api_row = ctk.CTkFrame(scroll, fg_color="transparent")
        api_row.pack(fill="x", padx=px(8), pady=(0,px(6)))

        tv_api = tk.StringVar(value=cur_api)
        # 初始顯示：有值就遮蔽，空白讓 placeholder 顯示
        initial_show = "*" if cur_api else ""
        api_entry = ctk.CTkEntry(
            api_row, textvariable=tv_api,
            show=initial_show,
            fg_color=eb, border_color=_dim(ac,0.5),
            text_color=tc, font=fct(11),
            placeholder_text="Token 或 https://xxx.workers.dev",
            state="disabled"
        )
        api_entry.pack(side="left", fill="x", expand=True, padx=(0,px(6)))

        edit_lbl = tk.StringVar(value="設定" if is_zh else "Edit")
        editing  = [False]

        def _toggle_edit():
            if not editing[0]:
                # 進入編輯模式：明文顯示方便輸入
                editing[0] = True
                edit_lbl.set("確定" if is_zh else "Confirm")
                api_entry.configure(state="normal", show="")
                api_entry.focus()
            else:
                # 確定儲存：URL 明文，token 遮蔽
                editing[0] = False
                edit_lbl.set("設定" if is_zh else "Edit")
                v = tv_api.get().strip()
                api_entry.configure(
                    state="disabled",
                    show="*" if tv_api.get().strip() else ""
                )
                _save_api()

        def _save_api():
            val = tv_api.get().strip()
            if val.startswith("http"):
                # Worker URL
                self.settings["api_url"]   = val
                self.settings["api_token"] = ""
            else:
                # Token
                self.settings["api_token"] = val
                self.settings["api_url"]   = ""
            config.save(self.settings)

        btn_col = s.get("btn_color") or ac
        ctk.CTkButton(
            api_row, textvariable=edit_lbl,
            width=px(52), height=px(28),
            fg_color=btn_col,
            hover_color=_dim(btn_col,1.6) if _is_dark(btn_col) else _dim(btn_col,0.8),
            text_color=tc, font=fct(11),
            command=_toggle_edit
        ).pack(side="right")

        ctk.CTkFrame(scroll,height=px(10),fg_color="transparent").pack()

    def _sound_row(self, parent, sk, px, ac, tc, sub, eb, fct, mk_opt):
        s=self.settings; cur=s.get(sk,"")
        if cur=="__mute__": cd=_t(s,"sound_mute")
        elif cur in ("","sound.wav"): cd=_t(s,"sound_default")
        else: cd=_t(s,"sound_custom")
        modes=[_t(s,"sound_mute"),_t(s,"sound_default"),_t(s,"sound_custom")]
        sv=ctk.StringVar(value=cd); sf=tk.StringVar(value=cur if cur not in ("","__mute__","sound.wav") else "")
        ir=ctk.CTkFrame(parent,fg_color="transparent")
        def _pick():
            from tkinter import filedialog
            p=filedialog.askopenfilename(parent=self.root,title="選擇音效",
                filetypes=[("Audio","*.mp3 *.wav *.ogg *.flac *.aac"),("All","*.*")])
            if p: sf.set(p); self.settings[sk]=p; config.save(self.settings); _ui(_t(s,"sound_custom"))
        def _ui(m):
            for w in ir.winfo_children(): w.destroy()
            if m==_t(s,"sound_mute"):
                ctk.CTkLabel(ir,text="🔇 "+_t(s,"sound_mute"),font=fct(10),text_color=sub,anchor="w").pack(side="left",padx=px(4))
            elif m==_t(s,"sound_default"):
                ctk.CTkLabel(ir,text="🔔 sound.wav",font=fct(10),text_color=sub,anchor="w").pack(side="left",padx=px(4))
            else:
                ctk.CTkLabel(ir,text=sf.get() or "（未選擇）",font=fct(10),text_color=sub,anchor="w",wraplength=px(200)).pack(side="left",fill="x",expand=True,padx=px(4))
                ctk.CTkButton(ir,text=_t(s,"sound_browse"),width=px(46),height=px(22),fg_color=_dim(ac,0.45),hover_color=ac,text_color=tc,font=fct(10),command=_pick).pack(side="right")
        def _om(v):
            if v==_t(s,"sound_mute"): self.settings[sk]="__mute__"; config.save(self.settings)
            elif v==_t(s,"sound_default"): self.settings[sk]=""; config.save(self.settings)
            _ui(v)
        mk_opt(parent,modes,sv,_om).pack(fill="x",padx=px(8),pady=(px(2),px(1)))
        ir.pack(fill="x",padx=px(8),pady=(0,px(4))); _ui(cd)

    # ── 動作 ──────────────────────────────────────────────────────────────────

    def _on_refresh(self):
        if self.scheduler: self.scheduler.force_refresh()

    def _toggle(self, key):
        self.settings[key] = not self.settings.get(key, True)
        config.save(self.settings)

    def _toggle_fav(self, group):
        favs=list(self.settings.get("favorites",[])); gid=group.get("id","")
        if gid in favs: favs.remove(gid)
        elif gid: favs.append(gid)
        self.settings["favorites"]=favs; config.save(self.settings); self._rebuild()

    def _update_favs(self):
        self.settings["favorites"]=[gid for gid,v in self._fav_vars.items() if v.get()]
        config.save(self.settings)

    def _toggle_lock(self):
        self._set_lock_pos(not self.settings.get("position_locked",False))

    def _toggle_transparent(self):
        self._set_text_only(not self.settings.get("text_only_mode",False))

    def _set_lock_pos(self, val):
        self.settings["position_locked"]=val; config.save(self.settings)
        _set_click_through(self.root.winfo_id(), val); self._rebuild()

    def _set_text_only(self, val):
        self.settings["text_only_mode"]=val; config.save(self.settings)
        self._rebuild()

    def _set_topmost(self, mode):
        self.settings["topmost_mode"]=mode
        if mode=="off":
            self.settings["always_on_top"]=False; self.root.attributes("-topmost",False)
        else:
            self.settings["always_on_top"]=True; self.root.attributes("-topmost",True)
            try: ctypes.windll.user32.SetWindowPos(self.root.winfo_id(),-1,0,0,0,0,0x0002|0x0001|0x0010)
            except Exception: pass
        config.save(self.settings)

    def _set_lang(self, lang_key):
        self.settings["lang"]=lang_key; config.save(self.settings); self._rebuild()

    def _set_theme(self, theme_id):
        self.settings=config.apply_theme(self.settings,theme_id); config.save(self.settings)
        self._rebuild()
        notifier.set_ui_colors(bg=self.settings.get("bg_color","#1e1030"),
            accent=self.settings.get("accent_color","#9d4edd"),text_color=self.settings.get("text_color","#e8d5b7"))

    def _save_theme(self):
        name=simpledialog.askstring(_t(self.settings,"save_theme"),_t(self.settings,"theme_name_prompt"),parent=self.root)
        if name and name.strip():
            self.settings=config.save_custom_theme(self.settings,name.strip()); config.save(self.settings)
            messagebox.showinfo(_t(self.settings,"save_theme"),_t(self.settings,"theme_saved"),parent=self.root)
            self._rebuild()

    def _delete_theme(self):
        cur=self.settings.get("theme","dark")
        if cur in config.THEMES:
            messagebox.showwarning(_t(self.settings,"delete_theme"),"Cannot delete built-in themes.",parent=self.root); return
        self.settings=config.delete_custom_theme(self.settings,cur); config.save(self.settings); self._rebuild()

    def _pick_color(self, key):
        color=colorchooser.askcolor(color=self.settings.get(key,"#888"),parent=self.root,title=key)[1]
        if color:
            self.settings[key]=color; config.save(self.settings); self._rebuild()
            notifier.set_ui_colors(bg=self.settings.get("bg_color","#1e1030"),
                accent=self.settings.get("accent_color","#9d4edd"),text_color=self.settings.get("text_color","#e8d5b7"))

    def _show_about(self):
        messagebox.showinfo(_t(self.settings,"about_title"),_t(self.settings,"about_msg"),parent=self.root)

    def _quit(self):
        if self.scheduler: self.scheduler.stop()
        try: self.root.destroy()
        except Exception: pass
        sys.exit(0)

    def reset_position(self):
        sw=self.root.winfo_screenwidth(); uh=_usable_height()
        w,h=self._win_size()
        x=max(0,sw-w-50); y=max(0,uh-h-50)
        self.settings["win_x"]=x; self.settings["win_y"]=y
        config.save(self.settings); self.root.geometry(f"+{x}+{y}")

    # ── Tick ──────────────────────────────────────────────────────────────────

    def _tick(self):
        if self.page=="main" and hasattr(self,"_cd_lbl"):
            try: self._cd_lbl.configure(text=_countdown())
            except Exception: pass
        self.root.after(1000, self._tick)

    # ── 外部呼叫 ──────────────────────────────────────────────────────────────

    def update_tz(self, cur_group, nxt_group, status):
        def _do():
            self.cur_group=cur_group; self.nxt_group=nxt_group; self.status=status
            if self.page in ("main","compact"): self._rebuild()
        self.root.after(0, _do)

    def on_notify_event(self, event: str):
        s=self.settings; lang=s.get("lang","en-us"); nm=s.get("notify_minutes",5)
        if event=="5min":
            if not s.get("notify_5min",True): return
            if self.cur_group:
                zone=_short_group_name(self.cur_group,lang,s)
                multi=len(self.cur_group.get("zones",[]))>1
                msg=(_t(s,"notif_5min_msg") if multi else _t(s,"notif_5min_single")).replace("{zone}",zone).replace("{n}",str(nm))
            else:
                msg=_t(s,"notify_5min")
            sound_url=s.get("sound_url_5min","")
        elif event=="fav":
            if not s.get("notify_fav",True): return
            if not self.nxt_group: return
            if self.nxt_group.get("id","") not in s.get("favorites",[]): return
            zone=_short_group_name(self.nxt_group,lang,s)
            multi=len(self.nxt_group.get("zones",[]))>1
            msg=(_t(s,"notif_fav_msg") if multi else _t(s,"notif_fav_single")).replace("{zone}",zone)
            sound_url=s.get("sound_url_fav","")
        else:
            return
        volume = s.get("sound_volume", 1.0)
        notifier.notify(title="D2R TZ Tracker", message=msg,
                        event_key=event, sound_url=sound_url, volume=volume)

    def get_tray_strings(self) -> dict:
        s=self.settings
        keys=["tray_show","tray_compact","tray_settings","tray_quit","tray_name",
              "tray_notify5","tray_notifyfav","tray_reset_pos","tray_refresh",
              "tray_lock_pos","tray_about","tray_transparent",
              "tray_sound","tray_sound_mute","tray_sound_default",
              "tray_sound_custom","tray_sound_not_set","topmost_off","topmost_hard"]
        return {k:_t(s,k) for k in keys}

    def show(self):
        self._visible=True; self.root.deiconify(); self.root.lift()

    def hide(self):
        self._visible=False; self.root.withdraw()

    def run(self):
        self.root.mainloop()

    def destroy(self):
        try: self.root.destroy()
        except Exception: pass