# Market Mind Cards Implementation Plan

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task.

**Goal:** Transform Crypto Intel Agent from a powerful analytical dashboard into a web-first, simple swipe/card training experience where users learn market pattern recognition while the AI accumulates experience from real chart snapshots and verified market outcomes. Human choices are stored as noisy calibration/UX signals, not as ground-truth training labels.

**Architecture:** Keep the existing dashboard and Auto Learner as the analytical engine. Add a new `Market Mind Cards` layer with a compact decision cockpit, card/session persistence, user-vs-AI-vs-market comparison, and a learning feedback loop that updates AI calibration from real chart features and verified market outcomes. Human decisions remain useful, but only as noisy behavioral/context signals for coaching and UX, not as labels that teach the AI what is true. The surface UI stays simple; the deep analytics remain available through progressive disclosure.

**Tech Stack:** Python 3.11 stdlib server, SQLite, existing `trader_assistant` modules, HTML/CSS/vanilla JS, TradingView Lightweight Charts where available, existing Binance public data/order book fetchers.

---

## Product Philosophy

The product teaches complex trading concepts through a simple interface:

```text
simple card UI
→ one decision
→ AI comparison
→ later/replay outcome
→ compact feedback
→ aggregated statistics
→ AI learns from chart features + verified market outcome
→ human choices are kept separately as noisy coaching/calibration signals
```

The product must avoid harsh feedback. Do not write:

```text
you were wrong
you failed
you did not guess
```

Use neutral coaching language:

```text
рынок подтвердил другой сценарий
стоит обратить внимание на оценку риска
зона внимания: объём / стакан / FOMO / уровень / риск
```

The product is not financial advice and not real trade execution. It is a training and decision-support environment.

---

## Core UX Flow

### Start Screen

User chooses training mode, not complex professional jargon first:

```text
Market Mind Cards

Что тренируем сегодня?
- Смешанная тренировка
- Быстрые движения
- Пробои
- Ложные пробои
- Отскоки / возврат к уровню
- Стакан и ликвидность
```

Internally these map to:

```text
mixed
quick_scalps
breakout_reads
fakeout_defense
vwap_level_reclaim
order_book_sense
```

### Card Screen

One real market snapshot:

```text
BINANCE · BTCUSDT · 15m · real snapshot
chart cut
mini order book
compact decision cockpit

↑ Рост
↓ Падение
Skip

Size:
Small / Medium / Large
```

### After User Choice

Do not immediately remove the card. Freeze it and show:

```text
Твой сценарий: ↑ Рост · Medium
ИИ: ↓ Падение · Small
Совпадение с ИИ: отличается
Статус: pending / reveal available

[Подробнее]
[Следующая карточка]
```

### Outcome / Verification

For historical replay: reveal immediately.

For live cards: save as pending, verify later by daemon, and surface in Results Inbox.

### End of Session

Compare three layers:

```text
human decision
AI decision
actual market outcome
```

Show aggregated statistics only at the end:

```text
Cards: 20
Совпадение с ИИ: 11/20
Сценарий пользователя подтвердился: 12/20
Сценарий ИИ подтвердился: 14/20
Risk-adjusted user score: +2.4R
Risk-adjusted AI score: +3.1R
Зоны внимания: FOMO, оценка риска, ложные пробои
```

---

## Data Model

### Task 1: Add card/session SQLite tables

**Objective:** Persist Market Mind Cards, user choices, AI forecasts, verified outcomes, and session-level summaries. User choices are stored for comparison/coaching; verified market outcomes remain the only ground-truth signal.

**Files:**
- Modify: `trader_assistant/journal.py`
- Test: `tests/test_mind_cards_schema.py`

**Schema additions:**

```sql
create table if not exists mind_card_sessions (
    id integer primary key autoincrement,
    created_at text not null,
    mode text not null,
    exchange text not null default 'BINANCE',
    symbols text not null,
    interval text not null,
    status text not null default 'active',
    completed_at text
);

create table if not exists mind_cards (
    id integer primary key autoincrement,
    session_id integer,
    created_at text not null,
    exchange text not null default 'BINANCE',
    symbol text not null,
    interval text not null,
    mode text not null,
    snapshot_ts integer,
    horizon_bars integer not null,
    chart_window_json text not null,
    order_book_json text,
    features_json text not null,
    ai_direction text not null,
    ai_size text not null,
    ai_confidence real,
    ai_reason_json text,
    potential_profit_pct real,
    risk_loss_pct real,
    risk_reward_ratio real,
    fomo_score real,
    setup_quality text,
    market_regime text,
    status text not null default 'unanswered',
    user_direction text,
    user_size text,
    user_decided_at text,
    agreement_with_ai integer,
    verified_at text,
    actual_outcome text,
    actual_direction text,
    user_scenario_confirmed integer,
    ai_scenario_confirmed integer,
    user_r_score real,
    ai_r_score real,
    focus_area text,
    coach_note text,
    foreign key(session_id) references mind_card_sessions(id)
);
```

**Test expectations:**

```python
def test_mind_card_tables_exist():
    con = init_journal(temp_db)
    tables = {r[0] for r in con.execute("select name from sqlite_master where type='table'")}
    assert 'mind_cards' in tables
    assert 'mind_card_sessions' in tables
```

**Verification:**

Run:

```bash
python tests/test_mind_cards_schema.py
```

Expected:

```text
OK mind cards schema tests passed
```

---

## Card Generation Backend

### Task 2: Create training mode profiles

**Objective:** Map user-friendly modes to strategy filters and defaults.

**Files:**
- Create: `trader_assistant/mind_card_modes.py`
- Test: `tests/test_mind_card_modes.py`

**Mode examples:**

```python
MIND_CARD_MODES = {
    'mixed': {
        'label': 'Смешанная тренировка',
        'intervals': ['15m', '1h'],
        'symbols': ['BTCUSDT', 'ETHUSDT', 'SOLUSDT'],
        'horizon_bars': 8,
        'feature_focus': ['trend', 'levels', 'volume', 'risk'],
    },
    'quick_scalps': {
        'label': 'Быстрые движения',
        'intervals': ['5m', '15m'],
        'symbols': ['BTCUSDT', 'ETHUSDT', 'SOLUSDT'],
        'horizon_bars': 4,
        'feature_focus': ['spread', 'order_book', 'volume_burst'],
    },
    'fakeout_defense': {
        'label': 'Ложные пробои',
        'intervals': ['15m', '1h'],
        'horizon_bars': 8,
        'feature_focus': ['liquidity_sweep', 'failed_breakout', 'volume_fade'],
    },
}
```

**Verification:**

```bash
python tests/test_mind_card_modes.py
```

---

### Task 3: Build card creation service

**Objective:** Generate a card from current or historical market data with chart window, order book, AI scenario, cockpit metrics, and explanation seeds.

**Files:**
- Create: `trader_assistant/mind_cards.py`
- Test: `tests/test_mind_cards.py`

**Core function:**

```python
def build_mind_card(snapshot, mode='mixed', exchange='BINANCE', horizon_bars=None):
    return {
        'exchange': exchange,
        'symbol': snapshot['symbol'],
        'interval': snapshot['interval'],
        'mode': mode,
        'snapshot_ts': snapshot['candles'][-1]['ts'],
        'horizon_bars': horizon_bars,
        'chart_window': snapshot['candles'][-80:],
        'order_book': snapshot.get('order_book'),
        'features': {...},
        'ai_direction': 'up' | 'down' | 'skip',
        'ai_size': 'small' | 'medium' | 'large' | 'none',
        'ai_confidence': 0.62,
        'potential_profit_pct': 1.8,
        'risk_loss_pct': 0.7,
        'risk_reward_ratio': 2.6,
        'fomo_score': 0.72,
        'setup_quality': 'mixed',
        'market_regime': 'chop',
        'ai_reason': [...],
    }
```

**Decision cockpit fields must be available without scrolling:**

```text
AI bias
potential profit %
risk loss %
risk/reward
AI confidence
FOMO/greed score
setup quality
market regime
```

---

### Task 4: Add persistence helpers for cards and choices

**Objective:** Save generated cards, user choices, and agreement with AI.

**Files:**
- Modify: `trader_assistant/mind_cards.py`
- Test: `tests/test_mind_cards.py`

**Functions:**

```python
def save_mind_card(con, card): ...
def record_user_choice(con, card_id, direction, size): ...
def recent_mind_cards(con, limit=20): ...
def mind_card_detail(con, card_id): ...
```

**Choice rules:**

```text
up/down/skip
small/medium/large/none
skip forces size = none / 0R
agreement_with_ai = user_direction == ai_direction
```

---

## Outcome + Learning Loop

### Task 5: Verify card outcomes

**Objective:** Compare user choice and AI choice against actual market movement after horizon.

**Files:**
- Create: `trader_assistant/mind_card_verifier.py`
- Test: `tests/test_mind_card_verifier.py`

**Rules:**

```text
actual_direction = up/down/flat
target/stop/timeout from existing simulation logic
user_scenario_confirmed = user_direction == actual_direction
ai_scenario_confirmed = ai_direction == actual_direction
```

Skip handling:

```text
If actual is flat/timeout/no clean move, skip is treated as disciplined.
If actual is strong directional move, skip is recorded as missed opportunity, not wrong.
```

No harsh language stored. Store neutral coach notes.

---

### Task 6: Add risk-adjusted scoring

**Objective:** Teach position sizing, not just direction.

**Files:**
- Create: `trader_assistant/mind_card_scoring.py`
- Test: `tests/test_mind_card_scoring.py`

**Size mapping:**

```python
SIZE_TO_RISK = {
    'none': 0.0,
    'small': 0.25,
    'medium': 0.5,
    'large': 1.0,
}
```

**Score rules:**

```text
target hit: +risk_size * risk_reward_ratio
stop hit: -risk_size
timeout/flat: 0 or small realized move score
skip: 0R, plus discipline label if no clean move
```

**Session stats:**

```text
user direction confirmation rate
AI direction confirmation rate
user risk-adjusted R score
AI risk-adjusted R score
agreement rate
focus areas
```

---

### Task 7: Add AI experience accumulation

**Objective:** Store learnings from every card so the AI improves calibration over time.

**Files:**
- Create: `trader_assistant/mind_card_memory.py`
- Modify: `trader_assistant/journal.py`
- Test: `tests/test_mind_card_memory.py`

**New table:**

```sql
create table if not exists mind_card_learning_events (
    id integer primary key autoincrement,
    created_at text not null,
    card_id integer not null,
    mode text not null,
    symbol text not null,
    interval text not null,
    feature_hash text not null,
    ai_direction text not null,
    user_direction text,
    actual_direction text,
    ai_scenario_confirmed integer,
    user_scenario_confirmed integer,
    setup_quality text,
    market_regime text,
    focus_area text,
    fomo_score real,
    risk_reward_ratio real,
    ai_confidence real,
    actual_outcome text,
    lesson_json text,
    foreign key(card_id) references mind_cards(id)
);
```

**Learning summary function:**

```python
def mind_card_learning_summary(con, mode=None, symbol=None, limit=500):
    return {
        'cards_seen': 123,
        'ai_confirmation_rate': 0.61,
        'user_confirmation_rate': 0.54,
        'high_fomo_underperformance': True,
        'weak_focus_areas': ['fakeout', 'risk_sizing'],
        'mode_breakdown': {...},
        'calibration_notes': [...],
    }
```

This is the “Pokemon Go” idea adapted to markets:

```text
people interact with real chart snapshots
→ higher usage means more real market diagrams/snapshots are processed
→ each snapshot is later linked to verified market outcome
→ the system learns which chart/order-book/features preceded which real outcome
→ human choices are stored separately as noisy behavioral signals for coaching, UX, and comparison, not as truth labels
```

---

### Task 8: Feed learning memory back into AI forecasts

**Objective:** Use accumulated card outcomes to adjust AI confidence and explanations.

**Files:**
- Modify: `trader_assistant/mind_cards.py`
- Modify: `trader_assistant/learning_autopilot.py` if shared calibration is useful
- Test: `tests/test_mind_card_memory.py`

**Approach:**

When building a new card, lookup similar historical learning events by:

```text
mode
symbol class
interval
market_regime
setup_quality
fomo bucket
SMC bias
risk/reward bucket
```

Adjust:

```text
ai_confidence
setup_quality
coach note
focus area
```

Example:

```text
Similar high-FOMO breakout cards underperformed historically.
AI confidence reduced from 64% to 57%.
Focus area: FOMO / late entry risk.
```

---

## Web API

### Task 9: Add Market Mind Cards API endpoints

**Objective:** Expose card/session/choice/outcome/stats via current stdlib HTTP server.

**Files:**
- Modify: `web_dashboard.py`
- Test: `tests/test_web_dashboard.py`
- Test: `tests/test_mind_cards_api.py`

**Endpoints:**

```text
GET  /api/mind-card/modes
POST /api/mind-card/session/start
GET  /api/mind-card/next?session_id=...&mode=...
POST /api/mind-card/choice
GET  /api/mind-card/detail?id=...
POST /api/mind-card/reveal?id=...        # historical/replay only
GET  /api/mind-card/results-inbox
GET  /api/mind-card/session/stats?id=...
GET  /api/mind-card/learning-summary
```

If adding POST parsing is inconvenient in current server, use query-param POST-like endpoints initially, but prefer proper JSON POST if already feasible.

---

## Web UI

### Task 10: Add Market Mind Cards section to dashboard

**Objective:** Add one top-level section in the existing web UI without breaking current dashboard.

**Files:**
- Modify: `web_dashboard.py`
- Test: `tests/test_web_dashboard.py`

**Required visible elements:**

```text
Market Mind Cards
Choose your drill
Decision Cockpit
↑ Рост
↓ Падение
Skip
Small / Medium / Large
Подробнее
Следующая карточка
Results Inbox
Session Stats
```

---

### Task 11: Build compact Decision Cockpit

**Objective:** Show all main parameters in one visible panel without requiring long scroll.

**Files:**
- Modify: `web_dashboard.py`
- Test: `tests/test_web_dashboard.py`

**Cockpit metrics:**

```text
AI bias
Your view
AI agreement
Potential +%
Risk -%
R/R
AI confidence
FOMO / Greed
Setup quality
Market regime
```

**Style:** warm premium, no blue.

**Copy rules:**

```text
No “wrong/fail/not guessed”.
Use “рынок подтвердил другой сценарий”, “зона внимания”, “стоит обратить внимание”.
```

---

### Task 12: Add progressive details panel

**Objective:** Keep surface simple while allowing deep learning.

**Files:**
- Modify: `web_dashboard.py`

**Detail levels:**

```text
Коротко
Подробно
Профессионально
```

Example:

```text
Коротко:
ИИ видел риск падения, потому что рост не был подтверждён.

Подробно:
Цена не удержала уровень, а объём на пробое начал слабеть.

Профессионально:
Failed breakout + volume fade + bearish order book imbalance + VWAP rejection.
```

---

### Task 13: Add Results Inbox

**Objective:** For live cards, show verified results later without requiring the user to wait.

**Files:**
- Modify: `web_dashboard.py`
- Create/modify tests as needed

**UI:**

```text
Results Inbox
3 new verified cards

BTCUSDT 15m
Ты: ↑ Рост · Medium
ИИ: ↓ Падение · Small
Рынок: ↓ Падение
Сверка: рынок подтвердил сценарий ИИ
Зона внимания: стакан и объём
```

---

### Task 14: Add session summary UI

**Objective:** Summarize human vs AI vs market only at the end of a session.

**Files:**
- Modify: `web_dashboard.py`

**Metrics:**

```text
cards total
AI agreement rate
human scenario confirmed rate
AI scenario confirmed rate
human risk-adjusted R
AI risk-adjusted R
good skips
high-risk choices on weak setups
focus areas
recommended next drill
```

No per-card shaming.

---

## Daemon Integration

### Task 15: Extend background learner to verify mind cards

**Objective:** The current learner should also verify pending live cards.

**Files:**
- Modify: `learning_daemon.py`
- Modify/Create: `trader_assistant/mind_card_verifier.py`
- Test: `tests/test_mind_card_verifier.py`

**Daemon cycle:**

```text
1. run existing forecast learning cycle
2. verify overdue mind_cards
3. write mind_card_learning_events
4. update heartbeat with mind card counts
```

Heartbeat should include:

```json
{
  "mind_cards": {
    "pending": 12,
    "verified_now": 3,
    "total_verified": 42
  }
}
```

---

## Validation

### Task 16: Full test suite and live smoke test

**Objective:** Prove the project still works end-to-end.

**Commands:**

```bash
python tests/test_mind_cards_schema.py
python tests/test_mind_card_modes.py
python tests/test_mind_cards.py
python tests/test_mind_card_scoring.py
python tests/test_mind_card_verifier.py
python tests/test_mind_card_memory.py
python tests/test_mind_cards_api.py
python tests/test_web_dashboard.py
python tests/test_learning_autopilot.py
python tests/test_forecast_due.py
python tests/test_daemon_control.py
python tests/test_forecast_outcomes.py
python tests/test_forecast_details.py
python tests/test_forecast_timeline.py
```

Then run broader suite already used in project.

**Live checks:**

```text
http://127.0.0.1:8765
/api/mind-card/modes
/api/mind-card/next?mode=mixed
/api/mind-card/session/stats?id=...
/api/mind-card/learning-summary
```

Browser DOM checks:

```text
Market Mind Cards visible
Decision Cockpit visible
no JS errors
card choice updates UI
session stats render
```

---

## Rollout Strategy

### Phase 1: Web MVP

```text
modes
one card
choice + size
AI comparison
cockpit
save decision
session stats
```

### Phase 2: Learning Loop

```text
verify outcomes
learning events
AI calibration summary
Results Inbox
```

### Phase 3: Replay Training

```text
historical cards
instant reveal
pattern-specific drills
```

### Phase 4: Mobile Web / PWA

```text
responsive card layout
large touch buttons
installable PWA
```

### Phase 5: Android only if web works

```text
WebView wrapper / React Native / Flutter
only after UX is validated
```

---

## Risks and Tradeoffs

### Risk: Product feels like gambling

Mitigation:

```text
use “training”, “scenario”, “risk units”
no money language
no “bet now”
no win/lose casino feedback
```

### Risk: AI “probability” appears guaranteed

Mitigation:

```text
call it AI confidence / estimated chance
show it as calibration, not promise
include not financial advice
```

### Risk: UI becomes too complex

Mitigation:

```text
one compact cockpit
progressive disclosure
short explanation first
professional details below
```

### Risk: Learning loop overfits small data

Mitigation:

```text
show sample size
avoid strong claims until enough cards
bucket similar setups
keep notes probabilistic
```

---

## Acceptance Criteria

The feature is ready when:

```text
1. User can start a Market Mind Cards session in the web UI.
2. User can choose training mode.
3. User sees one compact card with chart, exchange, pair, timeframe, cockpit metrics.
4. User can choose ↑ Growth / ↓ Fall / Skip and Small/Medium/Large risk size.
5. UI shows user choice, AI choice, and agreement without harsh criticism.
6. Live cards can be saved pending and verified later.
7. Historical/replay cards can reveal outcome instantly.
8. Session summary compares human vs AI vs market.
9. Learning events accumulate in SQLite.
10. AI confidence/explanation can use past learning summaries.
11. Full tests pass.
12. Dashboard loads with no JS errors.
```

---

## Implementation Notes

Keep the current dashboard and existing Auto Learner. Do not replace them. Add `Market Mind Cards` as the simple front layer above the same intelligence engine.

The long-term product identity:

```text
монстр под капотом
простая карточка сверху
ИИ учится на реальных диаграммах, стакане, признаках рынка и проверенных исходах
решения человека используются отдельно для сравнения, коучинга и UX, но не как истина
```
