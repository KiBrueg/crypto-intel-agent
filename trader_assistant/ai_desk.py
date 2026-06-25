from __future__ import annotations


def _get(d, *path, default=None):
    cur = d
    for p in path:
        if not isinstance(cur, dict):
            return default
        cur = cur.get(p)
    return default if cur is None else cur


def _trend_counts(snapshot):
    frames = _get(snapshot, 'multi_timeframe', 'frames', default=[]) or []
    counts = {'bullish': 0, 'bearish': 0, 'mixed': 0, 'neutral': 0}
    for f in frames:
        t = f.get('trend', 'neutral')
        counts[t] = counts.get(t, 0) + 1
    return counts


def _pattern_bias(snapshot):
    pats = snapshot.get('classic_patterns') or []
    bullish = [p.get('name') for p in pats if p.get('bias') == 'bullish']
    bearish = [p.get('name') for p in pats if p.get('bias') == 'bearish']
    neutral = [p.get('name') for p in pats if p.get('bias') not in ('bullish', 'bearish')]
    return bullish, bearish, neutral


def _rr_label(snapshot):
    rr = snapshot.get('risk_reward') or {}
    return rr.get('risk_reward_ratio'), ((rr.get('rr_quality') or {}).get('label') or 'n/a')


def _clean_text(items):
    forbidden = ('buy now', 'sell now', 'long now', 'short now', 'покупай', 'продавай')
    out = []
    for item in items:
        text = str(item)
        low = text.lower()
        for bad in forbidden:
            low = low.replace(bad, 'wait for confirmation')
        out.append(text)
    return out


def _build_five_lens_review(symbol, status, score, rr_value, rr_quality, bullish_pats, bearish_pats, counts, ob, pc, conflict):
    """Council-style five-lens review to avoid yes-man and no-man prompting."""
    support = []
    if bullish_pats:
        support.append(f"Bullish support: {', '.join(bullish_pats)} pattern hint(s).")
    if counts.get('bullish', 0):
        support.append(f"{counts.get('bullish')} timeframe(s) currently lean bullish.")
    if 'bid wall' in ' '.join(ob.get('signals') or []):
        support.append("Order book shows bid-side support hint.")
    if not support:
        support.append("No strong supportive evidence yet; idea needs confirmation.")

    against = []
    if bearish_pats:
        against.append(f"Evidence against: {', '.join(bearish_pats)} bearish pattern hint(s).")
    if counts.get('bearish', 0):
        against.append(f"{counts.get('bearish')} timeframe(s) lean bearish.")
    if rr_quality in ('weak', 'low', 'n/a') or (rr_value is not None and rr_value < 1.2):
        against.append(f"Risk/reward argues against forcing the idea: {rr_value} / {rr_quality}.")
    if not against:
        against.append("No major opposing evidence surfaced, but absence of evidence is not confirmation.")

    if conflict:
        contrarian = "Contrarian view: mixed evidence can trap both sides; the best edge may be waiting for resolution instead of choosing early."
    else:
        contrarian = "Contrarian view: ask what would make the obvious thesis wrong before trusting it."

    blockers = pc.get('blockers') or []
    next_checks = pc.get('next_checks') or []
    risk = blockers[0] if blockers else (next_checks[0] if next_checks else "Define invalidation and confirm R/R before considering the setup clean.")

    judge = f"Balanced judge: {symbol} is {status} ({score}/100). "
    judge += "Wait for cleaner confirmation." if status == 'not_clean' else "Keep watching for confirmation and invalidation."

    return [
        {'lens': 'Evidence For', 'advisor': 'Expansionist', 'stance': 'supportive', 'note': ' '.join(support)},
        {'lens': 'Evidence Against', 'advisor': 'Contrarian', 'stance': 'skeptical', 'note': ' '.join(against)},
        {'lens': 'Contrarian View', 'advisor': 'Outsider', 'stance': 'contrarian', 'note': contrarian},
        {'lens': 'Risk/Invalidation', 'advisor': 'Executor', 'stance': 'risk-first', 'note': risk},
        {'lens': 'Balanced Judge', 'advisor': 'Chair', 'stance': status, 'note': judge},
    ]


def build_ai_desk_notes(snapshot):
    """Create deterministic role-based AI desk notes from a dashboard snapshot.

    This is a local orchestrator skeleton: it mimics a small AI trading desk using
    structured project data and safe templates. It does not call an LLM and does
    not issue execution instructions.
    """
    symbol = snapshot.get('symbol', 'UNKNOWN')
    pc = snapshot.get('pro_checklist') or {}
    status = pc.get('status', 'watch')
    score = int(pc.get('readiness_score') or 0)
    rr_value, rr_quality = _rr_label(snapshot)
    counts = _trend_counts(snapshot)
    bullish_pats, bearish_pats, neutral_pats = _pattern_bias(snapshot)
    fg = snapshot.get('fear_greed') or {}
    ob = snapshot.get('order_book') or {}

    mtf_note = f"MTF counts: bullish={counts.get('bullish',0)}, bearish={counts.get('bearish',0)}, mixed={counts.get('mixed',0)}."
    conflict = bool(bullish_pats and bearish_pats) or (counts.get('bullish', 0) and counts.get('bearish', 0))

    cards = []
    cards.append({
        'role': 'Market Brief',
        'verdict': status,
        'key_points': _clean_text([
            f"{symbol} readiness is {score}/100 with checklist status `{status}`.",
            mtf_note,
            f"Sentiment: {fg.get('label', 'n/a')} with {fg.get('confirmation', 'n/a')} confirmation.",
            "Treat sentiment as context only; structure and risk come first.",
        ]),
        'template': 'templates/ai/market_brief.md',
    })

    analysis = snapshot.get('analysis') or {}
    indicators = analysis.get('indicators') or {}
    cards.append({
        'role': 'Technical Analyst',
        'verdict': analysis.get('trend', status),
        'key_points': _clean_text([
            f"Trend read: {analysis.get('trend', 'n/a')} at price {analysis.get('price', 'n/a')}.",
            f"RSI14={indicators.get('rsi_14', 'n/a')}, VWAP={indicators.get('vwap', 'n/a')}, ATR14={indicators.get('atr_14', 'n/a')}.",
            f"Pattern map: bullish={', '.join(bullish_pats) or 'none'}, bearish={', '.join(bearish_pats) or 'none'}.",
            "Technical job: locate structure, levels and invalidation before any thesis.",
        ]),
        'template': 'templates/ai/setup_review.md',
    })

    bull_points = []
    bear_points = []
    if bullish_pats:
        bull_points.append(f"Bullish pattern hints: {', '.join(bullish_pats)}.")
    if counts.get('bullish', 0):
        bull_points.append(f"At least {counts.get('bullish')} timeframe(s) show bullish structure.")
    if 'bid wall' in ' '.join(ob.get('signals') or []):
        bull_points.append("Order book shows bid-side support hint.")
    if bearish_pats:
        bear_points.append(f"Bearish pattern hints: {', '.join(bearish_pats)}.")
    if counts.get('bearish', 0):
        bear_points.append(f"At least {counts.get('bearish')} timeframe(s) show bearish structure.")
    if rr_quality in ('weak', 'low', 'n/a') or (rr_value is not None and rr_value < 1.2):
        bear_points.append(f"Risk/reward is not attractive yet: {rr_value} / {rr_quality}.")
    cards.append({
        'role': 'Bull Case',
        'verdict': 'possible' if bull_points else 'weak',
        'key_points': _clean_text(bull_points or ['No strong bullish evidence surfaced.']),
        'template': 'templates/ai/bull_bear_debate.md',
    })

    cards.append({
        'role': 'Bear Case',
        'verdict': 'possible' if bear_points else 'weak',
        'key_points': _clean_text([
            *(bear_points or ['No strong bearish evidence surfaced.']),
            'Conflict requires a resolving level, not a forced thesis.' if conflict else 'Continue checking for invalidation and failed-break risk.',
        ]),
        'template': 'templates/ai/bull_bear_debate.md',
    })

    risk_verdict = 'acceptable'
    if status == 'not_clean' or rr_quality in ('weak', 'low') or (rr_value is not None and rr_value < 1.0):
        risk_verdict = 'reject'
    elif status == 'watch' or conflict or (rr_value is not None and rr_value < 2.0):
        risk_verdict = 'caution'
    cards.append({
        'role': 'Risk Manager',
        'verdict': risk_verdict,
        'key_points': _clean_text([
            f"R/R check: {rr_value} / {rr_quality}.",
            f"Spread: {ob.get('spread_bps', 'n/a')} bps; order-book signals: {', '.join(ob.get('signals') or ['none'])}.",
            'Reject or wait when R/R is weak, spread is poor, or checklist has blockers.' if risk_verdict == 'reject' else 'Size/location should remain conservative until confirmations improve.',
        ]),
        'template': 'templates/ai/risk_manager.md',
    })

    coach = snapshot.get('trader_coach') or {}
    cards.append({
        'role': 'Trader Coach',
        'verdict': 'teach',
        'key_points': _clean_text([
            coach.get('headline') or f"Current context is {status}.",
            *(coach.get('teaching_points') or []),
            *(pc.get('next_checks') or ['Wait for clearer confirmation before trusting the setup.']),
        ]),
        'template': 'templates/ai/trader_coach.md',
    })

    return {
        'mode': 'ai_desk',
        'symbol': symbol,
        'overall_status': status,
        'readiness_score': score,
        'summary': f"AI Desk synthesis for {symbol}: {status} ({score}/100).",
        'cards': cards,
        'five_lens_review': _build_five_lens_review(symbol, status, score, rr_value, rr_quality, bullish_pats, bearish_pats, counts, ob, pc, conflict),
    }
