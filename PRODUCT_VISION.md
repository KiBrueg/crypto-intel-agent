# Product Vision — Pro Trader Workflow Automation

## Core idea

The product should do what a real experienced trader would manually check on a chart — only faster, more consistently and before the trader has to remember to check it.

It is not a buy/sell bot. It is a **pre-trade co-pilot** that compresses chart-reading, context checks, risk math and market structure into one usable dashboard.

## Product promise

```text
Before the trader asks "should I check this?", the assistant has already checked it.
```

## What a pro trader checks manually

A serious trader usually scans:

- market regime: trend, chop, high-volatility, risk-on/risk-off
- BTC/ETH context before alt decisions
- multiple timeframes: 15m / 1h / 4h / 1d
- support/resistance and obvious liquidity zones
- VWAP / EMA alignment
- RSI/ATR for momentum and volatility
- Fibonacci and pivot reference levels
- classic price-action patterns
- order book: spread, depth, bid/ask imbalance
- sentiment context such as Fear & Greed, but only if confirmed by structure
- exact entry/stop/target risk-reward math
- invalidation: what would make the idea wrong

The dashboard should keep expanding until these checks are done automatically and displayed as a shortlist of useful observations.

## Design rules

1. Never say "buy" or "sell" as an instruction.
2. Show context, confirmation, contradiction and invalidation.
3. Treat patterns as prompts to investigate, not signals.
4. Calculate risk/reward from the trader's actual entry when given.
5. Prefer short, high-signal summaries over giant scanner tables.
6. Save/export snapshots so the trader can review what the assistant saw.
7. Add automation only after the logic is testable and explainable.

## North-star user experience

The trader opens the dashboard and immediately sees:

```text
What is the market regime?
Which timeframes agree/disagree?
Which levels matter now?
Which pattern hints are visible?
Is sentiment real or stale/fake?
Does the order book support or contradict the setup?
If I enter here, is R/R acceptable?
What invalidates this idea?
```

This is the project’s key identity: **experienced-trader checklist automation**.
