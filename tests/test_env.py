"""Regression tests for utils.env — BOM / UTF-16 safe .env loading."""

from __future__ import annotations

import os
import textwrap
from pathlib import Path

import pytest

from utils.env import _detect_encoding, load_env_file


# ---------------------------------------------------------------------------
# _detect_encoding
# ---------------------------------------------------------------------------

class TestDetectEncoding:
    """Unit tests for the BOM-detection helper."""

    def test_utf16_le_bom(self):
        assert _detect_encoding(b"\xff\xfe") == "utf-16-le"

    def test_utf16_be_bom(self):
        assert _detect_encoding(b"\xfe\xff") == "utf-16-be"

    def test_utf8_sig_bom(self):
        assert _detect_encoding(b"\xef\xbb\xbf") == "utf-8-sig"

    def test_plain_utf8(self):
        assert _detect_encoding(b"HELLO=world") == "utf-8"

    def test_empty_bytes(self):
        assert _detect_encoding(b"") == "utf-8"


# ---------------------------------------------------------------------------
# load_env_file — encoding edge-cases
# ---------------------------------------------------------------------------

class TestLoadEnvFileEncodings:
    """Ensure .env files in various encodings are parsed correctly."""

    def _write_and_load(self, tmp_path: Path, data: bytes, var: str = "TEST_KEY"):
        env_file = tmp_path / ".env"
        env_file.write_bytes(data)
        # Clear the variable so the test is deterministic
        os.environ.pop(var, None)
        load_env_file(env_file)
        return os.environ.get(var)

    def test_utf8_plain(self, tmp_path):
        val = self._write_and_load(tmp_path, b"TEST_KEY=hello_utf8\n")
        assert val == "hello_utf8"

    def test_utf8_with_bom(self, tmp_path):
        val = self._write_and_load(tmp_path, b"\xef\xbb\xbfTEST_KEY=hello_bom\n")
        assert val == "hello_bom"

    def test_utf16_le_with_bom(self, tmp_path):
        text = "TEST_KEY=hello_utf16le\n"
        data = text.encode("utf-16-le")
        # Prepend the UTF-16 LE BOM
        val = self._write_and_load(tmp_path, b"\xff\xfe" + data)
        assert val == "hello_utf16le"

    def test_utf16_be_with_bom(self, tmp_path):
        text = "TEST_KEY=hello_utf16be\n"
        data = text.encode("utf-16-be")
        val = self._write_and_load(tmp_path, b"\xfe\xff" + data)
        assert val == "hello_utf16be"

    def test_missing_file_is_noop(self, tmp_path):
        """Loading a non-existent file should silently do nothing."""
        load_env_file(tmp_path / "does_not_exist.env")  # must not raise

    def test_existing_env_wins(self, tmp_path):
        """Variables already in os.environ must NOT be overwritten."""
        os.environ["KEEP_ME"] = "original"
        env_file = tmp_path / ".env"
        env_file.write_bytes(b"KEEP_ME=overwritten\n")
        load_env_file(env_file)
        assert os.environ["KEEP_ME"] == "original"
        os.environ.pop("KEEP_ME", None)
