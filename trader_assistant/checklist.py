from __future__ import annotations


def _num(x, default=0.0):
    try:
        if x is None:
            return default
        return float(x)
    except Exception:
        return default


def _item(name, status, detail, score_delta):
    return {'name': name, 'status': status, 'detail': detail, 'score_delta': score_delta}


def _trend_alignment(frames):
    if not frames:
        return 'unknown', 0, 'No multi-timeframe data available'
    bullish = sum(1 for f in frames if f.get('trend') == 'bullish')
    bearish = sum(1 for f in frames if f.get('trend') == 'bearish')
    mixed = len(frames) - bullish - bearish
    if bullish >= 2 and bearish == 0:
        return 'pass', 18, f'MTF mostly bullish ({bullish}/{len(frames)} bullish)'
    if bearish >= 2 and bullish == 0:
        return 'fail', -18, f'MTF mostly bearish ({bearish}/{len(frames)} bearish)'
    if bullish and bearish:
        return 'warn', -12, f'MTF conflict: {bullish} bullish, {bearish} bearish, {mixed} mixed'
    return 'warn', 0, f'MTF mixed/unclear: {bullish} bullish, {bearish} bearish, {mixed} mixed'


def _rr_check(rr):
    ratio = _num(rr.get('risk_reward_ratio'), None)
    if ratio is None or not rr.get('valid', False):
        return 'fail', -22, 'R/R invalid or missing'
    if ratio < 1:
        return 'fail', -24, f'R/R {ratio} is weak; reward is smaller than risk'
    if ratio < 2:
        return 'warn', -8, f'R/R {ratio} acceptable only with strong confirmation'
    if ratio < 3:
        return 'pass', 16, f'R/R {ratio} strong enough if setup confirms'
    return 'pass', 22, f'R/R {ratio} excellent arithmetic; still verify liquidity'


def _pattern_check(patterns):
    if not patterns:
        return 'warn', 0, 'No high-signal pattern detected; rely on levels/regime'
    bulls = [p for p in patterns if p.get('bias') == 'bullish']
    bears = [p for p in patterns if p.get('bias') == 'bearish']
    if bulls and bears:
        names = ', '.join(p.get('name', '?') for p in patterns[:3])
        return 'warn', -10, f'Conflicting pattern hints: {names}'
    if bulls:
        return 'pass', 8, 'Bullish pattern hint present: ' + ', '.join(p.get('name', '?') for p in bulls[:2])
    if bears:
        return 'warn', -8, 'Bearish pattern hint present: ' + ', '.join(p.get('name', '?') for p in bears[:2])
    return 'warn', 0, 'Neutral pattern context only'


def _book_check(ob):
    spread = _num(ob.get('spread_bps'), 999)
    imb = _num(ob.get('imbalance'), 0)
    signals = ', '.join(ob.get('signals') or [])
    if spread > 8:
        return 'fail', -18, f'Wide spread ({spread} bps); execution quality risk'
    if imb > 0.25:
        return 'pass', 9, f'Order book leans bid-side ({imb}); {signals}'
    if imb < -0.25:
        return 'warn', -9, f'Order book leans ask-side ({imb}); {signals}'
    return 'warn', 0, f'Order book neutral; spread {spread} bps; {signals}'


def _sentiment_check(fg):
    conf = str(fg.get('confirmation', 'neutral'))
    label = str(fg.get('label', 'neutral'))
    if conf == 'confirmed' and 'fear' in label:
        return 'warn', -6, f'Sentiment fear confirmed ({label}); defensive context'
    if conf == 'confirmed' and 'greed' in label:
        return 'warn', -6, f'Sentiment greed confirmed ({label}); crowding risk'
    if conf == 'contradicted':
        return 'warn', -4, 'Sentiment index is contradicted by structure; avoid using it alone'
    return 'pass', 3, f'Sentiment context {conf}/{label}; not a blocker'


def _technical_check(analysis):
    trend = analysis.get('trend', 'mixed')
    ind = analysis.get('indicators', {}) or {}
    rsi = _num(ind.get('rsi_14'), 50)
    if trend == 'bullish' and 35 <= rsi <= 72:
        return 'pass', 12, f'Technical context bullish with RSI {round(rsi,2)}'
    if trend == 'bearish':
        return 'warn', -10, f'Technical context bearish with RSI {round(rsi,2)}'
    if rsi >= 75:
        return 'warn', -8, f'RSI {round(rsi,2)} hot; chasing risk'
    if rsi <= 25:
        return 'warn', -6, f'RSI {round(rsi,2)} washed out; reversal/continuation conflict possible'
    return 'warn', 0, f'Technical context mixed with RSI {round(rsi,2)}'


def build_pro_trader_checklist(snapshot):
    """Compress what an experienced trader would check before acting.

    Output is a decision-support checklist, not a trade instruction.
    """
    checklist = []
    score = 50

    status, delta, detail = _technical_check(snapshot.get('analysis', {}))
    checklist.append(_item('Technical Structure', status, detail, delta)); score += delta

    status, delta, detail = _trend_alignment((snapshot.get('multi_timeframe') or {}).get('frames', []))
    checklist.append(_item('Multi-Timeframe Alignment', status, detail, delta)); score += delta

    status, delta, detail = _rr_check(snapshot.get('risk_reward', {}))
    checklist.append(_item('Risk/Reward', status, detail, delta)); score += delta

    status, delta, detail = _pattern_check(snapshot.get('classic_patterns', []))
    checklist.append(_item('Classic Patterns', status, detail, delta)); score += delta

    status, delta, detail = _book_check(snapshot.get('order_book', {}))
    checklist.append(_item('Order Book / Execution', status, detail, delta)); score += delta

    status, delta, detail = _sentiment_check(snapshot.get('fear_greed', {}))
    checklist.append(_item('Sentiment Confirmation', status, detail, delta)); score += delta

    score = max(0, min(100, int(round(score))))
    blockers = [x['detail'] for x in checklist if x['status'] == 'fail']
    warnings = [x['detail'] for x in checklist if x['status'] == 'warn']
    if blockers or score < 55:
        status = 'not_clean'
        summary = 'Setup is not clean. Wait for clearer alignment or better R/R.'
    elif score >= 75 and not blockers:
        status = 'clean'
        summary = 'Context is relatively clean; still require trigger, execution check and invalidation.'
    else:
        status = 'watch'
        summary = 'Context is watchable but not automatic; confirm trigger and invalidation.'

    next_checks = [
        'Confirm trigger/neckline/level acceptance on the active timeframe.',
        'Re-check spread/order-book flip before execution.',
        'Verify BTC/ETH context does not invalidate the setup.',
        'Use the exact entry, stop and target for final R/R math.',
    ]
    if warnings:
        next_checks.insert(0, 'Resolve warnings: ' + '; '.join(warnings[:2]))

    return {
        'readiness_score': score,
        'status': status,
        'summary': summary,
        'checklist': checklist,
        'blockers': blockers,
        'warnings': warnings,
        'next_checks': next_checks,
    }
