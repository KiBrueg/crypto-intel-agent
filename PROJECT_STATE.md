# Project State — Crypto Intel Agent

Path: `C:\Users\brueg\Desktop\projects\crypto-intel-agent`

## Completed

- CoinGecko market intelligence agent
- DexScreener token discovery monitor
- SQLite snapshots
- Markdown/HTML reports
- Tests
- Dockerfile
- GitHub-ready metadata
- n8n workflow blueprint
- LLM summary stub

## Run

```powershell
python .\tests\test_crypto_intel_agent_v2.py
python .\tests\test_dexscreener_monitor.py
python .\crypto_intel_agent_v2.py --per-page 40
python .\dexscreener_monitor.py --query SOL --limit 20
python .\llm_summary_stub.py
```
