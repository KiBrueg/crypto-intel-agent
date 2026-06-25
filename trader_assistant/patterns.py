from __future__ import annotations


def _f(x, default=0.0):
    try:
        return float(x)
    except Exception:
        return default


def _body(k):
    return abs(_f(k.get('close')) - _f(k.get('open')))


def _range(k):
    return max(_f(k.get('high')) - _f(k.get('low')), 1e-9)


def _direction(k):
    return 'bullish' if _f(k.get('close')) >= _f(k.get('open')) else 'bearish'


def _pattern(name, bias, confidence, trader_note, levels=None):
    return {
        'name': name,
        'bias': bias,
        'confidence': round(float(confidence), 3),
        'trader_note': trader_note,
        'levels': levels or {},
    }


def _local_pivots(candles, window=2):
    highs, lows = [], []
    for i in range(window, len(candles)-window):
        h = _f(candles[i]['high'])
        l = _f(candles[i]['low'])
        left = candles[i-window:i]
        right = candles[i+1:i+1+window]
        if all(h >= _f(x['high']) for x in left+right):
            highs.append((i, h))
        if all(l <= _f(x['low']) for x in left+right):
            lows.append((i, l))
    return highs, lows


def _detect_candlesticks(candles):
    out = []
    if len(candles) < 2:
        return out
    recent_start = max(1, len(candles) - 5)
    for idx in range(recent_start, len(candles)):
        prev, last = candles[idx-1], candles[idx]
        out.extend(_detect_candlestick_pair(prev, last))
    return out


def _detect_candlestick_pair(prev, last):
    out = []
    po, pc = _f(prev['open']), _f(prev['close'])
    lo, lc = _f(last['open']), _f(last['close'])
    lh, ll = _f(last['high']), _f(last['low'])
    body = _body(last)
    rng = _range(last)
    upper = lh - max(lo, lc)
    lower = min(lo, lc) - ll
    # Engulfing: last candle body covers previous body.
    if pc < po and lc > lo and lo <= pc and lc >= po:
        out.append(_pattern('bullish_engulfing', 'bullish', 0.64, 'Bullish engulfing candle: watch for follow-through above the engulfing high; invalidated if price loses the candle low.', {'trigger': lh, 'invalidation': ll}))
    if pc > po and lc < lo and lo >= pc and lc <= po:
        out.append(_pattern('bearish_engulfing', 'bearish', 0.64, 'Bearish engulfing candle: watch for acceptance below the engulfing low; invalidated if price reclaims the candle high.', {'trigger': ll, 'invalidation': lh}))
    # Hammer / shooting star: wick dominance.
    if lower >= max(body * 2, rng * 0.35) and upper <= rng * 0.3 and body <= rng * 0.45:
        out.append(_pattern('hammer', 'bullish', 0.55, 'Hammer-style rejection: lower wick shows demand response; stronger only if next candles hold above the low and reclaim VWAP/level.', {'invalidation': ll, 'trigger': max(lo, lc)}))
    if upper >= max(body * 2, rng * 0.35) and lower <= rng * 0.3 and body <= rng * 0.45:
        out.append(_pattern('shooting_star', 'bearish', 0.55, 'Shooting-star rejection: upper wick shows supply response; stronger only if next candles fail below the high.', {'invalidation': lh, 'trigger': min(lo, lc)}))
    # Doji / indecision.
    if body <= rng * 0.1:
        out.append(_pattern('doji_indecision', 'neutral', 0.35, 'Doji/indecision candle: avoid reading direction alone; wait for range break with volume.', {'high': lh, 'low': ll}))
    return out


def _detect_double_top_bottom(candles):
    out = []
    if len(candles) < 8:
        return out
    highs, lows = _local_pivots(candles, window=1)
    closes = [_f(k['close']) for k in candles]
    last_close = closes[-1]
    # Double top: two similar highs, dip between, current close below neckline or close to it.
    for a_i, a_h in highs[-6:]:
        for b_i, b_h in highs[-6:]:
            if b_i <= a_i + 2:
                continue
            diff = abs(a_h - b_h) / max(a_h, b_h)
            if diff > 0.025:
                continue
            valley = min(_f(k['low']) for k in candles[a_i:b_i+1])
            if valley >= min(a_h, b_h) * 0.985:
                continue
            if last_close <= valley * 1.015:
                out.append(_pattern('double_top', 'bearish', min(0.82, 0.62 + (0.025-diff)*5), 'Double top / failed continuation: neckline is the valley between the two highs; stronger only after acceptance below neckline.', {'top_1': a_h, 'top_2': b_h, 'neckline': valley}))
                return out
    # Double bottom.
    for a_i, a_l in lows[-6:]:
        for b_i, b_l in lows[-6:]:
            if b_i <= a_i + 2:
                continue
            diff = abs(a_l - b_l) / max(a_l, b_l)
            if diff > 0.025:
                continue
            peak = max(_f(k['high']) for k in candles[a_i:b_i+1])
            if peak <= max(a_l, b_l) * 1.015:
                continue
            if last_close >= peak * 0.985:
                out.append(_pattern('double_bottom', 'bullish', min(0.82, 0.62 + (0.025-diff)*5), 'Double bottom / failed breakdown: neckline is the peak between lows; stronger only after acceptance above neckline.', {'bottom_1': a_l, 'bottom_2': b_l, 'neckline': peak}))
                return out
    return out


def _detect_compression_and_flag(candles):
    out = []
    if len(candles) < 20:
        return out
    recent = candles[-16:]
    highs = [_f(k['high']) for k in recent]
    lows = [_f(k['low']) for k in recent]
    closes = [_f(k['close']) for k in recent]
    first_range = max(highs[:8]) - min(lows[:8])
    last_range = max(highs[8:]) - min(lows[8:])
    if first_range > 0 and last_range < first_range * 0.72:
        h_slope = highs[-1] - highs[0]
        l_slope = lows[-1] - lows[0]
        if h_slope < 0 and l_slope > 0:
            out.append(_pattern('symmetrical_triangle_compression', 'neutral', 0.52, 'Volatility compression / triangle: direction is unresolved; watch for breakout with volume and failed-break trap.', {'upper_proxy': highs[-1], 'lower_proxy': lows[-1]}))
    # Flag: impulse over previous window, small counter-trend consolidation.
    prior = candles[-30:-16] if len(candles) >= 30 else candles[:-16]
    if len(prior) >= 8:
        impulse = _f(prior[-1]['close']) - _f(prior[0]['close'])
        recent_move = closes[-1] - closes[0]
        avg_price = sum(closes) / len(closes)
        if abs(impulse) / max(avg_price, 1) > 0.035 and abs(recent_move) / max(avg_price, 1) < 0.018:
            if impulse > 0:
                out.append(_pattern('bull_flag_watch', 'bullish', 0.48, 'Bull flag watch: prior impulse with shallow consolidation; useful only if range high breaks and market regime confirms.', {'range_high': max(highs), 'range_low': min(lows)}))
            else:
                out.append(_pattern('bear_flag_watch', 'bearish', 0.48, 'Bear flag watch: prior sell impulse with shallow consolidation; useful only if range low breaks and market regime confirms.', {'range_high': max(highs), 'range_low': min(lows)}))
    return out


def detect_classic_patterns(candles, limit=8):
    """Detect classic TA pattern hints from OHLCV candles.

    These are heuristic watchlist hints inspired by widely taught technical-analysis
    concepts (candlestick reversals, double tops/bottoms, flags, triangles). They
    are not trade signals and require confirmation from trend, volume, levels and
    risk/reward.
    """
    if not candles:
        return []
    candles = list(candles)
    found = []
    found.extend(_detect_candlesticks(candles))
    found.extend(_detect_double_top_bottom(candles))
    found.extend(_detect_compression_and_flag(candles))
    return summarize_patterns(found, limit=limit)


def summarize_patterns(patterns, limit=5):
    seen = set()
    unique = []
    for p in sorted(patterns, key=lambda x: x.get('confidence', 0), reverse=True):
        name = p.get('name')
        if name in seen:
            continue
        seen.add(name)
        unique.append(p)
        if len(unique) >= limit:
            break
    return unique
