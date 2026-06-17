@echo off
title Blueprint NPU

echo.
echo ============================================================
echo  Blueprint NPU - Local Launcher
echo ============================================================
echo.

REM -- 1. Check if Ollama is already running --
curl -s http://127.0.0.1:11434/api/tags >nul 2>&1
if %errorlevel% == 0 (
    echo [OK] Ollama already running at :11434
    goto :start_server
)

REM -- 2. Start Ollama (portable, visible window) --
echo [..] Starting Ollama...
if exist "%~dp0..\ollama.exe" (
    start "Ollama IPEX" "%~dp0..\ollama.exe" serve
) else (
    echo [ERR] ollama.exe not found at: %~dp0..
    echo       Check that ollama.exe is in C:\Ollama-IPEX\
    pause
    exit /b 1
)

REM -- 3. Wait for Ollama (max 20s) --
echo [..] Waiting for Ollama to start...
set /a count=0
:wait_loop
timeout /t 1 /nobreak >nul
curl -s http://127.0.0.1:11434/api/tags >nul 2>&1
if %errorlevel% == 0 goto :ollama_ready
set /a count+=1
if %count% geq 20 (
    echo [ERR] Ollama did not start within 20 seconds
    pause
    exit /b 1
)
goto :wait_loop

:ollama_ready
echo [OK] Ollama online at :11434

:start_server
REM -- 4. Check if port 8080 is already in use --
netstat -ano | findstr ":8080 " | findstr "LISTEN" >nul 2>&1
if %errorlevel% == 0 (
    echo [OK] HTTP server already running at :8080
    goto :open_browser
)

REM -- 5. Start Python HTTP server (background, minimized) --
echo [..] Starting HTTP server on :8080...
where python >nul 2>&1
if %errorlevel% == 0 (
    start "Blueprint HTTP" /min python "%~dp0server\serve.py" --no-browser
    timeout /t 2 /nobreak >nul
    echo [OK] HTTP server running at http://127.0.0.1:8080
) else (
    echo [ERR] Python not found. Please install Python.
    pause
    exit /b 1
)

:open_browser
REM -- 6. Open Minimal.html directly --
echo.
echo [..] Opening Blueprint NPU...
start http://127.0.0.1:8080/Minimal.html

echo.
echo ============================================================
echo  Blueprint NPU is running
echo  Ollama  : http://127.0.0.1:11434
echo  Design  : http://127.0.0.1:8080/Minimal.html
echo  Home    : http://127.0.0.1:8080
echo ============================================================
echo.
echo  Close Ollama window to stop Ollama.
echo  To stop HTTP server: close the minimized Blueprint HTTP window.
echo.
pause
