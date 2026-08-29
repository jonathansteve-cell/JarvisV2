#!/usr/bin/env bash
# Jarvis V2 - Desktop app builder for macOS / Linux (PyInstaller onedir).
# Windows users: use packaging\build_exe.bat instead.
set -euo pipefail
cd "$(dirname "$0")/.."

PY_BIN="${PYTHON:-python3}"
command -v "$PY_BIN" >/dev/null 2>&1 || { echo "[ERROR] $PY_BIN not found"; exit 1; }

echo "[1/4] Creating virtual environment..."
if [ ! -d .venv ]; then "$PY_BIN" -m venv .venv; fi
# shellcheck disable=SC1091
source .venv/bin/activate

echo "[2/4] Installing dependencies..."
pip install --upgrade pip -q
pip install -r requirements.txt -q
pip install pyinstaller -q

# Linux often ships Python without Tk — the HUD needs it.
if [ "$(uname -s)" = "Linux" ] && ! "$PY_BIN" -c 'import tkinter' >/dev/null 2>&1; then
  echo "[WARN] tkinter is missing. Install it, e.g.:"
  echo "          sudo apt install python3-tk        # Debian/Ubuntu"
  echo "          sudo dnf install python3-tkinter   # Fedora"
fi

echo "[3/4] Building the app..."
"$PY_BIN" packaging/make_icon.py
"$PY_BIN" -m PyInstaller --noconfirm --clean packaging/jarvis.spec

echo "[4/4] Creating runtime folders..."
mkdir -p dist/JarvisV2/{data,logs,screenshots,documents}

echo
echo "DONE. Desktop app built at: dist/JarvisV2"
echo "  - Launch: dist/JarvisV2/JarvisV2"
echo "  - macOS: onedir produces an executable; for a .app bundle add a BUNDLE"
echo "    step to packaging/jarvis.spec (or use py2app) and codesign your build."
echo