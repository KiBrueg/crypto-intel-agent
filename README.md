# Crypto Intel Agent

Safe AI/crypto market-intelligence automation demo for monitoring public crypto/DEX market data, detecting volatility/liquidity/volume alerts, storing SQLite snapshots, and generating Telegram-ready reports.

> Monitoring and research only. No automatic trading, no client-fund management, no promised returns, no financial advice.

## Features

- CoinGecko market monitor: top crypto assets, 24h moves, volume/market-cap, intraday range.
- DexScreener monitor: DEX pair discovery, liquidity/volume candidates, high volume/liquidity ratio.
- SQLite snapshots.
- Markdown and HTML reports.
- Optional Telegram delivery path.
- Offline LLM summary stub for safe summaries.
- Tests and GitHub Actions CI.
- Dockerfile and n8n workflow blueprint.

## Quick start on Windows

```powershell
cd "C:\Users\brueg\Desktop\projects\crypto-intel-agent"
python .\crypto_intel_agent_v2.py --per-page 40
python .\dexscreener_monitor.py --query SOL --limit 20
python .\llm_summary_stub.py .\reports\crypto_intel_report.md
```

## Tests

```powershell
python .\tests\test_crypto_intel_agent_v2.py
python .\tests\test_dexscreener_monitor.py
```

## GitHub push

```powershell
git init
git add .
git commit -m "Initial Crypto Intel Agent MVP"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/crypto-intel-agent.git
git push -u origin main
```
