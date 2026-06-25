# Classic Pattern Hints — Source Notes

This project uses classic technical-analysis pattern concepts as **decision-support hints**, not as automatic trade signals.

## Pattern families implemented

- Candlestick reversals:
  - bullish engulfing
  - bearish engulfing
  - hammer
  - shooting star
  - doji / indecision
- Chart structures:
  - double top
  - double bottom
  - volatility compression / symmetrical triangle watch
  - bull flag watch
  - bear flag watch

## Educational lineage

These are common, widely taught concepts across recognized technical-analysis education rather than proprietary rules from one trader.

Useful names/sources to study further:

- Edwards & Magee — classical chart pattern language: trendlines, support/resistance, tops/bottoms.
- Thomas Bulkowski — statistical cataloging of chart patterns and failure rates.
- Steve Nison — candlestick pattern terminology and interpretation.
- Richard Wyckoff / Wyckoff method — accumulation/distribution, springs, upthrusts, volume confirmation.
- Linda Bradford Raschke — short-term price action, failed breaks, classic setups.
- Brian Shannon — multi-timeframe analysis and VWAP/anchored VWAP context.
- Al Brooks — price action, failed breakouts, ranges and trend bars.
- Mark Minervini — trend templates, contraction/volatility tightening and risk control.

## How the dashboard should use patterns

A pattern is only a prompt to investigate:

```text
pattern + level + volume/order book + multi-timeframe agreement + risk/reward
```

Do **not** treat a pattern by itself as a trading instruction.

Examples:

- Double top: useful only if price accepts below neckline; otherwise it can become a failed breakdown/reclaim.
- Double bottom: useful only if price accepts above neckline; otherwise it remains a range.
- Bull flag: useful only if consolidation is shallow and the range high breaks with participation.
- Hammer: useful only if follow-through holds the low and reclaims a meaningful level/VWAP.
- Shooting star: useful only if price fails below the rejection high.

## Why this is conservative

The detector intentionally produces **hints** with confidence scores. It avoids pretending that a pattern is certain. The trader still checks:

- market regime
- BTC/ETH context
- liquidity/spread
- order-book imbalance
- volatility/ATR
- invalidation
- R/R at the actual entry
