# Merge Record — JarvisV1 (CyberHUD UI) into JarvisV2

**Status: merged on branch `arena/01a058b1-jarvisv2`.**

The CyberHUD React interface from
[`jonathansteve-cell/JarvisV1`](https://github.com/jonathansteve-cell/JarvisV1)
now lives in `ui/`, the old hand-rolled browser dashboard is deleted, and the UI
is wired to live telemetry. See [`ui/README.md`](../ui/README.md) for how to run it.

---

## How the merge was done

The two repos shared no common ancestor, so a plain `git merge` was refused:

```
$ git merge --no-commit --no-ff v1/main
fatal: refusing to merge unrelated histories
```

A root-level merge with `--allow-unrelated-histories` produced exactly 2 conflicts
(`.env.example`, `.gitignore`, both `add/add`). Instead, a **subtree merge** into
`ui/` was used, which produced **0 conflicts** and kept JarvisV1's history:

```
$ git merge -s ours --no-commit --allow-unrelated-histories v1/main
$ git read-tree --prefix=ui/ -u v1/main
$ git commit
```

JarvisV1's commits are now real ancestors of `HEAD`:

```
$ git merge-base --is-ancestor 4e5b13f3cbfd6a4b7ba8c2f2a15fdd0e747f9e44 HEAD && echo yes
yes
```

## What changed

### Removed

- `dashboard/static/index.html` (774 lines) and `dashboard/static/hero_orb.png` —
  the old Spark-style browser dashboard. `docs/images/hero_orb.png` is untouched
  and still used by the Tkinter HUD.
- `ui/metadata.json` — AI Studio manifest declaring
  `MAJOR_CAPABILITY_SERVER_SIDE_GEMINI_API`, but no `server.js` ever existed and
  `@google/genai` was never imported.
- `ui/.env.example` with `GEMINI_API_KEY` — Jarvis V2 uses Groq, configured in
  the repo root `.env`.
- The `speedMult迷` identifier in `CenterCoreHUD.tsx` (a stray CJK character).

### Added

| File | Purpose |
| --- | --- |
| `dashboard/telemetry.py` | Per-partition drives, process list, network rate, GPU (NVML), weather (Open-Meteo, 15-min cache) |
| `ui/src/lib/api.ts` | Typed API client, snake_case → camelCase mapping, `useJarvis()` polling hook |
| `ui/src/components/CommandConsole.tsx` | Bottom-dock command input — restores the chat the old dashboard had |
| `tests/test_telemetry.py` | 14 tests for the probes and the `/api/state` contract |
| `tests/test_task_lifecycle.py` | 7 tests for the new task commands |
| `tests/test_dashboard_http.py` | 11 tests over a real socket against every route |
| `ui/README.md`, `ui/LICENSE` | Frontend docs and MIT licence (V1 had none) |

### Changed

- `dashboard/server.py` — serves `ui/dist/` with correct content types and SPA
  fallback; `/api/state` gained `drives`, `processes`, `net`, `gpu`, `weather`;
  tasks gained stable ids.
- `ui/src/App.tsx` — driven by `useJarvis()`. The 6 hardcoded drive / task /
  process / weather constants are gone; 3 placeholder drives remain for demo mode
  only, before the backend's first answer.
- `ui/src/components/CenterCoreHUD.tsx` — live gauges (`--` when a reading is
  unavailable), nullable weather, drive badges show real free space.
- `ui/vite.config.ts` — dev proxy `/api` → `http://127.0.0.1:8765`.
- `packaging/jarvis.spec`, `packaging/jarvis_desktop.spec` — bundle `ui/dist`
  when it has been built.
- `config_manager.py` — new `weather.city` key.

---

## Bugs found and fixed while wiring it up

Both were pre-existing, and both were caught by tests written for this work.

### 1. `python main.py --web` did not exist

The docstring documented `--web`, `--gui`, `--voice-only` and `--modern-ui`, but
`main()`'s argparse only accepted `--command`, `--check` and `--verbose`:

```
main.py: error: unrecognized arguments: --web
```

`run_web()`, `run_gui()`, `run_modern_ui()` and `run_voice_only()` were all
unreachable. They are now wired to a mutually exclusive `--web / --gui /
--voice-only / --voice-ui / --modern-ui` group plus `--port`, and the documented
default (`--web`) is real.

### 2. The dashboard kept a stale second `ProductivityController`

`DashboardState.__init__` built its own controller instead of reusing
`jarvis.productivity`. They are separate objects with separate in-memory `data`,
so tasks added through `/api/command` never appeared in `/api/state`:

```
jarvis.productivity is state.productivity: False
```

`DashboardState` now uses `jarvis.productivity`. The HTTP round-trip test covers
it.

---

## Verification

```
$ pytest tests/
147 passed in 6.86s                  # was 115 before this work

$ cd ui && npm run lint              # tsc --noEmit → exit 0
$ cd ui && npm run build             # 2086 modules, 394.39 kB JS / 45.92 kB CSS

$ python main.py --web
$ curl -s localhost:8765/api/health
{"status":"online","name":"J.A.R.V.I.S V2","assistant_name":"Jarvis","ui_built":true}
$ curl -s -X POST localhost:8765/api/command -H 'Content-Type: application/json' \
    -d '{"command":"system status"}'
{"text":"CPU is at 4.8 percent, memory at 8.2 percent, and disk usage at 6.4 percent.",
 "success":true,"intent":"system","provider":"local"}
```

Task round trip over HTTP — add appears, complete removes it:

```
after add     : [{'id': 'task-0', 'text': 'verify the merge', 'done': False, 'time': '05:08 PM'}]
after complete: []
```

### Not verified here

The sandbox blocks outbound TLS to `api.open-meteo.com`, so **the weather path
has not been exercised against the live API**. Its failure path is covered
(`test_weather_returns_none_when_the_lookup_fails`) and the cache is covered
(`test_weather_is_cached`), but the first real fetch should be confirmed on a
machine with normal network access.

---

## Remaining work

- **GPU** — `null` until `pynvml` is installed (`pip install nvidia-ml-py`).
  The gauge shows `--` rather than a simulated number.
- **Drive temperature** — permanently `null`; needs S.M.A.R.T. via `smartctl` or WMI.
- **Diagnostics modal** (`ui/src/components/Modals.tsx`) — still hardcoded
  theatre, including a fixed `C:\ - H:\` partition count.
- **Recycle bin widget** — decorative; no backend endpoint.
- **Process list** — deliberately read-only. Terminating a process on a
  mis-clicked HUD row is not worth the risk.
