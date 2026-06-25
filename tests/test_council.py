#!/usr/bin/env python3
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parents[1]))

from trader_assistant.council import run_council
from web_dashboard import render_dashboard_html, build_snapshot_payload


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
        'ai_desk': {'five_lens_review': [{'lens': 'Balanced Judge', 'note': 'not clean'}]},
    }


def test_council_runner_returns_named_advisors_and_chair():
    result = run_council(sample_snapshot())
    assert result['mode'] == 'council_runner'
    advisor_names = [a['advisor'] for a in result['advisors']]
    assert advisor_names == ['Contrarian', 'First Principles', 'Expansionist', 'Outsider', 'Executor']
    assert result['chair']['verdict'] in {'clean', 'watch', 'not_clean'}
    assert result['chair']['verdict'] == 'not_clean'
    assert result['chair']['action_bias'] == 'wait_for_confirmation'


def test_council_runner_surfaces_disagreement_and_next_actions():
    result = run_council(sample_snapshot())
    assert result['disagreements']
    assert any('risk' in item.lower() or 'r/r' in item.lower() for item in result['chair']['blockers'])
    assert any('wait' in item.lower() or 'reclaim' in item.lower() for item in result['chair']['next_actions'])
    text = str(result).lower()
    assert 'buy now' not in text
    assert 'sell now' not in text


def test_dashboard_contains_council_verdict_section():
    html = render_dashboard_html()
    assert 'Council Verdict' in html


if __name__ == '__main__':
    test_council_runner_returns_named_advisors_and_chair()
    test_council_runner_surfaces_disagreement_and_next_actions()
    test_dashboard_contains_council_verdict_section()
    print('OK council tests passed')
