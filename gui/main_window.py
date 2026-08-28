"""Hero Core HUD interface for Jarvis V2.

A cinematic black + cyan holographic desktop UI:

- animated hero core with dense orbiting particle rings and radial scan beams
- top navigation: HOME / AI / DASHBOARD
- slim bottom command console with SEND / SPEAK / ROBLOX / GRIND
- live telemetry (CPU, MEM, DSK, VOICE, AI, CORE) around the core and dashboard
- Roblox safe-mode panel for grind sessions, goals, and progress
"""

from __future__ import annotations

import math
import os
import random
import threading
import tkinter as tk
from tkinter import scrolledtext, ttk
from typing import Any

from core.jarvis import Jarvis
from voice.speech_recognition_engine import SpeechRecognitionEngine

try:
    import psutil  # type: ignore
except Exception:  # pragma: no cover
    psutil = None  # type: ignore

# ---------------------------------------------------------------- palette
BG = "#050505"
PANEL = "#0C0C0C"
PANEL_LINE = "#241407"
ORANGE = "#FF8C1A"
ORANGE_BRIGHT = "#FFB25E"
ORANGE_SOFT = "#FFC773"
ORANGE_DEEP = "#B4530A"
ORANGE_DIM = "#5A2E06"
TEXT = "#F5EDE0"
MUTED = "#9A8F7F"
GREEN = "#38E07C"
RED = "#E05555"

PLACEHOLDER = "Type command or press Speak..."


class SolarCoreCanvas(tk.Canvas):
    """Hero core view: photoreal sun image with twinkling sparkle stars."""

    def __init__(self, master: Any, width: int = 560, height: int = 400, **kwargs: Any) -> None:
        super().__init__(master, width=width, height=height, bg=BG, highlightthickness=0, **kwargs)
        self.size = width
        self._phase = 0.0
        self._running = True
        self._orb_photo = None
        self._telemetry: list[tuple[str, str]] = []
        self._stars = [
            {
                "x": random.uniform(8, width - 8),
                "y": random.uniform(8, height - 30),
                "size": random.uniform(1.2, 3.0),
                "phase": random.uniform(0, math.tau),
                "speed": random.uniform(0.4, 1.3),
            }
            for _ in range(46)
        ]
        self._load_orb()
        self._animate()

    def _load_orb(self) -> None:
        """Load the photoreal orb asset when available."""
        from pathlib import Path

        for candidate in (
            Path(__file__).resolve().parent.parent / "docs" / "images" / "hero_orb.png",
            Path("docs/images/hero_orb.png"),
        ):
            if candidate.exists():
                try:
                    photo = tk.PhotoImage(file=str(candidate))
                    while photo.width() > self.size - 12 or photo.height() > self.height - 12:
                        photo = photo.subsample(2, 2)
                    self._orb_photo = photo
                    return
                except Exception:
                    return

    # ------------------------------------------------------------- telemetry
    def set_telemetry(self, lines: list[tuple[str, str]]) -> None:
        """Store label/value pairs rendered beside the core (label, value)."""
        self._telemetry = lines

    def stop(self) -> None:
        self._running = False

    # ------------------------------------------------------------ draw frame
    def _animate(self) -> None:
        if not self._running:
            return
        self.delete("all")
        c = self.size / 2
        mid_y = self.height / 2 - 8

        # Photoreal orb image.
        if self._orb_photo is not None:
            self.create_image(c, mid_y, image=self._orb_photo)

        # Twinkling four-point sparkle stars.
        for star in self._stars:
            twinkle = 0.25 + 0.75 * abs(math.sin(self._phase * star["speed"] + star["phase"]))
            length = star["size"] * 2.6 * twinkle
            color = "#FFE9C9" if twinkle > 0.72 else ORANGE_BRIGHT if twinkle > 0.4 else ORANGE_DEEP
            x, y = star["x"], star["y"]
            self.create_line(x - length, y, x + length, y, fill=color, width=1)
            self.create_line(x, y - length, x, y + length, fill=color, width=1)

        self.create_text(c, self.size - 14, text="CORE ACTIVE", fill="#38E07C", font=("Consolas", 11, "bold"))

        self._phase += 0.05
        self.after(80, self._animate)


class JarvisMainWindow:
    """J.A.R.V.I.S V2 Hero Core HUD."""

    def __init__(self) -> None:
        self.jarvis = Jarvis()
        self.recognizer = SpeechRecognitionEngine(self.jarvis.config)
        self.root = tk.Tk()
        self.root.title("J.A.R.V.I.S V2 — Hero Core")
        self.root.geometry("1180x760")
        self.root.minsize(1000, 660)
        self.root.configure(bg=BG)
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        try:
            self.root.attributes("-alpha", float(self.jarvis.config.get("ui.transparency", 0.98)))
        except Exception:
            pass

        self._listening = False
        self._busy = False
        self._entry_placeholder = False

        self._build_topbar()
        self._build_views()
        self._build_console()
        self._show_view("home")
        self._update_telemetry()

        self.add_message("JARVIS", self.jarvis.boot_message())

    # ---------------------------------------------------------------- topbar
    def _build_topbar(self) -> None:
        bar = tk.Frame(self.root, bg=PANEL, height=44)
        bar.pack(fill="x", side="top")
        bar.pack_propagate(False)

        title = tk.Label(
            bar, text="J.A.R.V.I.S V2", fg=ORANGE, bg=PANEL,
            font=("Segoe UI", 13, "bold"),
        )
        title.pack(side="left", padx=(18, 6))

        self._nav_buttons: dict[str, tk.Label] = {}
        nav_labels = {"home": "✦ Home", "ai": "🗨 Chat", "dashboard": "▦ Dashboard"}
        for name in ("home", "ai", "dashboard"):
            label = tk.Label(
                bar, text=nav_labels[name], fg=MUTED, bg=PANEL,
                font=("Segoe UI", 10), cursor="hand2", padx=12,
            )
            label.pack(side="left", pady=8)
            label.bind("<Button-1>", lambda _event, view=name: self._show_view(view))
            label.bind("<Enter>", lambda _event, widget=label: widget.configure(fg=ORANGE_SOFT))
            label.bind("<Leave>", lambda _event, view=name, widget=label: widget.configure(
                fg=ORANGE if view == self._active_view else MUTED
            ))
            self._nav_buttons[name] = label

        self._status_bar = tk.Label(
            bar, text=self._status_summary(), fg=MUTED, bg=PANEL,
            font=("Consolas", 10), anchor="e",
        )
        self._status_bar.pack(side="right", padx=18)

    def _status_summary(self) -> str:
        groq = "AI GROQ" if self._groq_ready() else "AI OFFLINE"
        voice = "VOICE READY" if self.recognizer.available else "VOICE N/A"
        return f"{groq}  ·  {voice}  ·  CORE ACTIVE"

    def _groq_ready(self) -> bool:
        key = os.getenv("GROQ_API_KEY", "")
        return bool(key) and not key.lower().startswith("your_")

    # ----------------------------------------------------------------- views
    def _build_views(self) -> None:
        self.container = tk.Frame(self.root, bg=BG)
        self.container.pack(fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)
        self._active_view = "home"

        # HOME — photoreal hero core.
        self.view_home = tk.Frame(self.container, bg=BG)
        self.view_home.grid(row=0, column=0, sticky="nsew")
        self.solar = SolarCoreCanvas(self.view_home, width=580, height=430)
        self.solar.pack(expand=True, pady=(18, 4))
        self._telemetry = {"cpu": "--", "mem": "--", "dsk": "--"}
        self._telemetry_label = tk.Label(
            self.view_home, text="", fg=ORANGE_SOFT, bg=BG, font=("Consolas", 11),
        )
        self._telemetry_label.pack(pady=(0, 10))

        # AI — chat transcript.
        self.view_ai = tk.Frame(self.container, bg=BG)
        self.view_ai.grid(row=0, column=0, sticky="nsew")
        self.view_ai.grid_rowconfigure(1, weight=1)
        self.view_ai.grid_columnconfigure(0, weight=1)
        ai_header = tk.Label(
            self.view_ai,
            text=(
                f"AI · GROQ · {self.jarvis.config.get('ai.model', 'llama-3.3-70b-versatile')}"
                if self._groq_ready()
                else "AI OFFLINE · set GROQ_API_KEY in your local .env for full intelligence"
            ),
            fg=GREEN if self._groq_ready() else RED, bg=BG, font=("Consolas", 10),
        )
        ai_header.grid(row=0, column=0, sticky="w", padx=22, pady=(14, 6))

        self.chat = scrolledtext.ScrolledText(
            self.view_ai, bg=PANEL, fg=TEXT, insertbackground=ORANGE,
            relief="flat", wrap="word", font=("Segoe UI", 11),
        )
        self.chat.grid(row=1, column=0, sticky="nsew", padx=22, pady=(0, 14))
        self.chat.tag_config("user", foreground=ORANGE_SOFT)
        self.chat.tag_config("jarvis", foreground=ORANGE)
        self.chat.tag_config("system", foreground=MUTED)
        self.chat.configure(state="disabled")

        # DASHBOARD — telemetry, Roblox safe-mode, quick actions.
        self.view_dashboard = tk.Frame(self.container, bg=BG)
        self.view_dashboard.grid(row=0, column=0, sticky="nsew")

        left = tk.Frame(self.view_dashboard, bg=BG)
        left.pack(side="left", fill="both", expand=True, padx=(24, 10), pady=20)
        tk.Label(left, text="SYSTEM TELEMETRY", fg=ORANGE, bg=BG, font=("Consolas", 11, "bold")).pack(anchor="w")
        self.bars_canvas = tk.Canvas(left, width=430, height=150, bg=BG, highlightthickness=0)
        self.bars_canvas.pack(anchor="w", pady=10)
        tk.Label(left, text="QUICK ACTIONS", fg=ORANGE, bg=BG, font=("Consolas", 11, "bold")).pack(anchor="w", pady=(12, 6))
        actions = tk.Frame(left, bg=BG)
        actions.pack(anchor="w")
        for column, (text, command) in enumerate([
            ("System Status", "system status"),
            ("Screenshot", "take screenshot"),
            ("Open Chrome", "open chrome"),
            ("Calendar", "show calendar"),
            ("Memory", "what do you remember"),
            ("Tell a joke", "tell me a joke"),
        ]):
            ttk.Button(
                actions, text=text, style="Solar.TButton", width=16,
                command=lambda cmd=command: self.submit_text(cmd),
            ).grid(row=column // 2, column=column % 2, padx=4, pady=4, sticky="w")

        style = ttk.Style()
        try:
            style.theme_use("clam")
        except Exception:
            pass
        style.configure("Solar.TButton", background="#1A0F04", foreground=TEXT, borderwidth=1)
        style.map("Solar.TButton", background=[("active", "#2A1806")])

        right = tk.Frame(self.view_dashboard, bg=PANEL, highlightbackground=PANEL_LINE, highlightthickness=1)
        right.pack(side="right", fill="both", expand=True, padx=(10, 24), pady=20)
        tk.Label(right, text="ROBLOX · SAFE MODE", fg=ORANGE, bg=PANEL, font=("Consolas", 11, "bold")).pack(anchor="w", padx=18, pady=(16, 2))
        tk.Label(
            right,
            text=("Official links, grind sessions, goals and progress only.\n"
                  "No exploits, bots, or Robux generators. Ever."),
            fg=MUTED, bg=PANEL, font=("Segoe UI", 9), justify="left",
        ).pack(anchor="w", padx=18)

        self.roblox_status = tk.Label(right, text="", fg=TEXT, bg=PANEL, font=("Consolas", 10), justify="left", anchor="w")
        self.roblox_status.pack(fill="x", padx=18, pady=10)

        roblox_actions = tk.Frame(right, bg=PANEL)
        roblox_actions.pack(anchor="w", padx=18)
        for column, (text, command) in enumerate([
            ("Roblox stats", "roblox stats"),
            ("Start grind", "start 30 minute roblox grind session for daily quests"),
            ("Show goals", "show roblox goals"),
            ("Open Roblox", "open roblox"),
        ]):
            ttk.Button(
                roblox_actions, text=text, style="Solar.TButton", width=14,
                command=lambda cmd=command: self.submit_text(cmd),
            ).grid(row=column // 2, column=column % 2, padx=4, pady=4, sticky="w")

    def _show_view(self, view: str) -> None:
        self._active_view = view
        frames = {"home": self.view_home, "ai": self.view_ai, "dashboard": self.view_dashboard}
        frames[view].tkraise()
        for name, label in self._nav_buttons.items():
            label.configure(fg=ORANGE if name == view else MUTED)
        if view == "dashboard":
            self._refresh_roblox_panel()

    # --------------------------------------------------------------- console
    def _build_console(self) -> None:
        console = tk.Frame(self.root, bg=PANEL, highlightbackground=PANEL_LINE, highlightthickness=1)
        console.pack(fill="x", side="bottom")

        inner = tk.Frame(console, bg=PANEL)
        inner.pack(fill="x", padx=14, pady=10)
        inner.grid_columnconfigure(0, weight=1)

        self.entry = tk.Entry(
            inner, bg="#120A03", fg=TEXT, insertbackground=ORANGE,
            relief="flat", font=("Segoe UI", 12),
        )
        self.entry.grid(row=0, column=0, sticky="ew", ipady=9, padx=(4, 10))
        self.entry.bind("<Return>", lambda _event: self.submit())
        self.entry.bind("<FocusIn>", self._clear_placeholder)
        self.entry.bind("<FocusOut>", self._set_placeholder)
        self._set_placeholder()

        for column, (text, handler) in enumerate([
            ("SEND", self.submit),
            ("SPEAK", self.listen_once),
            ("ROBLOX", lambda: self.submit_text("roblox stats")),
            ("GRIND", self.grind_action),
        ]):
            width = 8 if text in ("SEND", "SPEAK") else 9
            tk.Button(
                inner, text=text, command=handler, width=width,
                bg="#1A0F04", fg=ORANGE_BRIGHT, activebackground="#2A1806",
                activeforeground=TEXT, relief="flat", font=("Segoe UI", 10, "bold"),
                cursor="hand2",
            ).grid(row=0, column=column + 1, padx=4, ipady=7)

    def _set_placeholder(self, _event: Any = None) -> None:
        if not self.entry.get():
            self.entry.insert(0, PLACEHOLDER)
            self.entry.configure(fg=MUTED)
            self._entry_placeholder = True

    def _clear_placeholder(self, _event: Any = None) -> None:
        if self._entry_placeholder:
            self.entry.delete(0, "end")
            self.entry.configure(fg=TEXT)
            self._entry_placeholder = False

    # ------------------------------------------------------------------ chat
    def add_message(self, sender: str, message: str) -> None:
        self.chat.configure(state="normal")
        if sender.upper().startswith("J"):
            tag = "jarvis"
        elif sender.upper().startswith("S"):
            tag = "system"
        else:
            tag = "user"
        self.chat.insert("end", f"{sender}: ", tag)
        self.chat.insert("end", f"{message}\n\n")
        self.chat.see("end")
        self.chat.configure(state="disabled")

    # ------------------------------------------------------------- processing
    def submit(self) -> None:
        self._clear_placeholder()
        command = self.entry.get().strip()
        if not command or self._busy:
            return
        self.entry.delete(0, "end")
        self.submit_text(command)

    def submit_text(self, command: str) -> None:
        if self._busy:
            self.add_message("SYSTEM", "Still working on the previous request, sir.")
            return
        self._show_view("ai")
        self.add_message("YOU", command)
        self._busy = True

        def worker() -> None:
            result = self.jarvis.process_command(command, speak=True)
            self.root.after(0, lambda: self._finish_command(result))

        threading.Thread(target=worker, daemon=True).start()

    def _finish_command(self, result: Any) -> None:
        self._busy = False
        self.add_message("JARVIS", result.text)
        if getattr(result, "intent", "") == "roblox":
            self._refresh_roblox_panel()

    def grind_action(self) -> None:
        if self.jarvis.roblox.session:
            self.submit_text("roblox stats")
        else:
            self.submit_text("start 30 minute roblox grind session for daily quests")

    # ------------------------------------------------------------------ voice
    def listen_once(self) -> None:
        if self._listening or self._busy:
            return
        self._listening = True
        self._show_view("ai")
        self.add_message("SYSTEM", "Listening...")

        def worker() -> None:
            text = self.recognizer.listen_once()
            self.root.after(0, lambda: self._finish_listen(text))

        threading.Thread(target=worker, daemon=True).start()

    def _finish_listen(self, text: str | None) -> None:
        self._listening = False
        if not text:
            self.add_message("SYSTEM", "I did not hear anything.")
            return
        self.add_message("YOU", text)
        self.submit_text(text)

    # -------------------------------------------------------------- telemetry
    def _read_stats(self) -> dict[str, Any]:
        if psutil:
            battery = psutil.sensors_battery() if hasattr(psutil, "sensors_battery") else None
            return {
                "cpu": psutil.cpu_percent(interval=None),
                "mem": psutil.virtual_memory().percent,
                "dsk": psutil.disk_usage("/").percent,
                "battery": battery.percent if battery else None,
            }
        return {"cpu": None, "mem": None, "dsk": None, "battery": None}

    def _update_telemetry(self) -> None:
        stats = self._read_stats()
        cpu = f"{stats['cpu']:.0f}%" if stats["cpu"] is not None else "N/A"
        mem = f"{stats['mem']:.0f}%" if stats["mem"] is not None else "N/A"
        dsk = f"{stats['dsk']:.0f}%" if stats["dsk"] is not None else "N/A"
        battery = f"{stats['battery']:.0f}%" if stats["battery"] is not None else "AC"

        self._telemetry_label.configure(
            text=f"CPU {cpu}    MEM {mem}    DSK {dsk}    PWR {battery}"
        )
        self.solar.set_telemetry([("CPU", cpu), ("MEM", mem), ("DSK", dsk)])
        self._status_bar.configure(text=self._status_summary())
        self._draw_bars(stats)
        self.root.after(2000, self._update_telemetry)

    def _draw_bars(self, stats: dict[str, Any]) -> None:
        canvas = self.bars_canvas
        canvas.delete("all")
        width = 430
        for row, (label, value) in enumerate(
            [("CPU", stats["cpu"]), ("MEMORY", stats["mem"]), ("DISK", stats["dsk"])]
        ):
            y = 18 + row * 46
            canvas.create_text(0, y, text=label, anchor="w", fill=TEXT, font=("Consolas", 10))
            canvas.create_rectangle(90, y - 8, width, y + 8, outline=PANEL_LINE, fill="#120A03")
            if value is not None:
                fill_width = 90 + (width - 90) * (value / 100.0)
                color = GREEN if value < 60 else ORANGE if value < 85 else RED
                canvas.create_rectangle(90, y - 8, fill_width, y + 8, outline="", fill=color)
                canvas.create_text(width, y, text=f"{value:.0f}%", anchor="e", fill=TEXT, font=("Consolas", 9))
            else:
                canvas.create_text(width, y, text="psutil required", anchor="e", fill=MUTED, font=("Consolas", 9))

    def _refresh_roblox_panel(self) -> None:
        roblox = self.jarvis.roblox
        if roblox.session:
            started = roblox.session["started_at"]
            focus = roblox.session.get("focus", "") or "free grind"
            session_text = f"SESSION ACTIVE · started {started[11:16]} · focus: {focus}"
        else:
            total_minutes = sum(int(s.get("minutes", 0)) for s in roblox.data["sessions"])
            session_text = f"NO ACTIVE SESSION · {total_minutes} lifetime minutes logged"
        goals = roblox.data["goals"]
        if goals:
            done = sum(1 for goal in goals if goal["done"])
            goal_lines = "\n".join(
                f"{'[x]' if goal['done'] else '[ ]'} {goal['text']}" for goal in goals[:4]
            )
            goals_text = f"\nGOALS {done}/{len(goals)}\n{goal_lines}"
        else:
            goals_text = "\nGOALS · none set. Try: set roblox goal: reach level 50"
        self.roblox_status.configure(text=f"{session_text}{goals_text}")

    # ----------------------------------------------------------------- run
    def run(self) -> None:
        self.root.mainloop()

    def close(self) -> None:
        self.solar.stop()
        self.jarvis.shutdown()
        self.root.destroy()
