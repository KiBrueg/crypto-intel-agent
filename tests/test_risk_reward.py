#!/usr/bin/env python3
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parents[1]))

from trader_assistant.risk_reward import calculate_risk_reward, build_level_setups


def test_long_risk_reward_uses_entry_stop_target():
    rr = calculate_risk_reward(entry=100, stop=95, target=115, side='long')
    assert rr['side'] == 'long'
    assert rr['risk_per_unit'] == 5
    assert rr['reward_per_unit'] == 15
    assert rr['risk_reward_ratio'] == 3.0
    assert rr['valid'] is True


def test_short_risk_reward_uses_entry_stop_target():
    rr = calculate_risk_reward(entry=100, stop=106, target=82, side='short')
    assert rr['risk_per_unit'] == 6
    assert rr['reward_per_unit'] == 18
    assert rr['risk_reward_ratio'] == 3.0
    assert rr['valid'] is True


def test_invalid_setup_is_flagged_not_crashed():
    rr = calculate_risk_reward(entry=100, stop=105, target=120, side='long')
    assert rr['valid'] is False
    assert rr['risk_reward_ratio'] is None
    assert rr['warnings']


def test_build_level_setups_creates_nearest_long_and_short_ideas():
    analysis = {
        'symbol': 'TESTUSDT',
        'price': 100.0,
        'levels': {
            'nearest': [94.0, 97.0, 103.0, 110.0],
            'support_resistance': [94.0, 97.0, 103.0, 110.0],
            'fibonacci': {'0.382': 103.0, '0.618': 97.0},
            'pivots': {'pivot': 100.0, 'r1': 106.0, 's1': 96.0},
        },
        'indicators': {'atr_14': 2.0},
    }
    setups = build_level_setups(analysis)
    assert {'long_breakout', 'long_pullback', 'short_breakdown', 'short_rejection'} <= set(setups)
    assert setups['long_breakout']['risk_reward_ratio'] is not None
    assert setups['short_breakdown']['risk_reward_ratio'] is not None
    assert all('invalidation' in s for s in setups.values())


if __name__ == '__main__':
    test_long_risk_reward_uses_entry_stop_target()
    test_short_risk_reward_uses_entry_stop_target()
    test_invalid_setup_is_flagged_not_crashed()
    test_build_level_setups_creates_nearest_long_and_short_ideas()
    print('OK risk/reward tests passed')
