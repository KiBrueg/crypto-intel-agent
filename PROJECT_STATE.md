# Project State — Crypto Intel Agent

Path: `C:\Users\brueg\Desktop\projects\crypto-intel-agent`

Status: **demo-ready local Windows app**.

## Primary launch

Double-click:

```text
Start_Crypto_Intel_Agent.bat
```

It starts the local dashboard server and opens:

```text
http://127.0.0.1:8765/landing
```

Direct URLs:

```text
Full dashboard:       http://127.0.0.1:8765
Market Mind Trainer:  http://127.0.0.1:8765/trainer
```

Demo instructions: `DEMO_READY.md`.

## Completed showable surfaces

- `/landing` entry page with links to full dashboard and trainer.
- `/` full market dashboard with crypto market context, chart/levels, news, risk/reward, council/checklist/simulation areas.
- `/trainer` Market Mind Cards trainer.
- Historical replay cards with hidden future.
- Growth/Fall/Skip workflow.
- You vs AI vs Market reveal.
- Visual pattern cheat sheet / FAQ.
- Right-side `ИИ помощник` popup.
- Historical Similarity Stats visible on cards.
- Bucket profile matching: trend, RSI, VWAP, R/R, FOMO, Volume, Range, Fakeout.
- Accumulated experience saved to SQLite and used for realistic confidence calibration.
- Forecast Realism / Calibration Memory panel.

## Safety/positioning

- Research/backtesting only.
- No trade execution.
- No financial advice.
- No private keys or exchange trading permissions.
- Human choices are coaching/UX signals; verified market outcomes are ground truth.

## Final verified test command

```bash
python -m py_compile web_dashboard.py trader_assistant/mind_cards.py trader_assistant/market_news.py
python tests/test_web_dashboard.py
python tests/test_mind_cards.py
python tests/test_mind_cards_schema.py
python tests/test_macro_news_calibration.py
python tests/test_mind_card_modes.py
```

Verified green on this state:

```text
OK web dashboard tests passed
OK mind cards tests passed
OK mind cards schema tests passed
OK macro news calibration tests passed
OK mind card modes tests passed
```

## Known future work, not required for this demo-ready cutoff

- Live-card Results Inbox that verifies pending decisions after future candles close.
- Calibration dashboard listing unreliable bucket profiles.
- Direction override when accumulated experience conflicts with chart trend.
- Extra buckets: pattern, macro regime, order-book imbalance, ATR/volatility.
- Anti-overfit weighting by sample size, age, and selected filter quality.
