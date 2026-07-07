# GitHub push commands

Project path:

```text
C:\Users\brueg\Desktop\projects\crypto-intel-agent
```

Current local branch is ahead of `origin/main`; the app is demo-ready locally.

## Push existing repo

If remote is already configured and credentials work:

```powershell
cd "C:\Users\brueg\Desktop\projects\crypto-intel-agent"
git status
git push origin main
```

## If GitHub CLI is installed and authenticated

```powershell
cd "C:\Users\brueg\Desktop\projects\crypto-intel-agent"
gh repo create crypto-intel-agent --public --source=. --remote=origin --push
```

If `origin` already exists, use only:

```powershell
git push origin main
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
cd "C:\Users\brueg\Desktop\projects\crypto-intel-agent"
git remote add origin https://github.com/KiBrueg/crypto-intel-agent.git
git branch -M main
git push -u origin main
```

If `remote origin already exists`, use:

```powershell
git remote set-url origin https://github.com/KiBrueg/crypto-intel-agent.git
git push -u origin main
```

## Suggested GitHub description

```text
Local crypto market-intelligence and Market Mind Cards trainer demo: dashboard, historical replay cards, similarity stats, forecast-realism calibration, SQLite learning memory. Research/backtesting only.
```

## Suggested topics

```text
python crypto market-data trading-tools backtesting sqlite dashboard trader-education ai-assistant candlestick-charts
```
