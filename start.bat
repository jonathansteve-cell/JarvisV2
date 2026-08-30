@echo off
setlocal enabledelayedexpansion
title Jarvis V2 - Voice AI Assistant
color 0A

echo.
echo  ============================================================
echo   JARVIS V2 - VOICE AI ASSISTANT
echo  ============================================================
echo.
echo   Starting Voice-Only 3D Interface...
echo.
echo  ============================================================
echo.

cd /d "%~dp0"

REM Check Python
where python >nul 2>nul
if errorlevel 1 (
    echo  [ERROR] Python not found!
    echo.
    echo  Please install Python 3.10+ from:
    echo    https://python.org
    echo.
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist .venv (
    echo  [INFO] First run detected. Setting up environment...
    echo.
    
    python -m venv .venv
    call .venv\Scripts\activate.bat
    
    echo  Installing dependencies...
    python -m pip install --upgrade pip -q
    pip install -r requirements.txt -q
    
    echo  Creating runtime folders...
    if not exist data mkdir data
    if not exist logs mkdir logs
    if not exist screenshots mkdir screenshots
    if not exist documents mkdir documents
    if not exist research mkdir research
    
    if not exist .env (
        if exist .env.example (
            copy .env.example .env >nul
        )
    )
    
    echo.
    echo  Setup complete!
    echo.
) else (
    call .venv\Scripts\activate.bat
)

REM Launch Voice-Only 3D UI
echo  Launching Jarvis V2 Voice AI...
echo.

python launch_voice_ui.py

pause
