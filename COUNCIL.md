# Council Runner

Council Runner is the next step after the six-pane AI Desk and Five-Lens Idea Review.

It models the "ask the council" workflow as a deterministic, testable local engine:

```text
idea/snapshot -> 5 advisors -> disagreements/consensus -> Chair verdict
```

## Advisors

1. **Contrarian** — searches for what kills the idea.
2. **First Principles** — asks what problem is actually being solved.
3. **Expansionist** — searches for overlooked upside/optionalities.
4. **Outsider** — catches obvious misses without project context.
5. **Executor** — asks what must happen tomorrow morning and what the next operational check is.
6. **Chair** — synthesizes the council into verdict, blockers and next actions.

## Why deterministic first

The first version does not call external LLMs. It is intentionally deterministic:

- no API keys
- works offline/local
- unit-testable
- safe baseline before adding real multi-LLM calls
- avoids hallucinated authority

## Output

```json
{
  "mode": "council_runner",
  "symbol": "BTCUSDT",
  "advisors": [],
  "consensus": [],
  "disagreements": [],
  "chair": {
    "verdict": "not_clean",
    "action_bias": "wait_for_confirmation",
    "summary": "Council verdict...",
    "blockers": [],
    "next_actions": []
  }
}
```

## Product rule

The council does not say buy/sell. It says:

- clean / watch / not clean
- what supports the idea
- what kills the idea
- what to check next
- what invalidates the thesis

This keeps the project as decision-support, not financial advice or execution automation.
