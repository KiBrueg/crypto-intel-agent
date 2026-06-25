# GitHub Research Notes — Trader Dashboard / Checklist Ideas

Searched GitHub for mature open-source trading/technical-analysis projects to avoid inventing every concept from scratch.

## Useful projects / patterns found

- `bukosabino/ta` — popular Python technical-analysis indicator library. Useful reminder: indicator families should be grouped by trend, momentum, volatility and volume.
- `AnalyzerREST/python-tradingview-ta` — TradingView-style technical analysis wrapper. Useful pattern: compress many checks into a concise summary/recommendation-like state, but our tool keeps it as decision support rather than buy/sell instructions.
- `freqtrade/freqtrade` — mature crypto trading-bot ecosystem. Useful architecture lesson: keep strategies, indicators, UI and risk controls separated.
- `freqtrade/freqtrade-strategies` and `freqtrade/technical` — examples of strategy modules and collected indicators. Useful lesson: rules should be testable and modular.
- `freqtrade/frequi` — UI project for trading workflow. Useful product lesson: dashboards need watchlists, summary cards and drill-down details.
- `nardew/talipp` / `kand-ta/kand` — incremental / high-performance TA libraries. Future direction if we need faster live updates.

## What we adopted conceptually

- Separate modules instead of one giant script:
  - indicators / technical context
  - patterns
  - risk-reward
  - sentiment confirmation
  - order-book context
  - pro trader checklist
- Dashboard-first workflow:
  - summary cards first
  - details below
  - explain why each item passed/failed/warned
- Checklist compression:
  - do not show 100 raw indicators
  - convert them into `pass / warn / fail` checks
  - show blockers and next checks

## What we deliberately did not copy

- No exchange API keys.
- No automatic order execution.
- No opaque strategy signal.
- No direct buy/sell recommendation.

The goal remains: **automate the experienced trader's pre-trade checklist**, not replace the trader.
