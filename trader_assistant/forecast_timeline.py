from __future__ import annotations

from collections import Counter

from trader_assistant.forecast_outcomes import outcome_badge


def _event_from_row(row):
    outcome = row['verified_outcome'] or 'pending'
    correct = row['correct_direction']
    badge = outcome_badge(outcome, correct)
    return {
        'id': row['id'],
        'created_at': row['created_at'],
        'symbol': row['symbol'],
        'interval': row['interval'],
        'direction': row['predicted_direction'] or 'mixed',
        'status': row['predicted_status'] or 'watch',
        'display_status': badge['display_status'],
        'outcome': outcome,
        'outcome_badge': badge,
        'correct_direction': correct,
        'entry': row['entry'],
        'stop': row['stop'],
        'target': row['target'],
        'readiness_score': row['readiness_score'],
        'council_verdict': row['council_verdict'],
        'smc_bias': row['smc_bias'],
        'verified_at': row['verified_at'],
    }


def build_forecast_timeline(con, limit=12, symbol=None, interval=None):
    where = []
    params = []
    if symbol:
        where.append('symbol = ?')
        params.append(str(symbol).upper())
    if interval:
        where.append('interval = ?')
        params.append(str(interval))
    sql = 'select * from predictions'
    if where:
        sql += ' where ' + ' and '.join(where)
    sql += ' order by id desc limit ?'
    params.append(int(limit))
    rows = con.execute(sql, params).fetchall()
    events = [_event_from_row(r) for r in rows]
    counts = Counter(e['display_status'] for e in events)
    return {
        'mode': 'forecast_timeline',
        'events': events,
        'last_forecast': events[0] if events else None,
        'summary': {
            'total_events': len(events),
            'pending': counts.get('pending', 0),
            'success': counts.get('success', 0),
            'failed': counts.get('failed', 0),
            'other': sum(v for k, v in counts.items() if k not in ('pending', 'success', 'failed')),
        },
    }
