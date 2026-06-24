#!/usr/bin/env python3
"""Professional trader context report: indicators, levels, Fibonacci, pivots and order-book imbalance."""
from __future__ import annotations
import argparse
from pathlib import Path
from trader_assistant.binance_public import fetch_klines, fetch_depth
from trader_assistant.technical_analysis import analyze_candles
from trader_assistant.order_book import analyze_order_book
from trader_assistant.pro_report import render_pro_trader_report


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--symbols', default='BTCUSDT,ETHUSDT,SOLUSDT')
    ap.add_argument('--interval', default='1h')
    ap.add_argument('--limit', type=int, default=160)
    ap.add_argument('--out-md', default='reports/pro_trader_report.md')
    ap.add_argument('--out-html', default='reports/pro_trader_report.html')
    args = ap.parse_args()
    analyses = []
    obs = {}
    for symbol in [s.strip().upper() for s in args.symbols.split(',') if s.strip()]:
        candles = fetch_klines(symbol, args.interval, args.limit)
        analysis = analyze_candles(symbol, candles)
        bids, asks = fetch_depth(symbol, limit=50)
        obs[symbol] = analyze_order_book(bids, asks, mid_price=analysis['price'])
        analyses.append(analysis)
    md, html = render_pro_trader_report(analyses, obs)
    Path(args.out_md).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out_md).write_text(md, encoding='utf-8')
    Path(args.out_html).write_text(html, encoding='utf-8')
    print(f'OK pro trader report md={args.out_md} html={args.out_html}')
    print(md)


if __name__ == '__main__':
    main()
