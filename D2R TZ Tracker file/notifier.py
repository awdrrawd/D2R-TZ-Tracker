# notifier.py
# 通知 + 音效播放（結束提醒 / 最愛提醒 音效分開設定）

import os
import sys
import threading
import time

_COOLDOWN = {"5min": 20 * 60, "fav": 25 * 60}
_last_notify: dict[str, float] = {}
_lock = threading.Lock()

_ui_colors: dict = {}


def set_ui_colors(bg: str, accent: str, text_color: str):
    _ui_colors["bg"]         = bg
    _ui_colors["accent"]     = accent
    _ui_colors["text_color"] = text_color


def _get_base_dir() -> str:
    return os.path.dirname(sys.executable) if getattr(sys, "frozen", False) \
           else os.path.dirname(os.path.abspath(__file__))


def _get_data_dir() -> str:
    """優先找 Data 子資料夾，找不到就用程式目錄"""
    base = _get_base_dir()
    data = os.path.join(base, "Data")
    return data if os.path.isdir(data) else base


def _resolve_sound(sound_url: str) -> str:
    """
    解析音效路徑：
    "__mute__"  → 靜音（回傳空字串）
    ""          → 找同資料夾 sound.wav
    絕對路徑    → 直接使用
    相對路徑    → 從程式目錄解析
    http(s)://  → 不支援，使用預設音
    """
    url = (sound_url or "").strip()

    if url == "__mute__":
        return ""

    if url.startswith("http://") or url.startswith("https://"):
        url = ""

    if url in ("", "sound.wav"):
        # 先找 Data/ 再找程式目錄
        default = os.path.join(_get_data_dir(), "sound.wav")
        if not os.path.exists(default):
            default = os.path.join(_get_base_dir(), "sound.wav")
        return default if os.path.exists(default) else ""

    if len(url) >= 2 and url[1] == ':':
        return url
    if url.startswith("\\\\"):
        return url

    return os.path.join(_get_base_dir(), url)


def _play_sound(sound_url: str, volume: float = 1.0):
    def _run():
        path = _resolve_sound(sound_url)
        if path:
            _play_local(path, max(0.0, min(1.0, volume)))
    threading.Thread(target=_run, daemon=True).start()


def _play_local(path: str, volume: float = 1.0):
    if not os.path.exists(path):
        print(f"[Notifier] 找不到音效檔: {path}")
        return

    ext = os.path.splitext(path)[1].lower()
    vol_pct = int(volume * 100)   # winsound 用 Windows 系統音量，無法單獨控制

    # WAV + 音量 = 1.0：winsound 最快
    if ext == ".wav" and volume >= 0.99:
        try:
            import winsound
            winsound.PlaySound(path, winsound.SND_FILENAME | winsound.SND_ASYNC)
            return
        except Exception as e:
            print(f"[Notifier] winsound 失敗: {e}")

    # 其他格式或需要音量控制：PowerShell MediaPlayer
    try:
        import subprocess
        ps = (
            "[void][System.Reflection.Assembly]::LoadWithPartialName('presentationcore'); "
            f"$mp = New-Object System.Windows.Media.MediaPlayer; "
            f"$mp.Open([uri]::new('{path}')); "
            f"$mp.Volume = {volume:.2f}; "
            f"$mp.Play(); "
            f"Start-Sleep -Milliseconds 8000; "
            f"$mp.Stop(); $mp.Close()"
        )
        subprocess.Popen(
            ["powershell", "-WindowStyle", "Hidden", "-NonInteractive", "-Command", ps],
            creationflags=0x08000000,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        return
    except Exception as e:
        print(f"[Notifier] MediaPlayer 失敗: {e}")

    # fallback：WMPlayer COM（volume 0–100）
    try:
        import subprocess
        ps = (
            f"$w = New-Object -ComObject 'WMPlayer.OCX'; "
            f"$w.settings.autoStart = $true; $w.settings.volume = {vol_pct}; "
            f"$w.URL = '{path}'; "
            f"$w.controls.play(); Start-Sleep -Milliseconds 8000; $w.controls.stop()"
        )
        subprocess.Popen(
            ["powershell", "-WindowStyle", "Hidden", "-NonInteractive", "-Command", ps],
            creationflags=0x08000000,
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
    except Exception as e:
        print(f"[Notifier] WMPlayer 失敗: {e}")


def notify(title: str, message: str,
           event_key: str = "", sound_url: str = "",
           volume: float = 1.0,
           bg: str = "", accent: str = "", text_color: str = ""):
    """
    發送通知視窗 + 播放音效。
    sound_url：該事件專屬的音效設定
    volume：音量 0.0~1.0
    """
    if event_key:
        cooldown = _COOLDOWN.get(event_key, 0)
        with _lock:
            if time.time() - _last_notify.get(event_key, 0) < cooldown:
                return
            _last_notify[event_key] = time.time()

    _play_sound(sound_url, volume)

    _bg = bg     or _ui_colors.get("bg",         "#1e1030")
    _ac = accent or _ui_colors.get("accent",     "#9d4edd")
    _tc = text_color or _ui_colors.get("text_color", "#e8d5b7")

    try:
        import toast
        toast.show(title, message, bg=_bg, accent=_ac, text_color=_tc)
    except Exception as e:
        print(f"[Notifier] 通知視窗失敗: {e}")


def reset_cooldown(event_key: str = ""):
    with _lock:
        if event_key:
            _last_notify.pop(event_key, None)
        else:
            _last_notify.clear()