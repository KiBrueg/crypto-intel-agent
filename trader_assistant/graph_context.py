from __future__ import annotations

import json
from collections import Counter, defaultdict

from trader_assistant.knowledge_graph import build_knowledge_graph


def _safe_json(text, fallback):
    try:
        return json.loads(text or '')
    except Exception:
        return fallback


def _snapshot_features(snapshot):
    rr = snapshot.get('risk_reward') or {}
    pc = snapshot.get('pro_checklist') or {}
    council = (snapshot.get('council') or {}).get('chair') or {}
    smc = snapshot.get('smc') or {}
    return {
        'symbol': str(snapshot.get('symbol') or 'UNKNOWN').upper(),
        'status': pc.get('status') or council.get('verdict') or 'unknown',
        'rr_quality': (rr.get('rr_quality') or {}).get('label') or 'n/a',
        'smc_bias': smc.get('bias') or 'n/a',
        'patterns': [p.get('name') for p in snapshot.get('classic_patterns', []) if p.get('name')],
        'council_verdict': council.get('verdict') or 'unknown',
    }


def _prediction_compact_stats(con, features):
    rows = con.execute('''
        select predicted_status,predicted_direction,verified_outcome,correct_direction,smc_bias,council_verdict,feature_json
        from predictions
        order by id desc limit 500
    ''').fetchall()
    by_status = defaultdict(Counter)
    by_smc = defaultdict(Counter)
    similar = Counter()
    total_verified = 0
    correct = 0
    counted = 0
    for r in rows:
        outcome = r['verified_outcome'] or 'pending'
        by_status[r['predicted_status'] or 'unknown'][outcome] += 1
        by_smc[r['smc_bias'] or 'n/a'][outcome] += 1
        if r['verified_outcome']:
            total_verified += 1
        if r['correct_direction'] is not None:
            counted += 1
            correct += int(r['correct_direction'])
        f = _safe_json(r['feature_json'], {})
        score = 0
        if (r['predicted_status'] or '') == features['status']:
            score += 2
        if (r['smc_bias'] or '') == features['smc_bias']:
            score += 2
        if (f.get('rr_quality') or '') == features['rr_quality']:
            score += 1
        if set(f.get('patterns') or []) & set(features['patterns']):
            score += 1
        if score:
            similar[(outcome, score)] += 1
    return {
        'by_status': {k: dict(v) for k, v in by_status.items()},
        'by_smc': {k: dict(v) for k, v in by_smc.items()},
        'verified': total_verified,
        'direction_accuracy': round(correct / counted, 4) if counted else None,
        'similar': [{'outcome': k[0], 'score': k[1], 'count': v} for k, v in similar.most_common(6)],
    }


def _setup_compact_stats(con, features):
    rows = con.execute('select symbol,outcome,rr_quality,patterns_json,checklist_status from setups order by id desc limit 500').fetchall()
    by_rr = defaultdict(Counter)
    by_status = defaultdict(Counter)
    by_pattern = defaultdict(Counter)
    for r in rows:
        outcome = r['outcome'] or 'unknown'
        by_rr[r['rr_quality'] or 'n/a'][outcome] += 1
        by_status[r['checklist_status'] or 'n/a'][outcome] += 1
        for p in _safe_json(r['patterns_json'], []):
            by_pattern[p][outcome] += 1
    matching_patterns = {p: dict(by_pattern[p]) for p in features['patterns'] if p in by_pattern}
    return {
        'by_rr_quality': {k: dict(v) for k, v in by_rr.items()},
        'by_checklist_status': {k: dict(v) for k, v in by_status.items()},
        'matching_patterns': matching_patterns,
    }


def _line_limited(lines, max_chars):
    out = []
    used = 0
    for line in lines:
        line = str(line).strip()
        if not line:
            continue
        add = len(line) + 1
        if out and used + add > max_chars:
            break
        if add > max_chars:
            line = line[:max(0, max_chars - 3)] + '...'
            add = len(line) + 1
        out.append(line)
        used += add
    return out, used


def build_graph_context(con, snapshot, max_chars=1600):
    """Return compact graph memory suitable for LLM context without raw journal dumps."""
    max_chars = max(350, int(max_chars or 1600))
    features = _snapshot_features(snapshot or {})
    graph = build_knowledge_graph(con, limit=120)
    pred = _prediction_compact_stats(con, features)
    setup = _setup_compact_stats(con, features)
    node_kinds = graph.get('summary', {}).get('node_kinds', {})
    top_rel = ', '.join(f"{r['type']}:{r['count']}" for r in (graph.get('top_relations') or [])[:5]) or 'none'

    lines = [
        f"GRAPH MEMORY: {graph['summary']['node_count']} nodes/{graph['summary']['edge_count']} edges; kinds={node_kinds}; top_relations={top_rel}.",
        f"CURRENT SETUP: symbol={features['symbol']}; status={features['status']}; rr={features['rr_quality']}; smc={features['smc_bias']}; patterns={','.join(features['patterns']) or 'none'}.",
    ]
    rr_counts = setup['by_rr_quality'].get(features['rr_quality'])
    if rr_counts:
        lines.append(f"PAST RR bucket {features['rr_quality']}: {rr_counts}.")
    status_counts = setup['by_checklist_status'].get(features['status'])
    if status_counts:
        lines.append(f"PAST checklist status {features['status']}: {status_counts}.")
    for p, counts in list(setup['matching_patterns'].items())[:4]:
        lines.append(f"PAST pattern {p}: {counts}.")
    pred_status = pred['by_status'].get(features['status'])
    if pred_status:
        lines.append(f"PREDICTION history for status {features['status']}: {pred_status}.")
    smc_counts = pred['by_smc'].get(features['smc_bias'])
    if smc_counts:
        lines.append(f"PREDICTION history for SMC {features['smc_bias']}: {smc_counts}.")
    if pred['direction_accuracy'] is not None:
        lines.append(f"AUTOPILOT direction accuracy={pred['direction_accuracy']} over verified={pred['verified']}.")
    if pred['similar']:
        sim = '; '.join(f"{x['outcome']}@score{x['score']}:{x['count']}" for x in pred['similar'][:4])
        lines.append(f"SIMILAR forecast outcomes: {sim}.")

    hints = []
    fail_like = {'failed', 'stopped'}
    if rr_counts and sum(rr_counts.get(x, 0) for x in fail_like) >= rr_counts.get('target', 0):
        hints.append(f"Caution: rr_quality={features['rr_quality']} historically leans failed/stopped vs target.")
    if status_counts and sum(status_counts.get(x, 0) for x in fail_like) >= status_counts.get('target', 0):
        hints.append(f"Do not over-trust {features['status']} status; past outcomes are not clearly positive.")
    if smc_counts and sum(smc_counts.get(x, 0) for x in fail_like) > smc_counts.get('target', 0):
        hints.append(f"SMC bias {features['smc_bias']} has weak verified follow-through in stored forecasts.")
    if not hints:
        hints.append('Insufficient verified graph memory; keep collecting forecasts before strong calibration changes.')
    for h in hints[:4]:
        lines.append('CALIBRATION HINT: ' + h)

    context_lines, char_count = _line_limited(lines, max_chars)
    return {
        'mode': 'compact_graph_context',
        'token_strategy': 'summarized_graph_memory_no_raw_rows',
        'char_budget': max_chars,
        'char_count': char_count,
        'features': features,
        'context_lines': context_lines,
        'calibration_hints': hints[:4],
        'graph_summary': graph.get('summary', {}),
    }
