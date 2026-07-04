@echo off
setlocal
cd /d "%~dp0"
set "PYTHONIOENCODING=utf-8"
echo Starting Crypto Trader Assistant trainer...
echo.
echo Browser URL with right-side AI helper: http://127.0.0.1:8765/trainer
echo Full dashboard URL: http://127.0.0.1:8765
echo Press Ctrl+C in this window to stop the server.
echo.
start "" http://127.0.0.1:8765/trainer
python web_dashboard.py --host 127.0.0.1 --port 8765
pause
