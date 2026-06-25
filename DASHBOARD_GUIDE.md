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

- Watchlist buttons for major pairs.
- Multi-timeframe context: 15m / 1h / 4h.
- Pro Trader Checklist: readiness score, pass/warn/fail checks, blockers and next checks.
- Trader Coach: teaching points, what to wait for, and optional learning memory from saved setup feedback.
- Setup Journal: save current snapshot, mark outcome, and feed local SQLite stats back into Coach.
- AI Desk Notes: six-pane role-based synthesis using Market Brief, Technical Analyst, Bull Case, Bear Case, Risk Manager and Trader Coach cards.
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
