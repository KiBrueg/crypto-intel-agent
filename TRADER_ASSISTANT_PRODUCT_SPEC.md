# Trader Assistant Product Spec

Decision-support tool for experienced crypto traders. It does not replace the trader and does not execute orders. It saves time by collecting market context, ranking candidates by strategy, and showing confirmation/invalidation/risk notes.

## Strategy families

### Scalping

Watch: spread, liquidity, short-term volume, volatility, nearby levels, fees/slippage.

Output: liquid scalping candidates, spread/liquidity warnings, short-term setup context.

### Intraday momentum / breakout

Watch: price near range high/low, volume expansion, trend alignment, volatility compression/expansion, BTC/ETH context.

Output: breakout candidates with confirmation and failed-breakout risk.

### Mean reversion

Watch: overextension from rolling mean/VWAP, z-score extremes, exhaustion volume, market regime.

Output: overextended assets where reversal traders may want to inspect manually.

### Pair trading / relative value

Watch: correlated pairs, spread z-score, correlation stability, hedge ratio, sector relationships.

Output: pair divergence watchlist with correlation-breakdown warnings.

### Funding / basis / carry later

Watch: perp funding, spot-perp basis, borrow/funding costs, liquidation/crowding risk.

## Important missing pieces to build next

- Market regime filter.
- Liquidity/spread/slippage filter.
- Multi-timeframe confirmation.
- Relative strength vs BTC/ETH/sector.
- Invalidation levels.
- Change detection since previous scan.
- Post-signal journal to measure whether flagged setups worked.

## Safety boundaries

Use language like candidate, watchlist, confirmation, invalidation, risk flag. Avoid buy/sell instructions, profit claims, automatic execution, private keys, and exchange trading permissions.
