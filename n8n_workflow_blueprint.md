# n8n Workflow Blueprint — Crypto Intel Agent

Cron Trigger -> run Python monitor -> read Markdown report -> send Telegram -> optional Notion row -> error Telegram.

## Daily market monitor

```bash
python crypto_intel_agent_v2.py --per-page 80
```

## DEX discovery monitor

```bash
python dexscreener_monitor.py --query SOL --limit 30
python dexscreener_monitor.py --query AI --limit 30
```

## Safety

Monitoring/research only. No automatic trading, no fund management, no guaranteed returns, no financial advice.
