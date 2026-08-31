# Architecture

`core.jarvis.Jarvis` is the orchestrator. It receives text from GUI, voice, or CLI, removes wake words, checks routines/chains, routes the command to modules, records memory, and speaks the response when enabled.

Modules expose a simple interface:

```python
def process(command: str) -> dict:
    return {"success": True, "response": "Done, sir."}
```

Major packages:

- `core`: configuration and orchestrator
- `modules`: desktop, productivity, and external integrations
- `voice`: speech-to-text and text-to-speech
- `personality`: Groq AI and offline fallback personality
- `gui`: Tkinter arc-reactor desktop UI
- `dashboard`: CyberHUD HTTP server + telemetry probes
- `ui`: React/TypeScript browser interface (merged from JarvisV1)
- `utils`: helpers, env loading, logging

## CyberHUD data flow

```
ui/src/App.tsx  ──useJarvis()──►  GET /api/state   ──►  DashboardState.snapshot()
      │                                                          │
      │                                     core.jarvis.Jarvis ◄─┤
      │                                     dashboard.telemetry  ◄─┘
      │                                     (drives, processes, net, gpu, weather)
      └──CommandConsole──►  POST /api/command  ──►  Jarvis.process_command()
```

`dashboard/telemetry.py` keeps every probe independent: one that fails returns
`None` and its panel renders a `NO SIGNAL` state instead of breaking the page.
Weather resolves on a background thread so a slow or blocked public API can never
stall a `/api/state` response.

`ui/src/lib/api.ts` is the only place that translates between the snake_case JSON
API and the camelCase the React components use.
