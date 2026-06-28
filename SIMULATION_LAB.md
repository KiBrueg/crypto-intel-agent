# Simulation Lab and Calibration Loop

A self-improving trading assistant is realistic if "learning" means a controlled calibration loop, not a magic model that rewrites itself.

The loop:

```text
1. generate a setup/verdict
2. simulate or wait for future candles
3. score what happened: target / stopped / timeout
4. compare outcome vs checklist/council prediction
5. calibrate thresholds/rules
6. repeat on more market regimes
```

## Current prototype

File:

```text
trader_assistant/simulation.py
```

API:

```text
GET /api/simulation?symbol=BTCUSDT&interval=1h&side=long
```

Dashboard section:

```text
Simulation Lab
```

Button:

```text
Run historical simulation
```

## What it simulates

The current version runs rolling historical windows over candle data:

- creates a hypothetical entry at a candle close
- derives a simple volatility-based stop
- derives target as R multiple
- walks forward N candles
- records whether target or stop was hit first
- groups outcomes by predicted status

## Why this matters

This turns subjective assistant output into measurable claims:

```text
when status=clean, did target happen often enough?
when status=not_clean, was caution justified?
when R/R is weak, did stop/timeout dominate?
```

## Calibration examples

The report keeps multiple scenarios instead of one brittle recommendation:

```text
bullish — assume risk-on/liquidity regime
base    — assume mixed/choppy regime
bearish — assume risk-off/false-break regime
```

If clean setups underperform:

```text
tighten checklist
raise readiness threshold
require stronger MTF agreement
require better R/R
```

If not_clean setups often hit target:

```text
check whether rules are too strict for this regime
inspect missed opportunities
split market regimes
```

## Realistic path to self-learning

1. deterministic simulation scoring
2. saved setup/council outcomes
3. graph memory of patterns/outcomes/verdicts
4. calibration reports
5. rules/threshold updates with tests
6. optional ML model later, trained on structured features

The safe version is not autonomous trading. It is a self-calibrating decision-support system.
