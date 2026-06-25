#!/usr/bin/env python3
from pathlib import Path
import json
import sqlite3
import sys
import tempfile
sys.path.insert(0, str(Path(__file__).parents[1]))

from trader_assistant.journal import init_journal, save_setup, mark_outcome, learning_stats
from web_dashboard import handle_journal_api


def sample_snapshot(symbol='BTCUSDT'):
    return {
        'symbol': symbol,
        'risk_reward': {'risk_reward_ratio': 2.3, 'rr_quality': {'label': 'strong'}},
        'pro_checklist': {'readiness_score': 72, 'status': 'watch'},
        'classic_patterns': [{'name': 'bull_flag_watch', 'bias': 'bullish'}],
        'multi_timeframe': {'frames': [{'interval': '1h', 'trend': 'bullish'}]},
        'trader_coach': {'headline': 'watchable'},
    }


def test_save_setup_and_mark_outcome_roundtrip():
    with tempfile.TemporaryDirectory() as d:
        db = Path(d) / 'journal.sqlite3'
        con = init_journal(db)
        try:
            setup_id = save_setup(con, sample_snapshot(), notes='test idea')
            assert isinstance(setup_id, int)
            updated = mark_outcome(con, setup_id, 'target', notes='worked')
            assert updated['outcome'] == 'target'
            rows = con.execute('select symbol, outcome, notes from setups').fetchall()
            assert rows[0]['symbol'] == 'BTCUSDT'
            assert rows[0]['outcome'] == 'target'
            assert 'worked' in rows[0]['notes']
        finally:
            con.close()


def test_learning_stats_group_by_pattern_and_rr_quality():
    with tempfile.TemporaryDirectory() as d:
        db = Path(d) / 'journal.sqlite3'
        con = init_journal(db)
        try:
            a = save_setup(con, sample_snapshot())
            b = save_setup(con, sample_snapshot('ETHUSDT'))
            mark_outcome(con, a, 'target')
            mark_outcome(con, b, 'failed')
            stats = learning_stats(con)
            assert stats['total'] == 2
            assert stats['patterns']['bull_flag_watch']['target'] == 1
            assert stats['patterns']['bull_flag_watch']['failed'] == 1
            assert stats['rr_quality']['strong']['target'] == 1
        finally:
            con.close()


def test_dashboard_journal_api_save_outcome_and_stats():
    with tempfile.TemporaryDirectory() as d:
        db = Path(d) / 'journal.sqlite3'
        save_resp = handle_journal_api('POST', '/api/journal/save', {}, json.dumps({'snapshot': sample_snapshot(), 'notes': 'from api'}), db_path=db)
        assert save_resp['ok'] is True
        setup_id = save_resp['setup_id']
        outcome_resp = handle_journal_api('POST', '/api/journal/outcome', {}, json.dumps({'setup_id': setup_id, 'outcome': 'failed'}), db_path=db)
        assert outcome_resp['ok'] is True
        stats_resp = handle_journal_api('GET', '/api/journal/stats', {}, None, db_path=db)
        assert stats_resp['total'] == 1
        assert stats_resp['patterns']['bull_flag_watch']['failed'] == 1


if __name__ == '__main__':
    test_save_setup_and_mark_outcome_roundtrip()
    test_learning_stats_group_by_pattern_and_rr_quality()
    test_dashboard_journal_api_save_outcome_and_stats()
    print('OK setup journal tests passed')
