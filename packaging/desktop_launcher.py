"""Entry point for the packaged Jarvis V2 desktop app.

Opens the native Tkinter HUD (gui.main_window) — the equivalent of running
`python main.py --gui`, but with paths fixed up for a frozen (PyInstaller)
executable so config/, personality/, .env and runtime data resolve beside
the app instead of the current working directory.
"""

from __future__ import annotations

import os
import sys

if getattr(sys, "frozen", False):
    # One-dir build: sys.executable lives in dist/JarvisV2/JarvisV2(.exe)
    BASE = os.path.dirname(os.path.abspath(sys.executable))
    os.chdir(BASE)
    sys.path.insert(0, BASE)

from main import run_gui  # noqa: E402  (import must come after frozen path setup)

if __name__ == "__main__":
    raise SystemExit(run_gui())