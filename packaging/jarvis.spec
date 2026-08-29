# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec for Jarvis V2 desktop app.
#
# Build with:  pyinstaller --noconfirm --clean packaging/jarvis.spec
# (or just run packaging/build_exe.bat on Windows)

import os
from pathlib import Path

# SPECPATH is the folder containing this .spec file (set by PyInstaller).
ROOT = Path(SPECPATH).resolve()
PROJECT = ROOT.parent

datas = [
    (str(PROJECT / "config"), "config"),                      # config/config.json
    (str(PROJECT / "personality"), "personality"),            # personality profiles
    (str(PROJECT / "docs" / "images"), "docs/images"),        # hero_orb.png for the HUD
    (str(PROJECT / "dashboard"), "dashboard"),                # web dashboard (--web still works)
    (str(PROJECT / ".env.example"), "."),                     # template for machine-local secrets
]

a = Analysis(
    [str(ROOT / "desktop_launcher.py")],
    pathex=[str(PROJECT)],
    binaries=[],
    datas=datas,
    hiddenimports=[
        # mic capture on Windows
        "pyaudio",
        # pyttsx3 loads its TTS drivers by name at runtime
        "pyttsx3.drivers",
        "pyttsx3.drivers.sapi5",
        "pyttsx3.drivers.nsss",
        "pyttsx3.drivers.espeak",
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=[
        "matplotlib", "numpy", "pandas", "scipy",
        "tensorflow", "torch", "IPython", "jupyter",
        "pytest", "tkinter.test",
    ],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,          # one-dir build (fastest startup, easiest to debug)
    name="JarvisV2",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,                  # GUI app: no console window. Set True for a debug build.
    icon=str(ROOT / "app.ico"),
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="JarvisV2",
)