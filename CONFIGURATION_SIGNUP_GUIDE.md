# Jarvis V2 - Configuration & Sign-Up Guide

## 🎯 Overview

Jarvis V2 now includes a complete **configuration and sign-up system** with:

- ✅ **User Registration** - Create your personal Jarvis account
- ✅ **First-Run Wizard** - Guided setup for new users
- ✅ **Login System** - Secure authentication for returning users
- ✅ **Settings Panel** - Configure all aspects of Jarvis
- ✅ **API Management** - Easy API key configuration
- ✅ **Voice Settings** - Customize how Jarvis sounds
- ✅ **Security Features** - Password protection and encryption

---

## 🚀 Quick Start

### **First Time Users**
When you first run Jarvis, the setup wizard will appear automatically:

```bash
python main.py
```

The wizard will guide you through:
1. Creating your account
2. Configuring API keys
3. Setting up voice preferences
4. Final configuration

### **Returning Users**
You'll see the login screen:

```bash
python main.py
```

Enter your username and password to continue.

---

## 📋 Features

### **1. User Registration**

Create your personal Jarvis account:

- **Username** - Unique identifier (3-30 characters)
- **Display Name** - How Jarvis addresses you
- **Email** - Optional, for notifications
- **Password** - Secure, minimum 8 characters

**Security Features:**
- Passwords hashed with PBKDF2 (100,000 iterations)
- Unique salt per user
- Encrypted storage

### **2. First-Run Setup Wizard**

Interactive wizard that runs on first launch:

**Step 1: Welcome**
- Introduction to Jarvis V2
- Feature overview

**Step 2: Account Creation**
- Username and password
- Display name and email

**Step 3: API Configuration**
- Groq AI (recommended)
- Email (Gmail)
- Twilio (WhatsApp/Phone)
- Spotify (Music)

**Step 4: Voice Settings**
- Voice profile selection
- TTS engine choice

**Step 5: Completion**
- Quick start guide
- Ready to use!

### **3. Login System**

Secure login for returning users:

- Username/password authentication
- Show/hide password toggle
- "Create New Account" option
- Error handling with helpful messages

### **4. Settings Panel**

Comprehensive settings dialog with tabs:

**Profile Tab**
- Display name
- Email address
- How Jarvis addresses you

**API Keys Tab**
- Groq AI configuration
- OpenAI configuration
- Email (Gmail) setup
- Twilio credentials
- Spotify credentials

**Voice Tab**
- Voice profile selection
- TTS engine choice

**Preferences Tab**
- Speak responses
- Remember conversations
- Learning enabled
- Confirm dangerous actions
- Window transparency

**Security Tab**
- Change password
- Logout option

---

## 🖥️ GUI Components

### **Setup Wizard GUI**
Graphical setup wizard with:
- Modern dark theme
- Progress tracking
- Step-by-step guidance
- Input validation

### **Login Dialog**
Clean login interface with:
- Username/password fields
- Show/hide password
- Error messages
- Registration link

### **Settings Dialog**
Tabbed settings panel with:
- Profile management
- API configuration
- Voice settings
- Preferences
- Security options

---

## 🔧 Command Line Interface

### **Setup Wizard (CLI)**
```bash
python -m core.setup_wizard
```

### **Login Check**
```bash
python -c "from core.setup_wizard import check_and_login; check_and_login()"
```

### **User Management**
```bash
# Check if users exist
python -c "from core.user_manager import get_user_manager; um = get_user_manager(); print(f'Users: {um.get_user_count()}')"

# Check if logged in
python -c "from core.user_manager import get_user_manager; um = get_user_manager(); print(f'Logged in: {um.is_logged_in()}')"
```

---

## 📁 File Structure

### **User Data**
```
data/
├── users.json              # User accounts (hashed passwords)
├── current_user.json       # Current session
└── user_preferences.json   # User preferences
```

### **Configuration**
```
config/
├── config.json             # App configuration
├── api_config.json         # API settings
├── .credentials.enc        # Encrypted credentials
└── .master.key             # Encryption key
```

### **Source Code**
```
core/
├── user_manager.py         # User management
├── setup_wizard.py         # CLI setup wizard
├── api_manager.py          # API management
├── api_validator.py        # API validation
└── secure_env.py           # Secure .env management

gui/
├── setup_wizard_gui.py     # GUI setup wizard
├── login_dialog.py         # Login dialog
└── settings_dialog.py      # Settings dialog
```

---

## 🔒 Security Features

### **Password Security**
- PBKDF2 hashing (100,000 iterations)
- Unique salt per user
- Never stored in plain text
- Minimum 8 characters required

### **API Key Security**
- Encrypted storage (Fernet/AES-256)
- Never committed to Git
- Masked in UI (shows ****)
- Secure key rotation

### **Session Security**
- Login required on startup
- Session persistence
- Secure logout
- Password change support

---

## 🎨 Customization

### **Voice Profiles**
Choose from 4 voice profiles:

1. **Dark Synthetic** (Default)
   - Slow, low, commanding
   - Perfect for Jarvis personality

2. **Jarvis Classic**
   - Calm, polite, professional
   - Butler-like demeanor

3. **Fast Operator**
   - Brisk, mission-control pace
   - Quick and efficient

4. **Gentle**
   - Softer, quieter voice
   - Late-night friendly

### **TTS Engines**
Choose your preferred engine:

1. **Auto** (Recommended)
   - Best available engine
   - Automatic fallback

2. **Edge Neural**
   - Natural, human-like
   - Requires internet

3. **pyttsx3**
   - Offline capable
   - Robotic voice

4. **System**
   - OS default voice
   - Basic quality

---

## 🧪 Testing

### **Test User Registration**
```bash
python -c "
from core.user_manager import get_user_manager
um = get_user_manager()
success, msg = um.register_user('testuser', 'password123', 'Test User')
print(f'Registration: {success} - {msg}')
"
```

### **Test Login**
```bash
python -c "
from core.user_manager import get_user_manager
um = get_user_manager()
success, msg = um.login('testuser', 'password123')
print(f'Login: {success} - {msg}')
"
```

### **Test Setup Wizard**
```bash
python -m core.setup_wizard
```

---

## 🎯 Integration with Main App

### **Automatic Detection**
The main application automatically detects:

1. **First Run** → Shows setup wizard
2. **Existing User** → Shows login dialog
3. **Logged In** → Proceeds to main app

### **GUI Integration**
```python
# In your main GUI code:
from gui.setup_wizard_gui import run_setup_wizard_gui
from gui.login_dialog import show_login_dialog

# Check if setup needed
if not run_setup_wizard_gui():
    return  # Setup failed

# Check if login needed
if not show_login_dialog():
    return  # Login failed

# Proceed to main app
```

### **CLI Integration**
```python
# In your main CLI code:
from core.setup_wizard import check_and_login

if not check_and_login():
    return 1  # Login failed

# Proceed with Jarvis
```

---

## 📊 User Data Storage

### **Users File (users.json)**
```json
{
  "username": {
    "username": "john",
    "display_name": "John Doe",
    "email": "john@example.com",
    "password_hash": "abc123...",
    "password_salt": "xyz789...",
    "created_at": "2026-08-30T10:00:00",
    "last_login": "2026-08-30T12:00:00",
    "login_count": 5,
    "preferences": {}
  }
}
```

### **Preferences File (user_preferences.json)**
```json
{
  "voice_profile": "dark_synthetic",
  "tts_engine": "auto",
  "speak_responses": true,
  "remember_conversations": true,
  "learning_enabled": true,
  "confirm_dangerous_actions": true,
  "transparency": 0.98,
  "owner_name": "sir"
}
```

---

## 🚀 Quick Commands

### **Start Setup Wizard**
```bash
python main.py  # Auto-detects first run
```

### **Force Setup Wizard**
```bash
python -m core.setup_wizard
```

### **Open Settings**
```bash
# From GUI: Click ⚙ Settings in the menu
# From CLI: python -m gui.settings_dialog
```

### **Change Password**
```bash
# From GUI: Settings → Security → Change Password
# From CLI: Use the settings dialog
```

---

## 💡 Tips

1. **First Run** - The setup wizard runs automatically on first launch
2. **Skip API Setup** - You can configure APIs later in Settings
3. **Voice Profiles** - Try different profiles to find your favorite
4. **Security** - Use a strong password for your account
5. **Backup** - Your data is stored in the `data/` folder

---

## 🆘 Troubleshooting

### **"Username already exists"**
- Choose a different username
- Or login with existing account

### **"Invalid password"**
- Check caps lock
- Use "Create New Account" if needed

### **"Setup wizard not appearing"**
- Delete `data/users.json` to reset
- Or run: `python -m core.setup_wizard`

### **"Settings not saving"**
- Check file permissions
- Ensure `data/` folder exists

---

## 📚 Documentation

- **`CONFIGURATION_SIGNUP_GUIDE.md`** - This guide
- **`API_CONFIGURATION_GUIDE.md`** - API setup details
- **`packaging/README.md`** - Installer guide

---

## 🎉 Summary

Your Jarvis V2 now includes:

✅ **Complete user system** - Registration, login, profiles
✅ **First-run wizard** - Guided setup for new users
✅ **Settings panel** - Configure everything
✅ **API management** - Easy key configuration
✅ **Voice customization** - Multiple profiles and engines
✅ **Security features** - Encryption and password protection
✅ **GUI components** - Modern, dark-themed interface

**Ready to get started?** Run `python main.py` and the setup wizard will guide you through everything! 🚀
