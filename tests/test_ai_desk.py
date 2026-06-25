#!/usr/bin/env python3
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parents[1]))

from trader_assistant.ai_desk import build_ai_desk_notes
from web_dashboard import render_dashboard_html


def sample_snapshot():
    return {
        'symbol': 'BTCUSDT',
        'analysis': {'trend': 'mixed', 'price': 65000, 'setup_notes': ['price below VWAP']},
        'risk_reward': {'risk_reward_ratio': 0.8, 'rr_quality': {'label': 'weak'}},
        'pro_checklist': {'readiness_score': 35, 'status': 'not_clean', 'blockers': ['Weak R/R'], 'warnings': ['MTF conflict'], 'next_checks': ['Wait for VWAP reclaim']},
        'trader_coach': {'headline': 'Context is not clean yet', 'teaching_points': ['Do not force low R/R']},
        'multi_timeframe': {'frames': [{'interval': '15m', 'trend': 'bullish'}, {'interval': '1h', 'trend': 'mixed'}, {'interval': '4h', 'trend': 'bearish'}]},
        'classic_patterns': [{'name': 'hammer', 'bias': 'bullish'}, {'name': 'bearish_engulfing', 'bias': 'bearish'}],
        'order_book': {'spread_bps': 0.5, 'signals': ['bid wall'], 'imbalance': 1.2},
        'fear_greed': {'label': 'extreme fear', 'confirmation': 'mixed'},
    }


def test_ai_desk_notes_create_role_cards_without_trade_commands():
    notes = build_ai_desk_notes(sample_snapshot())
    assert notes['mode'] == 'ai_desk'
    roles = [card['role'] for card in notes['cards']]
    assert 'Market Brief' in roles
    assert 'Bull/Bear Debate' in roles
    assert 'Risk Manager' in roles
    assert 'Trader Coach' in roles
    text = str(notes).lower()
    assert 'buy now' not in text
    assert 'sell now' not in text
    assert notes['overall_status'] == 'not_clean'


def test_ai_desk_notes_surface_conflicts_and_wait_conditions():
    notes = build_ai_desk_notes(sample_snapshot())
    debate = next(card for card in notes['cards'] if card['role'] == 'Bull/Bear Debate')
    assert any('conflict' in item.lower() or 'bearish' in item.lower() for item in debate['key_points'])
    risk = next(card for card in notes['cards'] if card['role'] == 'Risk Manager')
    assert risk['verdict'] in {'reject', 'caution'}
    assert any('R/R' in item or 'risk/reward' in item.lower() for item in risk['key_points'])


def test_dashboard_contains_ai_desk_section():
    html = render_dashboard_html()
    assert 'AI Desk Notes' in html


if __name__ == '__main__':
    test_ai_desk_notes_create_role_cards_without_trade_commands()
    test_ai_desk_notes_surface_conflicts_and_wait_conditions()
    test_dashboard_contains_ai_desk_section()
    print('OK ai desk tests passed')
