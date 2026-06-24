# Crypto Pro Trader Assistant

**Mode:** decision support only — not financial advice, no automatic trading.

This report compresses the things a pro trader would inspect manually: trend, VWAP/EMA, RSI/ATR, support/resistance, Fibonacci retracements, pivots, and order-book imbalance.

## BTCUSDT — Professional Trader Context
- Price: `59665.15`
- Trend: `bearish`
- EMA9/EMA21: `60731.71435833` / `61625.65316252`
- RSI14: `19.9709` | ATR14: `566.81` | VWAP: `62855.86546582`
- Nearest levels: 59521.29333333, 59939.88666667, 59102.7, 58985.40666667, 60475.77333333, 60498.00782
- Fibonacci 0.382/0.5/0.618: `63132.14034`, `62362.765`, `61593.38966`
- Pivots P/R1/S1: `59521.29333333`, `59939.88666667`, `58985.40666667`
- Order book spread: `0.0017` bps | imbalance: `-0.765962`
- Order book signals: ask wall / sell-side depth dominates, tight spread

### Setup notes
- EMA/VWAP alignment is bearish; shorts or defensive bias may dominate

### Hypothetical risk/reward from nearby levels
- **long_breakout** (valid math): entry `59939.88666667`, stop `59379.59083333`, target `60475.77333333`, R/R `0.9564`. Invalidation: fails if price cannot hold above breakout level. Notes: low reward/risk; may not justify execution risk
- **long_pullback** (valid math): entry `59521.29333333`, stop `59322.90983333`, target `59939.88666667`, R/R `2.11`. Invalidation: fails if support level is lost. Notes: no arithmetic warning
- **short_breakdown** (valid math): entry `59521.29333333`, stop `60081.58916667`, target `59102.7`, R/R `0.7471`. Invalidation: fails if price reclaims breakdown level. Notes: low reward/risk; may not justify execution risk
- **short_rejection** (valid math): entry `59939.88666667`, stop `60138.27016667`, target `59521.29333333`, R/R `2.11`. Invalidation: fails if resistance is accepted and holds. Notes: no arithmetic warning

### Confirmation checklist
- price accepts above/below the relevant level
- volume does not fade immediately
- order book does not flip against the idea
- BTC/ETH context does not invalidate the setup

### Invalidation
- reclaim/failure of the level being watched
- RSI/EMA/VWAP context flips
- spread/liquidity deteriorates
- correlation or BTC/ETH context breaks

### Risk notes
- RSI oversold; downside can continue but mean-reversion traders may watch

## ETHUSDT — Professional Trader Context
- Price: `1571.95`
- Trend: `bearish`
- EMA9/EMA21: `1614.15445318` / `1640.9809445`
- RSI14: `20.9692` | ATR14: `20.65` | VWAP: `1694.84398127`
- Nearest levels: 1570.48, 1588.01, 1552.95, 1543.13, 1601.5173, 1615.36
- Fibonacci 0.382/0.5/0.618: `1693.2051`, `1666.425`, `1639.6449`
- Pivots P/R1/S1: `1570.48`, `1588.01`, `1543.13`
- Order book spread: `0.0636` bps | imbalance: `0.886563`
- Order book signals: bid wall / buy-side depth dominates, tight spread

### Setup notes
- EMA/VWAP alignment is bearish; shorts or defensive bias may dominate

### Hypothetical risk/reward from nearby levels
- **long_breakout** (valid math): entry `1588.01`, stop `1565.3175`, target `1601.5173`, R/R `0.5952`. Invalidation: fails if price cannot hold above breakout level. Notes: low reward/risk; may not justify execution risk
- **long_pullback** (valid math): entry `1570.48`, stop `1563.2525`, target `1588.01`, R/R `2.4255`. Invalidation: fails if support level is lost. Notes: no arithmetic warning
- **short_breakdown** (valid math): entry `1570.48`, stop `1593.1725`, target `1552.95`, R/R `0.7725`. Invalidation: fails if price reclaims breakdown level. Notes: low reward/risk; may not justify execution risk
- **short_rejection** (valid math): entry `1588.01`, stop `1595.2375`, target `1570.48`, R/R `2.4255`. Invalidation: fails if resistance is accepted and holds. Notes: no arithmetic warning

### Confirmation checklist
- price accepts above/below the relevant level
- volume does not fade immediately
- order book does not flip against the idea
- BTC/ETH context does not invalidate the setup

### Invalidation
- reclaim/failure of the level being watched
- RSI/EMA/VWAP context flips
- spread/liquidity deteriorates
- correlation or BTC/ETH context breaks

### Risk notes
- RSI oversold; downside can continue but mean-reversion traders may watch

## SOLUSDT — Professional Trader Context
- Price: `65.76`
- Trend: `bearish`
- EMA9/EMA21: `67.33076318` / `68.40667356`
- RSI14: `25.6997` | ATR14: `0.95642857` | VWAP: `71.25120289`
- Nearest levels: 65.53666667, 66.36333333, 64.71, 66.91206, 64.15333333, 67.74666667
- Fibonacci 0.382/0.5/0.618: `71.06922`, `69.855`, `68.64078`
- Pivots P/R1/S1: `65.53666667`, `66.36333333`, `64.15333333`
- Order book spread: `1.5207` bps | imbalance: `0.440982`
- Order book signals: bid wall / buy-side depth dominates, tight spread

### Setup notes
- EMA/VWAP alignment is bearish; shorts or defensive bias may dominate

### Hypothetical risk/reward from nearby levels
- **long_breakout** (valid math): entry `66.36333333`, stop `65.29755953`, target `66.91206`, R/R `0.5149`. Invalidation: fails if price cannot hold above breakout level. Notes: low reward/risk; may not justify execution risk
- **long_pullback** (valid math): entry `65.53666667`, stop `65.20191667`, target `66.36333333`, R/R `2.4695`. Invalidation: fails if support level is lost. Notes: no arithmetic warning
- **short_breakdown** (valid math): entry `65.53666667`, stop `66.60244047`, target `64.71`, R/R `0.7756`. Invalidation: fails if price reclaims breakdown level. Notes: low reward/risk; may not justify execution risk
- **short_rejection** (valid math): entry `66.36333333`, stop `66.69808333`, target `65.53666667`, R/R `2.4695`. Invalidation: fails if resistance is accepted and holds. Notes: no arithmetic warning

### Confirmation checklist
- price accepts above/below the relevant level
- volume does not fade immediately
- order book does not flip against the idea
- BTC/ETH context does not invalidate the setup

### Invalidation
- reclaim/failure of the level being watched
- RSI/EMA/VWAP context flips
- spread/liquidity deteriorates
- correlation or BTC/ETH context breaks

### Risk notes
- RSI oversold; downside can continue but mean-reversion traders may watch
