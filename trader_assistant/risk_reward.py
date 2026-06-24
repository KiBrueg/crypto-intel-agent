from __future__ import annotations


def _num(x, default=None):
    try:
        if x is None:
            return default
        return float(x)
    except Exception:
        return default


def calculate_risk_reward(entry, stop, target, side='long'):
    """Calculate simple per-unit risk/reward for a hypothetical setup.

    This is decision-support math only; it does not recommend a trade.
    """
    entry = _num(entry)
    stop = _num(stop)
    target = _num(target)
    side = str(side).lower()
    warnings = []
    if entry is None or stop is None or target is None:
        return {'side': side, 'entry': entry, 'stop': stop, 'target': target, 'risk_per_unit': None, 'reward_per_unit': None, 'risk_reward_ratio': None, 'valid': False, 'warnings': ['missing numeric level']}
    if side not in {'long', 'short'}:
        warnings.append('side must be long or short')
    if side == 'long':
        risk = entry - stop
        reward = target - entry
        if stop >= entry:
            warnings.append('long stop must be below entry')
        if target <= entry:
            warnings.append('long target must be above entry')
    else:
        risk = stop - entry
        reward = entry - target
        if stop <= entry:
            warnings.append('short stop must be above entry')
        if target >= entry:
            warnings.append('short target must be below entry')
    valid = not warnings and risk > 0 and reward > 0
    ratio = None if not valid else round(reward / risk, 4)
    if valid and ratio < 1.5:
        warnings.append('low reward/risk; may not justify execution risk')
    return {
        'side': side,
        'entry': round(entry, 8),
        'stop': round(stop, 8),
        'target': round(target, 8),
        'risk_per_unit': None if risk <= 0 else round(risk, 8),
        'reward_per_unit': None if reward <= 0 else round(reward, 8),
        'risk_reward_ratio': ratio,
        'valid': valid,
        'warnings': warnings,
    }


def _sorted_levels(analysis):
    levels = set()
    lv = analysis.get('levels', {})
    for key in ('nearest', 'support_resistance'):
        for x in lv.get(key, []) or []:
            n = _num(x)
            if n:
                levels.add(n)
    for group in ('fibonacci', 'pivots'):
        obj = lv.get(group, {}) or {}
        for x in obj.values():
            n = _num(x)
            if n:
                levels.add(n)
    return sorted(levels)


def _below(levels, price):
    return sorted([x for x in levels if x < price], reverse=True)


def _above(levels, price):
    return sorted([x for x in levels if x > price])


def _annotate(rr, name, invalidation):
    rr = dict(rr)
    rr['setup'] = name
    rr['invalidation'] = invalidation
    return rr


def build_level_setups(analysis):
    """Build hypothetical R/R setups from nearest levels.

    The output is not a recommendation. It gives a trader the arithmetic for
    common level-based ideas: breakout, pullback, breakdown, rejection.
    """
    price = _num(analysis.get('price'))
    if price is None:
        return {}
    levels = _sorted_levels(analysis)
    below = _below(levels, price)
    above = _above(levels, price)
    atr = _num((analysis.get('indicators') or {}).get('atr_14'), price * 0.01) or price * 0.01
    pad = max(atr * 0.25, price * 0.001)
    setups = {}
    if len(above) >= 2 and below:
        entry = above[0]
        stop = max(below[0], price - atr) - pad
        target = above[1]
        setups['long_breakout'] = _annotate(calculate_risk_reward(entry, stop, target, 'long'), 'long_breakout', 'fails if price cannot hold above breakout level')
    if below and above:
        entry = below[0]
        stop = below[0] - max(pad, atr * 0.35)
        target = above[0]
        setups['long_pullback'] = _annotate(calculate_risk_reward(entry, stop, target, 'long'), 'long_pullback', 'fails if support level is lost')
    if len(below) >= 2 and above:
        entry = below[0]
        stop = min(above[0], price + atr) + pad
        target = below[1]
        setups['short_breakdown'] = _annotate(calculate_risk_reward(entry, stop, target, 'short'), 'short_breakdown', 'fails if price reclaims breakdown level')
    if above and below:
        entry = above[0]
        stop = above[0] + max(pad, atr * 0.35)
        target = below[0]
        setups['short_rejection'] = _annotate(calculate_risk_reward(entry, stop, target, 'short'), 'short_rejection', 'fails if resistance is accepted and holds')
    return setups
