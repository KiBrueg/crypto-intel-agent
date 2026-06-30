from __future__ import annotations

from trader_assistant.forecast_outcomes import classify_forecast_outcome
from trader_assistant.forecast_due import forecast_due_status


def _row_to_forecast(row):
    return {
        'id': row['id'],
        'created_at': row['created_at'],
        'symbol': row['symbol'],
        'interval': row['interval'],
        'direction': row['predicted_direction'] or 'mixed',
        'status': row['predicted_status'] or 'watch',
        'outcome': row['verified_outcome'] or 'pending',
        'correct_direction': row['correct_direction'],
        'verified_at': row['verified_at'],
        'horizon_bars': row['horizon_bars'],
    }


def build_forecast_detail(con, forecast_id):
    row = con.execute('select * from predictions where id = ?', (int(forecast_id),)).fetchone()
    if not row:
        return {'mode': 'forecast_detail', 'error': 'not_found', 'forecast_id': int(forecast_id)}
    forecast = _row_to_forecast(row)
    due = forecast_due_status(row['start_ts'], row['horizon_bars'], row['interval'], row['verified_at'])
    outcome_summary = classify_forecast_outcome(dict(row))
    forecast['due'] = due
    forecast['outcome_badge'] = outcome_summary['badge']
    rr = None
    try:
        if row['entry'] is not None and row['stop'] is not None and row['target'] is not None:
            risk = abs(float(row['entry']) - float(row['stop']))
            reward = abs(float(row['target']) - float(row['entry']))
            rr = reward / risk if risk else None
    except Exception:
        rr = None
    risk_plan = {
        'entry': row['entry'],
        'stop': row['stop'],
        'target': row['target'],
        'risk_reward_ratio': rr,
    }
    context = {
        'readiness_score': row['readiness_score'],
        'council_verdict': row['council_verdict'],
        'smc_bias': row['smc_bias'],
    }
    result = {
        'verified_outcome': row['verified_outcome'],
        'correct_direction': row['correct_direction'],
        'verified_at': row['verified_at'],
        'outcome_badge': outcome_summary['badge'],
        'actual_direction': outcome_summary.get('actual_direction'),
        'final_close': outcome_summary.get('final_close'),
        'bars_held': outcome_summary.get('bars_held'),
    }
    explanation = [
        f"Forecast #{row['id']} expected {forecast['direction']} on {row['symbol']} {row['interval']} with status {forecast['status']}.",
        f"Risk plan: entry {row['entry']}, stop {row['stop']}, target {row['target']}, R/R {rr}.",
        f"Context: readiness {row['readiness_score']}, council {row['council_verdict']}, SMC {row['smc_bias']}.",
        f"Outcome: {forecast['outcome']}.",
    ]
    return {
        'mode': 'forecast_detail',
        'forecast': forecast,
        'risk_plan': risk_plan,
        'context': context,
        'result': result,
        'explanation': explanation,
    }
