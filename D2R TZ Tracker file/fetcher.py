# fetcher.py
# 抓取 d2tz.info API，回傳當前與下個 TZ 資料（不再使用 OCR）

import threading
import time
import requests
import os
import sys

# ── 常數 ──────────────────────────────────────────────────────────────────────
API_URL_DEFAULT = "https://api.d2tz.info/public/tz"
FETCH_TIMEOUT = 15    # 秒
RETRY_DELAY   = 60    # 失敗後自動重試間隔（秒）
MAX_RETRIES   = 3     # 單次抓取最多重試次數


def _get_base_dir() -> str:
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def _build_group(entry: dict) -> dict | None:
    """
    將 API 單筆資料轉為內部 group 格式。
    API 格式：
      { "time":…, "zone_name":["Jail","Barracks"],
        "immunities":[…], "tier-exp":"B", "tier-loot":"C",
        "area_id":28, "area_ids":[28,29,30,31], "end_time":… }
    """
    if not entry:
        return None
    zones = entry.get("zone_name", [])
    if not zones:
        return None

    # 用 area_ids 排序後串接做穩定 id，供最愛功能比對
    area_ids = sorted(entry.get("area_ids", []))
    gid = "_".join(str(i) for i in area_ids) if area_ids else zones[0]

    return {
        "id":         gid,
        "zones":      zones,           # zone key list，與 area.json 的 key 一致
        "area_id":    entry.get("area_id"),
        "area_ids":   area_ids,
        "time":       entry.get("time"),
        "end_time":   entry.get("end_time"),
        "tier_exp":   entry.get("tier-exp", "?"),
        "tier_loot":  entry.get("tier-loot", "?"),
        "immunities": entry.get("immunities", []),
    }


class TZNotReadyError(Exception):
    """Worker 回傳 503：API 尚未更新，需要稍後重試"""
    def __init__(self, retry_after: int = 30):
        self.retry_after = retry_after
        super().__init__(f"TZ 資料尚未更新，{retry_after} 秒後重試")


def fetch_tz(token: str = "", api_url: str = "", force: bool = False) -> tuple[dict | None, dict | None]:
    """
    呼叫 API。
    - Worker URL：Worker 端驗證 end_time，過期回 503（TZNotReadyError）
    - 直連 d2tz.info：客戶端自行驗證 end_time
    """
    url = api_url if api_url else API_URL_DEFAULT
    is_worker = bool(api_url)

    params = {"_": int(time.time())}
    if token and not is_worker:
        params["token"] = token

    def _do_fetch(target_url, target_params):
        resp = requests.get(
            target_url,
            timeout=FETCH_TIMEOUT,
            headers={"Cache-Control": "no-cache"},
            params=target_params,
        )
        # 503 = Worker 判定資料尚未更新
        if resp.status_code == 503:
            retry_after = int(resp.headers.get("Retry-After", 30))
            raise TZNotReadyError(retry_after)
        resp.raise_for_status()
        data = resp.json()
        if not isinstance(data, list) or len(data) < 1:
            raise ValueError(f"API 回傳格式異常: {data}")
        return data

    data = _do_fetch(url, params)

    nxt_entry = data[0] if len(data) > 0 else None
    cur_entry = data[1] if len(data) > 1 else None

    # 直連時客戶端自行驗證時效
    if not is_worker and cur_entry:
        now = int(time.time())
        if cur_entry.get("end_time", 0) <= now:
            raise TZNotReadyError(30)

    cur = _build_group(cur_entry)
    nxt = _build_group(nxt_entry)

    if cur is None:
        raise ValueError(f"無法解析當前 TZ，原始: {data}")

    print(f"[API] cur={cur.get('zones')} exp={cur.get('tier_exp')} loot={cur.get('tier_loot')}")
    if nxt:
        print(f"[API] nxt={nxt.get('zones')} exp={nxt.get('tier_exp')} loot={nxt.get('tier_loot')}")
    return cur, nxt


# ── 背景排程器 ────────────────────────────────────────────────────────────────
class TZScheduler:
    """
    時序邏輯：
      :00 / :30  → current 升格，進入 waiting 狀態
      :01 / :31  → 抓 API，更新 next（早一分鐘，盡快顯示資料）
      其他時間   → 若 cache 超過 RETRY_DELAY 秒且狀態非 ok，自動重試
      手動刷新   → 立即重抓（force=True，直接覆蓋 current）

    callback 簽名：
      on_update(cur_group, nxt_group, status)
        status: 'ok' | 'waiting' | 'fetching' | 'error'
      on_notify(event)
        event: '5min' | 'fav'
    """

    CACHE_TTL = 35 * 60   # 35 分鐘強制刷新

    def __init__(self, on_update, on_notify, get_settings=None):
        self.on_update    = on_update
        self.on_notify    = on_notify
        self.get_settings = get_settings or (lambda: {})

        self.cur_group  = None
        self.nxt_group  = None
        self._pending   = None
        self.fetched_at = 0
        self._last_retry_at = 0
        self.status     = "idle"

        self._lock           = threading.Lock()
        self._stop_event     = threading.Event()
        self._last_fetch_min = -1
        self._last_flip_min  = -1
        self._notified_pre   = False   # 結束前 N 分鐘提醒
        self._notified_fav   = False   # 最愛提醒

        self._thread = threading.Thread(target=self._loop, daemon=True)

    def start(self):
        self._thread.start()

    def stop(self):
        self._stop_event.set()

    def force_refresh(self):
        """手動重抓（UI 按鈕）"""
        threading.Thread(target=self._do_fetch, args=(True,), daemon=True).start()

    # ── 內部 ──────────────────────────────────────────────────────────────────

    def _loop(self):
        # 啟動時先抓一次
        threading.Thread(target=self._do_fetch, args=(True,), daemon=True).start()
        while not self._stop_event.is_set():
            try:
                self._tick()
            except Exception as e:
                print(f"[Scheduler] tick 錯誤: {e}")
            time.sleep(1)

    def _get_notify_minutes(self) -> int:
        s = self.get_settings()
        return max(1, min(29, int(s.get("notify_minutes", 5))))

    def _tick(self):
        import datetime
        now = datetime.datetime.now()
        m, s = now.minute, now.second
        now_ts = time.time()

        # :00 / :30 → 升格
        if (m == 0 or m == 30) and s <= 15 and m != self._last_flip_min:
            self._last_flip_min = m
            self._notified_pre  = False
            self._notified_fav  = False
            with self._lock:
                if self._pending is not None:
                    self.cur_group = self._pending
                    self._pending  = None
                self.nxt_group = None
                self.status    = "waiting"
            self.on_update(self.cur_group, self.nxt_group, "waiting")

        # :01 / :31 → 抓 API
        elif (m == 1 or m == 31) and m != self._last_fetch_min:
            self._last_fetch_min = m
            threading.Thread(target=self._do_fetch, args=(False,), daemon=True).start()

        # cache 過期或錯誤 → 自動重試（限速：至少間隔 RETRY_DELAY 秒）
        elif (self.status in ("error", "idle") or
              now_ts - self.fetched_at > self.CACHE_TTL):
            if now_ts - self._last_retry_at > RETRY_DELAY:
                self._last_retry_at = now_ts
                threading.Thread(target=self._do_fetch, args=(False,), daemon=True).start()

        # 結束前 N 分鐘提醒
        nm = self._get_notify_minutes()
        trigger = {30 - nm, 60 - nm}
        if m in trigger and not self._notified_pre:
            self._notified_pre = True
            self.on_notify("5min")

    def _do_fetch(self, force: bool):
        with self._lock:
            if self.status == "fetching":
                return
            self.status = "fetching"
        self.on_update(self.cur_group, self.nxt_group, "fetching")

        token   = self.get_settings().get("api_token", "")
        api_url = self.get_settings().get("api_url", "")

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                cur, nxt = fetch_tz(token=token, api_url=api_url, force=force)
                with self._lock:
                    if force:
                        self.cur_group = cur
                        self.nxt_group = nxt
                        self._pending  = nxt
                    else:
                        if self.cur_group is None:
                            self.cur_group = cur
                        self.nxt_group = nxt
                        self._pending  = nxt
                    self.fetched_at     = time.time()
                    self._last_retry_at = time.time()
                    self.status         = "ok"
                self.on_update(self.cur_group, self.nxt_group, "ok")
                self._check_fav_notify()
                return
            except TZNotReadyError as e:
                # API 尚未更新（換場空窗期），按 retry_after 安排重試，不顯示錯誤
                print(f"[Fetcher] TZ 尚未更新，{e.retry_after} 秒後重試")
                with self._lock:
                    self.status = "waiting"
                self.on_update(self.cur_group, self.nxt_group, "waiting")
                self._last_retry_at = time.time() - RETRY_DELAY + e.retry_after
                return
            except Exception as e:
                print(f"[Fetcher] 第 {attempt} 次失敗: {e}")
                if attempt < MAX_RETRIES:
                    self.on_update(self.cur_group, self.nxt_group, "error")
                    time.sleep(10)
                else:
                    with self._lock:
                        self.status = "error"
                    self.on_update(self.cur_group, self.nxt_group, "error")

    def _check_fav_notify(self):
        if not self._notified_fav and self.nxt_group is not None:
            self._notified_fav = True
            self.on_notify("fav")