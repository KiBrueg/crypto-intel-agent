@echo off
setlocal
set "PROJECT_DIR=%~dp0"
set "PROJECT_DIR=%PROJECT_DIR:~0,-1%"
set "PYTHONIOENCODING=utf-8"
set "PORT=8765"
set "URL=http://127.0.0.1:%PORT%/trainer"
set "DASHBOARD_URL=http://127.0.0.1:%PORT%"

cd /d "%PROJECT_DIR%" || (
  echo Project folder not found: %PROJECT_DIR%
  pause
  exit /b 1
)

echo Ensuring Auto Learner is running...
start "Crypto Intel Auto Learner" /min "%PROJECT_DIR%\Start_Learning_Autopilot.bat"

netstat -ano | findstr /R /C:":%PORT% .*LISTENING" >nul 2>nul
if %errorlevel%==0 (
  echo Existing Crypto Intel Agent server found on port %PORT%.
  echo Restarting it so the latest trainer and right-side AI helper are loaded...
  for /f "tokens=5" %%P in ('netstat -ano ^| findstr /R /C:":%PORT% .*LISTENING"') do (
    taskkill /PID %%P /F >nul 2>nul
  )
  timeout /t 1 /nobreak >nul
)

echo Starting Crypto Intel Agent trainer...
echo Project: %PROJECT_DIR%
echo Trainer with right-side AI helper: %URL%
echo Full dashboard: %DASHBOARD_URL%

start "Crypto Intel Agent Server" /min cmd /k "cd /d "%PROJECT_DIR%" && python web_dashboard.py --host 127.0.0.1 --port %PORT%"

timeout /t 3 /nobreak >nul
start "" "%URL%"
exit /b 0
