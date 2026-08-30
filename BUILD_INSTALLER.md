# 🎯 How to Create Install.exe for Jarvis V2

## ⚡ Quick Answer

**On Windows, simply double-click:**
```
packaging\OneClickBuild.bat
```

**That's it!** This will automatically:
1. ✅ Check Python is installed
2. ✅ Download Inno Setup if needed
3. ✅ Build JarvisV2.exe
4. ✅ Create JarvisV2-Setup.exe installer

**Output:** `dist\installer\JarvisV2-Setup.exe`

---

## 📋 What You Need

### Required
- **Python 3.10+** - [Download](https://python.org)
  - ⚠️ **IMPORTANT:** Check "Add python.exe to PATH" during installation!

### Optional (Auto-installed)
- **Inno Setup 6** - The build script will offer to download it for you

---

## 🚀 Step-by-Step Instructions

### Step 1: Open Command Prompt
- Press `Win + R`
- Type `cmd` and press Enter
- Navigate to your JarvisV2 folder:
  ```batch
  cd C:\path\to\JarvisV2
  ```

### Step 2: Run the Build Script
```batch
packaging\OneClickBuild.bat
```

### Step 3: Wait for Build
- The script will automatically:
  - Create a virtual environment
  - Install all dependencies
  - Build the executable
  - Create the installer
- **Time:** 5-10 minutes (depending on your internet speed)

### Step 4: Find Your Installer
When complete, you'll see:
```
dist\installer\JarvisV2-Setup.exe
```

**Double-click this file to install Jarvis V2 on any Windows PC!**

---

## 🎁 What the Installer Does

When users run `JarvisV2-Setup.exe`:

### Installation
- ✅ Installs to `C:\Program Files\JarvisV2`
- ✅ Creates all necessary folders
- ✅ Copies configuration files
- ✅ Sets up environment

### Shortcuts
- ✅ Desktop shortcut (optional)
- ✅ Start Menu shortcuts:
  - Jarvis V2 (GUI mode)
  - Jarvis V2 Voice Mode
  - Jarvis V2 Web Dashboard
  - Uninstall

### Optional Features
- ✅ Start with Windows (voice mode)
- ✅ Add to PATH (for command-line usage)

### Uninstaller
- ✅ Complete removal
- ✅ Cleans up all files
- ✅ Removes shortcuts and registry entries

---

## 🔧 Alternative Build Methods

### Method 1: Advanced Build Script
```batch
packaging\BuildInstaller.bat
```
- More detailed output
- Better error handling
- For advanced users

### Method 2: Manual Build
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

REM Build installer
"C:\Program Files\Inno Setup 6\ISCC.exe" packaging\installer.iss
```

### Method 3: NSIS Alternative
If you prefer NSIS over Inno Setup:
```batch
REM Install NSIS from https://nsis.sourceforge.io/Download

REM Generate NSIS script
python packaging\installer_generator.py --platform windows --nsis

REM Build installer
makensis packaging\installer.nsi
```

---

## 🐧 macOS / Linux Users

### macOS
```bash
cd JarvisV2
chmod +x packaging/build_installer.sh
./packaging/build_installer.sh
```

### Linux
```bash
cd JarvisV2
chmod +x packaging/build_installer.sh
./packaging/build_installer.sh
```

**Note:** macOS/Linux builds create a portable app, not an .exe installer.

---

## ❓ Troubleshooting

### "Python not found"
**Solution:**
1. Install Python from https://python.org
2. During installation, **check "Add python.exe to PATH"**
3. Restart your terminal
4. Try again

### "Build failed"
**Solution:**
1. Check error messages in the console
2. Make sure you have internet connection (for downloading dependencies)
3. Try running as Administrator
4. Check if antivirus is blocking the build

### "Inno Setup not found"
**Solution:**
- The build script will offer to download it automatically
- Or download manually from https://jrsoftware.org/isdl.php
- Install and run the build script again

### "Antivirus flags the installer"
**Solution:**
- This is normal for PyInstaller executables
- Add exception for the JarvisV2 folder
- Or temporarily disable antivirus during build

### "App won't start after installation"
**Solution:**
1. Check if all folders exist (data, logs, screenshots, documents)
2. Try running from command line to see error messages
3. Make sure .env file is configured (copy from .env.example)

---

## 📁 Output Files

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
- Professional installation wizard
- Creates shortcuts and registry entries
- Includes uninstaller

---

## 🎨 Customization

### Change App Name/Version
Edit these files:
- `packaging/installer.iss` (Inno Setup)
- `packaging/installer.nsi` (NSIS)
- `packaging/jarvis.spec` (PyInstaller)

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

## 🔐 Code Signing (Production)

For professional distribution without Windows SmartScreen warnings:

1. **Get a certificate** from DigiCert, Sectigo, or similar
2. **Sign the executable**:
   ```batch
   signtool sign /f certificate.pfx /p password /t http://timestamp.digicert.com dist\JarvisV2\JarvisV2.exe
   ```
3. **Sign the installer**:
   ```batch
   signtool sign /f certificate.pfx /p password /t http://timestamp.digicert.com dist\installer\JarvisV2-Setup.exe
   ```

---

## 📚 Documentation

- **Full Guide:** `packaging/README.md`
- **Troubleshooting:** See above
- **Configuration:** Edit `config/config.json`
- **API Keys:** Edit `.env` (copy from `.env.example`)

---

## 🆘 Need Help?

1. **Check the error message** - usually tells you exactly what's wrong
2. **Run the test script**:
   ```batch
   python packaging\test_build.py
   ```
3. **Check GitHub Issues**: https://github.com/jonathansteve-cell/JarvisV2/issues
4. **Read the docs**: `docs/` folder

---

## ✅ Quick Checklist

Before building, make sure:

- [ ] Python 3.10+ is installed
- [ ] "Add python.exe to PATH" was checked during Python installation
- [ ] You have internet connection (for downloading dependencies)
- [ ] You have at least 500 MB free disk space
- [ ] Antivirus is not blocking the build folder

---

## 🎉 Ready to Build?

**Just double-click:**
```
packaging\OneClickBuild.bat
```

**And you'll have your installer in 5-10 minutes!**

---

*Built with ❤️ for the Jarvis V2 community*
