@echo off
cd /d "%~dp0"
if not exist .venv (
  echo Creating virtual environment, one moment...
  python -m venv .venv
)
call .venv\Scripts\activate
pip install -r requirements.txt -q
python main.py
pause
