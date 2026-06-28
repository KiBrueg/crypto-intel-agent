# Macro / RSS News Impact Indicator

Market learning cannot rely only on candles. Macro and news shocks often change the regime:

- Federal Reserve statements
- rate hike / rate cut expectations
- inflation surprises
- crypto regulation / ETF approvals
- war escalation / ceasefire
- oil routes, shipping routes, pipelines
- exchange hacks, lawsuits, sanctions

This module turns RSS/news headlines into a lightweight market-impact indicator.

## Current implementation

File:

```text
trader_assistant/market_news.py
```

API:

```text
GET /api/news-impact?limit_per_feed=6
```

Dashboard section:

```text
Macro/RSS News Impact
```

Button:

```text
Scan RSS macro/news
```

## Output

```json
{
  "mode": "market_news_impact",
  "net_bias": "bullish | bearish | mixed",
  "net_score": 0,
  "fear_greed_pressure": "fear_up | greed_up | mixed",
  "scored_items": [],
  "scenarios": {
    "bullish": {},
    "base": {},
    "bearish": {}
  }
}
```

## Heuristic drivers

Bullish drivers:

- liquidity: rate cuts, dovish Fed, easing, cooling inflation
- crypto adoption: ETF inflows/approval, regulation clarity
- risk-on: ceasefire, de-escalation, soft landing

Bearish drivers:

- rates: rate hike, higher-for-longer, hawkish Fed
- inflation: hot CPI/PPI
- geopolitical: war escalation, sanctions, shipping/oil route disruption
- crypto risk: hack, exploit, lawsuit, ban, outflows
- risk-off: recession, bank crisis, default risk

## Why scenarios matter

A single recommendation is too brittle. The dashboard now keeps multiple calibration lenses:

- bullish case
- base/mixed case
- bearish case

This gives the assistant competing hypotheses to validate against simulations and later real outcomes.

## Future upgrades

- configurable feed list
- severity weighting by source credibility
- event deduplication
- link news events into Knowledge Graph
- compare news bias vs subsequent BTC/ETH movement
- calibrate news weights by simulation/outcome history
