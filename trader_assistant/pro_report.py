from __future__ import annotations
import html


def _chart_svg(analysis, width=760, height=280):
    candles = analysis.get('candles', [])[-80:]
    if not candles:
        return '<svg></svg>'
    highs = [float(c['high']) for c in candles]
    lows = [float(c['low']) for c in candles]
    max_p, min_p = max(highs), min(lows)
    span = max(max_p - min_p, 1e-9)
    pad = 24
    inner_w = width - pad * 2
    inner_h = height - pad * 2
    def x(i): return pad + i * inner_w / max(len(candles) - 1, 1)
    def y(p): return pad + (max_p - float(p)) / span * inner_h
    elems = [f'<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">', '<rect width="100%" height="100%" fill="#07101f" rx="18"/>']
    # level lines: fib, pivots, support/resistance
    level_items = []
    for group in ['support_resistance']:
        for lv in analysis['levels'].get(group, [])[:8]:
            level_items.append((lv, '#334155', 'SR'))
    for name, lv in analysis['levels'].get('fibonacci', {}).items():
        if name in {'0.382', '0.500', '0.618'}:
            level_items.append((lv, '#7c3aed', 'F' + name))
    for name, lv in analysis['levels'].get('pivots', {}).items():
        if name in {'pivot', 'r1', 's1'}:
            level_items.append((lv, '#0891b2', name.upper()))
    for lv, color, label in level_items:
        yy = y(lv)
        if pad <= yy <= height - pad:
            elems.append(f'<line x1="{pad}" x2="{width-pad}" y1="{yy:.2f}" y2="{yy:.2f}" stroke="{color}" stroke-width="1" stroke-dasharray="4 4"/>')
            elems.append(f'<text x="{width-pad+4}" y="{yy+4:.2f}" fill="{color}" font-size="10">{html.escape(label)}</text>')
    body_w = max(3, inner_w / len(candles) * 0.55)
    for i, c in enumerate(candles):
        xx = x(i)
        o, h, l, cl = map(float, [c['open'], c['high'], c['low'], c['close']])
        color = '#22c55e' if cl >= o else '#ef4444'
        elems.append(f'<line x1="{xx:.2f}" x2="{xx:.2f}" y1="{y(h):.2f}" y2="{y(l):.2f}" stroke="{color}" stroke-width="1"/>')
        top, bot = min(y(o), y(cl)), max(y(o), y(cl))
        elems.append(f'<rect x="{xx-body_w/2:.2f}" y="{top:.2f}" width="{body_w:.2f}" height="{max(1, bot-top):.2f}" fill="{color}" opacity="0.85"/>')
    elems.append(f'<text x="{pad}" y="18" fill="#e5e7eb" font-size="13">{html.escape(analysis["symbol"])} pro context chart</text>')
    elems.append('</svg>')
    return ''.join(elems)


def _analysis_md(a, ob=None):
    ind = a['indicators']
    levels = a['levels']
    ob = ob or {}
    lines = [
        f"## {a['symbol']} — Professional Trader Context",
        f"- Price: `{a['price']}`",
        f"- Trend: `{a['trend']}`",
        f"- EMA9/EMA21: `{ind['ema_9']}` / `{ind['ema_21']}`",
        f"- RSI14: `{ind['rsi_14']}` | ATR14: `{ind['atr_14']}` | VWAP: `{ind['vwap']}`",
        f"- Nearest levels: {', '.join(str(x) for x in levels['nearest'])}",
        f"- Fibonacci 0.382/0.5/0.618: `{levels['fibonacci'].get('0.382')}`, `{levels['fibonacci'].get('0.500')}`, `{levels['fibonacci'].get('0.618')}`",
        f"- Pivots P/R1/S1: `{levels['pivots'].get('pivot')}`, `{levels['pivots'].get('r1')}`, `{levels['pivots'].get('s1')}`",
    ]
    if ob:
        lines += [
            f"- Order book spread: `{ob.get('spread_bps')}` bps | imbalance: `{ob.get('imbalance')}`",
            f"- Order book signals: {', '.join(ob.get('signals') or ['none'])}",
        ]
    lines += ['', '### Setup notes']
    lines += [f'- {x}' for x in a['setup_notes']]
    lines += ['', '### Confirmation checklist', '- price accepts above/below the relevant level', '- volume does not fade immediately', '- order book does not flip against the idea', '- BTC/ETH context does not invalidate the setup']
    lines += ['', '### Invalidation', '- reclaim/failure of the level being watched', '- RSI/EMA/VWAP context flips', '- spread/liquidity deteriorates', '- correlation or BTC/ETH context breaks']
    lines += ['', '### Risk notes']
    lines += [f'- {x}' for x in a['risk_notes']]
    return '\n'.join(lines)


def render_pro_trader_report(analyses, order_books=None, title='Crypto Pro Trader Assistant'):
    order_books = order_books or {}
    md = [f'# {title}', '', '**Mode:** decision support only — not financial advice, no automatic trading.', '', 'This report compresses the things a pro trader would inspect manually: trend, VWAP/EMA, RSI/ATR, support/resistance, Fibonacci retracements, pivots, and order-book imbalance.', '']
    html_parts = ['<!doctype html><html><head><meta charset="utf-8"><title>Crypto Pro Trader Assistant</title><style>body{background:#050914;color:#e5e7eb;font:15px Arial;padding:28px}main{max-width:1060px;margin:auto}section{background:#0f172a;border:1px solid #1e293b;border-radius:18px;padding:22px;margin:18px 0}pre{white-space:pre-wrap}h1,h2{color:#93c5fd}</style></head><body><main><h1>Crypto Pro Trader Assistant</h1><p>Decision support only — not financial advice.</p>']
    for a in analyses:
        ob = order_books.get(a['symbol'])
        md.append(_analysis_md(a, ob))
        md.append('')
        html_parts.append('<section>')
        html_parts.append(_chart_svg(a))
        html_parts.append('<pre>' + html.escape(_analysis_md(a, ob)) + '</pre>')
        html_parts.append('</section>')
    html_parts.append('</main></body></html>')
    return '\n'.join(md), ''.join(html_parts)
