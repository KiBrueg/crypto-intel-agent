from __future__ import annotations
from statistics import mean


def _f(x, default=0.0):
    try:
        return default if x is None else float(x)
    except Exception:
        return default


def ema(values, period: int):
    vals = [_f(v) for v in values]
    if not vals:
        return []
    alpha = 2.0 / (period + 1.0)
    out = [vals[0]]
    for v in vals[1:]:
        out.append(alpha * v + (1 - alpha) * out[-1])
    return out


def rsi(values, period: int = 14):
    vals = [_f(v) for v in values]
    if not vals:
        return []
    out = [50.0] * len(vals)
    gains, losses = [], []
    for i in range(1, len(vals)):
        diff = vals[i] - vals[i - 1]
        gains.append(max(diff, 0.0))
        losses.append(max(-diff, 0.0))
        if i >= period:
            avg_gain = mean(gains[-period:])
            avg_loss = mean(losses[-period:])
            out[i] = 100.0 if avg_loss == 0 else 100.0 - (100.0 / (1.0 + avg_gain / avg_loss))
    return out


def atr(candles, period: int = 14):
    trs = []
    prev_close = None
    for c in candles:
        high = _f(c.get('high'))
        low = _f(c.get('low'))
        close = _f(c.get('close'))
        if prev_close is None:
            tr = high - low
        else:
            tr = max(high - low, abs(high - prev_close), abs(low - prev_close))
        trs.append(max(tr, 0.0))
        prev_close = close
    out = []
    for i in range(len(trs)):
        window = trs[max(0, i - period + 1):i + 1]
        out.append(mean(window) if window else 0.0)
    return out


def vwap(candles):
    pv = 0.0
    vol = 0.0
    for c in candles:
        typical = (_f(c.get('high')) + _f(c.get('low')) + _f(c.get('close'))) / 3.0
        volume = max(_f(c.get('volume')), 0.0)
        pv += typical * volume
        vol += volume
    return 0.0 if vol == 0 else pv / vol


def fibonacci_levels(candles, lookback: int = 80):
    win = candles[-lookback:]
    high = max(_f(c.get('high')) for c in win)
    low = min(_f(c.get('low')) for c in win)
    span = high - low
    return {
        '0.000': round(high, 8),
        '0.236': round(high - span * 0.236, 8),
        '0.382': round(high - span * 0.382, 8),
        '0.500': round(high - span * 0.500, 8),
        '0.618': round(high - span * 0.618, 8),
        '0.786': round(high - span * 0.786, 8),
        '1.000': round(low, 8),
    }


def pivot_points(prev_candle):
    high = _f(prev_candle.get('high'))
    low = _f(prev_candle.get('low'))
    close = _f(prev_candle.get('close'))
    pivot = (high + low + close) / 3.0
    return {
        'pivot': round(pivot, 8),
        'r1': round(2 * pivot - low, 8),
        's1': round(2 * pivot - high, 8),
        'r2': round(pivot + (high - low), 8),
        's2': round(pivot - (high - low), 8),
    }


def support_resistance_levels(candles, lookback: int = 80, max_levels: int = 8):
    win = candles[-lookback:]
    raw = []
    for c in win:
        raw.extend([_f(c.get('high')), _f(c.get('low'))])
    if not raw:
        return []
    raw = sorted(raw)
    tolerance = (raw[-1] - raw[0]) * 0.006 if raw[-1] != raw[0] else 0.01
    clusters = []
    for level in raw:
        placed = False
        for cluster in clusters:
            if abs(mean(cluster) - level) <= tolerance:
                cluster.append(level)
                placed = True
                break
        if not placed:
            clusters.append([level])
    scored = sorted(clusters, key=lambda x: (len(x), -abs(mean(x) - _f(candles[-1].get('close')))), reverse=True)
    return sorted(round(mean(c), 8) for c in scored[:max_levels])


def _nearest_levels(price, levels, count=3):
    flat = []
    if isinstance(levels, dict):
        flat = list(levels.values())
    else:
        flat = list(levels)
    return sorted(flat, key=lambda x: abs(_f(x) - price))[:count]


def analyze_candles(symbol: str, candles: list[dict]) -> dict:
    if len(candles) < 5:
        raise ValueError('need at least 5 candles')
    closes = [_f(c.get('close')) for c in candles]
    last = candles[-1]
    price = closes[-1]
    ema_fast = ema(closes, 9)
    ema_slow = ema(closes, 21)
    rsi_vals = rsi(closes, 14)
    atr_vals = atr(candles, 14)
    vw = vwap(candles)
    fib = fibonacci_levels(candles)
    sr = support_resistance_levels(candles)
    piv = pivot_points(candles[-2])
    trend = 'bullish' if ema_fast[-1] > ema_slow[-1] and price > vw else 'bearish' if ema_fast[-1] < ema_slow[-1] and price < vw else 'mixed'
    range_high = max(_f(c.get('high')) for c in candles[-20:])
    range_low = min(_f(c.get('low')) for c in candles[-20:])
    near_high_pct = 0.0 if price == 0 else (range_high - price) / price * 100
    near_low_pct = 0.0 if price == 0 else (price - range_low) / price * 100
    notes = []
    risks = []
    if trend == 'bullish':
        notes.append('EMA/VWAP alignment is bullish; breakout traders may watch continuation levels')
    elif trend == 'bearish':
        notes.append('EMA/VWAP alignment is bearish; shorts or defensive bias may dominate')
    else:
        notes.append('trend is mixed; wait for confirmation instead of chasing')
    if near_high_pct <= 0.8:
        notes.append('price is close to recent range high; breakout/rejection zone')
    if near_low_pct <= 0.8:
        notes.append('price is close to recent range low; breakdown/bounce zone')
    if rsi_vals[-1] >= 70:
        risks.append('RSI overbought; breakout can continue but late entries are riskier')
    elif rsi_vals[-1] <= 30:
        risks.append('RSI oversold; downside can continue but mean-reversion traders may watch')
    if atr_vals[-1] / price * 100 > 4 if price else False:
        risks.append('ATR is high relative to price; reduce size or require stronger confirmation')
    return {
        'symbol': symbol.upper(),
        'price': round(price, 8),
        'trend': trend,
        'indicators': {
            'ema_9': round(ema_fast[-1], 8),
            'ema_21': round(ema_slow[-1], 8),
            'rsi_14': round(rsi_vals[-1], 4),
            'atr_14': round(atr_vals[-1], 8),
            'vwap': round(vw, 8),
            'near_high_pct': round(near_high_pct, 4),
            'near_low_pct': round(near_low_pct, 4),
        },
        'levels': {'fibonacci': fib, 'support_resistance': sr, 'pivots': piv, 'nearest': _nearest_levels(price, list(fib.values()) + sr + list(piv.values()), 6)},
        'setup_notes': notes,
        'risk_notes': risks or ['no automatic risk note; still confirm liquidity, news and order book manually'],
        'candles': candles,
    }
