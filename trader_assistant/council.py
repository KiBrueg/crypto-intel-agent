from __future__ import annotations


def _get(d, *path, default=None):
    cur = d
    for p in path:
        if not isinstance(cur, dict):
            return default
        cur = cur.get(p)
    return default if cur is None else cur


def _patterns(snapshot, bias):
    return [p.get('name') for p in (snapshot.get('classic_patterns') or []) if p.get('bias') == bias and p.get('name')]


def _trend_counts(snapshot):
    counts = {'bullish': 0, 'bearish': 0, 'mixed': 0, 'neutral': 0}
    for f in _get(snapshot, 'multi_timeframe', 'frames', default=[]) or []:
        t = f.get('trend', 'neutral')
        counts[t] = counts.get(t, 0) + 1
    return counts


def _rr(snapshot):
    rr = snapshot.get('risk_reward') or {}
    return rr.get('risk_reward_ratio'), ((rr.get('rr_quality') or {}).get('label') or 'n/a')


def _advisor(name, stance, verdict, points, next_actions=None):
    return {
        'advisor': name,
        'stance': stance,
        'verdict': verdict,
        'points': [str(p) for p in points if p],
        'next_actions': [str(a) for a in (next_actions or []) if a],
    }


def _dedupe(items):
    seen = set()
    out = []
    for item in items:
        key = str(item).lower()
        if key not in seen:
            seen.add(key)
            out.append(item)
    return out


def run_council(snapshot):
    """Run a deterministic multi-advisor council over one dashboard snapshot.

    Inspired by council-style prompting: avoid yes-man/no-man bias by forcing
    specialized views, then let a Chair synthesize consensus, disagreement,
    blockers and next actions. No trade commands or execution advice.
    """
    symbol = snapshot.get('symbol', 'UNKNOWN')
    pc = snapshot.get('pro_checklist') or {}
    status = pc.get('status', 'watch')
    score = int(pc.get('readiness_score') or 0)
    rr_value, rr_quality = _rr(snapshot)
    counts = _trend_counts(snapshot)
    bullish = _patterns(snapshot, 'bullish')
    bearish = _patterns(snapshot, 'bearish')
    ob = snapshot.get('order_book') or {}
    signals = ', '.join(ob.get('signals') or ['none'])
    blockers = list(pc.get('blockers') or [])
    warnings = list(pc.get('warnings') or [])
    next_checks = list(pc.get('next_checks') or [])

    advisors = []
    advisors.append(_advisor(
        'Contrarian',
        'find_what_kills_the_idea',
        'skeptical' if (bearish or rr_quality in ('weak', 'low') or status == 'not_clean') else 'watch',
        [
            f"Bearish pattern risk: {', '.join(bearish)}." if bearish else "No clear bearish pattern, but failed-break risk still matters.",
            f"R/R weakness can kill the idea: {rr_value} / {rr_quality}." if rr_quality in ('weak', 'low') or (rr_value is not None and rr_value < 1.2) else None,
            f"Checklist blockers: {', '.join(blockers)}." if blockers else None,
        ],
        next_checks or ['Wait for invalidation/confirmation level to resolve.'],
    ))
    advisors.append(_advisor(
        'First Principles',
        'what_problem_are_we_solving',
        'clarify',
        [
            f"The problem is not predicting {symbol}; it is deciding whether this setup is clean enough to deserve attention.",
            "Primary constraints: structure, invalidation, risk/reward, execution quality and timeframe agreement.",
            f"Current checklist says {status} at {score}/100.",
        ],
        ['State the exact thesis, invalidation and what evidence would change the thesis.'],
    ))
    advisors.append(_advisor(
        'Expansionist',
        'find_hidden_upside_or_optionalities',
        'possible' if bullish or counts.get('bullish', 0) or 'bid wall' in signals else 'weak',
        [
            f"Bullish pattern optionality: {', '.join(bullish)}." if bullish else None,
            f"{counts.get('bullish', 0)} timeframe(s) lean bullish." if counts.get('bullish', 0) else None,
            f"Order-book optionality: {signals}." if signals != 'none' else None,
        ] or ["No strong hidden upside surfaced yet."],
        ['If supportive evidence persists, demand a cleaner trigger rather than chasing.'],
    ))
    advisors.append(_advisor(
        'Outsider',
        'catch_obvious_misses_without_context',
        'caution',
        [
            "Outsider check: do not confuse many dashboard signals with a clean setup.",
            "If bull and bear evidence coexist, the obvious miss is forcing a side before resolution.",
            f"Sentiment is {_get(snapshot, 'fear_greed', 'label', default='n/a')} with {_get(snapshot, 'fear_greed', 'confirmation', default='n/a')} confirmation; it is not enough alone.",
        ],
        ['Reduce the decision to: trigger, invalidation, R/R, and one thing that would prove the thesis wrong.'],
    ))
    advisors.append(_advisor(
        'Executor',
        'what_happens_tomorrow_morning',
        'wait_for_confirmation' if status == 'not_clean' else 'prepare_watch_plan',
        [
            f"Next operational check: {next_checks[0]}" if next_checks else "Define next operational check before acting on the idea.",
            f"Risk manager must reject weak math: {rr_value} / {rr_quality}." if rr_quality in ('weak', 'low') else None,
            f"Execution spread/order-book context: spread={ob.get('spread_bps', 'n/a')} bps, signals={signals}.",
        ],
        next_checks or ['Wait for clearer confirmation and recompute R/R from the new location.'],
    ))

    all_verdicts = [a['verdict'] for a in advisors]
    disagreements = []
    if bullish and bearish:
        disagreements.append('Bullish and bearish pattern evidence coexist.')
    if counts.get('bullish', 0) and counts.get('bearish', 0):
        disagreements.append('Multi-timeframe structure is split between bullish and bearish reads.')
    if any(v in ('possible', 'prepare_watch_plan') for v in all_verdicts) and any(v in ('skeptical', 'wait_for_confirmation') for v in all_verdicts):
        disagreements.append('Council has both opportunity-seeking and risk-first views.')

    chair_verdict = 'clean'
    action_bias = 'prepare_watch_plan'
    if status == 'not_clean' or blockers or rr_quality in ('weak', 'low') or (rr_value is not None and rr_value < 1.2):
        chair_verdict = 'not_clean'
        action_bias = 'wait_for_confirmation'
    elif status == 'watch' or disagreements:
        chair_verdict = 'watch'
        action_bias = 'watch_plan_only'

    chair_blockers = _dedupe(blockers + [p for a in advisors for p in a['points'] if 'R/R' in p or 'risk' in p.lower()][:2])
    chair_next = _dedupe(next_checks + [a for adv in advisors for a in adv['next_actions']])[:5]
    if not chair_next:
        chair_next = ['Wait for cleaner confirmation and recompute setup quality.']

    return {
        'mode': 'council_runner',
        'symbol': symbol,
        'advisors': advisors,
        'consensus': _dedupe([
            f"Checklist status: {status} ({score}/100).",
            f"Risk/reward quality: {rr_value} / {rr_quality}.",
            "No direct execution; use as decision support only.",
        ]),
        'disagreements': disagreements,
        'chair': {
            'advisor': 'Chair',
            'verdict': chair_verdict,
            'action_bias': action_bias,
            'summary': f"Council verdict for {symbol}: {chair_verdict}. Bias: {action_bias}.",
            'blockers': chair_blockers or warnings or ['No hard blocker detected; still require invalidation and R/R check.'],
            'next_actions': chair_next,
        },
    }
