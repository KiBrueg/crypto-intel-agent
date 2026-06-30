from __future__ import annotations

import json

OUTCOME_META = {
    'pending': {'label': 'pending', 'class': 'warn', 'color': '#D2694E', 'display_status': 'pending'},
    'target': {'label': 'target hit', 'class': 'good', 'color': '#3f7a56', 'display_status': 'success'},
    'stopped': {'label': 'stopped out', 'class': 'bad', 'color': '#b54a3a', 'display_status': 'failed'},
    'stop': {'label': 'stopped out', 'class': 'bad', 'color': '#b54a3a', 'display_status': 'failed'},
    'failed': {'label': 'failed', 'class': 'bad', 'color': '#b54a3a', 'display_status': 'failed'},
    'timeout': {'label': 'timeout', 'class': 'warn', 'color': '#a96f24', 'display_status': 'timeout'},
    'neutral': {'label': 'neutral', 'class': 'muted', 'color': '#766b60', 'display_status': 'neutral'},
}


def normalize_outcome(raw):
    key = str(raw or 'pending').strip().lower()
    if key == 'none' or key == 'null' or not key:
        key = 'pending'
    return 'stopped' if key == 'stop' else key


def outcome_badge(raw, correct_direction=None):
    key = normalize_outcome(raw)
    meta = dict(OUTCOME_META.get(key, {'label': key, 'class': 'muted', 'color': '#766b60', 'display_status': key}))
    if key not in ('pending', 'target', 'stopped', 'failed') and correct_direction is not None:
        if int(correct_direction) == 1:
            meta.update({'class': 'good', 'color': '#3f7a56', 'display_status': 'direction_correct', 'label': f'{key} · direction correct'})
        else:
            meta.update({'class': 'bad', 'color': '#b54a3a', 'display_status': 'direction_wrong', 'label': f'{key} · direction wrong'})
    meta['key'] = key
    return meta


def _parse_result_json(value):
    try:
        return json.loads(value or '{}') if isinstance(value, str) else (value or {})
    except Exception:
        return {}


def classify_forecast_outcome(row):
    getter = row.get if hasattr(row, 'get') else row.__getitem__
    raw = getter('verified_outcome') if hasattr(row, 'get') else row['verified_outcome']
    correct = getter('correct_direction') if hasattr(row, 'get') else row['correct_direction']
    result_raw = getter('result_json') if hasattr(row, 'get') else row['result_json']
    result = _parse_result_json(result_raw)
    return {
        'badge': outcome_badge(raw, correct),
        'actual_direction': result.get('actual_direction'),
        'final_close': result.get('final_close'),
        'bars_held': result.get('bars_held') or result.get('bars_to_outcome'),
        'raw_result': result,
    }
