@echo off
setlocal enabledelayedexpansion
title Jarvis V2 - One-Click Installer Builder
color 0B

echo.
echo  ============================================================
echo   JARVIS V2 - ONE-CLICK INSTALLER BUILDER
echo  ============================================================
echo.
echo   This script will automatically:
echo     1. Check prerequisites
echo     2. Build JarvisV2.exe
echo     3. Create JarvisV2-Setup.exe installer
echo.
echo   Output files:
echo     - dist\JarvisV2\JarvisV2.exe (portable app)
echo     - dist\installer\JarvisV2-Setup.exe (installer)
echo.
echo  ============================================================
echo.

cd /d "%~dp0.."

REM ---------------------------------------------------------------
REM  Check Python
REM ---------------------------------------------------------------
echo [1/6] Checking Python...
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
    echo  After installing Python, run this script again.
    echo.
    pause
    start https://python.org
    exit /b 1
)

for /f "tokens=2 delims= " %%v in ('python --version 2^>^&1') do set PYVER=%%v
echo         Python %PYVER% found. [OK]

REM ---------------------------------------------------------------
REM  Check/Install Inno Setup
REM ---------------------------------------------------------------
echo.
echo [2/6] Checking Inno Setup...

set "ISCC="
if exist "%ProgramFiles%\Inno Setup 6\ISCC.exe" set "ISCC=%ProgramFiles%\Inno Setup 6\ISCC.exe"
if exist "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe" set "ISCC=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"

if not defined ISCC (
    echo.
    echo  [INFO] Inno Setup 6 not found.
    echo.
    echo  Inno Setup is needed to create the installer (.exe).
    echo  It's free and open-source.
    echo.
    set /p DOWNLOAD="  Download and install Inno Setup 6 now? (Y/N): "
    if /i "!DOWNLOAD!"=="Y" (
        echo.
        echo  Opening download page...
        start https://jrsoftware.org/isdl.php
        echo.
        echo  After installing Inno Setup, press any key to continue...
        pause >nul
        
        REM Check again
        if exist "%ProgramFiles%\Inno Setup 6\ISCC.exe" set "ISCC=%ProgramFiles%\Inno Setup 6\ISCC.exe"
        if exist "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe" set "ISCC=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
        
        if not defined ISCC (
            echo.
            echo  [WARN] Inno Setup still not found. Building portable app only.
            echo.
        ) else (
            echo         Inno Setup found. [OK]
        )
    ) else (
        echo.
        echo  [WARN] Skipping installer build. Building portable app only.
        echo.
    )
) else (
    echo         Inno Setup found. [OK]
)

REM ---------------------------------------------------------------
REM  Create virtual environment
REM ---------------------------------------------------------------
echo.
echo [3/6] Setting up build environment...

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
echo [4/6] Installing dependencies (this may take a few minutes)...

python -m pip install --upgrade pip -q 2>nul
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

echo         Dependencies installed. [OK]

REM ---------------------------------------------------------------
REM  Build executable
REM ---------------------------------------------------------------
echo.
echo [5/6] Building JarvisV2.exe...

echo         Generating icon and installer images...
python packaging\make_icon.py >nul 2>nul
python packaging\create_installer_images.py >nul 2>nul

echo         Compiling with PyInstaller (2-5 minutes)...
pyinstaller --noconfirm --clean packaging\jarvis.spec 2>nul
if errorlevel 1 (
    echo.
    echo  [ERROR] Build failed! Trying with console enabled for debugging...
    echo.
    
    REM Try with console for debugging
    pyinstaller --noconfirm --clean --console packaging\jarvis.spec
    if errorlevel 1 (
        echo.
        echo  [ERROR] Build failed. Please check the error messages above.
        pause
        exit /b 1
    )
)

REM Create runtime directories
if not exist dist\JarvisV2\data        mkdir dist\JarvisV2\data
if not exist dist\JarvisV2\logs        mkdir dist\JarvisV2\logs
if not exist dist\JarvisV2\screenshots mkdir dist\JarvisV2\screenshots
if not exist dist\JarvisV2\documents   mkdir dist\JarvisV2\documents

REM Copy config
if not exist dist\JarvisV2\config mkdir dist\JarvisV2\config
copy /y config\config.json dist\JarvisV2\config\ >nul 2>nul
copy /y config\config.example.json dist\JarvisV2\config\ >nul 2>nul

REM Copy README
copy /y README.md dist\JarvisV2\ >nul 2>nul
copy /y LICENSE dist\JarvisV2\ >nul 2>nul

echo         JarvisV2.exe built. [OK]

REM ---------------------------------------------------------------
REM  Build installer
REM ---------------------------------------------------------------
echo.
echo [6/6] Building installer...

if defined ISCC (
    echo         Compiling with Inno Setup...
    
    REM Create installer output directory
    if not exist dist\installer mkdir dist\installer
    
    REM Compile installer
    "%ISCC%" /Q "packaging\installer.iss"
    if errorlevel 1 (
        echo.
        echo  [ERROR] Installer compilation failed.
        echo          Try opening packaging\installer.iss manually in Inno Setup.
        echo.
        echo  The portable app is still available at: dist\JarvisV2\JarvisV2.exe
        echo.
        pause
        exit /b 1
    )
    
    echo         Installer built. [OK]
    
    REM Get file size
    for %%A in (dist\installer\JarvisV2-Setup.exe) do set INSTALLER_SIZE=%%~zA
    set /a SIZE_MB=!INSTALLER_SIZE! / 1048576
    
    echo.
    echo  ============================================================
    echo   BUILD COMPLETE!
    echo  ============================================================
    echo.
    echo   Files created:
    echo.
    echo   [1] Portable App:
    echo       dist\JarvisV2\JarvisV2.exe
    echo.
    echo   [2] Installer (!SIZE_MB! MB):
    echo       dist\installer\JarvisV2-Setup.exe
    echo.
    echo  ============================================================
    echo.
    echo   The installer will:
    echo     - Install to Program Files\JarvisV2
    echo     - Create Start Menu shortcuts
    echo     - Offer desktop shortcut
    echo     - Include uninstaller
    echo     - Launch after install
    echo.
    echo  ============================================================
    echo.
    
    set /p OPEN="  Open the installer folder? (Y/N): "
    if /i "!OPEN!"=="Y" (
        explorer dist\installer
    )
    
) else (
    echo         [SKIPPED] Inno Setup not found.
    echo.
    echo  ============================================================
    echo   BUILD COMPLETE (Portable Only)!
    echo  ============================================================
    echo.
    echo   Portable app created:
    echo     dist\JarvisV2\JarvisV2.exe
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
