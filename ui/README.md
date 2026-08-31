# CyberHUD — Jarvis V2 web interface

The browser interface for J.A.R.V.I.S V2. React 19 + Vite 6 + Tailwind v4 +
TypeScript, originally generated in Google AI Studio as the *CyberHUD Telemetry
Interface* and merged into this repo from
[`jonathansteve-cell/JarvisV1`](https://github.com/jonathansteve-cell/JarvisV1)
with its history preserved.

It is a **pure frontend**. All data comes from the Python backend in
`dashboard/server.py` over a small JSON API — there is no Node server, no
database, and no AI SDK in here.

---

## Run it

### Normal use (one server, production build)

```bash
cd ui
npm install
npm run build
cd ..
python main.py --web          # http://localhost:8765
```

`dashboard/server.py` serves `ui/dist/` directly. No proxy, no second process.

### Development (live reload)

```bash
python main.py --web          # terminal 1 — the API on :8765
cd ui && npm run dev          # terminal 2 — the UI on :3000
```

Vite proxies `/api/*` to `http://127.0.0.1:8765`. Point it elsewhere with
`JARVIS_API_URL=http://192.168.1.20:8765 npm run dev`.

---

## The API contract

Defined in TypeScript in [`src/lib/api.ts`](src/lib/api.ts). The Python side is
snake_case; that module is the only place that translates to the camelCase the
components use.

| Endpoint | Method | Purpose |
| --- | --- | --- |
| `/api/state` | GET | Full telemetry snapshot. Polled every 2 s by `useJarvis()`. |
| `/api/command` | POST | `{"command": "..."}` → runs the Jarvis pipeline. |
| `/api/health` | GET | Liveness + whether `ui/dist` exists. |

`/api/state` blocks the HUD consumes:

```
system        cpu, mem, disk, battery
drives[]      per-partition: letter, label, total/used/free, cache I/O
processes[]   pid, name, status, cpu, memory
net           throughput since the previous poll
gpu           NVIDIA only, via pynvml — otherwise null
weather       Open-Meteo, cached 15 min — otherwise null
productivity  tasks (with stable ids) + notes
memory        facts and stats
roblox        grind session state
conversations recent command/response pairs
```

Everything degrades independently. A probe that fails returns `null` and its
panel renders `NO SIGNAL` — a missing GPU driver or a blocked weather API never
blanks the whole dashboard.

---

## Honest telemetry policy

Nothing on screen is invented while the backend is reachable:

- **Drive temperature** — always `null`. Reading it needs S.M.A.R.T.
  (`smartctl`/WMI), which `psutil` does not expose. The card shows `--`.
- **GPU** — `null` unless `pynvml` is installed. The ring still animates, but
  the readout shows `--` rather than a made-up percentage.
- **Weather** — `null` until the first Open-Meteo lookup resolves, and whenever
  the network is unavailable. The panel shows `NO SIGNAL`.
- **Drive card spectrum bars** — decorative, but *derived* from the real fill
  percentage rather than shipped as constants.

The one exception is **demo mode**: until the backend answers its first poll,
three placeholder drives and an "AWAITING UPLINK" process row are shown so the
HUD is never blank. See `DEMO_DRIVES` in `src/App.tsx`. Once Jarvis responds,
none of it is used.

---

## What talks to the backend

| UI element | Command sent |
| --- | --- |
| Command console (bottom dock) | whatever you type, verbatim |
| Add task | `add task <text>` |
| Tick a task | `complete task <text>` |
| Untick a task | `reopen task <text>` |

Anything Jarvis understands works in the console — `system status`,
`open chrome then volume 40`, `start a 30 minute roblox grind session`.

The process list is deliberately **read-only**. Killing a process because
someone mis-clicked a HUD row is not a trade worth making.

---

## Layout

```
src/
  App.tsx                     state, polling, live/demo switching
  lib/api.ts                  fetch + snake_case → camelCase mapping + useJarvis()
  components/
    CenterCoreHUD.tsx         reactor core, CPU/RAM/GPU/NET rings, processes, weather
    DriveTelemetryCard.tsx    per-drive storage card
    CommandConsole.tsx        bottom-dock command input
    HeaderBar.tsx             clock + task list
    QuickDockControls.tsx     theme / scanlines / diagnostics / sleep
    RecycleBinWidget.tsx      decorative
    Modals.tsx                drive detail, diagnostics, weather, app launcher
    BackgroundGrid.tsx        starfield + hologram grid
  utils/theme.ts              four themes; solar-amber is the J.A.R.V.I.S V2 default
  utils/audio.ts              Web Audio API sound effects
```

## Still decorative

The **diagnostics modal** (`Modals.tsx`) and the **recycle bin widget** are
visual theatre with no backend behind them — the diagnostics lines are hardcoded
strings including a fixed `C:\ - H:\` partition count. Wire them up or treat
them as set dressing.

## Removed during the merge

- `metadata.json` — AI Studio app manifest. Declared
  `MAJOR_CAPABILITY_SERVER_SIDE_GEMINI_API`, but no `server.js` ever existed in
  the repo and the `@google/genai` dependency was never imported.
- `.env.example` with `GEMINI_API_KEY` — Jarvis V2 uses Groq, configured in the
  **repo root** `.env`, not here.
