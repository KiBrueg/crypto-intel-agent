# Crypto Trader Assistant — Browser Dashboard Guide

## One-click launch on Windows

Double-click:

```text
launch_dashboard_windows.bat
```

or run manually:

```powershell
cd "C:\\Users\\brueg\\Desktop\\projects\\crypto-intel-agent"
python web_dashboard.py
```

Open:

```text
http://127.0.0.1:8765
```

## What the dashboard shows

- Warm premium UI: modified Stripe style with `#fafaf8`, `#2D2D2D`, `#D2694E` and `#D2691D`; no blue accent dependency.
- Trader-style chart powered by TradingView Lightweight Charts when CDN is available; fallback schematic canvas if it is not. It includes horizontal price grid, right-side price scale, bottom time scale, OHLC header, current-price marker, volume bars, EMA9/EMA21/VWAP overlays, entry/stop/target lines, SMC/liquidity level lines, Auto Learner prediction markers, volume spike markers, overlay summary/legend and detected support/resistance/Fibonacci/pivot levels.
- External reference links: CoinMarketCap page and TradingView chart open in a separate tab instead of embedding/scraping third-party UI.
- Watchlist buttons for major pairs.
- Multi-timeframe context: 15m / 1h / 4h.
- Pro Trader Checklist: readiness score, pass/warn/fail checks, blockers and next checks.
- Trader Coach: teaching points, what to wait for, and optional learning memory from saved setup feedback.
- Setup Journal: save current snapshot, mark outcome, and feed local SQLite stats back into Coach.
- AI Desk Notes: six-pane role-based synthesis using Market Brief, Technical Analyst, Bull Case, Bear Case, Risk Manager and Trader Coach cards.
- Five-Lens Idea Review: council-style anti-bias review with evidence for, evidence against, contrarian/outside view, risk/invalidation and balanced judge.
- Council Verdict: multi-advisor council with Contrarian, First Principles, Expansionist, Outsider, Executor and Chair summary.
- Knowledge Graph: Graphify-style preview of nodes/edges linking setups, patterns, outcomes, council reviews, advisors and blockers.
- Compact Graph Context: token-budgeted graph summary used to give AI only high-signal memory instead of raw rows/candles.
- Simulation Lab: rolling historical simulations that score target/stop/timeout and suggest calibration changes.
- Learning Autopilot: saves current live forecasts, later verifies them against future candles, updates accuracy statistics and shows daemon status/heartbeat, pending/verified counts, last forecast, forecast timeline, canonical outcome badges and detailed forecast cards. The dashboard auto-starts the background learner on launch.
- Macro/RSS News Impact: headline-based indicator for Fed/rates/inflation/geopolitics/oil/regulation shocks with bullish/base/bearish scenarios.
- Smart Money Concepts: liquidity sweeps, FVG/imbalances, break of structure and order-block candidates.
- Candlestick chart with detected levels.
- EMA9 / EMA21 / VWAP / RSI14 / ATR14.
- Entry-based risk/reward calculator.
- Classic price-pattern hints: engulfing, hammer/shooting star, doji, double top/bottom, triangle compression and bull/bear flag watch.
- Fear & Greed confirmation: whether sentiment is confirmed or contradicted by structure.
- Order book spread, imbalance, bid/ask wall notes.
- Export JSON snapshot button.
- Auto-refresh every 60 seconds.

## Configure watchlist

Edit:

```text
dashboard_config.json
```

Example:

```json
{
  "default_symbol": "ETHUSDT",
  "default_interval": "1h",
  "watchlist": ["BTCUSDT", "ETHUSDT", "SOLUSDT", "LINKUSDT"]
}
```

Restart the dashboard after editing.

## Risk/Reward usage

Manual mode:

```text
Entry: 60000
Stop: 59000
Target: 63000
```

Auto mode: enter only `Entry`; the tool infers stop/target from nearby levels, pivots, Fibonacci and ATR buffer.

## Important

This is decision support only. It does not place trades, does not connect exchange API keys and does not provide financial advice.
