#!/usr/bin/env python3
"""Calculate risk/reward for a trader-supplied entry point.

Examples:
  python risk_reward_calculator.py --symbol BTCUSDT --side long --entry 60000 --stop 59000 --target 63000
  python risk_reward_calculator.py --symbol BTCUSDT --side long --entry 60000  # auto stop/target from levels
"""
from __future__ import annotations
import argparse
from trader_assistant.binance_public import fetch_klines
from trader_assistant.technical_analysis import analyze_candles
from trader_assistant.risk_reward import suggest_risk_reward_from_entry


def fmt(x):
    return 'n/a' if x is None else str(x)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--symbol', default='BTCUSDT')
    ap.add_argument('--side', choices=['long', 'short'], required=True)
    ap.add_argument('--entry', type=float, required=True)
    ap.add_argument('--stop', type=float)
    ap.add_argument('--target', type=float)
    ap.add_argument('--interval', default='1h')
    ap.add_argument('--limit', type=int, default=120)
    args = ap.parse_args()

    candles = fetch_klines(args.symbol, args.interval, args.limit)
    analysis = analyze_candles(args.symbol, candles)
    rr = suggest_risk_reward_from_entry(analysis, entry=args.entry, side=args.side, stop=args.stop, target=args.target)

    print('# Risk/Reward Calculator')
    print('Mode: arithmetic only — not financial advice, no automatic trading.')
    print(f'Symbol: {args.symbol.upper()}')
    print(f'Side: {rr["side"]}')
    print(f'Source: {rr.get("source")}')
    print(f'Entry: {fmt(rr.get("entry"))}')
    print(f'Stop: {fmt(rr.get("stop"))}')
    print(f'Target: {fmt(rr.get("target"))}')
    print(f'Risk per unit: {fmt(rr.get("risk_per_unit"))}')
    print(f'Reward per unit: {fmt(rr.get("reward_per_unit"))}')
    print(f'R/R: {fmt(rr.get("risk_reward_ratio"))}')
    print(f'Valid: {rr.get("valid")}')
    print(f'Invalidation: {rr.get("invalidation")}')
    levels = rr.get('nearest_levels_used')
    if levels:
        print(f'Nearest levels used: below={levels["below"]}, above={levels["above"]}, atr_buffer={levels["atr_buffer"]}')
    warnings = rr.get('warnings') or []
    if warnings:
        print('Warnings:')
        for w in warnings:
            print(f'- {w}')


if __name__ == '__main__':
    main()
