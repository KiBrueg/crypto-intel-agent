#!/usr/bin/env python3
"""Fear/Greed confirmation report with market-structure checks."""
from __future__ import annotations
from pathlib import Path
from crypto_intel_agent_v2 import fetch_markets
from trader_assistant.binance_public import fetch_klines, fetch_depth
from trader_assistant.technical_analysis import analyze_candles
from trader_assistant.order_book import analyze_order_book
from trader_assistant.fear_greed import fetch_fear_greed_index, evaluate_fear_greed, render_fear_greed_report


def context_for(symbol):
    candles = fetch_klines(symbol, '1h', 120)
    a = analyze_candles(symbol, candles)
    bids, asks = fetch_depth(symbol, 50)
    ob = analyze_order_book(bids, asks, mid_price=a['price'])
    vwap = a['indicators']['vwap'] or a['price']
    price_vs_vwap_pct = (a['price'] - vwap) / vwap * 100 if vwap else 0.0
    return {
        'trend': a['trend'],
        'price_vs_vwap_pct': round(price_vs_vwap_pct, 4),
        'rsi_14': a['indicators']['rsi_14'],
        'order_book_imbalance': ob['imbalance'],
        'spread_bps': ob['spread_bps'] or 0,
    }


def market_breadth(per_page=50):
    coins = fetch_markets(per_page=per_page)
    changes = [c.change_24h for c in coins if c.change_24h is not None]
    changes_sorted = sorted(changes)
    median = changes_sorted[len(changes_sorted)//2] if changes_sorted else 0.0
    positive = sum(1 for x in changes if x > 0)
    share_positive = positive / len(changes) if changes else 0.5
    btc_change = next((c.change_24h for c in coins if c.symbol == 'BTC'), 0.0) or 0.0
    top_risk = [c.change_24h for c in coins if c.symbol not in {'BTC','ETH','USDT','USDC'} and c.change_24h is not None][:20]
    risk_median = sorted(top_risk)[len(top_risk)//2] if top_risk else 0.0
    return {
        'share_above_vwap': round(share_positive, 4),  # proxy when broad VWAP set is unavailable
        'median_24h_change': round(median, 4),
        'risk_assets_outperform_btc': risk_median > btc_change,
    }


def main():
    fg = fetch_fear_greed_index()
    result = evaluate_fear_greed(
        index_value=fg['value'],
        btc_context=context_for('BTCUSDT'),
        eth_context=context_for('ETHUSDT'),
        breadth=market_breadth(),
    )
    report = render_fear_greed_report(result)
    out = Path('reports/fear_greed_confirmation_report.md')
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(report, encoding='utf-8')
    print(f'OK fear/greed report={out}')
    print(report)


if __name__ == '__main__':
    main()
