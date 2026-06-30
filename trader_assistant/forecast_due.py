from __future__ import annotations

import time


def interval_seconds(interval):
    text = str(interval or '1h').strip().lower()
    if text.endswith('m'):
        return int(float(text[:-1]) * 60)
    if text.endswith('h'):
        return int(float(text[:-1]) * 3600)
    if text.endswith('d'):
        return int(float(text[:-1]) * 86400)
    return int(float(text))


def forecast_due_status(start_ts, horizon_bars, interval, verified_at=None, now_ts=None):
    if verified_at:
        return {'state': 'verified', 'due_ts': None, 'seconds_until_due': None, 'label': 'verified'}
    if start_ts is None:
        return {'state': 'unknown', 'due_ts': None, 'seconds_until_due': None, 'label': 'due unknown'}
    start_ms = int(start_ts)
    if start_ms < 10_000_000_000:
        start_ms *= 1000
    due_ms = start_ms + int(horizon_bars or 0) * interval_seconds(interval) * 1000
    now_ms = int(now_ts if now_ts is not None else time.time() * 1000)
    seconds = int((due_ms - now_ms) / 1000)
    state = 'pending' if seconds > 0 else 'due'
    if state == 'pending':
        mins = max(1, int(seconds / 60))
        label = f'due in {mins}m'
    else:
        mins = max(0, int(abs(seconds) / 60))
        label = f'due now' if mins == 0 else f'overdue {mins}m'
    return {'state': state, 'due_ts': due_ms, 'seconds_until_due': seconds, 'label': label}
