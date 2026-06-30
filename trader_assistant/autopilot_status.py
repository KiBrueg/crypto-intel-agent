from __future__ import annotations

import json
import time
from pathlib import Path

from trader_assistant.journal import DEFAULT_DB, init_journal
from trader_assistant.learning_autopilot import prediction_stats, recent_predictions


def _read_json(path: Path, default=None):
    try:
        if path.exists():
            return json.loads(path.read_text(encoding='utf-8'))
    except Exception:
        return default
    return default


def _file_age_seconds(path: Path):
    try:
        if path.exists():
            return max(0, time.time() - path.stat().st_mtime)
    except Exception:
        return None
    return None


def build_autopilot_status(root_dir=None, db_path=None, stale_after_seconds=1800):
    root = Path(root_dir) if root_dir else Path(__file__).resolve().parents[1]
    data_dir = root / 'data'
    heartbeat_path = data_dir / 'learning_autopilot_heartbeat.json'
    lock_path = data_dir / 'learning_autopilot.lock'
    heartbeat = _read_json(heartbeat_path, {}) or {}
    lock = _read_json(lock_path, {}) or {}
    hb_age = _file_age_seconds(heartbeat_path)
    lock_age = _file_age_seconds(lock_path)
    heartbeat_fresh = hb_age is not None and hb_age <= int(stale_after_seconds)
    has_lock = lock_path.exists()

    con = init_journal(db_path or DEFAULT_DB)
    try:
        learning = prediction_stats(con)
        recent = recent_predictions(con, limit=1)
    finally:
        con.close()
    recent_forecast = recent[0] if recent else None
    state = 'active' if has_lock and heartbeat_fresh else ('stale' if has_lock else 'idle')
    summary = f"Auto Learner {state}: {learning.get('pending', 0)} pending / {learning.get('verified', 0)} verified / {learning.get('total', 0)} total"
    return {
        'mode': 'autopilot_status',
        'daemon': {
            'state': state,
            'has_lock': has_lock,
            'lock': lock,
            'lock_age_seconds': round(lock_age, 1) if lock_age is not None else None,
            'heartbeat': heartbeat,
            'heartbeat_age_seconds': round(hb_age, 1) if hb_age is not None else None,
            'heartbeat_fresh': heartbeat_fresh,
        },
        'learning': learning,
        'recent_forecast': recent_forecast,
        'summary': summary,
    }
