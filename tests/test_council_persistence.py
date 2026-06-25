#!/usr/bin/env python3
from pathlib import Path
import sqlite3
import sys
import tempfile
sys.path.insert(0, str(Path(__file__).parents[1]))

from trader_assistant.council import run_council
from trader_assistant.journal import init_journal, save_council_review, recent_council_reviews
from web_dashboard import handle_journal_api


def sample_snapshot():
    return {
        'symbol': 'BTCUSDT',
        'analysis': {'trend': 'mixed', 'price': 65000},
        'risk_reward': {'risk_reward_ratio': 0.8, 'rr_quality': {'label': 'weak'}},
        'pro_checklist': {'readiness_score': 35, 'status': 'not_clean', 'blockers': ['Weak R/R'], 'next_checks': ['Wait for VWAP reclaim']},
        'multi_timeframe': {'frames': [{'trend': 'bullish'}, {'trend': 'bearish'}]},
        'classic_patterns': [{'name': 'hammer', 'bias': 'bullish'}, {'name': 'bearish_engulfing', 'bias': 'bearish'}],
        'order_book': {'spread_bps': 0.5, 'signals': ['bid wall']},
        'fear_greed': {'label': 'fear', 'confirmation': 'mixed'},
    }


def test_save_and_list_council_reviews_in_sqlite():
    with tempfile.TemporaryDirectory() as d:
        con = init_journal(Path(d) / 'journal.sqlite3')
        council = run_council(sample_snapshot())
        review_id = save_council_review(con, sample_snapshot(), council, notes='manual ask council')
        assert isinstance(review_id, int)
        rows = recent_council_reviews(con, limit=5)
        assert len(rows) == 1
        assert rows[0]['id'] == review_id
        assert rows[0]['symbol'] == 'BTCUSDT'
        assert rows[0]['chair_verdict'] == 'not_clean'
        assert rows[0]['action_bias'] == 'wait_for_confirmation'
        assert rows[0]['advisor_count'] == 5
        con.close()


def test_council_save_api_shape():
    with tempfile.TemporaryDirectory() as d:
        db = Path(d) / 'journal.sqlite3'
        council = run_council(sample_snapshot())
        response = handle_journal_api('POST', '/api/council/save', body={'snapshot': sample_snapshot(), 'council': council, 'notes': 'api test'}, db_path=db)
        assert response['ok'] is True
        assert response['review_id'] >= 1
        stats = handle_journal_api('GET', '/api/council/recent', qs={'limit': ['5']}, db_path=db)
        assert stats['total'] == 1
        assert stats['recent'][0]['chair_verdict'] == 'not_clean'


if __name__ == '__main__':
    test_save_and_list_council_reviews_in_sqlite()
    test_council_save_api_shape()
    print('OK council persistence tests passed')
