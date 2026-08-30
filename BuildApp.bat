@echo off
setlocal enabledelayedexpansion
title Jarvis V2 - Application Builder
color 0A

echo.
echo  ============================================================
echo   JARVIS V2 - APPLICATION BUILDER
echo  ============================================================
echo.
echo   This script will build Jarvis V2 as a desktop application
echo   and create an installer (Install.exe).
echo.
echo  ============================================================
echo.

cd /d "%~dp0"

REM ---------------------------------------------------------------
REM  Check Python
REM ---------------------------------------------------------------
echo [1/5] Checking Python...
where python >nul 2>nul
if errorlevel 1 (
    echo.
    echo  [ERROR] Python is not installed!
    echo.
    echo  Please install Python 3.10+ from:
    echo    https://python.org
    echo.
    echo  IMPORTANT: Check "Add python.exe to PATH" during installation!
    echo.
    pause
    exit /b 1
)

for /f "tokens=2 delims= " %%v in ('python --version 2^>^&1') do set PYVER=%%v
echo         Python %PYVER% found. [OK]

REM ---------------------------------------------------------------
REM  Create virtual environment
REM ---------------------------------------------------------------
echo.
echo [2/5] Setting up build environment...

if not exist .venv (
    echo         Creating virtual environment...
    python -m venv .venv
    if errorlevel 1 (
        echo  [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
) else (
    echo         Virtual environment exists.
)

call .venv\Scripts\activate.bat

REM ---------------------------------------------------------------
REM  Install dependencies
REM ---------------------------------------------------------------
echo.
echo [3/5] Installing dependencies...

python -m pip install --upgrade pip -q 2>nul
pip install -r requirements.txt -q
pip install pyinstaller pillow -q

echo         Dependencies installed. [OK]

REM ---------------------------------------------------------------
REM  Build application
REM ---------------------------------------------------------------
echo.
echo [4/5] Building Jarvis V2 application...
echo         This may take 3-5 minutes...
echo.

REM Generate icons
python packaging\make_icon.py >nul 2>nul
python packaging\create_installer_images.py >nul 2>nul

REM Build with PyInstaller
pyinstaller --noconfirm --clean packaging\jarvis_desktop.spec

if errorlevel 1 (
    echo.
    echo  [ERROR] Build failed! Trying alternative spec...
    pyinstaller --noconfirm --clean packaging\jarvis.spec
    if errorlevel 1 (
        echo.
        echo  [ERROR] Build failed. Please check the error messages.
        pause
        exit /b 1
    )
)

REM Create runtime directories
if not exist dist\JarvisV2\data        mkdir dist\JarvisV2\data
if not exist dist\JarvisV2\logs        mkdir dist\JarvisV2\logs
if not exist dist\JarvisV2\screenshots mkdir dist\JarvisV2\screenshots
if not exist dist\JarvisV2\documents   mkdir dist\JarvisV2\documents
if not exist dist\JarvisV2\research    mkdir dist\JarvisV2\research

REM Copy config files
if not exist dist\JarvisV2\config mkdir dist\JarvisV2\config
copy /y config\config.json dist\JarvisV2\config\ >nul 2>nul
copy /y config\config.example.json dist\JarvisV2\config\ >nul 2>nul
copy /y config\api_config.json dist\JarvisV2\config\ >nul 2>nul

REM Copy other files
copy /y .env.example dist\JarvisV2\ >nul 2>nul
copy /y README.md dist\JarvisV2\ >nul 2>nul
copy /y LICENSE dist\JarvisV2\ >nul 2>nul

echo         Application built. [OK]

REM ---------------------------------------------------------------
REM  Create installer
REM ---------------------------------------------------------------
echo.
echo [5/5] Creating installer...

set "ISCC="
if exist "%ProgramFiles%\Inno Setup 6\ISCC.exe" set "ISCC=%ProgramFiles%\Inno Setup 6\ISCC.exe"
if exist "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe" set "ISCC=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"

if defined ISCC (
    echo         Compiling installer with Inno Setup...
    
    if not exist dist\installer mkdir dist\installer
    
    "%ISCC%" /Q "packaging\installer.iss"
    if errorlevel 1 (
        echo.
        echo  [WARN] Installer compilation failed.
        echo         The portable app is still available at: dist\JarvisV2\
    ) else (
        echo         Installer created. [OK]
    )
) else (
    echo         [SKIPPED] Inno Setup not found.
    echo.
    echo         To create an installer, install Inno Setup 6:
    echo         https://jrsoftware.org/isdl.php
)

REM ---------------------------------------------------------------
REM  Summary
REM ---------------------------------------------------------------
echo.
echo  ============================================================
echo   BUILD COMPLETE!
echo  ============================================================
echo.
echo   Files created:
echo.

if exist dist\JarvisV2\JarvisV2.exe (
    echo   [1] Desktop Application:
    echo       dist\JarvisV2\JarvisV2.exe
    echo.
)

if exist dist\installer\JarvisV2-Setup.exe (
    echo   [2] Windows Installer:
    echo       dist\installer\JarvisV2-Setup.exe
    echo.
)

echo   [3] Application Folder:
echo       dist\JarvisV2\
echo.
echo  ============================================================
echo.
echo   To run the app:
echo     - Double-click dist\JarvisV2\JarvisV2.exe
echo     - Or run the installer if available
echo.
echo  ============================================================
echo.

pause
exit /b 0
