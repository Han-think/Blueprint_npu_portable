@echo off
title Blueprint NPU · Start

echo.
echo  ============================================================
echo   Blueprint NPU  ^|  Local Launcher
echo  ============================================================
echo.

REM ── 1. Ollama 이미 실행 중인지 확인 ──────────────────────────
curl -s http://127.0.0.1:11434/api/tags >nul 2>&1
if %errorlevel% == 0 (
    echo  [OK]  Ollama already running at :11434
    goto :start_server
)

REM ── 2. Ollama 시작 ───────────────────────────────────────────
echo  [..] Starting Ollama IPEX...
if exist "C:\Ollama-IPEX\ollama.exe" (
    start "Ollama IPEX" /min "C:\Ollama-IPEX\ollama.exe" serve
) else (
    echo  [ERR] C:\Ollama-IPEX\ollama.exe not found
    echo        Check your Ollama-IPEX installation path.
    pause
    exit /b 1
)

REM ── 3. Ollama 준비 대기 (최대 15초) ─────────────────────────
echo  [..] Waiting for Ollama to start...
set /a count=0
:wait_loop
timeout /t 1 /nobreak >nul
curl -s http://127.0.0.1:11434/api/tags >nul 2>&1
if %errorlevel% == 0 goto :ollama_ready
set /a count+=1
if %count% geq 15 (
    echo  [ERR] Ollama did not start within 15 seconds.
    pause
    exit /b 1
)
goto :wait_loop

:ollama_ready
echo  [OK]  Ollama online at :11434

:start_server
REM ── 4. Python HTTP 서버 시작 ─────────────────────────────────
echo  [..] Starting local HTTP server on :8080...
where python >nul 2>&1
if %errorlevel% == 0 (
    start "Blueprint HTTP" /min cmd /c "cd /d "%~dp0" && python server\serve.py"
    timeout /t 2 /nobreak >nul
    echo  [OK]  HTTP server running at http://127.0.0.1:8080
    echo.
    echo  ── Opening browser ──────────────────────────────────────
    start http://127.0.0.1:8080
) else (
    echo  [WARN] Python not found — opening index.html directly
    echo         (CORS errors may occur — install Python if needed)
    start "" "%~dp0index.html"
)

echo.
echo  Blueprint NPU is running.
echo  Ollama   : http://127.0.0.1:11434
echo  Browser  : http://127.0.0.1:8080
echo.
echo  Close this window to stop monitoring (servers keep running).
pause
