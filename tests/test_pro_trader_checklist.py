#!/usr/bin/env python3
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parents[1]))

from trader_assistant.checklist import build_pro_trader_checklist
from web_dashboard import build_snapshot_payload


def base_snapshot(**overrides):
    snap = {
        'symbol': 'BTCUSDT',
        'analysis': {
            'symbol': 'BTCUSDT', 'price': 100.0, 'trend': 'bullish',
            'indicators': {'rsi_14': 55, 'vwap': 98, 'ema_9': 101, 'ema_21': 99, 'atr_14': 2},
            'setup_notes': ['EMA/VWAP alignment is bullish'],
            'risk_notes': [],
        },
        'multi_timeframe': {'frames': [
            {'interval': '15m', 'trend': 'bullish', 'price_vs_vwap_pct': 1.2, 'rsi_14': 58},
            {'interval': '1h', 'trend': 'bullish', 'price_vs_vwap_pct': 0.8, 'rsi_14': 61},
            {'interval': '4h', 'trend': 'mixed', 'price_vs_vwap_pct': 0.1, 'rsi_14': 52},
        ]},
        'risk_reward': {'risk_reward_ratio': 2.4, 'rr_quality': {'label': 'strong'}, 'valid': True, 'warnings': []},
        'fear_greed': {'confirmation': 'mixed', 'label': 'neutral', 'score': 0, 'interpretation': 'mixed'},
        'order_book': {'imbalance': 0.35, 'spread_bps': 1.5, 'signals': ['bid wall / buy-side depth dominates', 'tight spread']},
        'classic_patterns': [{'name': 'bull_flag_watch', 'bias': 'bullish', 'confidence': 0.55, 'trader_note': 'range high trigger'}],
    }
    snap.update(overrides)
    return snap


def test_checklist_scores_clean_context_as_watch_or_clean():
    result = build_pro_trader_checklist(base_snapshot())
    assert result['readiness_score'] >= 65
    assert result['status'] in {'watch', 'clean'}
    assert any(x['name'] == 'Risk/Reward' and x['status'] == 'pass' for x in result['checklist'])
    assert result['next_checks']


def test_checklist_flags_conflicting_context_and_weak_rr():
    snap = base_snapshot(
        risk_reward={'risk_reward_ratio': 0.7, 'rr_quality': {'label': 'weak'}, 'valid': True, 'warnings': ['low reward/risk']},
        multi_timeframe={'frames': [
            {'interval': '15m', 'trend': 'bullish', 'price_vs_vwap_pct': 1.0, 'rsi_14': 55},
            {'interval': '1h', 'trend': 'bearish', 'price_vs_vwap_pct': -1.0, 'rsi_14': 42},
            {'interval': '4h', 'trend': 'bearish', 'price_vs_vwap_pct': -2.0, 'rsi_14': 38},
        ]},
        classic_patterns=[
            {'name': 'bearish_engulfing', 'bias': 'bearish', 'confidence': 0.64, 'trader_note': 'supply response'},
            {'name': 'hammer', 'bias': 'bullish', 'confidence': 0.55, 'trader_note': 'demand response'},
        ],
    )
    result = build_pro_trader_checklist(snap)
    assert result['status'] == 'not_clean'
    assert result['readiness_score'] < 55
    assert result['blockers']
    assert any('R/R' in b or 'multi-timeframe' in b for b in result['blockers'])


def test_snapshot_payload_contains_pro_trader_checklist():
    def c(i, p):
        return {'ts': i, 'open': p-1, 'high': p+1, 'low': p-2, 'close': p, 'volume': 1000+i}
    payload = build_snapshot_payload(
        symbol='BTCUSDT', interval='1h', limit=120, entry=100, side='long',
        klines_fetcher=lambda symbol, interval, limit: [c(i, 100+i*0.2) for i in range(45)],
        depth_fetcher=lambda symbol, limit: ([[100, 5]], [[101, 5]]),
        fear_greed_fetcher=lambda: {'value': 50, 'classification': 'Neutral'},
    )
    assert 'pro_checklist' in payload
    assert 'readiness_score' in payload['pro_checklist']
    assert payload['pro_checklist']['checklist']


if __name__ == '__main__':
    test_checklist_scores_clean_context_as_watch_or_clean()
    test_checklist_flags_conflicting_context_and_weak_rr()
    test_snapshot_payload_contains_pro_trader_checklist()
    print('OK pro trader checklist tests passed')
