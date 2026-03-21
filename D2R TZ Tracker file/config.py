# config.py
# 設定管理：讀寫 settings.json，定義預設值與主題

import json
import os
import sys
from tz_data import detect_system_lang


def _get_base_dir() -> str:
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


_SETTINGS_PATH = os.path.join(_get_base_dir(), "settings.json")

# ── 預設主題 ──────────────────────────────────────────────────────────────────
THEMES = {
    "dark": {
        "name_key":      "theme_dark",
        "bg_color":      "#120d1f",
        "text_color":    "#e8d5b7",
        "accent_color":  "#9d4edd",
        "fav_color":     "#ffd700",
        "title_color":   "#c77dff",
        "sub_color":     "#7b6a9a",
        "btn_color":     "#6a3a9a",
        "opacity":       0.93,
        "transparent_bg": False,
    },
    "light": {
        "name_key":      "theme_light",
        "bg_color":      "#f0eee8",
        "text_color":    "#1a1a2e",
        "accent_color":  "#7b2fbf",
        "fav_color":     "#b8860b",
        "title_color":   "#4a0080",
        "sub_color":     "#666666",
        "btn_color":     "#7b2fbf",
        "opacity":       0.95,
        "transparent_bg": False,
    },
}

# ── 預設設定 ──────────────────────────────────────────────────────────────────
DEFAULT_SETTINGS = {
    # 語言
    "lang":              None,          # None = 啟動時自動偵測

    # API
    "api_token":         "",            # 個人 token，空字串 = 無 token

    # 外觀
    "theme":             "dark",
    "bg_color":          THEMES["dark"]["bg_color"],
    "text_color":        THEMES["dark"]["text_color"],
    "accent_color":      THEMES["dark"]["accent_color"],
    "fav_color":         THEMES["dark"]["fav_color"],
    "title_color":       THEMES["dark"]["title_color"],
    "sub_color":         THEMES["dark"]["sub_color"],
    "opacity":           THEMES["dark"]["opacity"],
    "transparent_bg":    False,

    # 純文字模式（背景完全透明，透明度滑桿只影響背景不影響文字）
    "text_only_mode":    False,

    # 視窗
    "pos_x":             50,
    "pos_y":             50,
    "always_on_top":     True,
    "topmost_mode":      "hard",
    "scale":             1.0,
    "font_size":         13,
    "font_scale":        1.0,

    # 鎖定位置（點擊穿透）
    "position_locked":   False,

    # 顯示選項
    "show_tier_exp":     True,          # 顯示 EXP 評級
    "show_tier_loot":    True,          # 顯示 LOOT 評級

    # 通知
    "notify_5min":       True,
    "notify_minutes":    5,             # 提前幾分鐘提醒（1~29）
    "notify_fav":        True,

    # 音效（結束提醒 / 最愛提醒 各自獨立設定）
    # 值："" = 預設 sound.wav，"__mute__" = 靜音，絕對路徑 = 自訂
    "sound_url_5min":    "",
    "sound_url_fav":     "",

    # 最愛群組
    "favorites":         [],

    # 最愛顏色功能開關
    "fav_color_enabled": True,
    "btn_color":         None,          # None = 跟隨 accent_color

    # 工作列小視窗
    "taskbar_pinned":    False,
    "taskbar_x":         -1,

    # 使用者儲存的自訂主題
    "saved_themes":      {},
}


def load() -> dict:
    """載入設定，缺失的 key 自動補預設值"""
    settings = dict(DEFAULT_SETTINGS)

    if os.path.exists(_SETTINGS_PATH):
        try:
            with open(_SETTINGS_PATH, "r", encoding="utf-8") as f:
                saved = json.load(f)
            settings.update(saved)
        except Exception:
            pass

    # 語言自動偵測
    if settings["lang"] is None:
        settings["lang"] = detect_system_lang()

    # 舊版音效設定遷移（sound_url / sound_muted → sound_url_5min / sound_url_fav）
    old_url   = settings.pop("sound_url",   None)
    old_muted = settings.pop("sound_muted", None)
    if old_url is not None or old_muted is not None:
        if old_muted:
            settings.setdefault("sound_url_5min", "__mute__")
            settings.setdefault("sound_url_fav",  "__mute__")
        elif old_url:
            settings.setdefault("sound_url_5min", old_url)
            settings.setdefault("sound_url_fav",  old_url)

    return settings


def save(settings: dict) -> None:
    try:
        with open(_SETTINGS_PATH, "w", encoding="utf-8") as f:
            json.dump(settings, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[Config] 儲存設定失敗: {e}")


def apply_theme(settings: dict, theme_name: str) -> dict:
    if theme_name in THEMES:
        t = THEMES[theme_name]
        settings["theme"]          = theme_name
        settings["bg_color"]       = t["bg_color"]
        settings["text_color"]     = t["text_color"]
        settings["accent_color"]   = t["accent_color"]
        settings["fav_color"]      = t["fav_color"]
        settings["title_color"]    = t["title_color"]
        settings["sub_color"]      = t["sub_color"]
        settings["opacity"]        = t["opacity"]
        settings["transparent_bg"] = t["transparent_bg"]
        settings["btn_color"]      = t.get("btn_color", settings.get("accent_color"))
        return settings

    saved = settings.get("saved_themes", {})
    if theme_name in saved:
        t = saved[theme_name]
        for key in ("bg_color", "text_color", "accent_color", "fav_color",
                    "title_color", "sub_color", "btn_color", "opacity", "transparent_bg"):
            if key in t:
                settings[key] = t[key]
        settings["theme"] = theme_name
        return settings

    return settings


def save_custom_theme(settings: dict, theme_name: str) -> dict:
    if "saved_themes" not in settings:
        settings["saved_themes"] = {}
    settings["saved_themes"][theme_name] = {
        "bg_color":       settings["bg_color"],
        "text_color":     settings["text_color"],
        "accent_color":   settings["accent_color"],
        "fav_color":      settings["fav_color"],
        "title_color":    settings["title_color"],
        "sub_color":      settings["sub_color"],
        "btn_color":      settings.get("btn_color"),
        "opacity":        settings["opacity"],
        "transparent_bg": settings["transparent_bg"],
    }
    return settings


def delete_custom_theme(settings: dict, theme_name: str) -> dict:
    settings.get("saved_themes", {}).pop(theme_name, None)
    if settings.get("theme") == theme_name:
        settings = apply_theme(settings, "dark")
    return settings


def get_all_theme_names(settings: dict) -> list[tuple[str, str]]:
    result = [(k, f"__{v['name_key']}__") for k, v in THEMES.items()]
    for name in settings.get("saved_themes", {}):
        result.append((name, name))
    return result
