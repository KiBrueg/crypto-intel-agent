# Learning Autopilot

Learning Autopilot is the first automatic forecast-verification loop.

It answers the user's core requirement:

```text
program receives online data
program makes a forecast / assumption
program stores it
program later checks what happened
program accumulates statistics
program uses that history for calibration
```

## Current implementation

File:

```text
trader_assistant/learning_autopilot.py
```

SQLite table:

```text
predictions
```

Dashboard section:

```text
Learning Autopilot
```

Button:

```text
Run learning cycle
```

APIs:

```text
GET /api/learning/run?symbol=BTCUSDT&interval=1h&side=long
GET /api/learning/stats
```

## Automatic background mode

Dashboard/launcher automation:

```text
Crypto Intel Agent.bat now starts the dashboard and also starts Auto Learner in the background.
```

The daemon:

```text
learning_daemon.py --symbols BTCUSDT,ETHUSDT,SOLUSDT --interval 15m --horizon 4 --sleep 900
```

It runs every 15 minutes and writes:

```text
data/learning_autopilot_heartbeat.json
data/learning_autopilot.log
```

## What one learning cycle does

```text
1. fetches live market data
2. builds the full snapshot
3. reads checklist/council/SMC/RR features
4. creates a forecast record
5. stores it in SQLite
6. checks older open forecasts if enough future candles exist
7. updates verified_outcome and direction correctness
8. returns cumulative statistics
```

## Stored forecast features

- symbol
- interval
- start timestamp
- horizon bars
- predicted direction: up/down/mixed
- predicted status: clean/watch/not_clean
- entry / stop / target
- readiness score
- council verdict
- SMC bias
- feature summary JSON
- full snapshot JSON
- verified outcome
- direction correctness

## Important limitation

The first run usually creates a forecast but cannot verify it immediately, because future candles do not exist yet.

Example:

```text
Run now -> saves forecast
Run again after enough candles -> verifies older forecast
```

For 1h interval and horizon 12, verification means roughly after 12 hours. For faster testing use 15m interval.

## What this is not

It is not auto-trading and not financial advice.

It is a controlled self-calibration loop for decision support.
