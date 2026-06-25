# AI Desk Orchestrator

The AI Desk is the role-based reasoning layer for Crypto Intel Agent.

It turns one dashboard snapshot into a small trading-desk style set of notes:

- Market Brief
- Bull/Bear Debate
- Risk Manager
- Trader Coach

## Why it exists

A single AI answer is easy to over-trust. A real trading desk separates jobs:

```text
analyst gathers facts
bull case tests upside
bear case tests downside
risk manager rejects bad math
coach teaches what to notice next
```

The AI Desk follows that pattern without automatic execution or direct trade commands.

## Current implementation

File:

```text
trader_assistant/ai_desk.py
```

Function:

```python
build_ai_desk_notes(snapshot) -> dict
```

The first version is deterministic and local. It does not call an external LLM yet. This is intentional:

- testable
- transparent
- no API keys needed
- safe baseline before adding LLM providers

## Output shape

```json
{
  "mode": "ai_desk",
  "symbol": "BTCUSDT",
  "overall_status": "not_clean",
  "readiness_score": 35,
  "summary": "AI Desk synthesis...",
  "cards": [
    {
      "role": "Market Brief",
      "verdict": "not_clean",
      "key_points": [],
      "template": "templates/ai/market_brief.md"
    }
  ]
}
```

## Future LLM upgrade

The deterministic cards can later be used as grounded context for a real LLM call:

```text
snapshot JSON + selected templates/ai/*.md -> structured AI Desk Notes
```

But the baseline remains useful even without an LLM.
