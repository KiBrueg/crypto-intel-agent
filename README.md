# Crypto Intel Agent

Automated market monitoring tool for CoinGecko and DexScreener data.

Collects public market data → detects unusual price/volume/liquidity movements → generates HTML and Markdown reports.

**Core product idea:** do what a real experienced trader would manually check on a chart — market regime, levels, patterns, order book, sentiment confirmation, multi-timeframe context and risk/reward — only faster, more consistently, and before the trader has to remember to check it.

See `PRODUCT_VISION.md` for the north-star workflow.
See `GITHUB_RESEARCH_NOTES.md` for open-source projects/concepts used as architecture inspiration.
See `TRADER_COACH.md` for the teaching/learning prompt layer.
See `SETUP_JOURNAL.md` for the local outcome-tracking loop.
See `AI_TRADING_AGENT_TEMPLATES.md` and `templates/ai/` for reusable AI prompt/agent templates inspired by GitHub research.
See `AI_DESK.md` for the role-based AI Desk synthesis layer.
See `COUNCIL.md` for the multi-advisor council runner and Chair verdict.
See `KNOWLEDGE_GRAPH.md` for the Graphify-style memory graph prototype.
See `GRAPH_CONTEXT.md` for compact graph context that prevents LLM token overload.
See `SIMULATION_LAB.md` for the historical simulation and calibration loop.
See `MACRO_NEWS_IMPACT.md` for the RSS/macro news impact indicator.
See `SMC.md` for the Smart Money Concepts structure/liquidity layer.
See `LEARNING_AUTOPILOT.md` for the automatic forecast verification loop.

**Not a trading bot. No financial advice. No fund management.**

---

## What it does

| Feature | Description |
|---|---|
| CoinGecko monitor | Top coins by market cap: price, 24h change, volume, intraday range |
| Price alerts | Flags coins with strong 24h moves (configurable threshold) |
| Volume alerts | Detects high `volume/market_cap` ratio as an attention signal |
| DexScreener monitor | DEX pairs by query (SOL, AI, PEPE, etc.): liquidity, volume, price change |
| DEX candidate detection | Finds pairs with high volume-to-liquidity ratio |
| Report generation | Outputs Markdown + HTML reports ready for Telegram, Notion, or browser |
| SQLite snapshots | Stores each run locally for historical comparison |
| Offline LLM stub | Generates a safe summary prompt from any report — no API key required |
| Trader Assistant | Strategy-specific decision-support report: scalping, breakout, mean reversion, pair-trading primitives |
| Pro Trader Report | Binance candles + order book context: EMA/VWAP/RSI/ATR, support/resistance, Fibonacci, pivots, SVG chart, book imbalance |
| Fear/Greed Confirmation | Pulls Fear & Greed Index and checks whether BTC/ETH structure, breadth and book context confirm or contradict it |
| Risk/Reward Math | Calculates hypothetical level-based R/R for breakout, pullback, breakdown and rejection setups with invalidation notes |
| Browser Dashboard | Local web UI at `http://127.0.0.1:8765` with watchlist buttons, auto-refresh, export JSON, multi-timeframe cards, chart, technical context, order book, Fear/Greed and entry-based R/R quality |
| Classic Pattern Hints | Detects conservative TA hints: engulfing, hammer/shooting star, doji, double top/bottom, triangle compression, bull/bear flag watch |
| Pro Trader Checklist | Compresses context into pass/warn/fail checks, readiness score, blockers and next checks — the “what a pro would check next” layer |
| Trader Coach | Turns checklist + patterns + R/R + MTF into teaching prompts: why it matters, what to wait for, and what similar saved feedback suggests |
| Setup Journal | Saves dashboard snapshots to SQLite, tracks outcomes, and feeds pattern/R/R/checklist statistics back into the Coach |
| AI Agent Templates | Markdown prompt templates for market brief, setup review, bull/bear debate, risk manager, trader coach and journal review |
| AI Desk Notes | Six-pane role-based synthesis plus Five-Lens Idea Review: evidence for, evidence against, contrarian/outside view, risk/invalidation and balanced judge |
| Council Runner | Deterministic multi-advisor council: Contrarian, First Principles, Expansionist, Outsider, Executor and Chair verdict; dashboard can save council verdicts to SQLite |
| Knowledge Graph | Graphify-style nodes/edges over setups, outcomes, patterns, council reviews, advisors, verdicts and blockers |
| Compact Graph Context | Token-budgeted Graphify summary for LLM reasoning: current features, similar outcomes, compact stats and calibration hints |
| Simulation Lab | Rolling historical simulations compare predicted setup status with target/stop/timeout outcomes for calibration |
| Macro/RSS News Impact | RSS headline classifier for Fed/rates/inflation/geopolitics/oil/regulation news with bullish/base/bearish scenarios |
| Smart Money Concepts | Liquidity sweeps, fair value gaps, break of structure and order-block candidates as extra structure context |
| Learning Autopilot | Saves live forecasts, verifies older forecasts against future candles, and accumulates accuracy/outcome statistics |

---

## Quick start

Windows one-click demo (recommended):

```bat
Start_Crypto_Intel_Agent.bat
```

It opens the entry page:

```text
http://127.0.0.1:8765/landing
```

Direct URLs:

```text
Full dashboard:       http://127.0.0.1:8765
Market Mind Trainer:  http://127.0.0.1:8765/trainer
```

For the current showable demo flow, use `DEMO_READY.md`. See `DASHBOARD_GUIDE.md` for dashboard usage and watchlist configuration.

CLI tools:

```bash
# No external packages required — stdlib only
python crypto_intel_agent_v2.py --per-page 40
python dexscreener_monitor.py --query SOL --limit 20
python trader_assistant_report.py --per-page 60
python pro_trader_report.py --symbols BTCUSDT,ETHUSDT,SOLUSDT --interval 1h --limit 120
python fear_greed_confirmation_report.py
python risk_reward_calculator.py --symbol BTCUSDT --side long --entry 60000 --stop 59000 --target 63000
python risk_reward_calculator.py --symbol BTCUSDT --side long --entry 60000  # auto stop/target from levels
python web_dashboard.py
python llm_summary_stub.py reports/crypto_intel_report.md
```

Reports are saved to `reports/`:
- `crypto_intel_report.md` / `crypto_intel_report.html`
- `dexscreener_report.md` / `dexscreener_report.html`

---

## Example output

```
=== PRICE ALERTS (24h) ===
SOL    +8.4%   $142.30
HYPE   -9.1%   $18.72
ZEC    -7.3%   $31.45

=== HIGH VOLUME / MARKET CAP ===
DOGE   vol/mcap: 0.38
XRP    vol/mcap: 0.21

=== DEX CANDIDATES (SOL pairs) ===
BONK/SOL   liq: $2.1M   vol24h: $8.4M   Δ: +12.3%
WIF/SOL    liq: $1.8M   vol24h: $6.2M   Δ: +7.1%
```

---

## Run tests

```bash
python tests/test_crypto_intel_agent_v2.py
python tests/test_dexscreener_monitor.py
```

Tests run offline — no network required.

---

## Configuration

Copy `.env.example` to `.env` and fill in to enable Telegram delivery:

```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
```

Get a bot token from [@BotFather](https://t.me/BotFather); get your chat ID by messaging the bot once and checking `https://api.telegram.org/bot<token>/getUpdates`.

Send any report to Telegram:

```bash
python crypto_intel_agent_v2.py --telegram
python dexscreener_monitor.py --query SOL --telegram
python telegram_notify.py reports/pro_trader_report.md   # send an existing report file
```

The dashboard also has a **Send to Telegram** button that sends the current snapshot summary.

See `config.example.json` for alert thresholds and query defaults.

---

## n8n / Make automation

The scripts are designed to drop into an automation workflow:

```
Cron trigger
→ run Python script
→ read report file
→ send Telegram message
→ save to Notion / Google Sheets
→ error notification
```

See `n8n_workflow_blueprint.md` for a ready-to-adapt workflow design.

---

## Use cases

- **Freelance portfolio** — demonstrates API integration, alert logic, report generation, and automation-ready design
- **Crypto/Web3 teams** — daily token monitoring digest without manual dashboard checks
- **DeFi research** — token discovery via DexScreener liquidity/volume screening
- **Telegram alert bot base** — add `/report`, `/alerts`, `/watch BTC` commands on top

---

## Stack

- Python 3.x — stdlib only, no dependencies to install
- CoinGecko public API
- DexScreener public API
- SQLite for local snapshots
- Docker-ready (`Dockerfile` included)

---

## What this is not

This tool is a **monitoring and reporting system**, not a trading system.

- Does not execute trades
- Does not manage funds
- Does not give buy/sell recommendations
- Not financial advice

Data is sourced from public APIs and presented for informational purposes only.

---

## Project structure

```
crypto-intel-agent/
├── crypto_intel_agent_v2.py   # CoinGecko monitor + alerts + reports
├── dexscreener_monitor.py     # DexScreener DEX pair monitor
├── telegram_notify.py         # Telegram Bot API sender (--telegram flag / standalone CLI)
├── llm_summary_stub.py        # Offline LLM summary prompt builder
├── tests/
│   ├── test_crypto_intel_agent_v2.py
│   └── test_dexscreener_monitor.py
├── reports/                   # Generated HTML + Markdown reports
├── n8n_workflow_blueprint.md  # Automation workflow design
├── Dockerfile
├── config.example.json
└── .env.example
```

---

## License

MIT
