# Jarvis V2 — To-Do List

What to add, and exactly how to get each item. Priority order: **P0 makes what you
already have work, P1 fixes things that are quietly broken, P2 adds real capability.**

Verify progress at any time with:

```bash
python main.py --check --verbose
```

---

## P0 — Free, 15 minutes, unlocks what's already built

- [ ] **Groq API key** — unlocks conversation instead of the "not configured" fallback.
  - *Get it:* [console.groq.com](https://console.groq.com) → **API Keys** → **Create API Key**. Free tier.
  - *Install it:* `.env` → `GROQ_API_KEY=gsk_…` and `GROQ_MODEL=llama-3.3-70b-versatile`
  - *Check:* `--check` must show `[OK] Groq API reachable, N models available`.

- [ ] **Gmail app password** — turns on real email send + inbox reading.
  - *Get it:* Google Account → **Security** → turn on **2-Step Verification** (required) →
    **App passwords** → generate a 16-character password. **Not** your normal password.
  - *Install it:* `.env` → `JARVIS_EMAIL_ADDRESS=you@gmail.com`,
    `JARVIS_EMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx`
  - *Use it:* `send email to tony@stark.com subject Update body The project is done`
  - ⚠️ Phrasing is rigid — see P1.

- [ ] **Voice dependencies** — currently `speech_recognition` and microphone show `[WARN]`.
  - *Get it:* `pip install -r requirements.txt`
  - *Windows mic fix:* `pip install pipwin && pipwin install pyaudio`
  - *Check:* `--check` should show `[OK] Microphone  N input device(s): …`

- [ ] **Neural voice playback** — `Audio player` warns without an mp3 player.
  - *Windows:* nothing to do, it uses the built-in WPF Media Player.
  - *Linux:* `sudo apt install mpv` (or `ffmpeg` for `ffplay`). *macOS:* already has `afplay`.
  - *Get it:* `pip install edge-tts` (already in `requirements.txt`).

- [ ] **Pillow** — screenshots currently fail without it.
  - *Get it:* `pip install pillow` → then `take screenshot` works.

- [ ] **Wake-on-LAN MAC** — `wake computer` says "needs a valid target MAC address".
  - *Get it:* on the PC you want to wake, run `ipconfig /all` → copy **Physical Address**.
  - *Install it:* `.env` → `JARVIS_TARGET_PC_MAC=AA:BB:CC:DD:EE:FF`

---

## P1 — Real bugs found in the code. Fix before trusting these features

- [ ] **Reminders never fire.** `remind me to stand up in 30 minutes` saves to
      `data/productivity.json` and nothing ever checks `due_at`. There is no scheduler
      anywhere in the codebase — the only timer in `productivity_controller.py` merely
      appends another JSON row.
  - *How to get it:* add a background sweeper thread started in `core/jarvis.py` that
    scans `data["reminders"]` every 20 s, speaks + marks done any entry whose `due_at`
    has passed. ~40 lines.

- [ ] **Absolute times are silently dropped.** `parse_delay()` (`utils/helpers.py:39`)
      only matches `in N minutes|hours|days`. `remind me to call mom at 6pm` stores
      `due_at: null` — verified.
  - *How to get it:* extend `parse_delay` with `at (\d{1,2})(:\d\d)?\s*(am|pm)?` and
    `tomorrow`, or pull in `dateparser` (`pip install dateparser`).

- [ ] **Smart home is dead code.** `SmartHomeController._home_assistant()` is defined at
      `modules/smart_home_controller.py:37` but **never called**. Verified: with
      `HOME_ASSISTANT_URL` + `HOME_ASSISTANT_TOKEN` set, `turn on living room light`
      still only writes local JSON — no HTTP request is made.
  - *How to get it:* call `_home_assistant("light", "turn_on", {...})` from `set_device()`
    and fall back to the local simulation only when it returns `False`.
  - *Then get the token:* Home Assistant → your **Profile** → **Long-Lived Access Tokens**
    → `.env` → `HOME_ASSISTANT_TOKEN=…`, `HOME_ASSISTANT_URL=http://homeassistant.local:8123`

- [ ] **Calendar ignores the time you say.** `add_event()` hard-codes
      `start = datetime.now() + timedelta(hours=1)` (`modules/calendar_controller.py:31`),
      so "dentist tomorrow" is filed an hour from now.
  - *How to get it:* reuse the improved `parse_delay` from above, or add Google Calendar
    via `google-api-python-client` + OAuth (free, needs a Google Cloud project).

- [ ] **Email phrasing is one brittle regex.** `send email to (\S+) subject (.+?) body (.+)`.
      `write an email to tony about the project` falls through to AI chat and sends nothing
      — verified.
  - *How to get it:* add a draft step — let Groq compose the body, read it back for
    confirmation, then call `send_email()`. Also add `reply to latest email`.

- [ ] **Phone calls never dial.** `phone_controller.py:21` returns "requires a TwiML URL"
      even with Twilio fully configured.
  - *How to get it:* host a TwiML bin that says `<Dial>{{to}}</Dial>`, put the URL in
    config, and call `client.calls.create(url=…)`.

---

## P2 — New capability, needs an account or a library

- [ ] **Spotify control** — `play song`, `pause`, `next`, `now playing` all return
      "Spotify API is not configured".
  - *Get it:* [developer.spotify.com/dashboard](https://developer.spotify.com/dashboard) →
    **Create app** → copy **Client ID** + **Client Secret**, set redirect URI to
    `http://localhost:8888/callback`.
  - *Install it:* `.env` → `SPOTIFY_CLIENT_ID`, `SPOTIFY_CLIENT_SECRET`, `SPOTIFY_REDIRECT_URI`
  - Note: needs Spotify **Premium** for playback control.

- [ ] **WhatsApp sending** — currently opens `wa.me` in a browser and asks you to hit send.
  - *Get it:* [twilio.com/try-twilio](https://www.twilio.com/try-twilio) (free trial) →
    Console → **Account SID** + **Auth Token**. For WhatsApp: Messaging → **Try it out** →
    send `join <your-code>` to **+1 415 523 8886**.
  - *Install it:* `.env` → `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_FROM_WHATSAPP`

- [ ] **Real Twitter/LinkedIn posting** — currently opens the site with text prepared.
  - *Get it:* [developer.twitter.com](https://developer.twitter.com) (paid tiers now) and a
    LinkedIn developer app. Honestly: not worth it for personal use, the browser fallback
    is fine.

- [ ] **`open roblox` launches the desktop app, not the website.**
  - *How to get it:* add a `roblox-player` entry to `applications.paths` in
    `config/config.json`, e.g.
    `"roblox": "C:/Program Files (x86)/Roblox/Versions/<version>/RobloxPlayerBeta.exe"`
  - The new any-app resolver (PR #3) will also find it via the Start Menu shortcut.

- [ ] **Windows notifications instead of speech-only alerts** — so reminders work while muted.
  - *Get it:* `pip install win11toast` or `pip install plyer`, then fire one from the
    reminder sweeper above.

---

## P3 — Polish

- [ ] **Reminder persistence across restarts** — re-arm timers on boot from
      `data/productivity.json`.
- [ ] **Natural-language email reading** — `read the email from Tony` (full body, not just
      subjects).
- [ ] **Multi-step Groq tool-calling** — let the AI pick modules instead of keyword matching,
      so "write an email to Tony about the project and remind me to follow up Friday" works
      in one breath.
- [ ] **`.env` hygiene** — already fixed in PR #3 (`11ddd10`); keep `.env` out of git.

---

## Suggested order

1. **Today, 15 min:** Groq key + Gmail app password + `pip install -r requirements.txt`
   + Pillow. That alone makes conversation, email, voice and screenshots real.
2. **Next session:** the three P1 code fixes — reminder sweeper, `parse_delay` absolute
   times, Home Assistant wiring. All small, all in this repo.
3. **When you want them:** Spotify and Twilio accounts.
