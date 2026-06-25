# Setup Journal / Outcome Tracker

The Setup Journal is the project memory for market observations. Hermes remembers the product direction; the journal remembers actual setup outcomes.

## Why it exists

The dashboard should not only analyze. It should learn from saved observations and teach better over time.

Workflow:

```text
see setup -> save snapshot -> mark outcome -> build stats -> Coach warns/teaches using similar history
```

## Storage

SQLite database:

```text
data/setup_journal.sqlite3
```

Main table:

```text
setups
```

Stores:

- symbol
- timestamp
- outcome
- readiness score
- checklist status
- R/R ratio
- R/R quality
- detected patterns
- full dashboard snapshot JSON
- notes

## Dashboard controls

- `Save Setup` — saves current full snapshot.
- `Mark target` — marks last saved setup as target outcome.
- `Mark failed` — marks last saved setup as failed outcome.

More outcome buttons can be added later:

- stopped
- neutral
- missed

## Learning stats

The journal groups outcomes by:

- pattern
- R/R quality
- symbol
- checklist status
- readiness score bucket

The Trader Coach can then add notes like:

```text
Learning memory: hammer has failed 3 times in saved feedback. Demand stronger confirmation next time.
```

## Design principle

This is not ML yet. It is a transparent feedback loop. The user can inspect the records, understand the stats, and only then decide whether a more advanced model/backtest layer is justified.
