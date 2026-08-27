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
- `utils`: helpers, env loading, logging
