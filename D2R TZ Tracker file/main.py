# main.py
import sys
import os
import config
from fetcher import TZScheduler
from ui import TZWindow
from tray import TrayIcon
from tz_data import get_group_name, match_group_id


def main():
    settings  = config.load()
    window    = TZWindow(settings)
    _tray_ref = [None]

    def _refresh():
        if _tray_ref[0]:
            _tray_ref[0].refresh_menu()

    # 通知顏色初始化
    import notifier, toast
    notifier.set_ui_colors(
        bg=settings.get("bg_color",     "#1e1030"),
        accent=settings.get("accent_color", "#9d4edd"),
        text_color=settings.get("text_color", "#e8d5b7"),
    )
    toast.set_root(window.root)

    # 視窗圖示（優先找 Data/ 資料夾）
    base = os.path.dirname(sys.executable) if getattr(sys, "frozen", False) \
           else os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base, "Data")
    for search in ([data_dir, base] if os.path.isdir(data_dir) else [base]):
        ico = os.path.join(search, "icon.ico")
        if os.path.exists(ico):
            try:
                window.root.iconbitmap(ico)
            except Exception:
                pass
            break

    # 置頂模式
    window._set_topmost(settings.get("topmost_mode", "hard"))

    # ── 排程器 ────────────────────────────────────────────────────────────────
    def _enrich_group(group: dict | None) -> dict | None:
        """
        將 API group 的 id 對應到 TZ_GROUPS 的固定 id。
        這樣最愛功能才能跨 session 正確比對。
        """
        if group is None:
            return None
        # 如果 id 還是 area_ids 串接格式，嘗試匹配 TZ_GROUPS
        canonical = match_group_id(group)
        group = dict(group)
        group["id"] = canonical
        return group

    def on_update(cur_group, nxt_group, status):
        cur = _enrich_group(cur_group)
        nxt = _enrich_group(nxt_group)
        window.update_tz(cur, nxt, status)
        if cur:
            lang     = settings.get("lang", "en-us")
            cur_name = get_group_name(cur, lang)
            nxt_name = get_group_name(nxt, lang) if nxt else "?"
            tray.update_tooltip(f"TZ: {cur_name}\nNext: {nxt_name}")
        else:
            tray.update_tooltip("D2R TZ Tracker")

    def on_notify(event):
        window.on_notify_event(event)

    scheduler = TZScheduler(
        on_update=on_update,
        on_notify=on_notify,
        get_settings=lambda: settings,
    )
    window.scheduler = scheduler

    # ── Tray 回呼 ─────────────────────────────────────────────────────────────
    def toggle_compact():
        try:
            if window.page == "compact":
                window.root.after(0, window._to_main)
            else:
                window.root.after(0, window._to_compact)
            _refresh()
        except Exception:
            pass

    def show_hide():
        try:
            if window._visible:
                window.hide()
            else:
                window.show()
        except Exception:
            pass
        _refresh()

    def open_settings():
        try:
            window.show()
            window._to_settings()
        except Exception:
            pass

    def toggle_notify5():
        settings["notify_5min"] = not settings.get("notify_5min", True)
        config.save(settings)
        _refresh()

    def toggle_notifyfav():
        settings["notify_fav"] = not settings.get("notify_fav", True)
        config.save(settings)
        _refresh()

    def set_topmost(mode: str):
        window.root.after(0, lambda: window._set_topmost(mode))
        _refresh()

    def reset_pos():
        window.root.after(0, window.reset_position)

    def do_refresh():
        scheduler.force_refresh()

    def toggle_lock():
        window.root.after(0, window._toggle_lock_pos)
        _refresh()

    def show_about():
        window.root.after(0, window._show_about)

    def quit_app():
        scheduler.stop()
        tray.stop()
        try:
            window.destroy()
        except Exception:
            pass
        sys.exit(0)

    def get_strings():
        return window.get_tray_strings()

    def get_states():
        return {
            "visible":          window._visible,
            "is_compact":       window.page == "compact",
            "notify5":          settings.get("notify_5min", True),
            "notifyfav":        settings.get("notify_fav", True),
            "topmost_mode":     settings.get("topmost_mode", "hard"),
            "position_locked":  settings.get("position_locked", False),
            "text_only_mode":   settings.get("text_only_mode", False),
        }

    def toggle_transparent():
        val = not settings.get("text_only_mode", False)
        settings["text_only_mode"] = val
        config.save(settings)
        window.root.after(0, lambda: window._set_text_only(val))
        _refresh()

    tray = TrayIcon(
        on_show=show_hide,
        on_toggle_compact=toggle_compact,
        on_quit=quit_app,
        on_settings=open_settings,
        get_strings=get_strings,
        get_states=get_states,
        on_toggle_notify5=toggle_notify5,
        on_toggle_notifyfav=toggle_notifyfav,
        on_set_topmost=set_topmost,
        on_reset_pos=reset_pos,
        on_refresh=do_refresh,
        on_toggle_lock=toggle_lock,
        on_about=show_about,
        on_toggle_transparent=toggle_transparent,
    )

    _tray_ref[0] = tray
    window.root.protocol("WM_DELETE_WINDOW", window.hide)
    scheduler.start()
    tray.start()
    window.run()


if __name__ == "__main__":
    main()