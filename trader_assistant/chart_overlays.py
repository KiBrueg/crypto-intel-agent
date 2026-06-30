from __future__ import annotations


def _time_from_candle(candle, fallback_index):
    raw = candle.get('ts') or candle.get('open_time') or candle.get('time')
    if raw is None:
        return fallback_index
    value = int(raw)
    return int(value / 1000) if value > 10_000_000_000 else value


def volume_spike_markers(candles, lookback=20, multiplier=2.5, limit=30):
    """Return TradingView Lightweight Charts markers for unusual volume candles."""
    rows = list(candles or [])
    markers = []
    lookback = max(2, int(lookback or 20))
    multiplier = float(multiplier or 2.5)
    for i, candle in enumerate(rows):
        if i < lookback:
            continue
        vol = float(candle.get('volume') or 0)
        prev = [float(c.get('volume') or 0) for c in rows[max(0, i - lookback):i]]
        avg = sum(prev) / len(prev) if prev else 0
        if avg > 0 and vol >= avg * multiplier:
            markers.append({
                'time': _time_from_candle(candle, i),
                'position': 'belowBar' if float(candle.get('close') or 0) >= float(candle.get('open') or 0) else 'aboveBar',
                'shape': 'circle',
                'color': '#D2691D',
                'text': f"vol spike {round(vol / avg, 1)}x",
                'kind': 'volume_spike',
                'volume': vol,
                'average_volume': avg,
            })
    return markers[-int(limit):]


def build_chart_overlays(candles, prediction_markers=None, volume_lookback=20, volume_multiplier=2.5):
    prediction_markers = list(prediction_markers or [])
    spikes = volume_spike_markers(candles, lookback=volume_lookback, multiplier=volume_multiplier)
    markers = sorted(prediction_markers + spikes, key=lambda m: (m.get('time') or 0, m.get('text') or ''))
    return {
        'mode': 'chart_overlays',
        'prediction_markers': prediction_markers,
        'volume_spike_markers': spikes,
        'markers': markers,
    }
