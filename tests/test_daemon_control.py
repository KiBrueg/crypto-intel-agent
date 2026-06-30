#!/usr/bin/env python3
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parents[1]))

from trader_assistant.daemon_control import daemon_start_command


def test_daemon_start_command_uses_current_python_and_learning_daemon():
    root = Path('C:/demo/project')
    cmd = daemon_start_command(root, symbols='BTCUSDT,ETHUSDT', interval='15m', horizon=4, sleep=900)
    assert Path(cmd[0]).name.lower().startswith('python')
    assert str(root / 'learning_daemon.py') in cmd
    assert '--symbols' in cmd and 'BTCUSDT,ETHUSDT' in cmd
    assert '--interval' in cmd and '15m' in cmd
    assert '--horizon' in cmd and '4' in cmd


if __name__ == '__main__':
    test_daemon_start_command_uses_current_python_and_learning_daemon()
    print('OK daemon control tests passed')
