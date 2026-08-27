# J.A.R.V.I.S V2 - All-in-One Desktop AI Assistant

> Voice-first desktop assistant inspired by Tony Stark's JARVIS and by the open-source Python Jarvis assistant ecosystem.

J.A.R.V.I.S V2 combines local desktop automation, voice recognition, text-to-speech, memory, AI chat with Groq, productivity tools, and optional integrations for email, WhatsApp, Spotify, calendar, phone calls, Zoom, Word documents, social posting, smart home devices, and Wake-on-LAN.

## Important security note

A Groq API key was provided in the chat, but real secrets are **not committed to GitHub**. GitHub blocks exposed API keys and it is unsafe to publish them. Use `.env.example` as a template, create a local `.env` on your PC, and place your key there:

```env
GROQ_API_KEY=your_real_key_here
```

`.env` is intentionally ignored by Git.

## What I read and merged

This implementation was built from the requirements in your pasted Jarvis V2 specification plus inspiration from:

- `kishanrajput23/Jarvis-Desktop-Voice-Assistant` — Python voice assistant features such as greetings, time/date, app launching, websites, Google/Wikipedia, music, notes, screenshots, jokes.
- `Blazehue/J.A.R.V.I.S` — advanced Jarvis V2 architecture, desktop control, voice, GUI, configuration, personality, screenshots, system control, window/file management.
- The `jarvis-ai-assistant` GitHub topic — common assistant patterns: modular controllers, NLP routing, voice I/O, automation, and optional third-party integrations.

This repository contains original modular code, not a blind copy-paste of those projects.

## Capability overview

### Voice and AI

- Wake words: `hey jarvis`, `jarvis`
- Speech recognition with `SpeechRecognition`
- Spoken responses with `pyttsx3` or OS fallback
- Groq chat completions when `GROQ_API_KEY` is configured
- Offline fallback responses when AI credentials are missing
- Voice-only mode with no GUI response output

### Desktop/system

- Open/close/list applications
- Volume and mute controls
- Lock, sleep, restart, shutdown safety handling
- CPU, memory, disk, and battery status
- Screenshot capture
- Window maximize/minimize/snap hotkeys
- File/folder opening, folder creation, and file search

### Web and productivity

- Google search
- Open common websites
- Wikipedia summaries
- Weather/news via browser search/pages
- Notes, tasks, reminders, and timers
- Persistent memory and learning using SQLite

### Integrations

- Email send/read/unread count through SMTP/IMAP
- WhatsApp messages through Twilio or WhatsApp Web fallback
- Spotify playback/search/status through Spotify API or web fallback
- Calendar events with local storage fallback
- Phone dialer through `tel:` links and Twilio-ready structure
- Zoom meeting join links and mute/video hotkeys
- Word document create/append/read using `python-docx`
- Twitter/LinkedIn posting helpers
- Smart-home simulation and Home Assistant-ready REST calls
- Wake-on-LAN for sleeping PCs

## Can it do whatever you want?

No software can literally do anything. Jarvis V2 can perform the commands it has modules for and can answer general questions through Groq AI. It cannot turn on a fully powered-off PC without Wake-on-LAN/smart-plug/BIOS support, bypass account security, perform illegal hacking, or do physical-world actions without hardware.

## Quick start

```bash
git clone https://github.com/jonathansteve-cell/JarvisV2.git
cd JarvisV2
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
# source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# edit .env and add your own local keys
python main.py
```

## Run modes

```bash
# Full arc-reactor desktop UI
python main.py

# Voice-only mode: no GUI, no command response printed to console
python main.py --voice-only
# or
python main_voice_only.py

# One command for testing
python main.py --command "what can you do"
```

## Example commands

```text
Hey Jarvis, what can you do?
Hey Jarvis, system status
Hey Jarvis, open Chrome
Hey Jarvis, take a screenshot
Hey Jarvis, set volume to 50
Hey Jarvis, remind me to check the oven in 20 minutes
Hey Jarvis, take note: order replacement cables
Hey Jarvis, remember my favorite color is blue
Hey Jarvis, what do you remember about me?
Hey Jarvis, send email to alex@example.com subject Hello body This is Jarvis
Hey Jarvis, send WhatsApp to +15551234567: I am on my way
Hey Jarvis, play song Time by Hans Zimmer
Hey Jarvis, join Zoom meeting 123456789
Hey Jarvis, create document Project Plan
Hey Jarvis, add to document: Phase one is complete
Hey Jarvis, wake computer
```

## Project structure

```text
JarvisV2/
├── main.py                       # GUI, voice-only, and one-command launcher
├── main_voice_only.py            # voice-only compatibility launcher
├── core/                         # orchestrator and configuration
├── modules/                      # feature controllers and integrations
├── voice/                        # speech recognition and TTS wrappers
├── personality/                  # Groq/offline response generator
├── gui/                          # Tkinter arc-reactor UI
├── utils/                        # logging, env loading, helpers
├── config/                       # safe config examples/default config
├── docs/                         # command, setup, integration, security docs
├── tests/                        # automated tests
├── data/                         # runtime memory DB (ignored)
└── logs/                         # runtime logs (ignored)
```

## Configuration

1. Copy `.env.example` to `.env`.
2. Add local secrets only on your machine.
3. Edit `config/config.json` for non-secret settings.

Common values:

```json
{
  "voice": {
    "wake_words": ["hey jarvis", "jarvis"],
    "tts_enabled": true,
    "continuous_listening": true
  },
  "behavior": {
    "confirm_dangerous_actions": true,
    "speak_responses": true,
    "remember_conversations": true
  }
}
```

## Power-on reality

Jarvis can shut down, restart, sleep, lock, and wake a sleeping PC with Wake-on-LAN if configured. It cannot turn on a completely powered-off computer by normal software alone. For true remote power-on, use Wake-on-LAN, a smart plug with BIOS "AC power restore", or enterprise hardware like Intel AMT/vPro.

## Development

```bash
pip install -r requirements-dev.txt
python -m pytest
python -m compileall core modules voice personality gui utils main.py
```

## License

MIT. See `LICENSE`.
