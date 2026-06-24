#!/usr/bin/env python3
from pathlib import Path
import argparse

def build_summary_prompt(report_text: str) -> str:
    return f"""You are a cautious crypto/fintech market-intelligence summarizer. Do not provide financial advice, trading signals, buy/sell instructions, or promises of returns.

Report:
---
{report_text[:8000]}
---

Return: executive summary, anomalies, caveats, automation opportunities, safety disclaimer.
"""

def offline_summary(report_text: str) -> str:
    alerts=[l.strip() for l in report_text.splitlines() if l.strip().startswith('- **')][:10]
    return '# Offline LLM Summary Stub\n\n' + '\n'.join(alerts or ['- No alert lines detected.']) + '\n\nMonitoring only. Not financial advice.\n'

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('report', nargs='?', default='reports/crypto_intel_report.md'); ap.add_argument('--prompt-out', default='reports/llm_summary_prompt.txt'); ap.add_argument('--summary-out', default='reports/llm_summary_stub.md'); a=ap.parse_args()
    text=Path(a.report).read_text(encoding='utf-8') if Path(a.report).exists() else '# Empty report\n'
    Path(a.prompt_out).parent.mkdir(parents=True, exist_ok=True); Path(a.prompt_out).write_text(build_summary_prompt(text), encoding='utf-8'); Path(a.summary_out).write_text(offline_summary(text), encoding='utf-8'); print(f'OK prompt={a.prompt_out} summary={a.summary_out}')
if __name__=='__main__': main()
