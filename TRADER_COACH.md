# Trader Coach / Learning Layer

The Trader Coach is the product layer that turns raw market context into **teaching-style prompts**.

It does not give trade commands. It explains:

- why the current setup is clean or not clean
- what a professional trader would check next
- what to wait for before trusting the idea
- what the user can learn from the current context
- whether saved feedback suggests caution around similar patterns

## Inputs

The coach consumes the existing dashboard snapshot:

- Pro Trader Checklist
- entry-based risk/reward
- multi-timeframe context
- pattern hints
- order-book/execution quality
- Fear/Greed confirmation
- technical structure
- optional local learning journal

## Output

```json
{
  "mode": "teaching_coach",
  "headline": "Context is not clean yet...",
  "explain_like_pro": "A pro first asks...",
  "teaching_points": [],
  "what_to_wait_for": [],
  "learning_notes": []
}
```

## Local learning memory

The coach can read local feedback from:

```text
reports/setup_learning.jsonl
```

Each row can contain:

```json
{"symbol":"BTCUSDT","patterns":["hammer"],"outcome":"failed","rr_quality":"weak"}
```

If similar patterns/quality buckets repeatedly failed, the coach adds caution notes.

## Product rule

The coach teaches and prompts. It should never say direct trade commands like "buy" or "sell".
