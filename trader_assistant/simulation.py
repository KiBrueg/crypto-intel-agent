from __future__ import annotations

from collections import Counter, defaultdict


def _f(v, default=0.0):
    try:
        return float(v)
    except Exception:
        return default


def simulate_trade_path(candles, entry, stop, target, side='long', start_index=0, lookahead=24):
    """Simulate whether stop or target is reached first after start_index.

    This is not prediction. It is the scoring function used to compare a prior
    setup/council verdict against what actually happened later.
    """
    entry = _f(entry)
    stop = _f(stop)
    target = _f(target)
    start = max(0, int(start_index))
    end = min(len(candles), start + int(lookahead) + 1)
    future = candles[start + 1:end]
    side = (side or 'long').lower()
    mfe = 0.0
    mae = 0.0
    for idx, c in enumerate(future, start=1):
        high = _f(c.get('high'))
        low = _f(c.get('low'))
        if side == 'short':
            mfe = max(mfe, entry - low)
            mae = max(mae, high - entry)
            stop_hit = high >= stop
            target_hit = low <= target
        else:
            mfe = max(mfe, high - entry)
            mae = max(mae, entry - low)
            stop_hit = low <= stop
            target_hit = high >= target
        # Conservative tie handling: if stop and target occur in same candle,
        # count stopped because intrabar order is unknown.
        if stop_hit and target_hit:
            return {'outcome': 'stopped', 'bars_to_outcome': idx, 'mfe': round(mfe, 8), 'mae': round(mae, 8), 'tie': True}
        if stop_hit:
            return {'outcome': 'stopped', 'bars_to_outcome': idx, 'mfe': round(mfe, 8), 'mae': round(mae, 8), 'tie': False}
        if target_hit:
            return {'outcome': 'target', 'bars_to_outcome': idx, 'mfe': round(mfe, 8), 'mae': round(mae, 8), 'tie': False}
    return {'outcome': 'timeout', 'bars_to_outcome': len(future), 'mfe': round(mfe, 8), 'mae': round(mae, 8), 'tie': False}


def _range_proxy(candles, i, lookback=8):
    chunk = candles[max(0, i - lookback):i + 1]
    vals = [_f(c.get('high')) - _f(c.get('low')) for c in chunk]
    vals = [v for v in vals if v > 0]
    return sum(vals) / len(vals) if vals else max(_f(candles[i].get('close')) * 0.01, 1e-9)


def _predicted_status(candles, i):
    if i < 3:
        return 'watch'
    closes = [_f(c.get('close')) for c in candles[max(0, i - 3):i + 1]]
    slope = closes[-1] - closes[0]
    if abs(slope) < max(_f(candles[i].get('close')) * 0.002, 1e-9):
        return 'watch'
    return 'clean' if slope > 0 else 'not_clean'


def run_rolling_simulations(candles, side='long', lookahead=12, stride=5, rr_multiple=2.0):
    """Run simple historical walk-forward simulations over candle windows.

    Each row creates a hypothetical setup at candle i, simulates future bars, and
    records whether the deterministic predicted_status was calibrated.
    """
    out = []
    max_i = len(candles) - int(lookahead) - 1
    for i in range(3, max(3, max_i + 1), max(1, int(stride))):
        entry = _f(candles[i].get('close'))
        risk = _range_proxy(candles, i)
        if side == 'short':
            stop = entry + risk
            target = entry - risk * rr_multiple
        else:
            stop = entry - risk
            target = entry + risk * rr_multiple
        sim = simulate_trade_path(candles, entry, stop, target, side=side, start_index=i, lookahead=lookahead)
        status = _predicted_status(candles, i)
        out.append({
            'index': i,
            'entry': round(entry, 8),
            'stop': round(stop, 8),
            'target': round(target, 8),
            'side': side,
            'predicted_status': status,
            'outcome': sim['outcome'],
            'bars_to_outcome': sim['bars_to_outcome'],
            'mfe': sim['mfe'],
            'mae': sim['mae'],
            'lookahead': lookahead,
        })
    return out


def calibrate_simulations(simulations):
    by_status = defaultdict(Counter)
    for s in simulations:
        by_status[s.get('predicted_status', 'unknown')][s.get('outcome', 'unknown')] += 1
    report = {'mode': 'simulation_calibration', 'total': len(simulations), 'by_predicted_status': {}, 'recommendations': []}
    for status, counts in by_status.items():
        total = sum(counts.values()) or 1
        target_rate = counts.get('target', 0) / total
        stop_rate = counts.get('stopped', 0) / total
        report['by_predicted_status'][status] = {**dict(counts), 'target_rate': round(target_rate, 4), 'stop_rate': round(stop_rate, 4), 'total': total}
        if status == 'clean' and target_rate < 0.45:
            report['recommendations'].append('Clean setups are underperforming in simulation; tighten checklist or require stronger confirmation.')
        if status == 'not_clean' and target_rate > 0.45:
            report['recommendations'].append('Some not_clean setups still reach target; inspect whether checklist is too strict for this regime.')
    if not report['recommendations']:
        report['recommendations'].append('Keep collecting simulations; no strong calibration change yet.')
    return report
