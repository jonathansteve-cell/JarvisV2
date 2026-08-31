# UI Guide — CyberHUD + Desktop HUD

Jarvis V2 ships **two interfaces**, both in the same black-and-orange Hero style:

1. **CyberHUD** (`ui/` + `dashboard/server.py`) — React browser dashboard, the
   default. `python main.py` → `http://localhost:8765`
2. **Hero Core HUD** (`gui/main_window.py`) — native Tkinter desktop app via
   `python main.py --gui`

![UI mockup](images/jarvis_v2_hero_ui_mockup.png)

## CyberHUD (browser)

A holographic telemetry dashboard: a central reactor core with live CPU / RAM /
GPU / NET rings, per-drive storage cards, a process monitor, a weather uplink,
a task list, and a natural-language command console.

Build it once, then run:

```bash
cd ui && npm install && npm run build
cd .. && python main.py --web          # http://localhost:8765
```

Open `http://localhost:8765` on the same machine, or `http://<your-pc-ip>:8765`
from a phone or tablet on the same network.

For live-reload development, run the API and the UI separately:

```bash
python main.py --web                   # terminal 1
cd ui && npm run dev                   # terminal 2 → http://localhost:3000
```

| Panel | Contents |
| --- | --- |
| Center core | Rotating reactor with live CPU / RAM / GPU / NET gauges; pulses while Jarvis speaks |
| Drive array | One card per mounted partition: fill, free space, disk I/O |
| Active modules | Top processes by memory, with per-process CPU |
| Weather uplink | Open-Meteo current conditions, cached 15 minutes |
| Header | Clock plus the live task list — add and tick tasks here |
| Command console | Bottom dock: **microphone** or keyboard; anything Jarvis understands works |
| Quick dock | Theme cycle (4 themes), scanlines, diagnostics, sleep mode |

### Voice

The console has an always-on microphone (Web Speech API). Say a command, and it
is transcribed, debounced into a single utterance, and sent through the same
`/api/command` pipeline as typed text. Replies are spoken back at rate 0.92 /
pitch 0.55 with an `en-GB` male voice, matching the `dark_synthetic` Python
persona. The mic mutes itself while Jarvis talks so he never hears his own reply.

Wake words come from `voice.wake_words` in `config/config.json`, so ambient
speech is ignored and you can say `hey jarvis, system status`.

Dictation needs Chrome, Edge or Safari, and needs HTTPS or `localhost` — over
plain `http://<lan-ip>` the browser blocks the microphone. The speaker icon mutes
replies; the mic icon toggles dictation. Details in [`ui/README.md`](../ui/README.md).

**Under the hood:** `dashboard/server.py` uses only the Python standard library
(`http.server`). `GET /api/state` returns the full snapshot (polled every 2 s),
`POST /api/command` runs any command through the same Jarvis pipeline, and
`ui/dist/` is served as static files. Server-side TTS is off by design: the
browser speaks, so audio lands on the machine running the browser.

Full details in [`ui/README.md`](../ui/README.md).

### Nothing on screen is invented

A probe that cannot report a value returns `null` and its panel reads `NO SIGNAL`
or `--` rather than showing a made-up number. That currently applies to:

- **Drive temperature** — needs S.M.A.R.T. (`smartctl`/WMI); `psutil` cannot read it.
- **GPU** — needs `pynvml` (`pip install nvidia-ml-py`); `psutil` has no GPU support.
- **Weather** — until the first Open-Meteo lookup resolves, or with no network.

Pin the weather location with `weather.city` in `config/config.json` (or
`JARVIS_WEATHER_CITY` in `.env`); leave it empty to geolocate by public IP.

Until the backend answers its first poll the HUD shows three placeholder drives
so it is never blank. Once Jarvis responds, every panel is live.


## Desktop HUD: Solar Core

A "solar core": a glowing energy sphere at the center of the screen, wrapped in dense
orbiting particle rings and long radial scan beams. Everything else in the UI is kept
dark and minimal so the core reads as the engine of the assistant.

## Layout

| Region | What it contains |
| --- | --- |
| Top bar | `J.A.R.V.I.S V2` title, navigation (`HOME / AI / DASHBOARD`), live status (`AI GROQ · VOICE READY · CORE ACTIVE`) |
| HOME view | The animated solar core (particle orbits, radial beams, pulsing glow) plus a live telemetry line: `CPU MEM DSK PWR` |
| AI view | Chat transcript with the assistant (user messages soft gold, JARVIS messages orange, system notes muted) |
| DASHBOARD view | Telemetry bars with color thresholds, quick-action buttons, and the Roblox safe-mode panel |
| Bottom console | Slim command bar with placeholder `Type command or press Speak...` and buttons `SEND / SPEAK / ROBLOX / GRIND` |

## Behavior notes

- Every command runs on a background thread, so the UI never freezes while Jarvis
  thinks, speaks, or waits for speech recognition.
- `GRIND` is context-aware: it starts a 30-minute Roblox grind session when none is
  running, and shows session stats when one is active.
- `ROBLOX` jumps straight to Roblox stats.
- The Roblox panel always shows the live session state, lifetime minutes, and goals.
- Telemetry refreshes every 2 seconds via `psutil` (falls back to `N/A` if psutil is
  not installed).
- Window transparency and all colors are configurable under the `ui` section of
  `config/config.json`.

## Voice personas

The UI pairs with the persona system in `voice/voice_profiles.py`. The active profile
is `voice.voice_profile` in config:

| Profile | Character |
| --- | --- |
| `dark_synthetic` (default) | Slow, low, heavy, commanding — an original dark synthetic persona |
| `jarvis_classic` | Calm, polite butler-style assistant |
| `fast_operator` | Brisk mission-control pace |
| `gentle` | Softer, quieter late-night voice |

Switch at runtime with the `apply_profile()` helper, or edit config. Note: profiles
tune rate, volume, pitch, and preferred system voices — the exact sound ultimately
depends on the TTS voices installed on your operating system. The `dark_synthetic`
profile is an original persona, not a clone of any film character.
