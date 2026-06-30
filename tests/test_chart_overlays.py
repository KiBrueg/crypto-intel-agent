#!/usr/bin/env python3
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parents[1]))

from trader_assistant.chart_overlays import volume_spike_markers, build_chart_overlays


BASE_TS = 1_700_000_000_000


def candle(offset_seconds, open_, high, low, close, volume):
    return {'ts': BASE_TS + offset_seconds * 1000, 'open': open_, 'high': high, 'low': low, 'close': close, 'volume': volume}


def test_volume_spike_markers_highlight_unusual_volume():
    candles = [
        candle(1, 100, 101, 99, 100, 10),
        candle(2, 100, 101, 99, 100, 11),
        candle(3, 100, 101, 99, 100, 9),
        candle(4, 100, 101, 99, 100, 10),
        candle(5, 100, 103, 98, 102, 35),
    ]
    markers = volume_spike_markers(candles, lookback=4, multiplier=2.0)
    assert len(markers) == 1
    assert markers[0]['time'] == BASE_TS // 1000 + 5
    assert markers[0]['shape'] == 'circle'
    assert markers[0]['position'] == 'belowBar'
    assert 'vol spike' in markers[0]['text']


def test_build_chart_overlays_combines_predictions_and_volume_spikes():
    candles = [
        candle(1, 100, 101, 99, 100, 10),
        candle(2, 100, 101, 99, 100, 10),
        candle(3, 100, 104, 99, 103, 30),
    ]
    predictions = [{'time': 2, 'shape': 'arrowUp', 'position': 'belowBar', 'color': '#D2694E', 'text': '#1 up pending'}]
    overlays = build_chart_overlays(candles, prediction_markers=predictions, volume_lookback=2, volume_multiplier=2.0)
    assert overlays['mode'] == 'chart_overlays'
    assert len(overlays['prediction_markers']) == 1
    assert len(overlays['volume_spike_markers']) == 1
    assert len(overlays['markers']) == 2


if __name__ == '__main__':
    test_volume_spike_markers_highlight_unusual_volume()
    test_build_chart_overlays_combines_predictions_and_volume_spikes()
    print('OK chart overlay tests passed')
