#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from trader_assistant.binance_public import fetch_klines
from trader_assistant.journal import DEFAULT_DB, init_journal
from trader_assistant.learning_autopilot import run_learning_cycle
from web_dashboard import build_snapshot_payload

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / 'data'
LOCK_PATH = DATA_DIR / 'learning_autopilot.lock'
HEARTBEAT_PATH = DATA_DIR / 'learning_autopilot_heartbeat.json'
LOG_PATH = DATA_DIR / 'learning_autopilot.log'


def _now():
    return datetime.now(timezone.utc).isoformat()


def _log(message):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    line = f"{_now()} {message}\n"
    with LOG_PATH.open('a', encoding='utf-8') as f:
        f.write(line)
    print(line, end='', flush=True)


def _heartbeat(payload):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    payload = {'updated_at': _now(), **payload}
    HEARTBEAT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')


def _lock_is_fresh(max_age_seconds=7200):
    if not LOCK_PATH.exists():
        return False
    try:
        age = time.time() - LOCK_PATH.stat().st_mtime
        return age < max_age_seconds
    except Exception:
        return True


def acquire_lock():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if _lock_is_fresh():
        _log('another learning daemon appears active; exiting')
        return False
    LOCK_PATH.write_text(json.dumps({'pid': os.getpid(), 'started_at': _now()}), encoding='utf-8')
    return True


def release_lock():
    try:
        if LOCK_PATH.exists():
            LOCK_PATH.unlink()
    except Exception:
        pass


def parse_args():
    p = argparse.ArgumentParser(description='Crypto Intel Agent automatic learner')
    p.add_argument('--symbols', default='BTCUSDT,ETHUSDT,SOLUSDT', help='comma-separated symbols')
    p.add_argument('--interval', default='15m')
    p.add_argument('--side', default='long')
    p.add_argument('--horizon', type=int, default=4)
    p.add_argument('--sleep', type=int, default=900, help='seconds between cycles')
    p.add_argument('--once', action='store_true', help='run one cycle and exit')
    return p.parse_args()


def run_once(symbols, interval, side, horizon):
    con = init_journal(DEFAULT_DB)
    results = []
    try:
        for symbol in symbols:
            try:
                result = run_learning_cycle(
                    con,
                    symbol=symbol,
                    interval=interval,
                    side=side,
                    snapshot_builder=lambda symbol, interval, side: build_snapshot_payload(symbol=symbol, interval=interval, side=side),
                    klines_fetcher=fetch_klines,
                    horizon_bars=horizon,
                )
                compact = {
                    'symbol': symbol,
                    'prediction_id': result.get('prediction_id'),
                    'total': result.get('total'),
                    'verified': result.get('verified'),
                    'pending': result.get('pending'),
                    'direction_accuracy': result.get('direction_accuracy'),
                }
                results.append(compact)
                _log(f"cycle ok {json.dumps(compact, ensure_ascii=False)}")
            except Exception as exc:
                results.append({'symbol': symbol, 'error': str(exc)})
                _log(f"cycle error {symbol}: {exc}")
    finally:
        con.close()
    _heartbeat({'symbols': symbols, 'interval': interval, 'side': side, 'horizon': horizon, 'results': results})
    return results


def main():
    args = parse_args()
    symbols = [s.strip().upper() for s in args.symbols.split(',') if s.strip()]
    if not acquire_lock():
        return 0
    _log(f"learning daemon started symbols={symbols} interval={args.interval} horizon={args.horizon} sleep={args.sleep}")
    try:
        while True:
            run_once(symbols, args.interval, args.side, args.horizon)
            if args.once:
                break
            time.sleep(max(60, int(args.sleep)))
    finally:
        _log('learning daemon stopped')
        release_lock()
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
