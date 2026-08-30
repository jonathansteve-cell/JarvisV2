@echo off
setlocal enabledelayedexpansion
title Jarvis V2 - Python Runner
color 0B

echo.
echo  ============================================================
echo   JARVIS V2 - PYTHON RUNNER
echo  ============================================================
echo.
echo   This script runs Python scripts with the Jarvis environment.
echo.
echo  ============================================================
echo.

cd /d "%~dp0"

REM Check if virtual environment exists
if not exist .venv (
    echo  [ERROR] Virtual environment not found!
    echo.
    echo  Please run start.bat first to set up the environment.
    echo.
    pause
    exit /b 1
)

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Check if script was provided
if "%~1"=="" (
    echo  Usage:
    echo    python_runner.bat ^<script.py^> [arguments]
    echo.
    echo  Examples:
    echo    python_runner.bat main.py --gui
    echo    python_runner.bat test_ai.py
    echo    python_runner.bat setup_apis.py
    echo.
    echo  Available scripts:
    echo    - main.py              Main application
    echo    - desktop_app.py       Desktop application
    echo    - setup_apis.py        API setup wizard
    echo    - test_*.py            Test scripts
    echo.
    pause
    exit /b 0
)

REM Run the script
echo  Running: %*
echo.

python %*

if errorlevel 1 (
    echo.
    echo  [ERROR] Script failed with error code %errorlevel%
    echo.
)

pause
