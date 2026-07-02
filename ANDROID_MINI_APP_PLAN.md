# Mind Cards — Android Mini App Plan

Consolidated from a planning session. Source mechanic already exists in
`trader_assistant/mind_cards.py` + `web_dashboard.py`
(`/api/mind-card/*`): show a real historical chart, user guesses
up/down, AI guesses too, both get checked against the real future
candles. Positioning: **"beat an AI with a public, verifiable track
record"** — not another swipe-to-trade app, not a prediction market
(no real money — keeps this out of gambling/copy-trading regulation).

Competitors checked: Polyswipe (Tinder-for-Polymarket, real-money,
ships as PWA — no app store), CoinMarketCap/Stocktwits sentiment
voting (aggregate opinion, no ground-truth check), Invstr (paper
trading tournaments). None of them pair a self-verifying AI accuracy
record with a real-chart guessing game — that pairing is the actual
differentiator here, not the swipe UI.

---

## Phase 0 — Foundation (blocks everything public/mobile)

Required before any Android client can talk to this safely.

- [ ] API key / token auth on `web_dashboard.py` endpoints
- [ ] Rate limiting on `/api/mind-card/*` and anything that calls out
      to Binance per-request (currently unauthenticated + unlimited —
      server can be used as a free proxy to hammer Binance)
- [ ] Allowlist validation on `symbol`/`interval` query params
- [ ] Wire `session_id` through `/api/mind-card/next` and
      `/api/mind-card/choice` (`save_mind_card()` already accepts it,
      the endpoint just never passes it — currently all users write
      into one anonymous bucket)
- [ ] Move from SQLite to Postgres for concurrent writes (reuse the
      existing VPS Postgres container from the JobRadar project —
      separate database, not shared schema)
- [ ] Deploy `web_dashboard.py` behind HTTPS reverse proxy on the VPS
      (Caddy/nginx) instead of `127.0.0.1` on a Windows laptop

## Phase 1 — Personal layer (ships solo, no other users needed)

Useful from day one, doesn't depend on user growth — build this
before the social layer, not after.

- [ ] Personal calibration chart: your accuracy vs AI's accuracy over
      time (data already computed by `learning_autopilot.prediction_stats()`,
      just needs a line chart reusing the existing canvas code)
- [ ] Post-guess "why" explanation — call `coach.build_trader_coach()`
      after reveal (already written, currently unused by mind cards —
      wiring only, no new logic)
- [ ] Personal "trophy case" — best-week ratio (e.g. 40/50), longest
      streak, biggest AI-beat margin. Pure aggregation over existing
      `mind_cards` rows, private to the user, no other names involved
- [ ] Daily free-card cap + streak counter (Wordle/Duolingo-hearts
      pattern) — one counter, creates a daily-return reason

## Phase 2 — Social layer (needs a real user base to be meaningful)

Don't build before Phase 0/1 ship and there are enough users for
comparison to mean anything.

- [ ] Global leaderboard ranked by accuracy, gated to a minimum
      sample size (e.g. 50+ verified calls) before anyone is shown as
      "top" — protects against a lucky streak reading as skill
- [ ] Shareable result card: canvas → PNG → native Android share
      sheet, surfaced only at achievement moments (beat-AI-for-the-week,
      streak milestone) — not a permanent always-visible button
- [ ] Stories rail of top predictors, **strictly opt-in**: eligible
      user gets a one-time prompt to self-publish
      (`published=true` flag); no editorial curation, no auto-blast.
      Story shows accuracy + sample size inline (e.g. "62% · 84 calls")
      so it never reads as "guaranteed skill"
- [ ] (v2, only if data shows the global leaderboard demotivates new
      users) weekly cohort leagues, Duolingo-style promote/demote

## Explicitly deferred / rejected

- **Real-money staking or copy-trading** — the one thing that would
  turn this from a hobby app into a regulated financial product.
  Keep it a practice/accuracy game, not a betting product.
- **Push notifications for re-engagement** — conflicts with the
  "don't spam" constraint set for this project. Revisit only if
  opt-in and rare, and only after there's real churn data to justify it.

## Distribution path

- **Path A (start here):** PWA + TWA wrapper (Bubblewrap) around the
  existing dashboard once it's on HTTPS. Closest real competitor
  (Polyswipe) ships this way too — not a compromise, it's the proven
  path for this category.
- **Path B (later, only if traction justifies it):** small native
  Kotlin/Compose app scoped to just the mind-card endpoints — better
  push notifications, home-screen widget (streak / AI accuracy), more
  native feel. Don't port the full trader dashboard (TA/order
  book/SMC) — that's a different, more niche audience.
