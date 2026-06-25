# AI Trading Agent Templates — Research Notes

GitHub scan focused on AI/LLM trading agent prompts, skills and markdown templates.

## Repositories / ideas reviewed

- `TauricResearch/TradingAgents` — multi-agent LLM financial trading framework. Useful idea: split reasoning into analyst team, bullish/bearish research debate, trader synthesis, risk/portfolio review, and persistent decision memory.
- `alphaparkinc/tradingagents-skill` — GenPark skill wrapping TradingAgents. Useful idea: package trading workflow as a reusable skill with role descriptions and expected outputs.
- `annaescalada/trading-gpt-assistant-nodejs` — generates daily prompts for a custom GPT using RSI, MA50/MA200, support/resistance, news and prior results, then stores JSON responses. Useful idea: prompt templates should enforce strict structured output and include prior results.
- `TradeNote` / trading journal projects — useful idea: an assistant should remember setups/outcomes and support review, not just generate live opinions.

## What we adopted

We do **not** copy prompts verbatim. We adapt the reusable architecture:

1. **Role separation**
   - Technical Analyst
   - Sentiment/News Analyst
   - Bull Case
   - Bear Case
   - Risk Manager
   - Coach / Teacher

2. **Structured output**
   - No loose prose only.
   - Output should fit JSON/Markdown sections consumed by dashboard.

3. **Debate before conclusion**
   - Always show both supportive and contradicting evidence.

4. **Memory loop**
   - Include prior saved outcomes from Setup Journal.

5. **Safety stance**
   - No automatic execution.
   - No direct buy/sell instructions.
   - Use `setup cleanliness`, `what to wait for`, `invalidation`, and `risk context` instead.

## Templates added

```text
templates/ai/market_brief.md
templates/ai/setup_review.md
templates/ai/bull_bear_debate.md
templates/ai/risk_manager.md
templates/ai/trader_coach.md
templates/ai/journal_review.md
```

These templates are meant for future LLM integration or manual copy/paste into another AI. They are project-specific and safe for our decision-support framing.
