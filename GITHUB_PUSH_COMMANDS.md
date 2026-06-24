# GitHub push commands

Recommended repository name:

```text
crypto-intel-agent
```

## If GitHub CLI is installed and authenticated

```powershell
cd "$env:USERPROFILE\Downloads\crypto_intel_agent_v2"
git init
git add .
git commit -m "Initial Crypto Intel Agent MVP"
gh repo create crypto-intel-agent --public --source=. --remote=origin --push
```

## If you created the repo manually on GitHub

Create this repo in the browser first:

```text
https://github.com/new
```

Repository name:

```text
crypto-intel-agent
```

Then run:

```powershell
cd "$env:USERPROFILE\Downloads\crypto_intel_agent_v2"
git init
git add .
git commit -m "Initial Crypto Intel Agent MVP"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/crypto-intel-agent.git
git push -u origin main
```

## Suggested GitHub description

```text
Safe AI/crypto market intelligence automation demo: CoinGecko data ingestion, SQLite snapshots, threshold alerts, Markdown/HTML reports, optional Telegram delivery.
```

## Suggested topics

```text
python crypto automation market-data telegram-bot sqlite fintech ai-automation coingecko trading-tools
```
