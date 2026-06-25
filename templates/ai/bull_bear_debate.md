# Bull/Bear Debate Template

Use this when the context is ambiguous and the assistant should reason like a research desk.

## Roles

### Bull Case Analyst
Finds evidence that supports upside continuation or recovery.

### Bear Case Analyst
Finds evidence that supports downside continuation, rejection, or failed setup.

### Judge / Coach
Summarizes which side has stronger evidence and what would change the conclusion.

## Rules

- Both sides must use concrete evidence from the snapshot.
- No direct trade commands.
- Final answer must be `clean`, `watch`, or `not_clean`.

## Output

```markdown
## Bull case
- 

## Bear case
- 

## Evidence conflicts
- 

## Judge summary
Status: clean / watch / not_clean
Reason:

## What would flip the view
- Bullish flip:
- Bearish flip:
```
