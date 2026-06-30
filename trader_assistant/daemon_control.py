from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from trader_assistant.autopilot_status import build_autopilot_status


def daemon_start_command(root_dir, symbols='BTCUSDT,ETHUSDT,SOLUSDT', interval='15m', horizon=4, sleep=900):
    root = Path(root_dir)
    return [
        sys.executable,
        str(root / 'learning_daemon.py'),
        '--symbols', str(symbols),
        '--interval', str(interval),
        '--horizon', str(int(horizon)),
        '--sleep', str(int(sleep)),
    ]


def ensure_learning_daemon(root_dir=None, stale_after_seconds=1800):
    root = Path(root_dir) if root_dir else Path(__file__).resolve().parents[1]
    status = build_autopilot_status(root_dir=root, stale_after_seconds=stale_after_seconds)
    if (status.get('daemon') or {}).get('state') == 'active':
        return {'started': False, 'reason': 'already_active', 'status': status}
    cmd = daemon_start_command(root)
    kwargs = {
        'cwd': str(root),
        'stdout': subprocess.DEVNULL,
        'stderr': subprocess.DEVNULL,
        'stdin': subprocess.DEVNULL,
    }
    if sys.platform.startswith('win'):
        kwargs['creationflags'] = getattr(subprocess, 'CREATE_NEW_PROCESS_GROUP', 0) | getattr(subprocess, 'DETACHED_PROCESS', 0)
    subprocess.Popen(cmd, **kwargs)
    return {'started': True, 'reason': 'spawned', 'command': cmd}
