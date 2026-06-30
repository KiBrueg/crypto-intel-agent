from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone

from trader_assistant.simulation import simulate_trade_path
from trader_assistant.forecast_outcomes import outcome_badge
from trader_assistant.forecast_due import interval_seconds


def _now():
    return datetime.now(timezone.utc).isoformat()


def _json(obj):
    return json.dumps(obj, ensure_ascii=False, sort_keys=True)


def _direction_from_snapshot(snapshot):
    smc_bias = (snapshot.get('smc') or {}).get('bias')
    trend = (snapshot.get('analysis') or {}).get('trend')
    status = (snapshot.get('pro_checklist') or {}).get('status')
    if smc_bias == 'bullish' or (trend == 'bullish' and status in ('clean', 'watch')):
        return 'up'
    if smc_bias == 'bearish' or trend == 'bearish':
        return 'down'
    return 'mixed'


def create_prediction_from_snapshot(snapshot, horizon_bars=12):
    rr = snapshot.get('risk_reward') or {}
    pc = snapshot.get('pro_checklist') or {}
    council = (snapshot.get('council') or {}).get('chair') or {}
    smc = snapshot.get('smc') or {}
    candles = snapshot.get('candles') or []
    start_ts = candles[-1].get('ts') if candles else None
    features = {
        'readiness_score': pc.get('readiness_score'),
        'checklist_status': pc.get('status'),
        'council_verdict': council.get('verdict'),
        'smc_bias': smc.get('bias'),
        'smc_score': smc.get('score'),
        'rr_quality': (rr.get('rr_quality') or {}).get('label'),
        'rr_ratio': rr.get('risk_reward_ratio'),
        'trend': (snapshot.get('analysis') or {}).get('trend'),
        'patterns': [p.get('name') for p in snapshot.get('classic_patterns', []) if p.get('name')],
    }
    return {
        'symbol': str(snapshot.get('symbol', 'UNKNOWN')).upper(),
        'interval': str(snapshot.get('interval', '1h')),
        'start_ts': start_ts,
        'horizon_bars': int(horizon_bars),
        'predicted_direction': _direction_from_snapshot(snapshot),
        'predicted_status': str(pc.get('status') or council.get('verdict') or 'watch'),
        'entry': rr.get('entry') or (snapshot.get('analysis') or {}).get('price'),
        'stop': rr.get('stop'),
        'target': rr.get('target'),
        'readiness_score': pc.get('readiness_score'),
        'council_verdict': council.get('verdict'),
        'smc_bias': smc.get('bias'),
        'feature_summary': features,
        'snapshot': snapshot,
    }


def save_prediction(con, prediction):
    con.execute('''
        insert into predictions(created_at, symbol, interval, start_ts, horizon_bars, predicted_direction, predicted_status, entry, stop, target, readiness_score, council_verdict, smc_bias, feature_json, snapshot_json)
        values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        _now(), prediction['symbol'], prediction['interval'], prediction.get('start_ts'), int(prediction.get('horizon_bars') or 12),
        prediction.get('predicted_direction') or 'mixed', prediction.get('predicted_status') or 'watch',
        prediction.get('entry'), prediction.get('stop'), prediction.get('target'), prediction.get('readiness_score'),
        prediction.get('council_verdict'), prediction.get('smc_bias'), _json(prediction.get('feature_summary') or {}), _json(prediction.get('snapshot') or {}),
    ))
    con.commit()
    return int(con.execute('select last_insert_rowid()').fetchone()[0])


def _row_to_prediction(row):
    d = dict(row)
    try:
        d['feature_summary'] = json.loads(d.pop('feature_json') or '{}')
    except Exception:
        d['feature_summary'] = {}
    return d


def recent_predictions(con, limit=20):
    return [_row_to_prediction(r) for r in con.execute('select * from predictions order by id desc limit ?', (int(limit),)).fetchall()]


def prediction_markers(con, symbol=None, interval=None, limit=80):
    where = []
    params = []
    if symbol:
        where.append('symbol = ?')
        params.append(str(symbol).upper())
    if interval:
        where.append('interval = ?')
        params.append(str(interval))
    sql = 'select id,symbol,interval,start_ts,predicted_direction,predicted_status,verified_outcome,correct_direction,entry from predictions'
    if where:
        sql += ' where ' + ' and '.join(where)
    sql += ' order by id desc limit ?'
    params.append(int(limit))
    rows = con.execute(sql, params).fetchall()
    markers = []
    for r in rows:
        if r['start_ts'] is None:
            continue
        outcome = r['verified_outcome'] or 'pending'
        direction = r['predicted_direction'] or 'mixed'
        badge = outcome_badge(outcome, r['correct_direction'])
        markers.append({
            'id': r['id'],
            'symbol': r['symbol'],
            'interval': r['interval'],
            'time': int(int(r['start_ts']) / 1000),
            'position': 'belowBar' if direction == 'up' else 'aboveBar',
            'shape': 'arrowUp' if direction == 'up' else ('arrowDown' if direction == 'down' else 'circle'),
            'color': badge['color'],
            'text': f"#{r['id']} {direction} {badge['label']}",
            'outcome': outcome,
            'outcome_badge': badge,
            'entry': r['entry'],
        })
    return list(reversed(markers))


def _find_start_index(candles, start_ts):
    if start_ts is None:
        return max(0, len(candles) - 2)
    idx = None
    for i, c in enumerate(candles):
        if int(c.get('ts') or 0) <= int(start_ts):
            idx = i
    return idx


def verification_fetch_limit(start_ts, interval, horizon_bars, now_ts=None, min_limit=80, max_limit=1000):
    if start_ts is None:
        return int(min_limit)
    try:
        start_ms = int(start_ts)
        if start_ms < 10_000_000_000:
            start_ms *= 1000
        now_ms = int(now_ts if now_ts is not None else datetime.now(timezone.utc).timestamp() * 1000)
        elapsed_bars = max(0, int((now_ms - start_ms) / (interval_seconds(interval) * 1000)))
        needed = elapsed_bars + int(horizon_bars or 0) + 20
        return max(int(min_limit), min(int(max_limit), int(needed)))
    except Exception:
        return int(min_limit)


def verify_open_predictions(con, klines_fetcher):
    rows = con.execute('select * from predictions where verified_outcome is null order by id asc').fetchall()
    verified = 0
    pending = 0
    for row in rows:
        p = dict(row)
        fetch_limit = verification_fetch_limit(p.get('start_ts'), p.get('interval'), p.get('horizon_bars'))
        candles = klines_fetcher(p['symbol'], p['interval'], fetch_limit)
        start_idx = _find_start_index(candles, p['start_ts'])
        if start_idx is None or len(candles) <= start_idx + int(p['horizon_bars']):
            pending += 1
            continue
        result = simulate_trade_path(candles, p['entry'], p['stop'], p['target'], side='long' if p['predicted_direction'] != 'down' else 'short', start_index=start_idx, lookahead=int(p['horizon_bars']))
        end_idx = min(len(candles) - 1, start_idx + int(p['horizon_bars']))
        entry = float(p['entry'] or candles[start_idx].get('close') or 0)
        final_close = float(candles[end_idx].get('close') or entry)
        actual_direction = 'up' if final_close > entry else ('down' if final_close < entry else 'flat')
        correct = None
        if p['predicted_direction'] in ('up', 'down'):
            correct = 1 if actual_direction == p['predicted_direction'] else 0
        con.execute('''
            update predictions set verified_at=?, verified_outcome=?, correct_direction=?, result_json=? where id=?
        ''', (_now(), result['outcome'], correct, _json({**result, 'actual_direction': actual_direction, 'final_close': final_close}), int(p['id'])))
        verified += 1
    con.commit()
    return {'verified': verified, 'pending': pending, 'checked': len(rows)}


def prediction_stats(con):
    rows = con.execute('select predicted_status,predicted_direction,verified_outcome,correct_direction,smc_bias,council_verdict from predictions').fetchall()
    outcomes = Counter()
    statuses = {}
    directions = Counter()
    correct = 0
    correct_counted = 0
    verified = 0
    for r in rows:
        if r['verified_outcome']:
            verified += 1
            outcomes[r['verified_outcome']] += 1
        statuses.setdefault(r['predicted_status'] or 'unknown', Counter())[r['verified_outcome'] or 'pending'] += 1
        directions[r['predicted_direction'] or 'mixed'] += 1
        if r['correct_direction'] is not None:
            correct_counted += 1
            correct += int(r['correct_direction'])
    return {
        'mode': 'learning_autopilot_stats',
        'total': len(rows),
        'verified': verified,
        'pending': len(rows) - verified,
        'direction_accuracy': round(correct / correct_counted, 4) if correct_counted else None,
        'outcomes': dict(outcomes),
        'by_predicted_status': {k: dict(v) for k, v in statuses.items()},
        'predicted_directions': dict(directions),
    }


def run_learning_cycle(con, symbol, interval, side, snapshot_builder, klines_fetcher, horizon_bars=12):
    """Save a fresh forecast, verify old forecasts, and return updated stats."""
    snapshot = snapshot_builder(symbol=symbol, interval=interval, side=side)
    pred_id = save_prediction(con, create_prediction_from_snapshot(snapshot, horizon_bars=int(horizon_bars)))
    verify = verify_open_predictions(con, klines_fetcher)
    stats = prediction_stats(con)
    stats['prediction_id'] = pred_id
    stats['verify_result'] = verify
    stats['recent'] = recent_predictions(con, limit=8)
    return stats
