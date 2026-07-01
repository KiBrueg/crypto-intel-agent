#!/usr/bin/env python3
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parents[1]))

from trader_assistant.mind_card_modes import available_mind_card_modes, get_mind_card_mode


def test_available_modes_include_beginner_and_trader_drills():
    modes = available_mind_card_modes()
    keys = {m['key'] for m in modes}
    assert {'mixed', 'quick_scalps', 'breakout_reads', 'fakeout_defense', 'vwap_level_reclaim', 'order_book_sense'}.issubset(keys)
    assert all(m['label'] for m in modes)
    assert all(m['description'] for m in modes)


def test_mode_profile_has_operational_defaults():
    mode = get_mind_card_mode('quick_scalps')
    assert mode['key'] == 'quick_scalps'
    assert 'BTCUSDT' in mode['symbols']
    assert mode['interval'] in ('5m', '15m')
    assert mode['horizon_bars'] > 0
    assert 'order_book' in mode['feature_focus']


def test_unknown_mode_falls_back_to_mixed():
    mode = get_mind_card_mode('not-real')
    assert mode['key'] == 'mixed'


if __name__ == '__main__':
    test_available_modes_include_beginner_and_trader_drills()
    test_mode_profile_has_operational_defaults()
    test_unknown_mode_falls_back_to_mixed()
    print('OK mind card modes tests passed')
