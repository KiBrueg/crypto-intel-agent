# Smart Money Concepts (SMC) Layer

SMC is useful in this project as an additional structure/liquidity lens, not as a standalone signal.

It helps answer:

```text
where was liquidity swept?
where are fair value gaps / imbalances?
did price break structure?
where is a possible order block / mitigation zone?
```

## Current implementation

File:

```text
trader_assistant/smc.py
```

Dashboard section:

```text
Smart Money Concepts
```

Snapshot field:

```json
"smc": {
  "mode": "smart_money_concepts",
  "bias": "bullish | bearish | mixed | neutral",
  "score": 0,
  "zones": []
}
```

## Detected concepts

- liquidity_sweep
- fair_value_gap
- break_of_structure
- order_block_candidate

## Why it helps

SMC adds a market-structure layer between raw indicators and the council:

```text
candles -> SMC zones -> checklist/council/coach -> journal/simulation/graph calibration
```

Potential benefits:

- better invalidation placement
- better entry-zone context
- improved distinction between continuation and liquidity grab
- extra features for simulation and graph learning
- more professional trader-style explanations

## Safety note

SMC labels are heuristics. The project should never treat them as direct buy/sell commands. They must be confirmed by:

- R/R
- MTF context
- VWAP/levels
- order book
- macro/news impact
- simulation history
- journal outcomes

## Future upgrades

- stronger swing high/low engine
- equal highs/equal lows liquidity pools
- premium/discount zones
- mitigation tracking
- SMC zones on chart canvas
- SMC feature storage in Knowledge Graph
- simulation stats by SMC pattern/outcome
