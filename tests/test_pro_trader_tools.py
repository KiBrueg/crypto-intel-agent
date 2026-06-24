#!/usr/bin/env python3
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parents[1]))

from trader_assistant.technical_analysis import (
    ema, rsi, atr, vwap, fibonacci_levels, support_resistance_levels,
    pivot_points, analyze_candles
)
from trader_assistant.order_book import analyze_order_book
from trader_assistant.pro_report import render_pro_trader_report


def candles():
    rows = []
    price = 100.0
    for i in range(60):
        open_ = price
        close = open_ + (0.4 if i < 30 else -0.15) + (0.05 * (i % 3))
        high = max(open_, close) + 0.8
        low = min(open_, close) - 0.6
        volume = 1000 + i * 20
        rows.append({'ts': i, 'open': open_, 'high': high, 'low': low, 'close': close, 'volume': volume})
        price = close
    return rows


def test_core_indicators_return_expected_shapes():
    cs = candles()
    closes = [c['close'] for c in cs]
    assert len(ema(closes, 10)) == len(closes)
    assert len(rsi(closes, 14)) == len(closes)
    assert len(atr(cs, 14)) == len(cs)
    assert vwap(cs) > 0
    assert 0 <= rsi(closes, 14)[-1] <= 100


def test_fibonacci_and_support_resistance_levels_are_sorted():
    cs = candles()
    fib = fibonacci_levels(cs)
    assert {'0.236', '0.382', '0.500', '0.618', '0.786'} <= set(fib)
    levels = support_resistance_levels(cs, lookback=40, max_levels=6)
    assert len(levels) <= 6
    assert levels == sorted(levels)
    pivots = pivot_points(cs[-2])
    assert pivots['r1'] > pivots['pivot'] > pivots['s1']


def test_order_book_imbalance_detects_bid_wall():
    bids = [[99.9, 10], [99.8, 20], [99.7, 30]]
    asks = [[100.1, 3], [100.2, 4], [100.3, 5]]
    ob = analyze_order_book(bids, asks, mid_price=100.0)
    assert ob['bid_notional'] > ob['ask_notional']
    assert ob['imbalance'] > 0
    assert any('bid' in flag.lower() for flag in ob['signals'])


def test_analyze_candles_builds_pro_trader_context():
    result = analyze_candles('TESTUSDT', candles())
    assert result['symbol'] == 'TESTUSDT'
    assert 'trend' in result
    assert 'levels' in result
    assert 'fibonacci' in result['levels']
    assert 'support_resistance' in result['levels']
    assert result['setup_notes']
    assert result['risk_notes']


def test_render_pro_report_contains_chart_and_decision_sections():
    analysis = analyze_candles('TESTUSDT', candles())
    order_book = analyze_order_book([[99, 10]], [[101, 10]], mid_price=100)
    md, html = render_pro_trader_report([analysis], {'TESTUSDT': order_book})
    assert 'Professional Trader Context' in md
    assert 'Confirmation checklist' in md
    assert 'Invalidation' in md
    assert '<svg' in html
    assert 'not financial advice' in md.lower()


if __name__ == '__main__':
    test_core_indicators_return_expected_shapes()
    test_fibonacci_and_support_resistance_levels_are_sorted()
    test_order_book_imbalance_detects_bid_wall()
    test_analyze_candles_builds_pro_trader_context()
    test_render_pro_report_contains_chart_and_decision_sections()
    print('OK pro trader tools tests passed')
