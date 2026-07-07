# Crypto Intel Agent — Demo Ready Guide

Status: ready to show as a local research/backtesting demo.

> Research/backtesting only. Not financial advice. No trade execution.

## One-click start on Windows

Double-click:

```text
Start_Crypto_Intel_Agent.bat
```

It starts the local server and opens:

```text
http://127.0.0.1:8765/landing
```

Useful direct URLs:

```text
Entry / landing:      http://127.0.0.1:8765/landing
Full dashboard:       http://127.0.0.1:8765
Market Mind Trainer:  http://127.0.0.1:8765/trainer
```

If the browser opens too early, wait a few seconds and refresh.

## What to show first

### 1. Landing page

Open `/landing` and show that the product has two surfaces:

- Full Market Dashboard
- Trainer + AI Helper

### 2. Market Mind Cards trainer

Open `/trainer`.

Demo flow:

1. Wait until the card loads.
2. Show the real historical candlestick fragment.
3. Point out the cockpit: Chance, Risk, R/R.
4. Click `Growth` or `Fall`.
5. Show the reveal panel:
   - Your choice / Ты
   - AI thought / ИИ думал
   - Market went / Рынок пошёл
6. Show `Historical Similarity Stats`:
   - sample size
   - up/down/flat rates
   - selected similarity filter
   - buckets: trend, RSI, VWAP, R/R, FOMO, Volume, Range, Fakeout
7. Show `Forecast Realism / Calibration Memory` on the right.
8. Open `KI-Helfer` and ask in German:
   - `Auf welcher Statistik basiert die KI?`
   - `Wo liegt die Invalidation?`
   - `Warum Skip?`
   - `VWAP/EMA?`

### 3. Full dashboard

Open `/`.

Show:

- watchlist / symbol controls
- market state and charts
- risk/reward and levels
- world/news impact
- Market Mind Card full view
- council / checklist / simulation context where visible

## What is currently implemented

- Local browser app with entry page, full dashboard, and trainer.
- Historical replay cards with hidden future candles.
- User vs AI vs Market reveal after a decision.
- Visible historical similarity statistics.
- Bucket matching:
  - trend
  - RSI
  - VWAP
  - R/R
  - FOMO
  - Volume
  - Range
  - Fakeout
- Fallback matching from exact profile down to broad historical sample.
- Accumulated experience stored in SQLite from verified replay outcomes.
- Confidence calibration from verified market outcomes, not from assuming human or AI is stronger.
- Forecast Realism / Calibration Memory panel.
- Pattern cheat sheet with visual TA and harmonic examples.
- Right-side educational AI helper popup.
- Local SQLite journal and learning event storage.

## What is intentionally not included

- No trade execution.
- No exchange account connection.
- No private key handling.
- No financial advice.
- No promise that AI direction is profitable.

## Final verification commands

From the project folder:

```bash
python -m py_compile web_dashboard.py trader_assistant/mind_cards.py trader_assistant/market_news.py
python tests/test_web_dashboard.py
python tests/test_mind_cards.py
python tests/test_mind_cards_schema.py
python tests/test_macro_news_calibration.py
python tests/test_mind_card_modes.py
```

Expected result:

```text
OK web dashboard tests passed
OK mind cards tests passed
OK mind cards schema tests passed
OK macro news calibration tests passed
OK mind card modes tests passed
```

## Known limitations / future work

These are intentionally left for a later phase:

- Results Inbox for live cards that verify after future candles close.
- Separate calibration dashboard listing the most unreliable bucket profiles.
- Stronger direction override when accumulated experience conflicts with chart trend.
- More buckets: pattern, order-book imbalance, macro regime, ATR/volatility, support/resistance distance.
- Anti-overfit weighting by sample size, age, and selected filter quality.

The current scope is good enough to show as a local demo/training product.