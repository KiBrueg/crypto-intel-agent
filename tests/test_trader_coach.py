#!/usr/bin/env python3
from pathlib import Path
import json
import sys
import tempfile
sys.path.insert(0, str(Path(__file__).parents[1]))

from trader_assistant.coach import build_trader_coach, record_setup_feedback, load_learning_stats
from web_dashboard import build_snapshot_payload


def sample_snapshot(**overrides):
    snap = {
        'symbol': 'BTCUSDT',
        'analysis': {
            'trend': 'bearish',
            'price': 100.0,
            'indicators': {'rsi_14': 28, 'vwap': 103, 'atr_14': 2.5},
        },
        'risk_reward': {'risk_reward_ratio': 0.8, 'rr_quality': {'label': 'weak'}, 'valid': True, 'warnings': ['low reward/risk']},
        'pro_checklist': {
            'status': 'not_clean',
            'readiness_score': 32,
            'blockers': ['R/R 0.8 is weak; reward is smaller than risk'],
            'warnings': ['MTF conflict: 1 bullish, 2 bearish'],
            'next_checks': ['Resolve warnings', 'Confirm trigger/neckline'],
        },
        'classic_patterns': [
            {'name': 'hammer', 'bias': 'bullish', 'confidence': 0.55, 'trader_note': 'lower wick rejection'},
            {'name': 'bearish_engulfing', 'bias': 'bearish', 'confidence': 0.64, 'trader_note': 'supply response'},
        ],
        'multi_timeframe': {'frames': [
            {'interval': '15m', 'trend': 'bullish'},
            {'interval': '1h', 'trend': 'bearish'},
            {'interval': '4h', 'trend': 'bearish'},
        ]},
        'fear_greed': {'confirmation': 'mixed', 'label': 'extreme fear'},
        'order_book': {'spread_bps': 1.2, 'imbalance': -0.4, 'signals': ['ask wall / sell-side depth dominates']},
    }
    snap.update(overrides)
    return snap


def test_coach_explains_why_setup_is_not_clean_without_trade_commands():
    coach = build_trader_coach(sample_snapshot())
    text = json.dumps(coach).lower()
    assert coach['mode'] == 'teaching_coach'
    assert coach['headline']
    assert coach['explain_like_pro']
    assert coach['what_to_wait_for']
    assert any('risk/reward' in x.lower() or 'r/r' in x.lower() for x in coach['teaching_points'])
    assert 'buy' not in text and 'sell' not in text
    assert 'покуп' not in text and 'прода' not in text


def test_learning_stats_influence_coach_when_pattern_failed_before():
    with tempfile.TemporaryDirectory() as d:
        journal = Path(d) / 'learning.jsonl'
        record_setup_feedback(journal, {'symbol': 'BTCUSDT', 'patterns': ['hammer'], 'outcome': 'failed', 'rr_quality': 'weak'})
        record_setup_feedback(journal, {'symbol': 'ETHUSDT', 'patterns': ['hammer'], 'outcome': 'failed', 'rr_quality': 'weak'})
        stats = load_learning_stats(journal)
        coach = build_trader_coach(sample_snapshot(), learning_stats=stats)
        assert any('hammer' in x.lower() and 'failed' in x.lower() for x in coach['learning_notes'])


def test_snapshot_payload_contains_trader_coach():
    def c(i, p):
        return {'ts': i, 'open': p-1, 'high': p+1, 'low': p-2, 'close': p, 'volume': 1000+i}
    payload = build_snapshot_payload(
        symbol='BTCUSDT', interval='1h', limit=120, entry=100, side='long',
        klines_fetcher=lambda symbol, interval, limit: [c(i, 100+i*0.2) for i in range(45)],
        depth_fetcher=lambda symbol, limit: ([[100, 5]], [[101, 5]]),
        fear_greed_fetcher=lambda: {'value': 50, 'classification': 'Neutral'},
    )
    assert 'trader_coach' in payload
    assert payload['trader_coach']['teaching_points']


if __name__ == '__main__':
    test_coach_explains_why_setup_is_not_clean_without_trade_commands()
    test_learning_stats_influence_coach_when_pattern_failed_before()
    test_snapshot_payload_contains_trader_coach()
    print('OK trader coach tests passed')
