# Compact Graph Context

This layer solves the token-overload problem.

Instead of sending the AI:

```text
all candles
all journal rows
all council reviews
all predictions
all RSS/news items
full graph nodes/edges
```

it sends a compact Graphify-style context:

```text
current setup features
small graph summary
top relevant relations
past outcomes for matching RR/status/patterns/SMC
verified forecast stats
calibration hints
```

## Module

```text
trader_assistant/graph_context.py
```

## API

```text
POST /api/graph-context
```

Body:

```json
{
  "snapshot": {"...": "current dashboard snapshot"},
  "max_chars": 1600
}
```

Response:

```json
{
  "mode": "compact_graph_context",
  "token_strategy": "summarized_graph_memory_no_raw_rows",
  "char_budget": 1600,
  "char_count": 927,
  "context_lines": [
    "GRAPH MEMORY: ...",
    "CURRENT SETUP: ...",
    "PAST RR bucket weak: ...",
    "CALIBRATION HINT: ..."
  ],
  "calibration_hints": []
}
```

## Dashboard

Section:

```text
Compact Graph Context
```

Button:

```text
Build compact context
```

The dashboard also refreshes this automatically after a new snapshot.

## Why this matters

LLMs degrade when fed too much raw state. Graph Context keeps the reasoning input small and high-signal.

Good:

```text
PAST RR bucket weak: {'failed': 4, 'target': 1}
PREDICTION history for SMC bearish: {'stopped': 3, 'pending': 2}
CALIBRATION HINT: Do not over-trust not_clean status; past outcomes are not clearly positive.
```

Bad:

```text
500 raw rows of SQLite
thousands of candles
full RSS dumps
full graph node/edge JSON
```

This is the bridge between accumulated memory and LLM reasoning.
