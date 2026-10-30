@echo off
chcp 65001 >nul
cd /d "%~dp0"
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1

set "PY=C:/Users/Yufei Ji\.workbuddy-ai\binaries\python\envs\dfu\Scripts\python.exe"

if exist "%PY%" goto run

echo.
echo [ERROR] Python venv not found at:
echo         %PY%
echo.
echo Trying system python instead...
where py >nul 2>nul && (set "PY=py -3") || (set "PY=python")

:run
echo Using: %PY%
echo.
"%PY%" flash_dfu.py %*
set RC=%ERRORLEVEL%
echo.
pause
exit /b %RC%
