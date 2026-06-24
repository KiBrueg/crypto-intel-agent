from __future__ import annotations
from datetime import datetime, timezone
from .scoring import rank_candidates


def _fmt_score(row, strategy):
    reasons = '; '.join(row.get('reasons', {}).get(strategy, [])[:3]) or 'score-based candidate'
    risk = '; '.join(row.get('risk_flags', [])[:2]) or 'manual confirmation required'
    setup = row.get('setup', {})
    return (
        f"- **{row['symbol']}** score={row['scores'][strategy]:.1f}\n"
        f"  - Why: {reasons}\n"
        f"  - Confirmation: {setup.get('confirmation', 'confirm manually')}\n"
        f"  - Invalidation: {setup.get('invalidation', 'manual invalidation required')}\n"
        f"  - Risk: {risk}"
    )


def render_trader_report(scored, pair_results=None, title='Crypto Trader Assistant Report', limit=3):
    pair_results = pair_results or []
    ts = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')
    lines = [
        f'# {title}', '',
        f'**Time:** {ts}',
        '**Mode:** decision support only — not financial advice, no automatic trading.', '',
        '## Market Regime Snapshot',
        '- Use this report as a shortlist, not as a trade signal.',
        '- Confirm levels, order book, liquidity, news and risk manually.', '',
    ]
    sections = [
        ('scalping', 'Top Scalping Candidates'),
        ('breakout', 'Top Breakout Candidates'),
        ('mean_reversion', 'Top Mean Reversion Candidates'),
    ]
    for key, heading in sections:
        lines += [f'## {heading}']
        candidates = rank_candidates(scored, key, limit=limit)
        lines += [_fmt_score(c, key) for c in candidates] or ['- No candidates above threshold.']
        lines.append('')
    lines += ['## Pair Trading Watchlist']
    if pair_results:
        for p in pair_results[:limit]:
            flags = '; '.join(p.get('risk_flags', [])) or 'manual confirmation required'
            lines.append(f"- **{p['pair']}** z={p['spread_zscore']}, corr={p['correlation']}, hedge={p['hedge_ratio']} — {p['direction']}. Risk: {flags}")
    else:
        lines.append('- No pair results supplied.')
    lines += ['', '## Risk Flags']
    seen = []
    for row in scored:
        for flag in row.get('risk_flags', []):
            item = f"{row['symbol']}: {flag}"
            if item not in seen:
                seen.append(item)
    lines += [f'- {x}' for x in seen[:10]] or ['- No major automatic risk flags.']
    return '\n'.join(lines) + '\n'
