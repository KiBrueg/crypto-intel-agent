# 🤖 Crypto Intel Agent v2 Report

**Time:** 2026-06-24 05:06 UTC  
**Universe:** top 40 coins by market cap, vs `USD`  
**Mode:** research/monitoring only — not financial advice.

## Alerts
- **HIGH** LAB (LAB): 24h price move = -11.08%
- **MED** GRAM (Gram (prev. Toncoin)): 24h price move = -8.28%
- **MED** GRAM (Gram (prev. Toncoin)): wide intraday range = +14.10%
- **MED** HYPE (Hyperliquid): 24h price move = -7.23%
- **MED** LAB (LAB): wide intraday range = +21.94%
- **MED** USD1 (USD1): high volume/market-cap = 19.22%
- **MED** USDT (Tether): high volume/market-cap = 26.17%

## Top gainers 24h
- AVAX (Avalanche) — +2.46%, price $6.43, vol $284.5M
- XMR (Monero) — +0.68%, price $321.90, vol $154.3M
- USDG (Global Dollar) — +0.01%, price $0.999987, vol $50.5M
- DAI (Dai) — +0.00%, price $0.999633, vol $159.0M
- USD1 (USD1) — -0.00%, price $0.999067, vol $919.0M

## Top losers 24h
- LAB (LAB) — -11.08%, price $15.09, vol $43.9M
- GRAM (Gram (prev. Toncoin)) — -8.28%, price $1.56, vol $143.4M
- HYPE (Hyperliquid) — -7.23%, price $61.49, vol $751.9M
- ZEC (Zcash) — -6.68%, price $414.21, vol $311.3M
- LTC (Litecoin) — -5.95%, price $41.76, vol $234.7M

## High volume / market-cap attention
- USDT (Tether) — vol/mcap 26.17%, range +0.02%, change -0.01%
- USD1 (USD1) — vol/mcap 19.22%, range +0.15%, change -0.00%
- USDC (USDC) — vol/mcap 15.24%, range +0.04%, change -0.00%
- SUI (Sui) — vol/mcap 13.21%, range +6.37%, change -3.02%
- AVAX (Avalanche) — vol/mcap 10.26%, range +7.47%, change +2.46%

## Highest intraday range
- LAB (LAB) — vol/mcap 0.93%, range +21.94%, change -11.08%
- GRAM (Gram (prev. Toncoin)) — vol/mcap 3.42%, range +14.10%, change -8.28%
- HYPE (Hyperliquid) — vol/mcap 5.50%, range +9.58%, change -7.23%
- ZEC (Zcash) — vol/mcap 4.48%, range +8.44%, change -6.68%
- AVAX (Avalanche) — vol/mcap 10.26%, range +7.47%, change +2.46%

## Automation angle
- Schedule via n8n/Hermes cron.
- Send Telegram alerts when thresholds trigger.
- Store snapshots in SQLite/PostgreSQL.
- Add LLM summary layer.
- Extend with CCXT/Binance/Bybit/Kraken.

## Safety
This tool monitors public market data. It does not execute trades, manage funds, promise returns, or provide financial advice.
