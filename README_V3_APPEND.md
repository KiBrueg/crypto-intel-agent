
## v3 DexScreener monitor

Additional DEX/token discovery monitor:

```powershell
cd "$env:USERPROFILE\Downloads\crypto_intel_agent_v2"
python .\dexscreener_monitor.py --query SOL --limit 20
```

Run v3 test:

```powershell
python .\tests\test_dexscreener_monitor.py
```

Outputs:

```text
reports\dexscreener_report.md
reports\dexscreener_report.html
DEXSCREENER_V3_RUN_LOG.txt
```

Use this as a second portfolio angle: DEX token discovery, liquidity/volume monitoring, Telegram alert candidates, and safe AI/crypto automation.
