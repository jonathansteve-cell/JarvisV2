# The "Best Jarvis" Checklist

A prioritised, concrete roadmap to take Jarvis V2 from "works" to "the best assistant
on your desk". Statuses:

- `[x]` done on this branch (`arena/01a04d6c-jarvisv2`)
- `[key]` works once you add the named credential to `.env` (see docs/TODO.md P0)
- `[ ]` not yet built — a genuine upgrade idea

Run `python main.py --check --verbose` after each item to confirm it went green.

---

## 1. Presence — make it feel alive

- [x] **Neural voice.** `edge-tts` gives human-like speech; falls back to SAPI/eSpeak
      offline. (`voice.tts_engine` in config.)
- [x] **Always-on mic** with wake-free continuous listening and mic/SPEAK chips.
- [x] **A real face.** The FACE SCAN panel now renders an unmistakable holographic
      face (head, brows, blinking eyes, nose, mouth) with a scan sweep — not a blob.
- [x] **Living home.** 3D wireframe sun orb, breathes and rotates.
- [ ] **Lip-sync the face.** Drive the mouth curve from the TTS audio envelope so the
      face visibly talks. (~30 lines: sample volume while speaking, scale mouth path.)
- [ ] **Eyes track the speaker / cursor.** Subtle gaze motion sells "alive".
- [ ] **Mood lighting.** Shift the orb/face hue with intent (green=ok, amber=thinking,
      red=error) so state is visible at a glance.

## 2. Usefulness — make it actually do things

- [key] **Groq** → conversation. `GROQ_API_KEY`.
- [key] **Email** → `JARVIS_EMAIL_*`; send, unread count, latest subjects.
- [key] **Spotify** → `SPOTIFY_*`; play/pause/next/now-playing (needs Premium).
- [key] **WhatsApp / calls** → `TWILIO_*` (+ `TWILIO_TWIML_URL` for live dialling).
- [key] **Smart home** → `HOME_ASSISTANT_*`; lights/thermostat/locks for real.
- [key] **Wake-on-LAN** → `JARVIS_TARGET_PC_MAC`.
- [x] **Open ANY app** by fuzzy name (Start Menu / App Paths / .desktop / Applications).
- [x] **Reminders that fire**, absolute times, calendar that honours your stated time.
- [x] **Honest failures** — every module says what it did *and* what it simulated.
- [ ] **Groq tool-calling.** Let the AI pick modules, so "email Tony the report and
      remind me Friday" works in one breath (needs the Groq key).

## 3. Intelligence — make it remember and reason

- [x] **Persistent memory** (`my name is…`, facts) with `--check`-visible stats.
- [ ] **Episodic recall.** "what did we do last Tuesday?" from the conversation log.
- [ ] **Proactive briefings.** On wake: unread email count, first calendar item,
      weather — assembled from already-wired modules.
- [ ] **Learns app paths.** When you correct a launch once, save it to
      `applications.paths` automatically.

## 4. Reliability — make it trustworthy

- [x] **`--check`** self-diagnostic; exits non-zero on failure (CI-friendly).
- [x] **104 automated tests** incl. stubbed network paths for every integration.
- [x] **`.env` never committed** (removed from git in `11ddd10`).
- [ ] **Self-update notifier.** Compare local commit to GitHub; say "update available".
- [ ] **Crash-safe logs.** Ship a `jarvis --logs` tail command for debugging.

## 5. Interface — make it beautiful (this turn)

- [x] **Three buttons, not tabs.** Nav is exactly `HOME / CHAT / DASHBOARD`; the mic
      status and telemetry sit in a corner, clearly not a fourth tab.
- [x] **Clean home.** The bottom console (type box + SEND + SPEAK) is gone; Home is
      now just the living orb. Talk to it, or use CHAT / DASHBOARD to type.
- [x] **A real face** on the dashboard (see §1).
- [ ] **Command palette.** `Ctrl+K` to type any command from any view.
- [ ] **Theme toggle.** Keep the cyan HUD but offer a warm "solar" variant.

---

## Suggested next three moves

1. Add the P0 credentials (docs/TODO.md) so email / Spotify / smart home go live.
2. Lip-sync + mood lighting (§1) — the cheapest way to make it *feel* like Jarvis.
3. Groq tool-calling (§2) — the biggest jump in raw capability.
