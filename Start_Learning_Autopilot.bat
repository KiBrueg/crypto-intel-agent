@echo off
setlocal
cd /d "%~dp0" || exit /b 1
set "PYTHONIOENCODING=utf-8"
python learning_daemon.py --symbols BTCUSDT,ETHUSDT,SOLUSDT --interval 15m --horizon 4 --sleep 900
exit /b %errorlevel%
