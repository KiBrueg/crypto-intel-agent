from __future__ import annotations
import json
import urllib.request


def classify_fear_greed(value: int | float) -> str:
    v = float(value)
    if v <= 24:
        return 'extreme fear'
    if v <= 44:
        return 'fear'
    if v <= 55:
        return 'neutral'
    if v <= 75:
        return 'greed'
    return 'extreme greed'


def fetch_fear_greed_index():
    """Fetch Alternative.me Crypto Fear & Greed Index. Public endpoint, no key."""
    req = urllib.request.Request('https://api.alternative.me/fng/?limit=1&format=json', headers={'User-Agent': 'crypto-trader-assistant/1.0'})
    with urllib.request.urlopen(req, timeout=25) as r:
        data = json.loads(r.read().decode('utf-8'))
    item = (data.get('data') or [{}])[0]
    return {
        'value': int(item.get('value')),
        'classification': str(item.get('value_classification') or classify_fear_greed(int(item.get('value')))),
        'timestamp': item.get('timestamp'),
    }


def _num(d, key, default=0.0):
    try:
        return default if d.get(key) is None else float(d.get(key))
    except Exception:
        return default


def _trend_points(ctx):
    trend = str(ctx.get('trend', 'mixed')).lower()
    pts = 0
    evidence = []
    if trend == 'bullish':
        pts += 2; evidence.append('trend is bullish')
    elif trend == 'bearish':
        pts -= 2; evidence.append('trend is bearish')
    pv = _num(ctx, 'price_vs_vwap_pct')
    if pv > 1:
        pts += 2; evidence.append('price above VWAP')
    elif pv < -1:
        pts -= 2; evidence.append('below VWAP')
    r = _num(ctx, 'rsi_14', 50)
    if r >= 70:
        pts += 1; evidence.append('RSI is hot')
    elif r <= 30:
        pts -= 1; evidence.append('RSI is washed out')
    imb = _num(ctx, 'order_book_imbalance')
    if imb > 0.25:
        pts += 1; evidence.append('book depth leans bid-side')
    elif imb < -0.25:
        pts -= 1; evidence.append('book depth leans ask-side')
    spread = _num(ctx, 'spread_bps', 0)
    if spread > 20:
        evidence.append('spread is wide; sentiment signal is less reliable')
    return pts, evidence


def evaluate_fear_greed(index_value, btc_context, eth_context=None, breadth=None):
    label = classify_fear_greed(index_value)
    eth_context = eth_context or {}
    breadth = breadth or {}
    score = 0
    evidence = []
    btc_score, btc_e = _trend_points(btc_context)
    eth_score, eth_e = _trend_points(eth_context)
    score += btc_score * 1.4 + eth_score
    evidence += ['BTC ' + x for x in btc_e]
    evidence += ['ETH ' + x for x in eth_e]

    share_above = _num(breadth, 'share_above_vwap', 0.5)
    median_chg = _num(breadth, 'median_24h_change', 0.0)
    risk_out = bool(breadth.get('risk_assets_outperform_btc', False))
    if share_above >= 0.6:
        score += 2; evidence.append('market breadth is constructive')
    elif share_above <= 0.35:
        score -= 2; evidence.append('market breadth is weak')
    if median_chg >= 2:
        score += 1; evidence.append('median 24h market change is positive')
    elif median_chg <= -2:
        score -= 1; evidence.append('median 24h market change is negative')
    if risk_out:
        score += 1; evidence.append('risk assets outperform BTC')
    else:
        evidence.append('risk assets do not clearly outperform BTC')

    if label in ('fear', 'extreme fear'):
        if score <= -3:
            confirmation = 'confirmed'
            interpretation = 'Index says fear and market structure confirms defensive conditions.'
        elif score >= 3:
            confirmation = 'contradicted'
            interpretation = 'Index says fear, but market structure is improving; fear may be stale or exaggerated.'
        else:
            confirmation = 'mixed'
            interpretation = 'Index says fear, but confirmations are mixed; treat it as context, not a standalone signal.'
    elif label in ('greed', 'extreme greed'):
        if score >= 3:
            confirmation = 'confirmed'
            interpretation = 'Index says greed and market structure confirms risk-on conditions.'
        elif score <= -3:
            confirmation = 'contradicted'
            interpretation = 'Index says greed, but market structure is weak; greed may be stale or vulnerable.'
        else:
            confirmation = 'mixed'
            interpretation = 'Index says greed, but confirmations are mixed; avoid reading the index in isolation.'
    else:
        confirmation = 'neutral'
        interpretation = 'Index is neutral; use structure, levels, and liquidity as primary context.'
    return {
        'index_value': int(index_value),
        'label': label,
        'confirmation': confirmation,
        'score': round(score, 3),
        'evidence': evidence,
        'interpretation': interpretation,
        'btc_context': btc_context,
        'eth_context': eth_context,
        'breadth': breadth,
    }


def render_fear_greed_report(result):
    lines = [
        '# Fear/Greed Confirmation Report', '',
        '**Mode:** market context only — not financial advice, no automatic trading.', '',
        f"- Index: `{result['index_value']}` / `{result['label']}`",
        f"- Confirmation: `{result['confirmation']}`",
        f"- Structure score: `{result['score']}`",
        f"- Interpretation: {result['interpretation']}", '',
        '## Evidence',
    ]
    lines += [f'- {x}' for x in result.get('evidence', [])]
    lines += ['', '## How to use', '- Treat the index as a sentiment input, not a command.', '- Require alignment with VWAP/EMA, breadth, liquidity, and order-book context.', '- If the index and structure disagree, mark it as stale/exaggerated sentiment and inspect manually.']
    return '\n'.join(lines) + '\n'
