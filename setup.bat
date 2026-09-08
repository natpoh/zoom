@echo off
chcp 65001 >nul
title Zoom Automation Setup
cd /d "%~dp0"

echo ==========================================
echo    Запуск установки Zoom Automation
echo ==========================================
echo.

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0setup.ps1"

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Произошла ошибка во время установки!
    pause
)
