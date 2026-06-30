@echo off
setlocal
set "PROJECT_DIR=C:\Users\brueg\Desktop\projects\crypto-intel-agent"
set "PORT=8765"
set "URL=http://127.0.0.1:%PORT%"

cd /d "%PROJECT_DIR%" || (
  echo Project folder not found: %PROJECT_DIR%
  pause
  exit /b 1
)

echo Ensuring Auto Learner is running...
start "Crypto Intel Auto Learner" /min "%PROJECT_DIR%\Start_Learning_Autopilot.bat"

netstat -ano | findstr /R /C:":%PORT% .*LISTENING" >nul 2>nul
if %errorlevel%==0 (
  echo Crypto Intel Agent is already running on %URL%
  start "" "%URL%"
  exit /b 0
)

echo Starting Crypto Intel Agent dashboard...
echo Project: %PROJECT_DIR%
echo URL: %URL%

start "Crypto Intel Agent Server" /min cmd /k "cd /d "%PROJECT_DIR%" && python web_dashboard.py --host 127.0.0.1 --port %PORT%"

timeout /t 3 /nobreak >nul
start "" "%URL%"
exit /b 0
