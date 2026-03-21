# tz_data.py
# TZ 群組定義 + 多語言支援，場景名稱從外部 area.json 讀取

import os
import sys
import json

# ── 語言設定 ──────────────────────────────────────────────────────────────────
LANG_MAP = {
    "zh-tw": "繁體中文",
    "zh-cn": "简体中文",
    "en-us": "English",
    "ko":    "한국어",
    "ja":    "日本語",
    "de":    "Deutsch",
    "es":    "Español",
    "fr":    "Français",
    "it":    "Italiano",
    "pl":    "Polski",
    "pt-br": "Português",
    "ru":    "Русский",
}

WINDOWS_LOCALE_MAP = {
    "zh_tw": "zh-tw", "zh_hk": "zh-tw", "zh_mo": "zh-tw",
    "zh_cn": "zh-cn", "zh_sg": "zh-cn",
    "en":    "en-us", "ko": "ko", "ja": "ja",
    "de":    "de",    "es": "es", "fr": "fr",
    "it":    "it",    "pl": "pl", "pt": "pt-br", "ru": "ru",
}


def _get_base_dir() -> str:
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def _get_data_dir() -> str:
    """優先找 Data 子資料夾，找不到就用程式目錄（向下相容）"""
    base = _get_base_dir()
    data = os.path.join(base, "Data")
    return data if os.path.isdir(data) else base


# ── 外部 area.json 載入（惰性快取）───────────────────────────────────────────
_AREA_DATA: dict | None = None


def _load_area_data() -> dict:
    global _AREA_DATA
    if _AREA_DATA is not None:
        return _AREA_DATA
    path = os.path.join(_get_data_dir(), "area.json")
    if not os.path.exists(path):
        print(f"[TZData] 找不到 area.json: {path}")
        _AREA_DATA = {}
        return _AREA_DATA
    try:
        with open(path, "r", encoding="utf-8") as f:
            _AREA_DATA = json.load(f)
        print(f"[TZData] 載入 area.json，共 {len(_AREA_DATA)} 筆場景")
        return _AREA_DATA
    except Exception as e:
        print(f"[TZData] 讀取 area.json 失敗: {e}")
        _AREA_DATA = {}
        return _AREA_DATA


def reload_area_data() -> dict:
    """強制重新載入 area.json"""
    global _AREA_DATA
    _AREA_DATA = None
    return _load_area_data()


def get_zone_name(zone_key: str, lang: str) -> str:
    """從 area.json 取得場景的多語言名稱，找不到則 fallback 英文再 fallback key"""
    data  = _load_area_data()
    entry = data.get(zone_key, {})
    return entry.get(lang) or entry.get("en-us") or zone_key.replace("_", " ")


def get_group_name(group: dict, lang: str) -> str:
    """取得群組的顯示名稱（所有場景名稱連接）"""
    zones = group.get("zones", [])
    sep   = "、" if lang in ("zh-tw", "zh-cn", "ja") else ", "
    names, seen = [], set()
    for zk in zones:
        name = get_zone_name(zk, lang)
        if name not in seen:
            seen.add(name)
            names.append(name)
    return sep.join(names) if names else "—"


# ── TZ 群組定義（與 d2tz.info 分組一致，34 組）──────────────────────────────
# 這裡的 id 是固定字串，用於最愛功能存檔
# API 回傳的 group id 是 area_ids 組合，透過 match_group_id() 轉換
TZ_GROUPS = [
    # Act 1
    {"id": "A01", "zones": ["Blood_Moor", "Den_of_Evil"]},
    {"id": "A02", "zones": ["Cold_Plains", "Cave"]},
    {"id": "A03", "zones": ["Burial_Grounds", "Crypt", "Mausoleum"]},
    {"id": "A04", "zones": ["Stony_Field", "Tristram"]},
    {"id": "A05", "zones": ["Dark_Wood", "Underground_Passage"]},
    {"id": "A06", "zones": ["Black_Marsh", "Hole", "Forgotten_Tower"]},
    {"id": "A07", "zones": ["Tamoe_Highland", "Pit", "Monastery_Gate", "Outer_Cloister"]},
    {"id": "A08", "zones": ["Jail", "Barracks"]},
    {"id": "A09", "zones": ["Cathedral", "Inner_Cloister", "Catacombs"]},
    {"id": "A10", "zones": ["Moo_Moo_Farm"]},
    # Act 2
    {"id": "B01", "zones": ["Lut_Gholein_Sewers"]},
    {"id": "B02", "zones": ["Rocky_Waste", "Stony_Tomb"]},
    {"id": "B03", "zones": ["Dry_Hills", "Halls_of_the_Dead"]},
    {"id": "B04", "zones": ["Far_Oasis", "Maggot_Lair"]},
    {"id": "B05", "zones": ["Lost_City", "Valley_of_Snakes", "Claw_Viper_Temple", "Ancient_Tunnels"]},
    {"id": "B06", "zones": ["Arcane_Sanctuary", "Harem", "Palace_Cellar"]},
    {"id": "B07", "zones": ["Tal_Rashas_Tomb", "Tal_Rashas_Chamber", "Canyon_of_The_Magi"]},
    # Act 3
    {"id": "C01", "zones": ["Spider_Forest", "Arachnid_Lair", "Spider_Cavern"]},
    {"id": "C02", "zones": ["Great_Marsh"]},
    {"id": "C03", "zones": ["Flayer_Jungle", "Flayer_Dungeon", "Swampy_Pit"]},
    {"id": "C04", "zones": ["Kurast_Bazaar", "Kurast_Causeway", "Kurast_Sewers",
                             "Ruined_Temple", "Disused_Fane", "Forgotten_Reliquary",
                             "Forgotten_Temple", "Ruined_Fane", "Disused_Reliquary"]},
    {"id": "C05", "zones": ["Travincal"]},
    {"id": "C06", "zones": ["Durance_of_Hate"]},
    # Act 4
    {"id": "D01", "zones": ["Outer_Steppes", "Plains_of_Despair"]},
    {"id": "D02", "zones": ["River_of_Flame", "City_of_the_Damned"]},
    {"id": "D03", "zones": ["Chaos_Sanctuary"]},
    # Act 5
    {"id": "E01", "zones": ["Bloody_Foothills", "Frigid_Highlands", "Abaddon"]},
    {"id": "E02", "zones": ["Arreat_Plateau", "Pit_of_Acheron"]},
    {"id": "E03", "zones": ["Crystalline_Passage", "Frozen_River"]},
    {"id": "E04", "zones": ["Glacial_Trail", "Drifter_Cavern"]},
    {"id": "E05", "zones": ["Nihlathaks_Temple", "Halls_of_Anguish", "Halls_of_Pain", "Halls_of_Vaught"]},
    {"id": "E06", "zones": ["Frozen_Tundra", "Infernal_Pit"]},
    {"id": "E07", "zones": ["Ancients_Way", "Icy_Cellar"]},
    {"id": "E08", "zones": ["Worldstone_Keep", "Throne_of_Destruction", "Worldstone_Chamber"]},
]

# 快速查表：zone_key → 所有包含該 zone 的 group id
_ZONE_TO_GROUPS: dict[str, list[str]] = {}
for _g in TZ_GROUPS:
    for _z in _g["zones"]:
        _ZONE_TO_GROUPS.setdefault(_z, []).append(_g["id"])


def match_group_id(api_group: dict) -> str:
    """
    將 API 回傳的 group（zone_name 清單）對應到 TZ_GROUPS 的固定 id。
    用 zone 名稱交集計分，取最高分者。
    找不到則回傳 API 自帶的 id（area_ids 串接）。
    """
    zones    = api_group.get("zones", [])
    zone_set = set(zones)

    scores: dict[str, int] = {}
    for zk in zone_set:
        for gid in _ZONE_TO_GROUPS.get(zk, []):
            scores[gid] = scores.get(gid, 0) + 1

    if scores:
        best_id = max(scores, key=lambda k: scores[k])
        # 要求至少 50% 命中
        g = next((g for g in TZ_GROUPS if g["id"] == best_id), None)
        if g:
            total = len(g["zones"])
            if scores[best_id] / total >= 0.5:
                return best_id

    return api_group.get("id", zones[0] if zones else "unknown")


def detect_system_lang() -> str:
    """偵測 Windows 系統語言，回傳對應的 lang key"""
    try:
        import locale
        loc = locale.getdefaultlocale()[0] or ""
        loc = loc.lower().replace("-", "_")
        if loc in WINDOWS_LOCALE_MAP:
            return WINDOWS_LOCALE_MAP[loc]
        return WINDOWS_LOCALE_MAP.get(loc[:2], "en-us")
    except Exception:
        return "en-us"