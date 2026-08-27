"""Logging setup for Jarvis V2."""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_logging(log_dir: str = "logs", level: str = "INFO", console: bool = True) -> None:
    """Configure rotating file logs and optional console output."""

    Path(log_dir).mkdir(parents=True, exist_ok=True)
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    root = logging.getLogger()
    root.setLevel(numeric_level)
    root.handlers.clear()

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    app_handler = RotatingFileHandler(
        Path(log_dir) / "jarvis.log", maxBytes=1_000_000, backupCount=5, encoding="utf-8"
    )
    app_handler.setFormatter(formatter)
    app_handler.setLevel(numeric_level)
    root.addHandler(app_handler)

    error_handler = RotatingFileHandler(
        Path(log_dir) / "errors.log", maxBytes=1_000_000, backupCount=5, encoding="utf-8"
    )
    error_handler.setFormatter(formatter)
    error_handler.setLevel(logging.ERROR)
    root.addHandler(error_handler)

    if console:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(numeric_level)
        root.addHandler(console_handler)
