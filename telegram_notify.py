#!/usr/bin/env python3
"""Send report text/files to Telegram via the Bot API. Stdlib only, no dependencies."""
from __future__ import annotations
import argparse, json, os, re, urllib.error, urllib.parse, urllib.request
from pathlib import Path

API = 'https://api.telegram.org/bot{token}/sendMessage'
MAX_LEN = 4096

def load_env(path='.env'):
    p = Path(path)
    if not p.exists():
        return
    for line in p.read_text(encoding='utf-8').splitlines():
        line = line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        key, _, value = line.partition('=')
        key = key.strip()
        if key and key not in os.environ:
            os.environ[key] = value.strip()

def plain_text(md: str) -> str:
    """Strip markdown decoration so Telegram doesn't choke on unescaped MarkdownV2 chars."""
    text = re.sub(r'^#{1,6}\s*', '', md, flags=re.MULTILINE)
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    text = re.sub(r'^-\s+', '• ', text, flags=re.MULTILINE)
    return text.strip()

def truncate(text: str, limit: int = MAX_LEN) -> str:
    if len(text) <= limit:
        return text
    return text[: limit - 20].rstrip() + '\n\n… (truncated)'

def send_telegram_message(text: str, token: str | None = None, chat_id: str | None = None) -> dict:
    token = token or os.environ.get('TELEGRAM_BOT_TOKEN')
    chat_id = chat_id or os.environ.get('TELEGRAM_CHAT_ID')
    if not token or not chat_id:
        raise RuntimeError('TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID not set (env or .env)')
    body = json.dumps({'chat_id': chat_id, 'text': truncate(plain_text(text)), 'disable_web_page_preview': True}).encode()
    req = urllib.request.Request(API.format(token=token), data=body, headers={'Content-Type': 'application/json'}, method='POST')
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        raise RuntimeError(f'Telegram API error {e.code}: {e.read().decode(errors="replace")}') from e

def notify_safe(text: str, token: str | None = None, chat_id: str | None = None) -> bool:
    """Best-effort send for use inside report scripts — never raises, prints a warning instead."""
    try:
        send_telegram_message(text, token, chat_id)
        return True
    except Exception as e:
        print(f'WARN telegram send skipped: {e}')
        return False

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('report', nargs='?', help='Path to a report file (.md) to send')
    ap.add_argument('--text', help='Send this text instead of a file')
    a = ap.parse_args()
    load_env()
    if not a.report and not a.text:
        raise SystemExit('Provide a report file path or --text')
    text = a.text if a.text else Path(a.report).read_text(encoding='utf-8')
    result = send_telegram_message(text)
    print('OK sent' if result.get('ok') else f'FAILED {result}')

if __name__ == '__main__':
    main()
