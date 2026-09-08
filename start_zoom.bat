@echo off
chcp 65001 >nul
title Zoom Automation Launcher
cd /d "%~dp0"

echo ==========================================
echo       Zoom Automation Launcher
echo ==========================================
echo.

if not exist "venv\Scripts\python.exe" (
    echo [ERROR] Виртуальное окружение не найдено!
    echo Сначала запустите setup.bat для установки Python и зависимостей.
    echo.
    pause
    exit /b 1
)

"venv\Scripts\python.exe" zoom.py

echo.
echo ==========================================
echo Скрипт завершил работу или произошла ошибка.
echo ==========================================
pause
