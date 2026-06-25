#!/usr/bin/env python3
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parents[1]))

from trader_assistant.patterns import detect_classic_patterns, summarize_patterns
from web_dashboard import build_snapshot_payload


def c(i, o, h, l, cl, v=1000):
    return {'ts': i, 'open': o, 'high': h, 'low': l, 'close': cl, 'volume': v}


def test_detects_bullish_engulfing_and_hammer():
    candles = [
        c(1, 100, 101, 95, 96),
        c(2, 95, 103, 94, 102),
        c(3, 101, 102, 92, 100),
    ]
    pats = detect_classic_patterns(candles)
    names = {p['name'] for p in pats}
    assert 'bullish_engulfing' in names
    assert 'hammer' in names
    assert all('bias' in p and 'confidence' in p and 'trader_note' in p for p in pats)


def test_detects_double_top_as_bearish_caution():
    prices = [100, 105, 110, 106, 101, 106, 111, 107, 99, 97, 96]
    candles = [c(i, p-0.4, p+1, p-1, p) for i, p in enumerate(prices)]
    pats = detect_classic_patterns(candles)
    dt = [p for p in pats if p['name'] == 'double_top']
    assert dt
    assert dt[0]['bias'] == 'bearish'
    assert 'neckline' in dt[0]['trader_note'].lower()


def test_detects_double_bottom_as_bullish_watch():
    prices = [110, 105, 99, 104, 109, 104, 98, 103, 111, 113, 114]
    candles = [c(i, p+0.4, p+1, p-1, p) for i, p in enumerate(prices)]
    pats = detect_classic_patterns(candles)
    db = [p for p in pats if p['name'] == 'double_bottom']
    assert db
    assert db[0]['bias'] == 'bullish'


def test_summarize_patterns_sorts_high_confidence_first():
    patterns = [
        {'name': 'weak', 'confidence': 0.2, 'bias': 'neutral', 'trader_note': 'x'},
        {'name': 'strong', 'confidence': 0.8, 'bias': 'bullish', 'trader_note': 'y'},
    ]
    summary = summarize_patterns(patterns, limit=1)
    assert summary[0]['name'] == 'strong'


def test_snapshot_payload_includes_classic_patterns():
    payload = build_snapshot_payload(
        symbol='BTCUSDT', interval='1h', limit=120, entry=100, side='long',
        klines_fetcher=lambda symbol, interval, limit: [
            c(1, 100, 101, 95, 96), c(2, 95, 103, 94, 102), c(3, 101, 102, 92, 100)
        ] + [c(i, 100+i*0.1, 101+i*0.1, 99+i*0.1, 100+i*0.1) for i in range(4, 45)],
        depth_fetcher=lambda symbol, limit: ([[100, 5]], [[101, 5]]),
        fear_greed_fetcher=lambda: {'value': 50, 'classification': 'Neutral'},
    )
    assert 'classic_patterns' in payload
    assert isinstance(payload['classic_patterns'], list)


if __name__ == '__main__':
    test_detects_bullish_engulfing_and_hammer()
    test_detects_double_top_as_bearish_caution()
    test_detects_double_bottom_as_bullish_watch()
    test_summarize_patterns_sorts_high_confidence_first()
    test_snapshot_payload_includes_classic_patterns()
    print('OK classic pattern tests passed')
