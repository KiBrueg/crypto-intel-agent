@echo off
setlocal
cd /d "%~dp0"
echo Starting Crypto Trader Assistant dashboard...
echo.
echo Browser URL: http://127.0.0.1:8765
echo Press Ctrl+C in this window to stop the server.
echo.
start "" http://127.0.0.1:8765
python web_dashboard.py --host 127.0.0.1 --port 8765
pause
