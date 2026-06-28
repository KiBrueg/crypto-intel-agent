#!/usr/bin/env python3
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parents[1]))

from trader_assistant.smc import detect_smc_context
from web_dashboard import render_dashboard_html


def c(o, h, l, cl):
    return {'open': o, 'high': h, 'low': l, 'close': cl, 'time': 0}


def test_smc_detects_bullish_liquidity_sweep_and_fvg():
    candles = [
        c(100, 104, 99, 103),
        c(103, 105, 101, 104),
        c(104, 106, 102, 105),
        c(105, 107, 103, 106),
        c(106, 108, 104, 107),
        c(107, 109, 98, 108),   # swept prior lows and reclaimed
        c(108, 112, 109.5, 111), # creates bullish FVG vs prior high 109
    ]
    smc = detect_smc_context(candles)
    assert smc['mode'] == 'smart_money_concepts'
    assert smc['bias'] in {'bullish', 'mixed'}
    assert any(z['type'] == 'liquidity_sweep' and z['direction'] == 'bullish' for z in smc['zones'])
    assert any(z['type'] == 'fair_value_gap' and z['direction'] == 'bullish' for z in smc['zones'])
    assert smc['summary']


def test_smc_detects_bearish_bos_and_order_block_candidate():
    candles = [
        c(100, 103, 99, 102),
        c(102, 105, 101, 104),
        c(104, 106, 102, 105),
        c(105, 107, 103, 106),
        c(106, 108, 104, 107),
        c(107, 109, 105, 108),
        c(108, 110, 106, 109),
        c(109, 109.5, 97, 98), # breaks structure down
    ]
    smc = detect_smc_context(candles)
    assert smc['bias'] in {'bearish', 'mixed'}
    assert any(z['type'] == 'break_of_structure' and z['direction'] == 'bearish' for z in smc['zones'])
    assert any(z['type'] == 'order_block_candidate' and z['direction'] == 'bearish' for z in smc['zones'])


def test_dashboard_contains_smc_section():
    html = render_dashboard_html()
    assert 'Smart Money Concepts' in html


if __name__ == '__main__':
    test_smc_detects_bullish_liquidity_sweep_and_fvg()
    test_smc_detects_bearish_bos_and_order_block_candidate()
    test_dashboard_contains_smc_section()
    print('OK SMC tests passed')
