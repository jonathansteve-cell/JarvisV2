@echo off
REM ============================================================
REM  Jarvis V2 - Desktop App Builder (Windows)
REM  Creates a double-clickable JarvisV2.exe in dist\JarvisV2\
REM  Requires: Python 3.10+ installed (python.org) and checked
REM            "Add python.exe to PATH" during install.
REM ============================================================
setlocal
cd /d "%~dp0.."

where python >nul 2>nul
if errorlevel 1 (
  echo [ERROR] Python not found. Install Python 3.10+ from https://python.org
  echo         and tick "Add python.exe to PATH".
  pause
  exit /b 1
)

echo [1/4] Creating virtual environment...
if not exist .venv python -m venv .venv
call .venv\Scripts\activate.bat

echo [2/4] Installing dependencies...
python -m pip install --upgrade pip -q
pip install -r requirements.txt -q
pip install pyinstaller -q

echo [3/4] Building the app (this can take a few minutes)...
python packaging\make_icon.py || goto :err
pyinstaller --noconfirm --clean packaging\jarvis.spec || goto :err

echo [4/4] Creating runtime folders...
if not exist dist\JarvisV2\data        mkdir dist\JarvisV2\data
if not exist dist\JarvisV2\logs        mkdir dist\JarvisV2\logs
if not exist dist\JarvisV2\screenshots mkdir dist\JarvisV2\screenshots
if not exist dist\JarvisV2\documents   mkdir dist\JarvisV2\documents

echo.
echo ============================================================
echo  DONE. Your desktop app is here:
echo
echo      dist\JarvisV2\JarvisV2.exe
echo
echo  Run it, or send the whole dist\JarvisV2 folder to another PC.
echo  For a proper installer, open packaging\installer.iss in
echo  Inno Setup 6 (https://jrsoftware.org/isdl.php) and Compile.
echo ============================================================
pause
exit /b 0

:err
echo.
echo [FAILED] Build step failed - see the message above.
pause
exit /b 1