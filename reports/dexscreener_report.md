# 🧭 DexScreener Monitor v3 Report

**Time:** 2026-06-24 05:43 UTC  
**Query:** `SOL`  
**Pairs scanned:** 20  
**Mode:** token discovery / monitoring only — not financial advice.

## Alerts
- **MED** SOL on base: high volume/liquidity ratio = 10.83x — https://dexscreener.com/base/0x1131db5977242a03ebead1acd18f80a9a29e5922
- **MED** SOL on base: high volume/liquidity ratio = 12.02x — https://dexscreener.com/base/0xccfa472815563ff9eb2de95c7b2be1ccf91f7f31
- **MED** SOL on base: high volume/liquidity ratio = 2.10x — https://dexscreener.com/base/0x04d25d8f94a2018f8ddde1e7941c625fa1a2c7ce
- **MED** SOL on base: high volume/liquidity ratio = 18.18x — https://dexscreener.com/base/0x415c88a05b75d1a65822d899f4a78b4c0d7cbefd
- **MED** SOL on base: high volume/liquidity ratio = 7.05x — https://dexscreener.com/base/0xbf9d262f0199fea8bef911175b1b313055af4b1b
- **MED** SOL on base: liquidity+volume candidate = liq $261,794.87, vol $2.8M — https://dexscreener.com/base/0x1131db5977242a03ebead1acd18f80a9a29e5922
- **MED** SOL on base: liquidity+volume candidate = liq $278,370.10, vol $3.3M — https://dexscreener.com/base/0xccfa472815563ff9eb2de95c7b2be1ccf91f7f31
- **MED** SOL on base: liquidity+volume candidate = liq $183,016.07, vol $254,755.99 — https://dexscreener.com/base/0xab07de353e15b80fa3b4224d5c8fdf3ac9f50670
- **MED** SOL on base: liquidity+volume candidate = liq $112,488.25, vol $236,551.25 — https://dexscreener.com/base/0x04d25d8f94a2018f8ddde1e7941c625fa1a2c7ce
- **MED** SOL on base: liquidity+volume candidate = liq $197,678.42, vol $203,476.55 — https://dexscreener.com/base/0x8df6dd38d718bd726374521c2dcfe90eb9cb7d43
- **MED** SOL on bsc: liquidity+volume candidate = liq $902,505.61, vol $857,705.28 — https://dexscreener.com/bsc/0xbffec96e8f3b5058b1817c14e4380758fada01ef
- **MED** SOL on solana: liquidity+volume candidate = liq $1.45B, vol $191,769.90 — https://dexscreener.com/solana/ant7fvs9yehgzvxfqh7esifgb2da2cu4a6yybhczepx7

## Top by 24h volume
- SOL/cbBTC on base/aerodrome — price $70.16, change -1.46%, vol $3.3M, liq $278,370.10, vol/liq 12.02x
- SOL/USDC on base/aerodrome — price $70.00, change -1.50%, vol $2.8M, liq $261,794.87, vol/liq 10.83x
- SOL/WBNB on bsc/pancakeswap — price $70.09, change -1.44%, vol $857,705.28, liq $902,505.61, vol/liq 0.95x
- SOL/cbBTC on base/pancakeswap — price $70.07, change -1.39%, vol $541,248.52, liq $29,766.99, vol/liq 18.18x
- SOL/WETH on base/pancakeswap — price $70.07, change -1.40%, vol $254,755.99, liq $183,016.07, vol/liq 1.39x
- SOL/USDC on base/pancakeswap — price $69.98, change -1.49%, vol $236,551.25, liq $112,488.25, vol/liq 2.10x
- SOL/cbBTC on base/pancakeswap — price $70.17, change -1.20%, vol $203,476.55, liq $197,678.42, vol/liq 1.03x
- SOL/USDC on solana/raydium — price $69.27, change n/a, vol $191,769.90, liq $1.45B, vol/liq 0.00x

## Top by liquidity
- SOL/USDC on solana/raydium — price $91.10, change n/a, vol $61,898.32, liq $1.91B, vol/liq 0.00x
- SOL/USDC on solana/raydium — price $88.29, change n/a, vol $61,896.94, liq $1.85B, vol/liq 0.00x
- SOL/USDC on solana/raydium — price $69.27, change n/a, vol $191,769.90, liq $1.45B, vol/liq 0.00x
- SOL/H2O on polkadot/hydration — price $69.82, change -1.21%, vol $2,491.00, liq $11.4M, vol/liq 0.00x
- SOL/USDC on solana/raydium — price $78.36, change -0.03%, vol $61,892.90, liq $7.1M, vol/liq 0.01x
- SOL/#BTB on polygon/sushiswap — price $69.20, change -2.47%, vol $284.79, liq $1.6M, vol/liq 0.00x
- SOL/WBNB on bsc/pancakeswap — price $70.09, change -1.44%, vol $857,705.28, liq $902,505.61, vol/liq 0.95x
- SOL/#BB on arbitrum/sushiswap — price $69.62, change -2.89%, vol $54.95, liq $517,459.67, vol/liq 0.00x

## Automation angle
- Token discovery, DEX monitoring and Telegram alerts.
- Schedule with n8n/Hermes cron.
- Extend with LLM summaries, risk labels and watchlists.
- Safe positioning: monitoring/research only, no automatic trading.
