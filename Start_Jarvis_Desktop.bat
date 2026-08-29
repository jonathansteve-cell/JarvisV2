@echo off
REM Launch Jarvis V2 as the DESKTOP app (native Tkinter HUD).
REM Note: the original Start_Jarvis.bat opens the WEB dashboard in a browser.
REM This one opens the real desktop window: python main.py --gui
cd /d "%~dp0"
if not exist .venv (
  echo Creating virtual environment, one moment...
  python -m venv .venv
)
call .venv\Scripts\activate
pip install -r requirements.txt -q
python main.py --gui
pause