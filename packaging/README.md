# Jarvis V2 - Installer & Packaging Guide

This directory contains everything needed to build a professional installer for Jarvis V2.

## Quick Start (Windows)

The easiest way to build a complete installer:

```batch
packaging\BuildInstaller.bat
```

This will:
1. Create a Python virtual environment
2. Install all dependencies
3. Build `JarvisV2.exe` with PyInstaller
4. Compile `JarvisV2-Setup.exe` with Inno Setup 6

**Output:**
- Portable app: `dist\JarvisV2\JarvisV2.exe`
- Installer: `dist\installer\JarvisV2-Setup.exe`

## Prerequisites

### Required
- **Python 3.10+** - [Download](https://python.org) (check "Add to PATH" during install)
- **PyInstaller** - Installed automatically by the build script

### For Installer (.exe)
- **Inno Setup 6** - [Download](https://jrsoftware.org/isdl.php)
  - Free, open-source installer builder
  - Creates professional Windows installers
  - Alternative: NSIS (see below)

## Build Options

### Option 1: One-Click Build (Recommended)

```batch
cd JarvisV2
packaging\BuildInstaller.bat
```

### Option 2: Manual Build

```batch
cd JarvisV2

REM Create virtual environment
python -m venv .venv
.venv\Scripts\activate

REM Install dependencies
pip install -r requirements.txt
pip install pyinstaller

REM Build executable
python packaging\make_icon.py
pyinstaller --noconfirm --clean packaging\jarvis.spec

REM Create runtime folders
mkdir dist\JarvisV2\data
mkdir dist\JarvisV2\logs
mkdir dist\JarvisV2\screenshots
mkdir dist\JarvisV2\documents

REM Build installer (requires Inno Setup 6)
"C:\Program Files\Inno Setup 6\ISCC.exe" packaging\installer.iss
```

### Option 3: NSIS Alternative

If you prefer NSIS over Inno Setup:

1. Install [NSIS](https://nsis.sourceforge.io/Download)
2. Generate the script:
   ```bash
   python packaging/installer_generator.py --platform windows --nsis
   ```
3. Build:
   ```batch
   makensis packaging\installer.nsi
   ```

## macOS Build

```bash
cd JarvisV2
chmod +x packaging/build_installer.sh
./packaging/build_installer.sh
```

For a `.app` bundle:
```bash
python packaging/installer_generator.py --platform macos
```

For a `.dmg` installer:
```bash
brew install create-dmg
create-dmg --volname "Jarvis V2" dist/JarvisV2.dmg dist/JarvisV2.app
```

## Linux Build

```bash
cd JarvisV2
chmod +x packaging/build_installer.sh
./packaging/build_installer.sh
```

For an AppImage:
```bash
python packaging/installer_generator.py --platform linux
# Download appimagetool from https://github.com/AppImage/AppImageKit
./appimagetool dist/JarvisV2.AppDir dist/JarvisV2.AppImage
```

## What the Installer Does

The Windows installer (`JarvisV2-Setup.exe`) provides:

### Installation
- Installs to `C:\Program Files\JarvisV2` (or user-selected location)
- Creates all necessary runtime directories
- Copies configuration files
- Sets up PATH environment variable (optional)

### Shortcuts
- **Desktop shortcut** (optional, checked by default)
- **Start Menu shortcuts**:
  - Jarvis V2 (GUI mode)
  - Jarvis V2 Voice Mode
  - Jarvis V2 Web Dashboard
  - Uninstall

### Optional Features
- **Start with Windows** - Launch voice mode on startup
- **File associations** - Associate `.jarvis` files with the app

### Uninstaller
- Complete uninstall with cleanup
- Removes all installed files
- Removes shortcuts and registry entries
- Optionally removes user data (logs, screenshots, etc.)

## Customization

### Changing App Metadata

Edit the constants at the top of these files:
- `packaging/installer.iss` - Inno Setup script
- `packaging/installer_generator.py` - Generator script
- `packaging/jarvis.spec` - PyInstaller spec

### Adding Files to the Installer

Edit the `[Files]` section in `installer.iss`:

```ini
[Files]
Source: "..\dist\JarvisV2\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs
; Add more files here:
Source: "..\docs\*"; DestDir: "{app}\docs"; Flags: ignoreversion recursesubdirs
```

### Custom Icon

Replace `packaging/app.png` (1024x1024 recommended) and run:
```bash
python packaging/make_icon.py
```

## Troubleshooting

### "Python not found"
- Install Python from https://python.org
- Make sure "Add python.exe to PATH" is checked during installation

### "PyInstaller build failed"
- Check that all dependencies are installed: `pip install -r requirements.txt`
- Try running PyInstaller with console enabled for debugging:
  Edit `jarvis.spec` and set `console=True`

### "Inno Setup not found"
- Download and install Inno Setup 6 from https://jrsoftware.org/isdl.php
- The portable app (`dist\JarvisV2\JarvisV2.exe`) will still work without it

### "Antivirus flags the installer"
- This is common with PyInstaller executables
- Add an exception for the build directory
- Consider code signing the executable for production distribution

## File Structure

```
packaging/
├── app.ico                    # Windows icon (generated from app.png)
├── app.png                    # Source icon (1024x1024)
├── build_app.sh               # macOS/Linux build script
├── build_exe.bat              # Windows build script (basic)
├── BuildInstaller.bat         # Windows complete installer builder
├── build_installer.sh         # macOS/Linux complete build script
├── desktop_launcher.py        # Entry point for packaged app
├── installer.iss              # Inno Setup script (Windows installer)
├── installer_generator.py     # Cross-platform installer generator
├── installer.nsi              # NSIS script (alternative)
├── jarvis.spec                # PyInstaller specification
├── make_icon.py               # Icon generator
└── README.md                  # This file
```

## Distribution

### For End Users
- Share `JarvisV2-Setup.exe` - double-click to install
- No Python or technical knowledge required
- Includes everything needed to run

### For Developers
- Share the `dist\JarvisV2` folder as a portable app
- Include `README.md` and `.env.example`
- Users need Python 3.10+ to run from source

## Code Signing (Production)

For production distribution, sign the executable:

1. Obtain a code signing certificate (e.g., from DigiCert, Sectigo)
2. Sign the executable:
   ```batch
   signtool sign /f certificate.pfx /p password /t http://timestamp.digicert.com dist\JarvisV2\JarvisV2.exe
   ```
3. Sign the installer:
   ```batch
   signtool sign /f certificate.pfx /p password /t http://timestamp.digicert.com dist\installer\JarvisV2-Setup.exe
   ```

This prevents Windows SmartScreen warnings and builds user trust.

---

**Need help?** Open an issue on [GitHub]({APP_URL}).
