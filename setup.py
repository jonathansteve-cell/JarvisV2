"""Setup helper for Jarvis V2.

This is intentionally lightweight. Use `pip install -r requirements.txt` for runtime dependencies.
"""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path


def init_project() -> None:
    Path("data").mkdir(exist_ok=True)
    Path("logs").mkdir(exist_ok=True)
    Path("screenshots").mkdir(exist_ok=True)
    Path("documents").mkdir(exist_ok=True)
    if not Path(".env").exists() and Path(".env.example").exists():
        shutil.copy(".env.example", ".env")
    print("Jarvis V2 initialized. Edit .env with your local secrets before using integrations.")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--init", action="store_true", help="Create local runtime directories and .env")
    args = parser.parse_args()
    if args.init:
        init_project()
    else:
        print("Run `python setup.py --init` to initialize local runtime files.")


if __name__ == "__main__":
    main()
