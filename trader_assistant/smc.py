from __future__ import annotations


def _f(v, default=0.0):
    try:
        return float(v)
    except Exception:
        return default


def _zone(kind, direction, low, high, index, strength=1, note=''):
    return {
        'type': kind,
        'direction': direction,
        'low': round(float(low), 8),
        'high': round(float(high), 8),
        'index': index,
        'strength': strength,
        'note': note,
    }


def detect_smc_context(candles, lookback=40):
    """Detect lightweight Smart Money Concept context.

    This is a deterministic decision-support layer, not a trading signal.
    It looks for common SMC-style structures:
    - liquidity sweeps
    - fair value gaps / imbalances
    - break of structure
    - order block candidates
    """
    candles = list(candles or [])[-int(lookback):]
    zones = []
    if len(candles) < 5:
        return {'mode': 'smart_money_concepts', 'bias': 'neutral', 'score': 0, 'zones': zones, 'summary': 'Not enough candles for SMC context.'}

    # Liquidity sweeps: new extreme through recent swing, then close back inside.
    for i in range(3, len(candles)):
        c = candles[i]
        prev = candles[max(0, i - 5):i]
        prev_low = min(_f(x.get('low')) for x in prev)
        prev_high = max(_f(x.get('high')) for x in prev)
        low = _f(c.get('low'))
        high = _f(c.get('high'))
        close = _f(c.get('close'))
        open_ = _f(c.get('open'))
        if low < prev_low and close > prev_low and close >= open_:
            zones.append(_zone('liquidity_sweep', 'bullish', low, prev_low, i, 2, 'Swept sell-side liquidity and reclaimed prior lows.'))
        if high > prev_high and close < prev_high and close <= open_:
            zones.append(_zone('liquidity_sweep', 'bearish', prev_high, high, i, 2, 'Swept buy-side liquidity and rejected prior highs.'))

    # Fair value gaps: three-candle imbalance.
    for i in range(2, len(candles)):
        a = candles[i - 2]
        c = candles[i]
        a_high = _f(a.get('high'))
        a_low = _f(a.get('low'))
        c_low = _f(c.get('low'))
        c_high = _f(c.get('high'))
        if c_low > a_high:
            zones.append(_zone('fair_value_gap', 'bullish', a_high, c_low, i, 1, 'Bullish imbalance / FVG; watch for mitigation.'))
        if c_high < a_low:
            zones.append(_zone('fair_value_gap', 'bearish', c_high, a_low, i, 1, 'Bearish imbalance / FVG; watch for mitigation.'))

    # Break of structure on latest candle vs recent range.
    latest = candles[-1]
    recent = candles[-8:-1]
    recent_high = max(_f(x.get('high')) for x in recent)
    recent_low = min(_f(x.get('low')) for x in recent)
    latest_close = _f(latest.get('close'))
    if latest_close > recent_high:
        zones.append(_zone('break_of_structure', 'bullish', recent_high, latest_close, len(candles) - 1, 3, 'Closed above recent structure high.'))
        # Last bearish candle before the break becomes bullish OB candidate.
        for j in range(len(candles) - 2, -1, -1):
            x = candles[j]
            if _f(x.get('close')) < _f(x.get('open')):
                zones.append(_zone('order_block_candidate', 'bullish', _f(x.get('low')), _f(x.get('high')), j, 2, 'Last down candle before bullish structure break.'))
                break
    if latest_close < recent_low:
        zones.append(_zone('break_of_structure', 'bearish', latest_close, recent_low, len(candles) - 1, 3, 'Closed below recent structure low.'))
        for j in range(len(candles) - 2, -1, -1):
            x = candles[j]
            if _f(x.get('close')) > _f(x.get('open')):
                zones.append(_zone('order_block_candidate', 'bearish', _f(x.get('low')), _f(x.get('high')), j, 2, 'Last up candle before bearish structure break.'))
                break

    # Keep the most relevant / recent zones, but preserve enough context.
    zones = sorted(zones, key=lambda z: (z['strength'], z['index']), reverse=True)[:12]
    bull_score = sum(z['strength'] for z in zones if z['direction'] == 'bullish')
    bear_score = sum(z['strength'] for z in zones if z['direction'] == 'bearish')
    if bull_score > bear_score + 1:
        bias = 'bullish'
    elif bear_score > bull_score + 1:
        bias = 'bearish'
    elif bull_score or bear_score:
        bias = 'mixed'
    else:
        bias = 'neutral'
    summary = f"SMC bias {bias}: {len(zones)} zones detected; bullish score {bull_score}, bearish score {bear_score}."
    return {
        'mode': 'smart_money_concepts',
        'bias': bias,
        'score': bull_score - bear_score,
        'bullish_score': bull_score,
        'bearish_score': bear_score,
        'zones': zones,
        'summary': summary,
    }
