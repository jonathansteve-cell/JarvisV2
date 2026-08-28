# J.A.R.V.I.S V2 — All-in-One Package

Welcome, sir. This package contains the complete Jarvis V2 desktop assistant:

- **Hero Core HUD** — photoreal burning-sun core with sparkle starfield, orange on black
- **Voice in / voice out** — wake words, speech recognition, and configurable voices
  (`dark_synthetic` heavy synthetic persona by default — an original persona, not a
  clone of any film character)
- **Groq AI chat** (Llama 3.3 70B) with offline fallback persona
- **Persistent SQLite memory** — your name, preferences, facts, conversation history
- **19 modules** — system control, apps, windows, screenshots, files, web, jokes,
  time/date, productivity, music (Spotify **+ local `~/Music` playback**), email,
  WhatsApp, phone, calendar, Zoom, Word docs, social, smart home, Wake-on-LAN
- **Roblox safe mode** — grind sessions, goals, progress tracking, official links,
  and honest Robux guidance. No exploits, bots, or Robux generators — ever.

## Quick start (2 minutes)

```bash
cd JarvisV2
python -m venv .venv

# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
python setup.py --init
python main.py
```

## Add your Groq API key (optional, unlocks full AI chat)

```bash
cp .env.example .env        # Windows: copy .env.example .env
```

Then open `.env` in any editor and set:

```env
GROQ_API_KEY=your_real_groq_api_key
GROQ_MODEL=llama-3.3-70b-versatile
```

Get a free key at console.groq.com. **Never share the key or commit `.env`** — and
if you ever paste a key into a chat, revoke it and create a new one.

## Run modes

| Mode | Command |
| --- | --- |
| Solar Core HUD (default) | `python main.py` |
| **Web Dashboard (Spark-style)** | `python main.py --web` → open http://localhost:8765 |
| Voice only, no window | `python main.py --voice-only` |
| One command, then exit | `python main.py --command "system status"` |

The **Web Dashboard** is a glassmorphism control center in your browser: circular
CPU/MEM/DISK gauges, AI chat console, tasks/notes/memory cards, Roblox session
panel, quick actions, and browser-side voice replies. It runs on Python's standard
library only — no extra dependencies. Open `http://<your-pc-ip>:8765` from a phone
on the same network to control your PC from the couch.

## Try these first

```text
what can you do?
system status
tell me a joke
what time is it / what's the date today?
play music
start 30 minute roblox grind session for daily quests
roblox stats
set roblox goal: reach level 50
how do I get robux safely?
remember my name is Tony
```

Full documentation: see `README.md` and `docs/UI.md` inside this package.
