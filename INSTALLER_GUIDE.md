# Jarvis V2 - Complete Installer Guide

## 🚀 Quick Start (Windows)

**The easiest way to build your installer:**

1. **Double-click** `packaging\OneClickBuild.bat`
2. Wait for the build to complete (5-10 minutes)
3. Find your installer at `dist\installer\JarvisV2-Setup.exe`

That's it! The script handles everything automatically.

---

## 📋 What You Get

After building, you'll have:

### 1. Portable App
```
dist\JarvisV2\JarvisV2.exe
```
- Standalone executable
- No installation required
- Can be copied to any Windows PC
- Run directly from USB drive

### 2. Professional Installer
```
dist\installer\JarvisV2-Setup.exe
```
- Double-click to install
- Installs to Program Files
- Creates Start Menu shortcuts
- Desktop shortcut option
- Includes uninstaller
- Registry entries for Add/Remove Programs
- Optional: Start with Windows
- Optional: Add to PATH

---

## 🛠️ Prerequisites

### Required
- **Python 3.10+** - [Download](https://python.org)
  - During installation, **check "Add python.exe to PATH"**
  - This is critical for the build script to work

### For Installer (Optional)
- **Inno Setup 6** - [Download](https://jrsoftware.org/isdl.php)
  - Free, open-source installer builder
  - Creates professional Windows installers
  - The build script can download it for you

---

## 📦 Build Options

### Option 1: One-Click Build (Recommended)

```batch
packaging\OneClickBuild.bat
```

**Features:**
- Automatic prerequisite checking
- Downloads Inno Setup if needed
- Creates virtual environment
- Installs all dependencies
- Builds executable
- Creates installer
- Opens output folder when done

### Option 2: Advanced Build

```batch
packaging\BuildInstaller.bat
```

**Features:**
- More control over the process
- Detailed progress output
- Better error handling
- For advanced users

### Option 3: Manual Build

```batch
cd JarvisV2

REM 1. Create virtual environment
python -m venv .venv
.venv\Scripts\activate

REM 2. Install dependencies
pip install -r requirements.txt
pip install pyinstaller

REM 3. Build executable
python packaging\make_icon.py
pyinstaller --noconfirm --clean packaging\jarvis.spec

REM 4. Create runtime folders
mkdir dist\JarvisV2\data
mkdir dist\JarvisV2\logs
mkdir dist\JarvisV2\screenshots
mkdir dist\JarvisV2\documents

REM 5. Build installer (requires Inno Setup 6)
"C:\Program Files\Inno Setup 6\ISCC.exe" packaging\installer.iss
```

---

## 🎯 Installer Features

The `JarvisV2-Setup.exe` installer provides:

### Installation Options
- **Install Location**: Choose where to install (default: Program Files)
- **Desktop Shortcut**: Optional desktop icon
- **Start Menu**: Shortcuts for all modes
- **Auto-Start**: Launch with Windows (voice mode)
- **PATH**: Add to system PATH for CLI usage

### Shortcuts Created
- **Desktop**: Jarvis V2 (GUI mode)
- **Start Menu**:
  - Jarvis V2 (GUI mode)
  - Jarvis V2 Voice Mode
  - Jarvis V2 Web Dashboard
  - Uninstall

### Uninstaller
- Complete removal of installed files
- Optional: Remove user data (logs, screenshots, etc.)
- Cleans up registry entries
- Removes shortcuts

---

## 🔧 Customization

### Change App Name/Version

Edit these files:
- `packaging/installer.iss` (Inno Setup)
- `packaging/installer.nsi` (NSIS alternative)
- `packaging/jarvis.spec` (PyInstaller)

Look for:
```python
APP_NAME = "Jarvis V2"
APP_VERSION = "2.0.0"
```

### Custom Icon

1. Replace `packaging/app.png` with your icon (1024x1024 recommended)
2. Run: `python packaging/make_icon.py`
3. Rebuild

### Add Files to Installer

Edit `packaging/installer.iss`:

```ini
[Files]
Source: "..\dist\JarvisV2\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs
; Add more files:
Source: "..\docs\*"; DestDir: "{app}\docs"; Flags: ignoreversion recursesubdirs
```

---

## 🐧 macOS / Linux

### macOS

```bash
cd JarvisV2
chmod +x packaging/build_installer.sh
./packaging/build_installer.sh
```

**Create .app bundle:**
```bash
python packaging/installer_generator.py --platform macos
```

**Create .dmg installer:**
```bash
brew install create-dmg
create-dmg --volname "Jarvis V2" dist/JarvisV2.dmg dist/JarvisV2.app
```

### Linux

```bash
cd JarvisV2
chmod +x packaging/build_installer.sh
./packaging/build_installer.sh
```

**Create AppImage:**
```bash
python packaging/installer_generator.py --platform linux
# Download appimagetool from https://github.com/AppImage/AppImageKit
./appimagetool dist/JarvisV2.AppDir dist/JarvisV2.AppImage
```

---

## ❓ Troubleshooting

### "Python not found"
- Install Python from https://python.org
- Make sure "Add python.exe to PATH" is checked
- Restart your terminal after installation

### "PyInstaller build failed"
- Check error messages in the console
- Try running with console enabled:
  Edit `packaging/jarvis.spec`, change `console=False` to `console=True`
- Rebuild and check for import errors

### "Inno Setup not found"
- Download from https://jrsoftware.org/isdl.php
- Install and run the build script again
- Or use the NSIS alternative (see below)

### "Antivirus flags the installer"
- This is common with PyInstaller executables
- Add exception for the build folder
- Consider code signing for production

### "App won't start"
- Check if all runtime folders exist (data, logs, screenshots, documents)
- Try running from command line to see error messages
- Make sure .env file is configured (copy from .env.example)

---

## 🎨 Alternative: NSIS Installer

If you prefer NSIS over Inno Setup:

1. **Install NSIS**: https://nsis.sourceforge.io/Download
2. **Generate script**:
   ```bash
   python packaging/installer_generator.py --platform windows --nsis
   ```
3. **Build**:
   ```batch
   makensis packaging\installer.nsi
   ```

---

## 🔐 Code Signing (Production)

For professional distribution:

1. **Get a certificate** from DigiCert, Sectigo, or similar
2. **Sign the executable**:
   ```batch
   signtool sign /f certificate.pfx /p password /t http://timestamp.digicert.com dist\JarvisV2\JarvisV2.exe
   ```
3. **Sign the installer**:
   ```batch
   signtool sign /f certificate.pfx /p password /t http://timestamp.digicert.com dist\installer\JarvisV2-Setup.exe
   ```

**Benefits:**
- No Windows SmartScreen warnings
- Builds user trust
- Professional appearance

---

## 📁 File Structure

```
packaging/
├── app.ico                    # Windows icon (generated)
├── app.png                    # Source icon (1024x1024)
├── build_app.sh               # macOS/Linux build script
├── build_exe.bat              # Basic Windows build
├── BuildInstaller.bat         # Advanced Windows build
├── build_installer.sh         # macOS/Linux complete build
├── desktop_launcher.py        # Entry point for packaged app
├── installer.iss              # Inno Setup script (Windows)
├── installer.nsi              # NSIS script (alternative)
├── installer_generator.py     # Cross-platform generator
├── jarvis.spec                # PyInstaller specification
├── make_icon.py               # Icon generator
├── OneClickBuild.bat          # One-click build script
└── README.md                  # This file
```

---

## 🚀 Distribution

### For End Users
- Share `JarvisV2-Setup.exe`
- Double-click to install
- No technical knowledge required
- Includes everything needed

### For Developers
- Share `dist\JarvisV2` folder as portable app
- Include README.md and .env.example
- Users need Python 3.10+ to run from source

---

## 💡 Tips

1. **Test the installer** on a clean Windows VM before distributing
2. **Include .env.example** so users know what to configure
3. **Add a README** with setup instructions
4. **Consider auto-updates** for future versions
5. **Use code signing** for production releases

---

## 📞 Support

- **Issues**: https://github.com/jonathansteve-cell/JarvisV2/issues
- **Documentation**: See `docs/` folder
- **Configuration**: Edit `config/config.json`

---

**Ready to build?** Double-click `packaging\OneClickBuild.bat` and you're done! 🎉
