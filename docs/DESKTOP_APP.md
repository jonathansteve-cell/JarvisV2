# Turn Jarvis V2 into a Desktop App

Jarvis V2 is **already a desktop app in source form**: `gui/main_window.py` is a
native Tkinter window ("Hero Core HUD"). This guide covers the three levels of
"desktop app", from "just run it" to "installable .exe".

> ⚠️ `python main.py` with no arguments starts the **web dashboard** (`--web`).
> Use `python main.py --gui` for the desktop window. `Start_Jarvis_Desktop.bat`
> does that for you.

---

## Level 0 — Run it as a desktop app right now (2 minutes)

```bash
# Windows
Start_Jarvis_Desktop.bat

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py --gui
```

A black-and-orange HUD window opens with the solar-core orb. That *is* the
desktop app.

## Level 1 — A real double-clickable executable (Windows)

`packaging/` contains everything needed to freeze the app with **PyInstaller**:

```bat
  double-click:  packaging\build_exe.bat
```

The script will:

1. Create `.venv` and install `requirements.txt` + PyInstaller.
2. Build `packaging/app.ico` from `packaging/app.png` (multi-size icon).
3. Produce **`dist\JarvisV2\JarvisV2.exe`** — a windowed (no console) GUI app,
   with `config/`, `personality/`, the HUD's orb image, the web dashboard, and
   `.env.example` bundled next to it.
4. Create runtime folders (`data`, `logs`, `screenshots`, `documents`) next to
   the exe.

Run `JarvisV2.exe` — done. You can copy the whole `dist\JarvisV2` folder to
another PC and it will run there (no Python install needed). **First run on a
new machine:** copy `.env.example` to `.env` next to the exe and fill in the
keys you use.

> PyInstaller spec: `packaging/jarvis.spec`. The frozen app auto-chdirs to its
> own folder via `packaging/desktop_launcher.py`, so config and runtime data
> always live beside the exe — no "current directory" surprises.

## Level 2 — A proper installer with shortcuts (Windows)

1. Run `packaging\build_exe.bat` (Level 1).
2. Install **Inno Setup 6** from https://jrsoftware.org/isdl.php
3. Open **`packaging\installer.iss`** in Inno Setup → **Build → Compile**.
4. Output: **`dist\installer\JarvisV2-Setup.exe`** — installs to
   `Program Files\JarvisV2`, adds Start-menu (and optional desktop) shortcuts,
   and offers "Launch Jarvis V2 now".

## Level 3 — Make it start with your PC (optional)

- Inno Setup already adds a Start-menu shortcut; copy it into
  `shell:startup` (Win+R → `shell:startup`), or create a shortcut to
  `JarvisV2.exe` there for auto-launch at login.
- macOS/Linux: use your OS's login items.

---

## macOS & Linux

Run `packaging/build_app.sh` (uses Python 3, venv, PyInstaller). It produces a
run-able binary at `dist/JarvisV2/JarvisV2`.

- **Linux** first run: `import tkinter` failing? Install `python3-tk`
  (`sudo apt install python3-tk` on Debian/Ubuntu, `sudo dnf install
  python3-tkinter` on Fedora).
- **macOS** for a true `.app`: add a `BUNDLE` section to `jarvis.spec` (or use
  `py2app`), then codesign/notarize before distributing — otherwise Gatekeeper
  will warn.

---

## Where does the data live?

The frozen app stores everything **beside the executable**:

| Path (next to JarvisV2.exe) | Contents |
| --- | --- |
| `config/config.json` | settings (bundled, read-only unless you edit) |
| `.env` | **your secrets** — create from `.env.example`, never share it |
| `data/` | memory + productivity store (SQLite/JSON) |
| `logs/` | log files |
| `screenshots/` | screenshots Jarvis takes |
| `documents/` | Word documents it creates |

## Troubleshooting

| Symptom | Fix |
| --- | --- |
| SmartScreen "Unknown publisher" | Not code-signed; click **More info → Run anyway** (or buy a code-signing cert for broad distribution) |
| Antivirus flags the exe | Frozen Python exes are sometimes false-positives; upload to VirusTotal to verify |
| Mic/speech not working | Windows: `pip install pipwin && pipwin install pyaudio` **before** building; allow mic permission for the app |
| Need console logs to debug | In `packaging/jarvis.spec` set `console=False` → `console=True` and rebuild |
| `JarvisV2.exe` closes instantly | Run from a terminal to see the error, or rebuild with `console=True`; check `.env` exists beside the exe |
| Tkinter missing on Linux | See macOS & Linux section above |