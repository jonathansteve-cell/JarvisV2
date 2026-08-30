@echo off
setlocal enabledelayedexpansion
title Jarvis V2 - Installer Builder
color 0A

echo.
echo  ============================================================
echo   JARVIS V2 - COMPLETE INSTALLER BUILDER
echo  ============================================================
echo   This script builds everything needed for Install.exe:
echo     1. Virtual environment + dependencies
echo     2. PyInstaller executable (JarvisV2.exe)
echo     3. Inno Setup installer (JarvisV2-Setup.exe)
echo  ============================================================
echo.

cd /d "%~dp0.."

REM ---------------------------------------------------------------
REM  Pre-flight checks
REM ---------------------------------------------------------------
echo [CHECK] Verifying prerequisites...

where python >nul 2>nul
if errorlevel 1 (
    echo.
    echo  [ERROR] Python is not installed or not in PATH.
    echo          Download Python 3.10+ from https://python.org
    echo          IMPORTANT: Check "Add python.exe to PATH" during install!
    echo.
    pause
    exit /b 1
)

for /f "tokens=2 delims= " %%v in ('python --version 2^>^&1') do set PYVER=%%v
echo         Python %PYVER% found.

REM Check for Inno Setup 6
set "ISCC="
if exist "%ProgramFiles%\Inno Setup 6\ISCC.exe" set "ISCC=%ProgramFiles%\Inno Setup 6\ISCC.exe"
if exist "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe" set "ISCC=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
if defined ISCC (
    echo         Inno Setup 6 found.
) else (
    echo.
    echo  [WARN] Inno Setup 6 not found. The installer (.exe) step will be skipped.
    echo         Download from https://jrsoftware.org/isdl.php
    echo         The portable app build will still complete.
    echo.
)

echo.
echo  ============================================================
echo  STEP 1/5: Creating virtual environment
echo  ============================================================
if not exist .venv (
    python -m venv .venv
    if errorlevel 1 (
        echo  [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
    echo         Virtual environment created.
) else (
    echo         Virtual environment already exists.
)
call .venv\Scripts\activate.bat

echo.
echo  ============================================================
echo  STEP 2/5: Installing dependencies
echo  ============================================================
python -m pip install --upgrade pip -q
pip install -r requirements.txt -q
if errorlevel 1 (
    echo  [ERROR] Failed to install requirements.
    pause
    exit /b 1
)
pip install pyinstaller -q
if errorlevel 1 (
    echo  [ERROR] Failed to install PyInstaller.
    pause
    exit /b 1
)
echo         All dependencies installed.

echo.
echo  ============================================================
echo  STEP 3/5: Generating application icon and installer images
echo  ============================================================
python packaging\make_icon.py
if errorlevel 1 (
    echo  [WARN] Icon generation failed - using default icon.
)

python packaging\create_installer_images.py
if errorlevel 1 (
    echo  [WARN] Installer image generation failed - using defaults.
)

echo.
echo  ============================================================
echo  STEP 4/5: Building JarvisV2.exe with PyInstaller
echo  ============================================================
echo         This may take 2-5 minutes depending on your system...
echo.
pyinstaller --noconfirm --clean packaging\jarvis.spec
if errorlevel 1 (
    echo.
    echo  [ERROR] PyInstaller build failed. Check the output above.
    pause
    exit /b 1
)

REM Create runtime directories in the dist folder
if not exist dist\JarvisV2\data        mkdir dist\JarvisV2\data
if not exist dist\JarvisV2\logs        mkdir dist\JarvisV2\logs
if not exist dist\JarvisV2\screenshots mkdir dist\JarvisV2\screenshots
if not exist dist\JarvisV2\documents   mkdir dist\JarvisV2\documents

REM Copy config files to dist
if not exist dist\JarvisV2\config mkdir dist\JarvisV2\config
copy /y config\config.json dist\JarvisV2\config\ >nul 2>nul
copy /y config\config.example.json dist\JarvisV2\config\ >nul 2>nul

echo         JarvisV2.exe built successfully!

echo.
echo  ============================================================
echo  STEP 5/5: Building installer with Inno Setup
echo  ============================================================
if defined ISCC (
    echo         Compiling installer...
    "%ISCC%" /Q "packaging\installer.iss"
    if errorlevel 1 (
        echo.
        echo  [ERROR] Inno Setup compilation failed.
        echo          Try opening packaging\installer.iss manually in Inno Setup.
        pause
        exit /b 1
    )
    echo         Installer compiled successfully!
    echo.
    echo  ============================================================
    echo   BUILD COMPLETE!
    echo  ============================================================
    echo.
    echo   Portable app:  dist\JarvisV2\JarvisV2.exe
    echo   Installer:     dist\installer\JarvisV2-Setup.exe
    echo.
    echo   The installer will:
    echo     - Install to Program Files\JarvisV2
    echo     - Create Start Menu shortcuts
    echo     - Offer desktop shortcut
    echo     - Include uninstaller
    echo     - Launch after install
    echo.
    echo  ============================================================
) else (
    echo         [SKIPPED] Inno Setup not found.
    echo.
    echo  ============================================================
    echo   BUILD COMPLETE (portable only)!
    echo  ============================================================
    echo.
    echo   Portable app:  dist\JarvisV2\JarvisV2.exe
    echo.
    echo   To create an installer, install Inno Setup 6:
    echo     https://jrsoftware.org/isdl.php
    echo   Then run this script again.
    echo.
    echo  ============================================================
)

echo.
pause
exit /b 0
