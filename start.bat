@echo off
title Blueprint XPU
REM Single entry point: all launch logic lives in start.ps1 (LM Studio primary).
REM ASCII only in this file - CP949 consoles garble UTF-8 Korean comments.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0start.ps1" %*
