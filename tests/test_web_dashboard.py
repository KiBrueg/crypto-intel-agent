#!/usr/bin/env python3
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parents[1]))

from web_dashboard import (
    render_dashboard_html, render_trainer_html, render_landing_html,
    build_snapshot_payload, build_risk_reward_payload,
    classify_rr_quality, build_multi_timeframe_payload, DEFAULT_WATCHLIST,
    load_dashboard_config, build_watchlist_payload,
)


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


def fake_klines(symbol, interval, limit):
    base = {'15m': 100, '1h': 120, '4h': 140}.get(interval, 100)
    return [
        {'ts': i, 'open': base+i, 'high': base+2+i, 'low': base-1+i, 'close': base+1+i, 'volume': 1000+i}
        for i in range(40)
    ]


def test_dashboard_html_contains_core_controls_and_sections():
    html = render_dashboard_html()
    assert '<!doctype html>' in html.lower()
    assert 'Crypto Trader Assistant' in html
    assert 'symbol' in html.lower()
    assert 'entry' in html.lower()
    assert 'risk/reward' in html.lower()
    assert 'Watchlist' in html
    assert 'Auto refresh' in html
    assert 'Export JSON' in html
    assert 'Multi-Timeframe' in html
    assert 'Classic Price Patterns' in html
    assert 'Pro Trader Checklist' in html
    assert 'Trader Coach' in html
    assert 'Setup Journal' in html
    assert 'Knowledge Graph' in html
    assert 'Compact Graph Context' in html
    assert 'chartoverlayinfo' in html
    assert 'Simulation Lab' in html
    assert 'Learning Autopilot' in html
    assert 'Market Mind Cards' in html
    assert 'mindcardcockpit' in html
    assert 'Mini Market Cards' in html
    assert 'miniCardStack' in html
    assert 'miniChooseMindCard' in html
    assert 'miniOpenFullMindCard' in html
    assert 'More' in html
    assert 'Market result' in html
    assert 'mindResultComparison' in html
    assert 'miniResultHint' in html
    assert 'AI thought' in html
    assert 'Market went' in html
    assert 'miniPrefetchCard' in html
    assert 'miniUsePrefetchedCard' in html
    assert 'Loading next card' in html
    assert '/api/mind-card/modes' in html
    assert 'historical=1' in html
    assert '/api/mind-card/next' in html
    assert 'autopilotstatus' in html
    assert 'forecasttimeline' in html
    assert 'forecastdetail' in html
    assert '/api/snapshot' in html
    assert '/api/risk-reward' in html
    assert '/api/multi-timeframe' in html


def test_dashboard_has_pattern_help_button_and_abbreviation_faq():
    html = render_dashboard_html()
    assert 'showPatternGuide' in html
    assert 'patternGuidePanel' in html
    assert 'Pattern cheat sheet' in html
    assert 'Графические паттерны' in html
    assert 'Гармонические паттерны' in html
    assert 'Head and Shoulders' in html
    assert 'Cup and Handle' in html
    assert 'Gartley' in html
    assert 'Butterfly' in html
    assert 'FAQ по сокращениям' in html
    assert 'SMC = Smart Money Concepts' in html
    assert 'R/R = Risk/Reward' in html
    assert 'VWAP = Volume Weighted Average Price' in html
    assert 'FOMO = Fear Of Missing Out' in html


def test_trainer_html_is_sellable_clean_training_page():
    html = render_trainer_html()
    assert '<!doctype html>' in html.lower()
    assert 'Market Mind Cards Trainer' in html
    assert 'trainerSessionTarget' in html
    assert 'trainerSessionStats' in html
    assert 'trainerFinalSummary' in html
    assert 'trainerShareText' in html
    assert 'copyTrainerShare' in html
    assert 'Mixed Session' in html
    assert 'Breakout Reads' in html
    assert 'Fakeout Defense' in html
    assert 'VWAP Reclaims' in html
    assert 'You vs AI vs Market' in html
    assert 'research/backtesting only' in html
    assert 'Start 10-card session' in html
    assert 'Skip/Next' in html
    assert 'Open full dashboard' in html


def test_landing_html_contains_demo_and_sales_assets():
    html = render_landing_html()
    assert '<!doctype html>' in html.lower()
    assert 'Train your market reading' in html
    assert 'Watch demo' in html
    assert 'For trading communities' in html
    assert 'White-label pilot' in html
    assert 'marketmindcards' in html.lower()
    assert 'not a signal bot' in html.lower()
    assert 'Telegram/Discord' in html
    assert 'I built a small AI-assisted crypto chart trainer' in html


def test_default_watchlist_has_major_pairs():
    assert 'BTCUSDT' in DEFAULT_WATCHLIST
    assert 'ETHUSDT' in DEFAULT_WATCHLIST
    assert 'SOLUSDT' in DEFAULT_WATCHLIST


def test_dashboard_config_allows_custom_watchlist(tmp_path):
    cfg = tmp_path / 'dashboard_config.json'
    cfg.write_text('{"watchlist": ["btcusdt", "ethusdt", "solusdt"], "default_symbol": "ethusdt"}')
    loaded = load_dashboard_config(cfg)
    assert loaded['watchlist'] == ['BTCUSDT', 'ETHUSDT', 'SOLUSDT']
    assert loaded['default_symbol'] == 'ETHUSDT'


def test_watchlist_payload_uses_configured_pairs(tmp_path):
    cfg = tmp_path / 'dashboard_config.json'
    cfg.write_text('{"watchlist": ["linkusdt", "avaxusdt"]}')
    payload = build_watchlist_payload(cfg)
    assert payload['watchlist'] == ['LINKUSDT', 'AVAXUSDT']


def test_rr_quality_classification():
    assert classify_rr_quality(None)['label'] == 'n/a'
    assert classify_rr_quality(0.8)['label'] == 'weak'
    assert classify_rr_quality(1.7)['label'] == 'acceptable'
    assert classify_rr_quality(2.5)['label'] == 'strong'
    assert classify_rr_quality(4.0)['label'] == 'excellent'


def test_snapshot_payload_shape_from_injected_fetchers():
    payload = build_snapshot_payload(
        symbol='BTCUSDT', interval='1h', limit=120, entry=60000, side='long',
        klines_fetcher=fake_klines,
        depth_fetcher=lambda symbol, limit: ([[140, 2], [139, 1]], [[141, 1], [142, 1]]),
        fear_greed_fetcher=lambda: {'value': 50, 'classification': 'Neutral'},
    )
    assert payload['symbol'] == 'BTCUSDT'
    assert 'analysis' in payload
    assert 'order_book' in payload
    assert 'risk_reward' in payload
    assert 'fear_greed' in payload
    assert 'rr_quality' in payload['risk_reward']


def test_multi_timeframe_payload_returns_each_requested_interval():
    payload = build_multi_timeframe_payload('BTCUSDT', intervals=('15m', '1h', '4h'), klines_fetcher=fake_klines)
    assert [x['interval'] for x in payload['frames']] == ['15m', '1h', '4h']
    assert all('trend' in x and 'price_vs_vwap_pct' in x for x in payload['frames'])


def test_risk_reward_payload_uses_entry_side_stop_target():
    snapshot = fake_snapshot()
    payload = build_risk_reward_payload(snapshot['analysis'], entry=60000, side='long', stop=59000, target=63000)
    assert payload['entry'] == 60000
    assert payload['risk_reward_ratio'] == 3.0
    assert payload['source'] == 'manual_stop_target'
    assert payload['rr_quality']['label'] == 'excellent'


if __name__ == '__main__':
    test_dashboard_html_contains_core_controls_and_sections()
    test_dashboard_has_pattern_help_button_and_abbreviation_faq()
    test_trainer_html_is_sellable_clean_training_page()
    test_landing_html_contains_demo_and_sales_assets()
    test_default_watchlist_has_major_pairs()
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        test_dashboard_config_allows_custom_watchlist(Path(d))
        test_watchlist_payload_uses_configured_pairs(Path(d))
    test_rr_quality_classification()
    test_snapshot_payload_shape_from_injected_fetchers()
    test_multi_timeframe_payload_returns_each_requested_interval()
    test_risk_reward_payload_uses_entry_side_stop_target()
    print('OK web dashboard tests passed')
