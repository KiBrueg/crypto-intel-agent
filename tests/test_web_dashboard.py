#!/usr/bin/env python3
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parents[1]))

from web_dashboard import (
    render_dashboard_html, render_trainer_html, render_landing_html,
    build_snapshot_payload, build_risk_reward_payload, build_trainer_chat_reply,
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


def test_dashboard_adds_world_news_as_general_mind_card_factor():
    html = render_dashboard_html()
    assert 'currentGlobalNewsImpact' in html
    assert 'worldNewsFactor' in html
    assert 'World News / Мировые новости' in html
    assert 'Crypto impact' in html
    assert 'Stocks impact' in html


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


def test_pattern_guides_have_visual_candlestick_charts_not_only_text():
    dashboard = render_dashboard_html()
    trainer = render_trainer_html()
    for html in (dashboard, trainer):
        assert 'pattern-visual' in html
        assert '<svg' in html
        assert 'class="candle' in html
        assert 'neckline' in html
        assert 'triangle-lines' in html
        assert 'Head and Shoulders visual' in html
        assert 'Double Top / Bottom visual' in html
        assert 'Triangle visual' in html
        assert 'Flag / Pennant visual' in html


def test_pattern_guides_visualize_inverse_cup_and_harmonics_too():
    dashboard = render_dashboard_html()
    trainer = render_trainer_html()
    expected_visuals = [
        'Inverse Head and Shoulders visual',
        'Cup and Handle visual',
        'Gartley harmonic visual',
        'Butterfly harmonic visual',
        'Bat / Crab harmonic visual',
        'ABCD harmonic visual',
        'Cypher harmonic visual',
        'PRZ harmonic visual',
    ]
    for html in (dashboard, trainer):
        for label in expected_visuals:
            assert label in html
        assert html.count('pattern-visual') >= 12
        assert 'harmonic-leg' in html
        assert 'prz-zone' in html


def test_pattern_guides_visualize_wedge_and_range_fakeout_too():
    dashboard = render_dashboard_html()
    trainer = render_trainer_html()
    for html in (dashboard, trainer):
        assert 'Wedge visual' in html
        assert 'Range breakout / fakeout visual' in html
        assert 'wedge-lines' in html
        assert 'range-box' in html
        assert 'fakeout-marker' in html
        assert html.count('pattern-visual') >= 14


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
    assert 'trainerChoose' in html
    assert 'finishTrainerSession' in html
    assert 'Join pilot waitlist' in html
    assert 'Copy share text' in html
    assert 'showTrainerGuide' in html
    assert 'trainerGuidePanel' in html
    assert 'Pattern cheat sheet' in html
    assert 'Графические паттерны' in html
    assert 'FAQ по сокращениям' in html
    assert '/api/mind-card/next?historical=1' in html
    assert 'assistantBubble' in html
    assert 'trainerAssistantPanel' in html
    assert 'askTrainerAssistant' in html
    assert '/api/trainer-chat' in html
    assert 'ИИ помощник' in html


def test_trainer_has_forecast_realism_calibration_panel_without_strength_framing():
    html = render_trainer_html()
    assert 'Forecast Realism / Calibration Memory' in html
    assert 'trainerCalibrationPanel' in html
    assert 'realism drift' in html
    assert 'bucket reliability' in html
    assert 'bucketBreakdown' in html
    assert 'Overconfidence flags' in html
    assert 'Human Edge' not in html
    assert 'User edge' not in html
    assert 'where your read beats AI' not in html
    assert 'AI weak spots' not in html

    assert 'рынок подтвердил другой сценарий' in html or 'market confirmed another scenario' in html


def test_trainer_assistant_popup_has_quick_questions_and_explain_modes():
    html = render_trainer_html()
    assert 'assistantQuickActions' in html
    assert 'assistantAskQuick' in html
    assert 'assistantTone' in html
    assert 'Объясни новичку' in html
    assert 'Как трейдеру' in html
    assert 'Почему AI так думает?' in html
    assert 'Где invalidation?' in html
    assert 'VWAP/EMA?' in html
    assert 'Какой паттерн?' in html
    assert 'Почему Skip?' in html
    assert 'assistant-panel' in html and 'right:24px' in html


def test_trainer_chat_reply_handles_invalidation_pattern_and_vwap_questions():
    card = {
        'symbol': 'ETHUSDT', 'interval': '15m', 'ai_direction': 'skip',
        'ai_confidence': 0.46, 'risk_reward_ratio': 1.2,
        'risk_loss_pct': 1.4, 'potential_profit_pct': 1.7,
        'setup_quality': 'mixed', 'market_regime': 'choppy', 'fomo_score': 0.61,
        'ai_reason': ['Range high fakeout risk.', 'Price is under VWAP.', 'Pattern: wedge compression.'],
    }
    inv = build_trainer_chat_reply('Где invalidation?', card, {'tone': 'pro'})
    assert inv['topic'] == 'invalidation'
    assert 'invalidation' in inv['answer'].lower()
    assert 'стоп' in inv['answer'].lower() or 'уров' in inv['answer'].lower()
    pat = build_trainer_chat_reply('Какой паттерн и что смотреть?', card, {'tone': 'beginner'})
    assert pat['topic'] == 'pattern'
    assert 'wedge' in pat['answer'].lower() or 'паттерн' in pat['answer'].lower()
    assert 'нович' in pat['answer'].lower()
    vwap = build_trainer_chat_reply('VWAP/EMA?', card, {})
    assert vwap['topic'] == 'vwap_ema'
    assert 'VWAP' in vwap['answer'] and 'EMA' in vwap['answer']


def test_dashboard_and_trainer_render_visible_historical_stats_block():
    dashboard = render_dashboard_html()
    trainer = render_trainer_html()
    for html in (dashboard, trainer):
        assert 'renderHistoricalStats' in html
        assert 'Historical Similarity Stats' in html
        assert 'histStatBars' in html
        assert 'histStatProfile' in html
        assert 'stat_direction' in html
        assert 'selected_filter' in html
        assert 'renderExperienceCalibration' in html
        assert 'Accumulated Experience' in html
        assert 'recommended realistic confidence' in html


def test_trainer_chat_explains_historical_stats_basis_when_available():
    card = {
        'symbol': 'BTCUSDT', 'interval': '1h', 'ai_direction': 'up', 'ai_confidence': 0.61,
        'ai_reason': ['Historical stats: 38 historical windows matched by trend+rsi+vwap → up 58%, down 29%, flat 13%.'],
        'historical_stats': {
            'sample_size': 38, 'up_rate': 0.58, 'down_rate': 0.29, 'flat_rate': 0.13,
            'avg_change_pct': 0.22, 'stat_direction': 'up', 'stat_confidence': 0.61,
            'stat_edge': 0.29, 'selected_filter': 'trend+rsi+vwap',
            'match_profile': {'trend_bucket': 'bullish', 'rsi_bucket': 'high', 'vwap_bucket': 'above_vwap', 'rr_bucket': 'ok_rr', 'fomo_bucket': 'mid_fomo'},
        },
    }
    reply = build_trainer_chat_reply('На какой статистике основан AI?', card, {})
    assert reply['topic'] == 'historical_stats'
    assert '38' in reply['answer']
    assert '58%' in reply['answer']
    assert 'trend+rsi+vwap' in reply['answer']
    assert 'не финансовый совет' in reply['answer'].lower()


def test_trainer_chat_reply_uses_card_context_and_safe_tone():
    card = {
        'symbol': 'BTCUSDT', 'interval': '1h', 'ai_direction': 'down',
        'ai_confidence': 0.72, 'risk_reward_ratio': 1.8,
        'risk_loss_pct': 2.1, 'potential_profit_pct': 3.8,
        'setup_quality': 'clean', 'market_regime': 'bearish', 'fomo_score': 0.24,
        'ai_reason': ['Trend context: bearish.', 'SMC bias: bearish.', 'VWAP rejection risk.'],
        'known_outcome': {'direction': 'down', 'change_pct': -0.7},
    }
    reply = build_trainer_chat_reply('что означает R/R и почему ИИ думает падение?', card, {'mode': 'Fakeout Defense', 'stats': {'cards': 3}})
    assert reply['ok'] is True
    assert 'BTCUSDT' in reply['answer']
    assert 'R/R' in reply['answer']
    assert 'bearish' in reply['answer'] or 'пад' in reply['answer'].lower()
    assert 'не финансовый совет' in reply['answer'].lower()
    assert reply['topic'] in ('risk_reward', 'current_card', 'glossary')


def test_landing_html_contains_demo_and_sales_assets():
    html = render_landing_html()
    assert '<!doctype html>' in html.lower()
    assert 'Train your market reading' in html
    assert 'Watch demo' in html
    assert 'Full Market Dashboard' in html
    assert 'Open analytics dashboard' in html
    assert 'charts, reports and market-state assessment' in html
    assert 'Trainer + AI Helper' in html
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


def test_windows_launcher_opens_entry_page_with_both_modes():
    launcher = Path(__file__).resolve().parents[1] / 'Start_Crypto_Intel_Agent.bat'
    text = launcher.read_text(encoding='utf-8')
    assert 'http://127.0.0.1:%PORT%/landing' in text
    assert 'TRAINER_URL=http://127.0.0.1:%PORT%/trainer' in text
    assert 'DASHBOARD_URL=http://127.0.0.1:%PORT%' in text
    assert 'Full dashboard' in text
    assert 'Trainer with right-side AI helper' in text


if __name__ == '__main__':
    test_dashboard_html_contains_core_controls_and_sections()
    test_dashboard_adds_world_news_as_general_mind_card_factor()
    test_dashboard_has_pattern_help_button_and_abbreviation_faq()
    test_pattern_guides_have_visual_candlestick_charts_not_only_text()
    test_pattern_guides_visualize_inverse_cup_and_harmonics_too()
    test_pattern_guides_visualize_wedge_and_range_fakeout_too()
    test_trainer_html_is_sellable_clean_training_page()
    test_trainer_has_forecast_realism_calibration_panel_without_strength_framing()
    test_trainer_assistant_popup_has_quick_questions_and_explain_modes()
    test_trainer_chat_reply_handles_invalidation_pattern_and_vwap_questions()
    test_dashboard_and_trainer_render_visible_historical_stats_block()
    test_trainer_chat_explains_historical_stats_basis_when_available()
    test_trainer_chat_reply_uses_card_context_and_safe_tone()
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
    test_windows_launcher_opens_entry_page_with_both_modes()
    print('OK web dashboard tests passed')
