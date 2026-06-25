from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

FORBIDDEN_WORDS = ('buy', 'sell', 'покуп', 'прода')


def _safe(text):
    # Keep the coach as decision support, not direct trade instruction.
    s = str(text or '')
    replacements = {
        'buy': 'act', 'sell': 'act', 'Buy': 'Act', 'Sell': 'Act',
        'покуп': 'действ', 'прода': 'действ',
    }
    low = s.lower()
    for bad in FORBIDDEN_WORDS:
        if bad in low:
            return 'Use this as context only; require confirmation, invalidation and risk control.'
    return s


def _pattern_names(snapshot):
    return [p.get('name', '') for p in snapshot.get('classic_patterns', []) if p.get('name')]


def load_learning_stats(path='reports/setup_learning.jsonl'):
    path = Path(path)
    stats = {
        'total': 0,
        'patterns': {},
        'rr_quality': {},
        'symbols': {},
    }
    counters = {
        'patterns': defaultdict(Counter),
        'rr_quality': defaultdict(Counter),
        'symbols': defaultdict(Counter),
    }
    if not path.exists():
        return stats
    for line in path.read_text(encoding='utf-8').splitlines():
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except Exception:
            continue
        outcome = str(row.get('outcome', 'unknown')).lower()
        stats['total'] += 1
        for p in row.get('patterns', []) or []:
            counters['patterns'][str(p)][outcome] += 1
        if row.get('rr_quality'):
            counters['rr_quality'][str(row['rr_quality'])][outcome] += 1
        if row.get('symbol'):
            counters['symbols'][str(row['symbol']).upper()][outcome] += 1
    for group, counter in counters.items():
        stats[group] = {k: dict(v) for k, v in counter.items()}
    return stats


def record_setup_feedback(path, record):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    row = dict(record)
    row.setdefault('recorded_at', datetime.now(timezone.utc).isoformat())
    with path.open('a', encoding='utf-8') as f:
        f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + '\n')
    return row


def _headline(snapshot):
    checklist = snapshot.get('pro_checklist', {})
    status = checklist.get('status', 'watch')
    score = checklist.get('readiness_score', 'n/a')
    if status == 'not_clean':
        return f'Context is not clean yet ({score}/100). Treat this as a wait-and-verify situation.'
    if status == 'clean':
        return f'Context is relatively clean ({score}/100), but still needs trigger + invalidation discipline.'
    return f'Context is watchable ({score}/100), but not automatic. Let the market confirm.'


def _teaching_points(snapshot):
    points = []
    checklist = snapshot.get('pro_checklist', {})
    rr = snapshot.get('risk_reward', {})
    ratio = rr.get('risk_reward_ratio')
    if ratio is not None:
        if float(ratio) < 1:
            points.append('Risk/reward is weak: the potential reward is smaller than the defined risk. A pro usually waits for a better location or a clearer target.')
        elif float(ratio) < 2:
            points.append('R/R is acceptable only if the setup has strong confirmation. Weak confirmation plus average R/R is usually not enough.')
        else:
            points.append('R/R arithmetic is strong enough to inspect further, but it still needs trend, level and execution confirmation.')
    blockers = checklist.get('blockers') or []
    if blockers:
        points.append('Blockers matter more than attractive chart shapes: ' + '; '.join(blockers[:2]))
    warnings = checklist.get('warnings') or []
    if warnings:
        points.append('Warnings show where a pro would slow down: ' + '; '.join(warnings[:2]))
    patterns = snapshot.get('classic_patterns', [])
    bulls = [p for p in patterns if p.get('bias') == 'bullish']
    bears = [p for p in patterns if p.get('bias') == 'bearish']
    if bulls and bears:
        points.append('Pattern conflict is information: one side reacted, but another side rejected. Wait for the level that resolves the conflict.')
    elif patterns:
        points.append('Pattern hints are prompts, not signals. Confirm with level acceptance, volume/order book and multi-timeframe context.')
    fg = snapshot.get('fear_greed', {})
    if fg.get('confirmation') in ('mixed', 'contradicted'):
        points.append('Sentiment is not enough by itself: when Fear/Greed is mixed or contradicted, structure has higher priority.')
    return [_safe(x) for x in points[:6]] or ['No strong lesson detected. Focus on level, invalidation and R/R before acting.']


def _what_to_wait_for(snapshot):
    waits = []
    checklist = snapshot.get('pro_checklist', {})
    waits.extend((checklist.get('next_checks') or [])[:3])
    rr = snapshot.get('risk_reward', {})
    if rr.get('risk_reward_ratio') is not None and float(rr.get('risk_reward_ratio') or 0) < 1.5:
        waits.append('Wait for either a better entry location, a closer invalidation level or a farther realistic target.')
    frames = (snapshot.get('multi_timeframe') or {}).get('frames', [])
    trends = {f.get('trend') for f in frames}
    if 'bullish' in trends and 'bearish' in trends:
        waits.append('Wait for multi-timeframe conflict to resolve instead of forcing a thesis.')
    if snapshot.get('classic_patterns'):
        waits.append('Wait for the pattern trigger/neckline to be accepted, not just touched.')
    return [_safe(x) for x in waits[:6]]


def _learning_notes(snapshot, learning_stats):
    notes = []
    stats = learning_stats or {}
    pat_stats = stats.get('patterns', {})
    for name in _pattern_names(snapshot):
        s = pat_stats.get(name, {})
        failed = int(s.get('failed', 0))
        worked = int(s.get('worked', 0)) + int(s.get('target', 0))
        if failed >= 2 and failed >= worked:
            notes.append(f'Learning memory: {name} has failed {failed} time(s) in saved feedback. Demand stronger confirmation next time.')
    rrq = (snapshot.get('risk_reward', {}).get('rr_quality') or {}).get('label')
    rr_stats = stats.get('rr_quality', {}).get(str(rrq), {}) if rrq else {}
    if rrq and int(rr_stats.get('failed', 0)) >= 2:
        notes.append(f'Learning memory: setups tagged {rrq} often failed in saved feedback. Treat this quality bucket conservatively.')
    return [_safe(x) for x in notes[:4]]


def build_trader_coach(snapshot, learning_stats=None):
    """Build teaching/coaching hints from the dashboard snapshot.

    The coach explains what matters and what to wait for. It does not issue trade commands.
    """
    coach = {
        'mode': 'teaching_coach',
        'headline': _safe(_headline(snapshot)),
        'explain_like_pro': _safe('A pro first asks whether the context is clean, where the idea is invalidated, and whether the exact entry has enough R/R. The assistant highlights the weak links before you have to remember them.'),
        'teaching_points': _teaching_points(snapshot),
        'what_to_wait_for': _what_to_wait_for(snapshot),
        'learning_notes': _learning_notes(snapshot, learning_stats or {}),
    }
    return coach
