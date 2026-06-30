#!/usr/bin/env python3
from pathlib import Path
import json
import sqlite3
import tempfile
import time
import sys
sys.path.insert(0, str(Path(__file__).parents[1]))

from trader_assistant.autopilot_status import build_autopilot_status
from trader_assistant.journal import init_journal
from trader_assistant.learning_autopilot import create_prediction_from_snapshot, save_prediction


def sample_snapshot():
    return {
        'symbol': 'BTCUSDT',
        'interval': '1h',
        'candles': [{'ts': 1_700_000_000_000, 'open': 100, 'high': 101, 'low': 99, 'close': 100, 'volume': 1}],
        'analysis': {'trend': 'bullish', 'price': 100},
        'risk_reward': {'entry': 100, 'stop': 95, 'target': 110, 'risk_reward_ratio': 2.0, 'rr_quality': {'label': 'strong'}},
        'pro_checklist': {'status': 'clean', 'readiness_score': 80},
        'council': {'chair': {'verdict': 'clean'}},
        'smc': {'bias': 'bullish', 'score': 2},
    }


def test_autopilot_status_reads_heartbeat_lock_stats_and_recent_forecast():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        data = root / 'data'
        data.mkdir()
        hb = data / 'learning_autopilot_heartbeat.json'
        lock = data / 'learning_autopilot.lock'
        hb.write_text(json.dumps({'updated_at': '2026-06-30T10:00:00+00:00', 'interval': '15m', 'symbols': ['BTCUSDT'], 'results': [{'symbol': 'BTCUSDT', 'prediction_id': 7, 'pending': 3}]}), encoding='utf-8')
        lock.write_text(json.dumps({'pid': 123, 'started_at': '2026-06-30T09:00:00+00:00'}), encoding='utf-8')
        db = root / 'test.sqlite3'
        con = init_journal(db)
        try:
            save_prediction(con, create_prediction_from_snapshot(sample_snapshot(), horizon_bars=4))
        finally:
            con.close()
        status = build_autopilot_status(root_dir=root, db_path=db, stale_after_seconds=999999999)
        assert status['mode'] == 'autopilot_status'
        assert status['daemon']['has_lock'] is True
        assert status['daemon']['heartbeat']['interval'] == '15m'
        assert status['learning']['total'] == 1
        assert status['learning']['pending'] == 1
        assert status['recent_forecast']['symbol'] == 'BTCUSDT'
        assert status['summary'].startswith('Auto Learner')


if __name__ == '__main__':
    test_autopilot_status_reads_heartbeat_lock_stats_and_recent_forecast()
    print('OK autopilot status tests passed')
