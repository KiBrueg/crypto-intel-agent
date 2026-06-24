#!/usr/bin/env python3
"""Generate a trader-focused decision-support report from CoinGecko market data."""
from __future__ import annotations
import argparse
from pathlib import Path
from crypto_intel_agent_v2 import fetch_markets
from trader_assistant.scoring import score_market
from trader_assistant.trader_report import render_trader_report


STABLE_OR_WRAPPED = {'USDT', 'USDC', 'DAI', 'FDUSD', 'TUSD', 'USDE', 'USD1', 'WETH', 'WBTC', 'STETH'}


def coin_to_row(c):
    # CoinGecko does not provide live spread/depth. Use conservative defaults so
    # the assistant does not overstate scalping quality without order-book data.
    return {
        'symbol': c.symbol + 'USDT',
        'price': c.price,
        'change_24h': c.change_24h or 0.0,
        'volume_24h': c.volume_24h or 0.0,
        'market_cap': c.market_cap or 0.0,
        'range_pct': c.range_pct or abs(c.change_24h or 0.0),
        'vol_to_mcap': c.vol_to_mcap or 0.0,
        'spread_bps': 12.0,
        'liquidity_usd': min(c.volume_24h or 0.0, 25_000_000),
        'near_high_pct': max(0.0, (c.high_24h or c.price or 0.0) - (c.price or 0.0)) / (c.price or 1.0) * 100,
        'distance_from_mean_pct': abs(c.change_24h or 0.0) / 2,
        'trend_5': (c.change_24h or 0.0) / 4,
        'trend_20': c.change_24h or 0.0,
        'volume_zscore': min((c.vol_to_mcap or 0.0) * 10, 5.0),
        'btc_relative_strength': 0.0,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--per-page', type=int, default=60)
    ap.add_argument('--out', default='reports/trader_assistant_report.md')
    args = ap.parse_args()
    coins = [c for c in fetch_markets(per_page=args.per_page) if c.symbol not in STABLE_OR_WRAPPED]
    rows = [coin_to_row(c) for c in coins]
    scored = score_market(rows)
    report = render_trader_report(scored)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(report, encoding='utf-8')
    print(f'OK trader report={args.out}')
    print(report)


if __name__ == '__main__':
    main()
