# AI Desk Orchestrator

The AI Desk is the role-based reasoning layer for Crypto Intel Agent.

It turns one dashboard snapshot into a six-pane trading-desk style set of notes — inspired by "one window, multiple AIs, each doing a job" utilities:

- Market Brief
- Technical Analyst
- Bull Case
- Bear Case
- Risk Manager
- Trader Coach

## Why it exists

A single AI answer is easy to over-trust. A real trading desk separates jobs:

```text
analyst gathers facts
risk/technical analyst maps structure
bull case tests upside
bear case tests downside
risk manager rejects bad math
coach teaches what to notice next
```

The AI Desk follows that pattern without automatic execution or direct trade commands.

## Five-Lens Idea Review

Inspired by the "ask the council" pattern from the user's video transcript: one model can become a yes-man or a no-man depending on how the question is asked. To reduce that bias, each setup also gets five explicit lenses:

1. **Evidence For / Expansionist** — what upside/supportive evidence might be missed?
2. **Evidence Against / Contrarian** — what could kill the idea?
3. **Contrarian View / Outsider** — what obvious miss would an outsider catch without our context?
4. **Risk/Invalidation / Executor** — what has to be true tomorrow morning, and what invalidates it?
5. **Balanced Judge / Chair** — final synthesis without blindly agreeing or rejecting.

This does not produce a trade command. It produces a safer decision-support review.

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
    {"role": "Market Brief", "verdict": "not_clean"},
    {"role": "Technical Analyst", "verdict": "mixed"},
    {"role": "Bull Case", "verdict": "possible"},
    {"role": "Bear Case", "verdict": "possible"},
    {"role": "Risk Manager", "verdict": "reject"},
    {"role": "Trader Coach", "verdict": "teach"}
  ]
}
```

## Future LLM upgrade

The deterministic cards can later be used as grounded context for a real LLM call:

```text
snapshot JSON + selected templates/ai/*.md -> structured AI Desk Notes
```

But the baseline remains useful even without an LLM.
