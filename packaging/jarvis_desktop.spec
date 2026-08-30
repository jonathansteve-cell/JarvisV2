# -*- mode: python ; coding: utf-8 -*-
# Jarvis V2 - Desktop Application PyInstaller Spec
#
# Build with:  pyinstaller --noconfirm --clean packaging/jarvis_desktop.spec
# Or use:      python packaging/create_installer.py

import os
import sys
from pathlib import Path

# SPECPATH is the folder containing this .spec file (set by PyInstaller).
ROOT = Path(SPECPATH).resolve()
PROJECT = ROOT.parent

# Data files to include
datas = [
    # Configuration files
    (str(PROJECT / "config"), "config"),
    
    # Personality profiles
    (str(PROJECT / "personality"), "personality"),
    
    # Dashboard files
    (str(PROJECT / "dashboard"), "dashboard"),
    
    # Documentation images
    (str(PROJECT / "docs" / "images"), "docs/images"),
    
    # Environment template
    (str(PROJECT / ".env.example"), "."),
    
    # README
    (str(PROJECT / "README.md"), "."),
    
    # License
    (str(PROJECT / "LICENSE"), "."),
]

# Hidden imports that PyInstaller might miss
hiddenimports = [
    # Voice and audio
    "pyaudio",
    "pyttsx3",
    "pyttsx3.drivers",
    "pyttsx3.drivers.sapi5",
    "pyttsx3.drivers.nsss",
    "pyttsx3.drivers.espeak",
    "speech_recognition",
    
    # Web and API
    "requests",
    "beautifulsoup4",
    "wikipedia",
    
    # GUI
    "tkinter",
    "tkinter.ttk",
    "tkinter.scrolledtext",
    "tkinter.messagebox",
    "tkinter.filedialog",
    
    # System
    "psutil",
    "pyautogui",
    "pillow",
    "pyperclip",
    
    # Data
    "json",
    "sqlite3",
    "csv",
    
    # Networking
    "socket",
    "http.server",
    "urllib",
    
    # Threading
    "threading",
    "concurrent.futures",
    
    # Encryption
    "cryptography",
    "cryptography.fernet",
    
    # Email
    "smtplib",
    "imaplib",
    "email",
    
    # Other
    "dotenv",
    "jokes",
    "spotipy",
    "twilio",
    "tweepy",
    "docx",
]

# Exclude unnecessary packages to reduce size
excludes = [
    "matplotlib",
    "numpy",
    "pandas",
    "scipy",
    "tensorflow",
    "torch",
    "IPython",
    "jupyter",
    "pytest",
    "tkinter.test",
    "unittest",
    "test",
    "distutils",
    "setuptools",
    "pip",
    "wheel",
]

# Analysis
a = Analysis(
    [str(PROJECT / "desktop_app.py")],
    pathex=[str(PROJECT)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    excludes=excludes,
    noarchive=False,
    optimize=2,
)

# PYZ (Python archive)
pyz = PYZ(a.pure, a.zipped_data)

# EXE
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="JarvisV2",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # GUI app - no console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(ROOT / "app.ico"),
    version_info={
        "CompanyName": "jonathansteve-cell",
        "FileDescription": "Jarvis V2 - All-in-One Desktop AI Assistant",
        "FileVersion": "2.0.0.0",
        "InternalName": "JarvisV2",
        "OriginalFilename": "JarvisV2.exe",
        "ProductName": "Jarvis V2",
        "ProductVersion": "2.0.0.0",
        "LegalCopyright": "Copyright © 2026 jonathansteve-cell",
    } if (ROOT / "app.ico").exists() else None,
)

# COLLECT (one-dir build)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="JarvisV2",
)
