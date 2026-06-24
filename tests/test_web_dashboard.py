#!/usr/bin/env python3
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parents[1]))

from web_dashboard import render_dashboard_html, build_snapshot_payload, build_risk_reward_payload


def fake_snapshot():
    return {
        'symbol': 'BTCUSDT',
        'analysis': {
            'symbol': 'BTCUSDT', 'price': 60000, 'trend': 'mixed',
            'indicators': {'ema_9': 60100, 'ema_21': 59900, 'rsi_14': 51, 'atr_14': 350, 'vwap': 59800},
            'levels': {'nearest': [59500, 60400], 'fibonacci': {'0.382': 61000, '0.500': 60000, '0.618': 59000}, 'pivots': {'pivot': 60000, 'r1': 60700, 's1': 59300}, 'support_resistance': [59500, 60400]},
            'setup_notes': ['mixed trend'], 'risk_notes': ['confirm manually'], 'candles': []
        },
        'order_book': {'spread_bps': 1.2, 'imbalance': 0.15, 'signals': ['tight spread']},
        'risk_reward': {'risk_reward_ratio': 2.5, 'entry': 60000, 'stop': 59500, 'target': 61250, 'valid': True, 'warnings': []},
        'fear_greed': {'index_value': 50, 'label': 'neutral', 'confirmation': 'neutral', 'interpretation': 'neutral context'},
    }


def test_dashboard_html_contains_core_controls_and_sections():
    html = render_dashboard_html()
    assert '<!doctype html>' in html.lower()
    assert 'Crypto Trader Assistant' in html
    assert 'symbol' in html.lower()
    assert 'entry' in html.lower()
    assert 'risk/reward' in html.lower()
    assert '/api/snapshot' in html
    assert '/api/risk-reward' in html


def test_snapshot_payload_shape_from_injected_fetchers():
    payload = build_snapshot_payload(
        symbol='BTCUSDT', interval='1h', limit=120, entry=60000, side='long',
        klines_fetcher=lambda symbol, interval, limit: [
            {'ts': i, 'open': 100+i, 'high': 102+i, 'low': 99+i, 'close': 101+i, 'volume': 1000+i}
            for i in range(40)
        ],
        depth_fetcher=lambda symbol, limit: ([[140, 2], [139, 1]], [[141, 1], [142, 1]]),
        fear_greed_fetcher=lambda: {'value': 50, 'classification': 'Neutral'},
    )
    assert payload['symbol'] == 'BTCUSDT'
    assert 'analysis' in payload
    assert 'order_book' in payload
    assert 'risk_reward' in payload
    assert 'fear_greed' in payload


def test_risk_reward_payload_uses_entry_side_stop_target():
    snapshot = fake_snapshot()
    payload = build_risk_reward_payload(snapshot['analysis'], entry=60000, side='long', stop=59000, target=63000)
    assert payload['entry'] == 60000
    assert payload['risk_reward_ratio'] == 3.0
    assert payload['source'] == 'manual_stop_target'


if __name__ == '__main__':
    test_dashboard_html_contains_core_controls_and_sections()
    test_snapshot_payload_shape_from_injected_fetchers()
    test_risk_reward_payload_uses_entry_side_stop_target()
    print('OK web dashboard tests passed')
