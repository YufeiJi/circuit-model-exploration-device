@echo off
chcp 65001 >nul
cd /d "%~dp0"
title 电路模型探究装置 - 调试台

set "PORT=8765"

rem ---------- 找一个能用的本地端口 ----------
:chkport
netstat -ano | findstr /C:":%PORT%" | findstr /C:"LISTENING" >nul
if not errorlevel 1 (
  set /a PORT=%PORT%+1
  if %PORT% GTR 8795 goto noport
  goto chkport
)
goto haveport

:noport
echo [错误] 8765-8795 端口都被占用了，请手动关掉占用程序后重试。
pause
exit /b 1

:haveport

rem ---------- 找一个能用的 python ----------
set "PY="
for %%P in (
  "C:/Users/Yufei Ji/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe"
  "D:/Anaconda3/python.exe"
) do if not defined PY if exist %%P set "PY=%%~P"

if not defined PY (
  where python >nul 2>nul && set "PY=python"
)
if not defined PY (
  echo [错误] 没找到 Python。浏览器要求页面跑在 localhost 上才能访问串口和 USB，
  echo        所以需要一个本地静态服务。装个 Python 或用 Anaconda 都行。
  pause
  exit /b 1
)

echo.
echo   电路模型探究装置 - 调试台
echo   ----------------------------------------
echo   本地服务  http://127.0.0.1:%PORT%/
echo   Python    %PY%
echo.
echo   保持这个窗口开着。用完直接关掉它，服务就停了。
echo.

start "" /b "%PY%" -m http.server %PORT% --bind 127.0.0.1
timeout /t 2 /nobreak >nul

rem ---------- 用 Edge 的独立窗口打开 ----------
set "EDGE=C:/Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
if not exist "%EDGE%" set "EDGE=C:/Program Files\Microsoft\Edge\Application\msedge.exe"

if exist "%EDGE%" (
  start "" "%EDGE%" --app=http://127.0.0.1:%PORT%/ --window-size=1180,820
) else (
  echo [提示] 没找到 Edge，改用默认浏览器打开。
  echo        Firefox 不支持 Web Serial 和 WebUSB，请手动用 Chrome 打开下面的地址。
  start "" http://127.0.0.1:%PORT%/
)

echo   已打开调试台。按任意键停止服务并退出。
pause >nul
