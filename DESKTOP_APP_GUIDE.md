# Jarvis V2 - Desktop Application Guide

## 🎯 Overview

Jarvis V2 is now a complete desktop application with:

- ✅ **Professional Desktop App** - Standalone executable
- ✅ **Windows Installer** - Easy installation with Install.exe
- ✅ **Portable Version** - No-install ZIP package
- ✅ **First-Run Setup** - Guided configuration wizard
- ✅ **User Login System** - Secure authentication
- ✅ **All Features Included** - Research, Roblox, Serious Mode

---

## 🚀 Quick Start

### **Option 1: Use the Installer (Recommended)**
1. Download `JarvisV2-Setup.exe`
2. Double-click to install
3. Follow the installation wizard
4. Launch from desktop shortcut

### **Option 2: Portable Version**
1. Download `JarvisV2-Portable-2.0.0.zip`
2. Extract to any folder
3. Run `JarvisV2.exe`

### **Option 3: Build from Source**
```bash
# Windows
BuildApp.bat

# Or manually
python packaging/create_installer.py
```

---

## 📁 Application Structure

```
JarvisV2/
├── JarvisV2.exe              # Main application
├── config/                   # Configuration files
│   ├── config.json          # App settings
│   ├── api_config.json      # API settings
│   └── config.example.json  # Example config
├── data/                     # User data
│   ├── users.json           # User accounts
│   ├── current_user.json    # Current session
│   └── user_preferences.json # User settings
├── logs/                     # Application logs
├── screenshots/              # Saved screenshots
├── documents/                # Created documents
├── research/                 # Research folders
├── .env.example             # Environment template
├── README.md                # Documentation
└── LICENSE                  # License file
```

---

## 🖥️ First Launch

### **Step 1: Setup Wizard**
When you first run Jarvis V2, the setup wizard appears:

1. **Welcome Screen**
   - Introduction to Jarvis V2
   - Feature overview

2. **Create Account**
   - Username (3-30 characters)
   - Display name
   - Email (optional)
   - Password (min 8 characters)

3. **Configure APIs**
   - Groq AI (recommended)
   - Email (Gmail)
   - Twilio (WhatsApp/Phone)
   - Spotify (Music)

4. **Voice Settings**
   - Voice profile selection
   - TTS engine choice

5. **Complete**
   - Quick start guide
   - Ready to use!

### **Step 2: Login**
After setup, you'll see the login screen:
- Enter your username and password
- Click "Sign In"
- Or create a new account

### **Step 3: Main Application**
The main Jarvis V2 interface appears with:
- **Home** - Solar Core HUD
- **AI Chat** - Conversation interface
- **Dashboard** - System telemetry and controls

---

## 🎮 Features

### **Research Mode**
Automated topic research with organized folders.

```
Hey Jarvis, research about artificial intelligence
Hey Jarvis, add note: Neural networks are inspired by the brain
Hey Jarvis, generate research report
```

**Output:**
```
research/
└── artificial_intelligence_20260830/
    ├── research_log.md
    ├── RESEARCH_REPORT.md
    ├── quick_facts.md
    ├── sources/
    └── notes/
```

### **Roblox Grind Mode**
Automated Roblox grinding for Robux.

```
Hey Jarvis, start roblox grind for 30 minutes
Hey Jarvis, set roblox goal: reach level 50
Hey Jarvis, roblox grind status
Hey Jarvis, end grind session
```

**Features:**
- 8 popular grind games
- Session tracking
- Robux estimation
- Goal management

### **Serious Mode**
Productivity workspaces for learning and work.

```
Hey Jarvis, open coding workspace
Hey Jarvis, open study mode
Hey Jarvis, enable focus mode
```

**Available Workspaces:**
- Coding, Studying, Writing, Research
- Math, Science, Language Learning
- Business, Creative, Exam Prep

---

## ⚙️ Configuration

### **User Settings**
Access via: Settings → Profile

- Display name
- Email address
- How Jarvis addresses you

### **API Configuration**
Access via: Settings → API Keys

- Groq AI key
- OpenAI key
- Email credentials
- Twilio credentials
- Spotify credentials

### **Voice Settings**
Access via: Settings → Voice

- Voice profiles:
  - Dark Synthetic (default)
  - Jarvis Classic
  - Fast Operator
  - Gentle

- TTS engines:
  - Auto (recommended)
  - Edge Neural
  - pyttsx3
  - System

### **Preferences**
Access via: Settings → Preferences

- Speak responses
- Remember conversations
- Learning enabled
- Confirm dangerous actions
- Window transparency

---

## 🔒 Security

### **Password Protection**
- PBKDF2 hashing (100,000 iterations)
- Unique salt per user
- Minimum 8 characters
- Never stored in plain text

### **API Key Security**
- Encrypted storage (Fernet/AES-256)
- Never committed to Git
- Masked in UI
- Secure key rotation

### **Session Management**
- Login required on startup
- Session persistence
- Secure logout
- Password change support

---

## 🛠️ Building from Source

### **Prerequisites**
- Python 3.10+
- pip (Python package manager)
- Inno Setup 6 (for installer)

### **Quick Build**
```bash
# Windows
BuildApp.bat

# Or
python packaging/create_installer.py
```

### **Manual Build**
```bash
# 1. Create virtual environment
python -m venv .venv
.venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt
pip install pyinstaller pillow

# 3. Generate icons
python packaging/make_icon.py
python packaging/create_installer_images.py

# 4. Build executable
pyinstaller --noconfirm --clean packaging/jarvis_desktop.spec

# 5. Create installer (requires Inno Setup 6)
"C:\Program Files\Inno Setup 6\ISCC.exe" packaging/installer.iss
```

### **Output Files**
- `dist/JarvisV2/JarvisV2.exe` - Desktop application
- `dist/installer/JarvisV2-Setup.exe` - Windows installer
- `dist/JarvisV2-Portable-2.0.0.zip` - Portable package

---

## 📋 File Structure

### **Source Code**
```
JarvisV2/
├── desktop_app.py           # Desktop app entry point
├── main.py                  # Main launcher
├── core/                    # Core modules
│   ├── jarvis.py           # Main orchestrator
│   ├── config_manager.py   # Configuration
│   ├── user_manager.py     # User management
│   ├── api_manager.py      # API management
│   └── ...
├── gui/                     # GUI components
│   ├── main_window.py      # Main window
│   ├── login_dialog.py     # Login dialog
│   ├── settings_dialog.py  # Settings
│   └── setup_wizard_gui.py # Setup wizard
├── modules/                 # Feature modules
│   ├── research_controller.py
│   ├── roblox_grind_controller.py
│   ├── serious_mode_controller.py
│   └── ...
└── packaging/               # Build scripts
    ├── create_installer.py
    ├── installer.iss
    └── ...
```

### **Build Output**
```
dist/
├── JarvisV2/                # Application folder
│   ├── JarvisV2.exe        # Executable
│   ├── config/             # Configuration
│   ├── data/               # User data
│   └── ...
├── installer/               # Installer folder
│   └── JarvisV2-Setup.exe  # Installer
└── JarvisV2-Portable.zip   # Portable package
```

---

## 🎨 Customization

### **Change Application Icon**
1. Replace `packaging/app.png` with your icon (1024x1024)
2. Run: `python packaging/make_icon.py`
3. Rebuild: `python packaging/create_installer.py`

### **Modify Configuration**
Edit `config/config.json`:
```json
{
  "app": {
    "name": "J.A.R.V.I.S V2",
    "mode": "gui"
  },
  "voice": {
    "voice_profile": "dark_synthetic"
  }
}
```

### **Add Custom Workspaces**
Edit `modules/serious_mode_controller.py`:
```python
WORKSPACES["my_workspace"] = {
    "name": "My Workspace",
    "apps": [...],
    "websites": [...]
}
```

---

## 🧪 Testing

### **Test the Application**
```bash
# Run directly
python desktop_app.py

# Or run the main launcher
python main.py --gui
```

### **Test Specific Features**
```bash
# Test research mode
python -c "from modules.research_controller import get_research_controller; rc = get_research_controller(); print(rc.start_research('test'))"

# Test Roblox grind
python -c "from modules.roblox_grind_controller import get_roblox_grind_controller; rgc = get_roblox_grind_controller(); print(rgc.get_available_games())"

# Test serious mode
python -c "from modules.serious_mode_controller import get_serious_mode_controller; smc = get_serious_mode_controller(); print(smc.get_available_workspaces())"
```

---

## 🆘 Troubleshooting

### **"Application won't start"**
- Check if all runtime folders exist (data, logs, screenshots, documents)
- Try running from command line to see error messages
- Make sure .env file is configured

### **"Build failed"**
- Check Python version (3.10+ required)
- Install all dependencies: `pip install -r requirements.txt`
- Check for error messages in the console

### **"Installer not created"**
- Install Inno Setup 6: https://jrsoftware.org/isdl.php
- Or use the portable version instead

### **"Login not working"**
- Delete `data/users.json` to reset
- Or run: `python -m core.setup_wizard`

---

## 📚 Documentation

- **`DESKTOP_APP_GUIDE.md`** - This guide
- **`MODES_GUIDE.md`** - Research, Roblox, Serious modes
- **`CONFIGURATION_SIGNUP_GUIDE.md`** - User setup
- **`API_CONFIGURATION_GUIDE.md`** - API setup
- **`INSTALLER_GUIDE.md`** - Installer details

---

## 🎉 Summary

Your Jarvis V2 desktop application includes:

✅ **Professional Desktop App** - Standalone executable
✅ **Windows Installer** - Easy installation
✅ **Portable Version** - No-install package
✅ **First-Run Setup** - Guided configuration
✅ **User Login System** - Secure authentication
✅ **Research Mode** - Automated topic research
✅ **Roblox Grind Mode** - Automated grinding
✅ **Serious Mode** - Productivity workspaces
✅ **All Original Features** - 19+ modules

**Ready to build?** Run `BuildApp.bat` and you'll have your installer! 🚀

---

## 📞 Support

- **GitHub Issues**: https://github.com/jonathansteve-cell/JarvisV2/issues
- **Documentation**: See `docs/` folder
- **Configuration**: Edit `config/config.json`
