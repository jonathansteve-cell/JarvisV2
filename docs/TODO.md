# Jarvis V2 — To-Do List

What to add, and exactly how to get each item. Priority order: **P0 makes what you
already have work, P1 fixes things that are quietly broken, P2 adds real capability.**

P1 is complete; P0 is credentials you must supply yourself.

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

## P1 — Bugs found in the code — **all six now fixed on this branch**

Verified by 104 passing tests plus a live end-to-end run.

- [x] **Reminders now actually fire.** `core/jarvis.py` starts a daemon sweeper
      (`ProductivityController.start_notifier`) that scans `data/productivity.json`
      every 20 s, speaks every overdue reminder, and marks it `done` + stamps
      `fired_at` so it can only fire once. A failing callback cannot kill the
      sweeper, and `shutdown()` stops the thread. New command: `any reminders due`.
- [x] **Absolute times are parsed.** `parse_delay()` now understands `at 6pm`,
      `at 18:30`, `at 6:30 pm`, `tomorrow`, `tomorrow at 6pm`, and `in N weeks`.
      A bare `at 6` reads as 6pm; a time already gone today rolls to tomorrow.
      A reminder with no parseable time now *says so* instead of silently storing
      `due_at: null`.
- [x] **Smart home actually calls Home Assistant.** `set_device()` maps the spoken
      device onto a real entity (`light.living_room_light`, `climate.thermostat`,
      `lock.front_door`, `fan.ceiling_fan`) and POSTs to
      `/api/services/<domain>/<service>`. On failure it falls back to the local
      simulation *and says which one happened*. `smart home status` reports the
      real mode, including "configured but unreachable — simulating".
- [x] **Calendar uses the time you said.** `add_event()` parses the phrase, so
      "dentist tomorrow at 6pm" is filed for tomorrow 18:00 instead of an hour from
      now. Unparseable input is filed an hour out **and tells you**. `show calendar`
      now prints times, sorted.
- [x] **Email understands natural phrasing.** Added `email X saying Y`,
      `email to X subject Y body Z`, and a **draft → confirm** flow:
      `write an email to X about Y` holds a draft (never written to disk) until you
      say `send the email` or `cancel the email`. A waiting draft reminds you.
- [x] **Phone calls actually dial.** With `TWILIO_TWIML_URL` set it calls
      `client.calls.create(to, from_, url)` and returns the call SID. Without it,
      it opens the dialer and says exactly what is missing instead of dead-ending.
      A Twilio error is reported, not swallowed.

### Bonus bug found while fixing those

- [x] **A fresh `.env` counted as "configured".** Every placeholder
      (`your_twilio_sid_here`, `your_home_assistant_long_lived_token_here`, …) is a
      truthy string, so smart home claimed "Home Assistant" and phone claimed
      "Twilio is configured" while every call failed. New shared
      `utils.helpers.is_placeholder_secret()` is now used by email, smart home and
      phone, and `utils/health_check.py` imports the same constant instead of
      keeping its own copy.

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
2. **P1 code fixes:** done — reminder sweeper, absolute-time parsing, Home Assistant
   wiring, calendar times, email phrasing, phone dialling, and placeholder-credential
   detection all landed on this branch.
3. **When you want them:** Spotify and Twilio accounts.
