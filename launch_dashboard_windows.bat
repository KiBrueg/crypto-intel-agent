@echo off
setlocal
cd /d "%~dp0" || exit /b 1
call "%~dp0Start_Crypto_Intel_Agent.bat"
exit /b %errorlevel%
