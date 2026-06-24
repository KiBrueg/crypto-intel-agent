from __future__ import annotations
from typing import Iterable


def _f(row, key, default=0.0):
    try:
        v = row.get(key, default)
        return default if v is None else float(v)
    except Exception:
        return default


def _clamp(x, lo=0.0, hi=100.0):
    return max(lo, min(hi, float(x)))


def _score_liquidity(row):
    liquidity = _f(row, 'liquidity_usd', 0.0)
    volume = _f(row, 'volume_24h', 0.0)
    spread = _f(row, 'spread_bps', 15.0)
    liq_score = min(liquidity / 10_000_000 * 35, 35) if liquidity else min(volume / 1_000_000_000 * 25, 25)
    spread_score = 30 if spread <= 5 else 18 if spread <= 15 else 5 if spread <= 40 else -20
    return liq_score + spread_score


def _risk_flags(row):
    flags = []
    if _f(row, 'liquidity_usd', 10_000_000) < 100_000:
        flags.append('low liquidity / high slippage risk')
    if _f(row, 'spread_bps', 0) > 30:
        flags.append('wide spread; poor for scalping')
    if _f(row, 'range_pct', 0) > 25:
        flags.append('extreme volatility; position sizing risk')
    if _f(row, 'volume_24h', 1_000_000) < 100_000:
        flags.append('low 24h volume')
    return flags


def score_asset(row: dict) -> dict:
    symbol = str(row.get('symbol') or row.get('base_symbol') or 'UNKNOWN').upper()
    spread = _f(row, 'spread_bps', 12.0)
    liquidity = _f(row, 'liquidity_usd', 0.0)
    range_pct = _f(row, 'range_pct', abs(_f(row, 'change_24h', 0.0)))
    volume_z = _f(row, 'volume_zscore', min(_f(row, 'vol_to_mcap', 0.0) * 50, 5))
    trend_5 = _f(row, 'trend_5', _f(row, 'change_24h', 0.0) / 4)
    trend_20 = _f(row, 'trend_20', _f(row, 'change_24h', 0.0))
    near_high = _f(row, 'near_high_pct', 5.0)
    dist_mean = abs(_f(row, 'distance_from_mean_pct', _f(row, 'change_24h', 0.0) / 2))
    rel_strength = _f(row, 'btc_relative_strength', 0.0)
    liq_component = _score_liquidity(row)

    scalping = liq_component + min(volume_z * 8, 24) + min(range_pct * 3, 18) + (12 if abs(trend_5) > 0.5 else 0)
    if spread <= 5:
        scalping += 12
    if liquidity and liquidity < 200_000:
        scalping -= 45
    if spread > 30:
        scalping -= 35

    breakout = 25 + min(volume_z * 10, 30) + max(0, 20 - near_high * 5) + max(0, trend_20 * 2) + max(0, rel_strength * 8)
    # Breakouts need tradable liquidity and controlled volatility; otherwise they
    # are often just noisy pumps that experienced traders will filter out.
    if range_pct > 12:
        breakout -= 20
    if range_pct > 20:
        breakout -= 25
    if dist_mean > 8:
        breakout -= 18
    if liquidity and liquidity < 200_000:
        breakout -= 45
    if spread > 30:
        breakout -= 35

    mean_reversion = min(dist_mean * 8, 45) + min(abs(_f(row, 'change_24h', 0)) * 2, 35) + min(volume_z * 5, 15)
    if abs(trend_20) > 15:
        mean_reversion -= 10
    if liquidity and liquidity < 200_000:
        mean_reversion -= 20

    scores = {
        'scalping': round(_clamp(scalping), 2),
        'breakout': round(_clamp(breakout), 2),
        'mean_reversion': round(_clamp(mean_reversion), 2),
    }
    reasons = {'scalping': [], 'breakout': [], 'mean_reversion': []}
    if spread <= 5:
        reasons['scalping'].append('tight spread')
    if liquidity >= 1_000_000:
        reasons['scalping'].append('sufficient liquidity')
    if volume_z >= 1.5:
        reasons['scalping'].append('elevated short-term volume')
        reasons['breakout'].append('volume expansion')
    if near_high <= 1.0:
        reasons['breakout'].append('price near range high')
    if trend_20 > 0:
        reasons['breakout'].append('positive trend alignment')
    if dist_mean >= 5:
        reasons['mean_reversion'].append('extended away from rolling mean')
    if abs(_f(row, 'change_24h', 0)) >= 10:
        reasons['mean_reversion'].append('large 24h move may attract reversion traders')

    setup = {
        'confirmation': 'wait for volume to stay elevated and price to hold the relevant level',
        'invalidation': 'setup weakens if price returns inside prior range or liquidity/spread deteriorates',
        'risk': '; '.join(_risk_flags(row)) or 'normal execution risk; confirm manually',
    }
    out = dict(row)
    out.update({'symbol': symbol, 'scores': scores, 'reasons': reasons, 'risk_flags': _risk_flags(row), 'setup': setup})
    return out


def score_market(rows: Iterable[dict]) -> list[dict]:
    return [score_asset(r) for r in rows]


def rank_candidates(scored: list[dict], strategy: str, limit=5, min_score=0.0) -> list[dict]:
    items = [r for r in scored if r.get('scores', {}).get(strategy, 0.0) >= min_score]
    return sorted(items, key=lambda r: r['scores'][strategy], reverse=True)[:limit]
