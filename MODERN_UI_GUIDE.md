# Jarvis V2 - Modern UI Guide

## 🎨 Overview

The Modern UI is a sleek, professional interface for Jarvis V2 featuring:

- ✅ **Dark Theme** - Easy on the eyes with orange accents
- ✅ **Chat Interface** - Natural conversation with Jarvis
- ✅ **Voice Controls** - One-click voice input
- ✅ **System Status** - Real-time CPU, memory, disk monitoring
- ✅ **Mode Selection** - Quick access to Research, Roblox, Serious modes
- ✅ **Settings Panel** - Easy configuration
- ✅ **Responsive Design** - Adapts to window size

---

## 🚀 Quick Start

### **Launch Modern UI**
```bash
python launch_modern_ui.py
```

### **Or use the start script**
```bash
start.bat
```

---

## 🖥️ Interface Layout

### **Header**
- **Logo** - Jarvis V2 branding
- **Title** - "J.A.R.V.I.S V2"
- **Navigation** - Chat, Dashboard, Settings buttons
- **User Info** - Current user display

### **Left Sidebar**

#### **🎮 Modes Panel**
Quick access to different modes:

| Mode | Description |
|------|-------------|
| 🔬 Research | Automated topic research |
| 🎮 Roblox Grind | Automated Roblox grinding |
| 💼 Serious Mode | Productivity workspaces |
| 🎤 Voice Only | Voice-only mode |

#### **📊 System Panel**
Real-time system monitoring:

- **CPU** - Current CPU usage with progress bar
- **Memory** - RAM usage with progress bar
- **Disk** - Storage usage with progress bar
- **Battery** - Battery level (if available)

#### **⚙ Settings Panel**
Current configuration display:

- Voice Profile
- TTS Engine
- Speak Responses
- Remember Conversations
- API Status (Groq, Email, Spotify)

### **Main Content Area**

#### **💬 Chat Panel**
Main conversation interface:

- **Message History** - Scrollable chat log
- **Input Field** - Type messages here
- **Send Button** - Send message
- **Voice Button** - 🎤 Voice input

### **Status Bar**
Bottom status bar showing:

- **AI Status** - Online/Offline indicator
- **Voice Status** - Ready/Not Available
- **Current Time** - Real-time clock

---

## 🎯 Features

### **Chat Interface**

#### **Sending Messages**
1. Type your message in the input field
2. Press Enter or click Send
3. Jarvis will respond in the chat

#### **Voice Input**
1. Click the 🎤 button
2. Speak your command
3. Jarvis will process and respond

#### **Message Types**
- **User Messages** - Your input (orange text)
- **Jarvis Responses** - AI responses (orange text)
- **System Messages** - Status updates (gray text)
- **Error Messages** - Error notifications (red text)

### **Mode Selection**

#### **Research Mode**
```
1. Click "🔬 Research" in the sidebar
2. Type your research topic
3. Jarvis will research and organize findings
```

#### **Roblox Grind Mode**
```
1. Click "🎮 Roblox Grind" in the sidebar
2. Select a game
3. Set goals and duration
4. Jarvis will track your progress
```

#### **Serious Mode**
```
1. Click "💼 Serious Mode" in the sidebar
2. Select a workspace (Coding, Studying, etc.)
3. Jarvis will open relevant apps and websites
```

#### **Voice-Only Mode**
```
1. Click "🎤 Voice Only" in the sidebar
2. Jarvis will listen for voice commands
3. No GUI interaction needed
```

### **System Monitoring**

The system panel shows real-time statistics:

| Metric | Description |
|--------|-------------|
| CPU | Processor usage (0-100%) |
| Memory | RAM usage (0-100%) |
| Disk | Storage usage (0-100%) |
| Battery | Battery level (if available) |

Progress bars provide visual representation:
- **Green** (< 60%) - Normal usage
- **Orange** (60-85%) - Moderate usage
- **Red** (> 85%) - High usage

### **Settings Display**

The settings panel shows current configuration:

| Setting | Description |
|---------|-------------|
| Voice Profile | Current voice (Dark Synthetic, etc.) |
| TTS Engine | Text-to-speech engine (Auto, Edge, etc.) |
| Speak Responses | Whether Jarvis speaks aloud |
| Remember Conversations | Whether to save chat history |

API status shows connection state:
- **Connected** - API is configured and working
- **Not configured** - API key not set

---

## 🎨 Customization

### **Color Scheme**

The UI uses a dark theme with orange accents:

```python
COLORS = {
    'bg': '#0a0a0a',           # Main background
    'bg_secondary': '#121212', # Secondary background
    'accent': '#FF8C1A',       # Orange accent
    'text': '#FFFFFF',         # White text
    'text_secondary': '#A0A0A0', # Gray text
    'success': '#38E07C',      # Green for success
    'error': '#E05555',        # Red for errors
}
```

### **Font Settings**

Default fonts:
- **Headers** - Segoe UI, 14-16pt, Bold
- **Body** - Segoe UI, 10-11pt
- **Monospace** - Consolas, 10pt

### **Window Size**

Default: 1200x800 pixels
Minimum: 1000x600 pixels

---

## 🔧 Technical Details

### **Architecture**

```
ModernJarvisUI
├── Header (logo, title, navigation)
├── Main Content
│   ├── Sidebar
│   │   ├── ModePanel
│   │   ├── SystemPanel
│   │   └── SettingsPanel
│   └── Content Area
│       └── ChatPanel
└── StatusBar
```

### **Components**

| Component | File | Description |
|-----------|------|-------------|
| ModernJarvisUI | modern_ui.py | Main application |
| ChatPanel | modern_ui.py | Chat interface |
| ModePanel | modern_ui.py | Mode selection |
| SystemPanel | modern_ui.py | System monitoring |
| SettingsPanel | modern_ui.py | Settings display |
| StatusBar | modern_ui.py | Status bar |
| ModernButton | modern_ui.py | Styled button |
| ModernEntry | modern_ui.py | Styled input |

### **Threading**

Voice input and AI processing run in separate threads to keep the UI responsive:

```python
threading.Thread(target=self.on_send, args=(message,), daemon=True).start()
```

### **Real-time Updates**

System stats update every 2 seconds:
```python
self.root.after(2000, self._update_system_stats)
```

Time updates every second:
```python
self.after(1000, self._update_time)
```

---

## 🧪 Testing

### **Run the UI**
```bash
python launch_modern_ui.py
```

### **Test Components**
```bash
# Test chat functionality
python -c "from gui.modern_ui import ModernJarvisUI; ui = ModernJarvisUI(); ui.run()"

# Test system monitoring
python -c "import psutil; print(f'CPU: {psutil.cpu_percent()}%')"
```

---

## 🆘 Troubleshooting

### **UI won't start**
- Make sure Python 3.10+ is installed
- Install required packages: `pip install psutil`
- Check for error messages in the console

### **System stats not showing**
- Install psutil: `pip install psutil`
- Some stats may not be available on all systems

### **Voice input not working**
- Check microphone permissions
- Install PyAudio: `pip install pyaudio`
- Verify voice recognition is configured

### **Chat not responding**
- Check if Jarvis core is initialized
- Verify API keys are configured (for AI responses)
- Check console for error messages

---

## 📚 Related Documentation

- **`DESKTOP_APP_GUIDE.md`** - Desktop application guide
- **`MODES_GUIDE.md`** - Research, Roblox, Serious modes
- **`CONFIGURATION_SIGNUP_GUIDE.md`** - User setup
- **`API_CONFIGURATION_GUIDE.md`** - API setup

---

## 🎉 Summary

The Modern UI provides:

✅ **Professional Interface** - Dark theme with orange accents
✅ **Chat Interface** - Natural conversation with Jarvis
✅ **Voice Controls** - One-click voice input
✅ **System Monitoring** - Real-time CPU, memory, disk stats
✅ **Mode Selection** - Quick access to all modes
✅ **Settings Display** - Easy configuration view
✅ **Responsive Design** - Adapts to window size

**Ready to try it?** Run `python launch_modern_ui.py` and experience the modern Jarvis V2 interface! 🚀
