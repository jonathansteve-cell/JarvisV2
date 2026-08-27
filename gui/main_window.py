"""Arc-reactor inspired Tkinter UI for Jarvis V2."""

from __future__ import annotations

import math
import threading
import time
import tkinter as tk
from tkinter import scrolledtext, ttk
from typing import Any

from core.jarvis import Jarvis
from voice.speech_recognition_engine import SpeechRecognitionEngine

try:
    import psutil  # type: ignore
except Exception:  # pragma: no cover
    psutil = None  # type: ignore


class JarvisMainWindow:
    """Desktop GUI with chat, quick actions, and system telemetry."""

    def __init__(self) -> None:
        self.jarvis = Jarvis()
        self.recognizer = SpeechRecognitionEngine(self.jarvis.config)
        self.root = tk.Tk()
        self.root.title("J.A.R.V.I.S V2")
        self.root.geometry("1120x720")
        self.root.minsize(980, 640)
        self.root.configure(bg="#050A12")
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        try:
            self.root.attributes("-alpha", float(self.jarvis.config.get("ui.transparency", 0.96)))
        except Exception:
            pass
        self._listening = False
        self._build_style()
        self._build_layout()
        self._animate_arc()
        self._update_stats()
        self.add_message("JARVIS", self.jarvis.boot_message())

    def _build_style(self) -> None:
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Jarvis.TButton", background="#0B2134", foreground="#EAFBFF", borderwidth=1)
        style.map("Jarvis.TButton", background=[("active", "#123D5A")])

    def _build_layout(self) -> None:
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        left = tk.Frame(self.root, bg="#06101C", width=310)
        left.grid(row=0, column=0, sticky="ns")
        left.grid_propagate(False)

        title = tk.Label(left, text="J.A.R.V.I.S", fg="#00D4FF", bg="#06101C", font=("Segoe UI", 25, "bold"))
        title.pack(pady=(24, 4))
        subtitle = tk.Label(left, text="V2 DESKTOP INTELLIGENCE", fg="#78A6B8", bg="#06101C", font=("Segoe UI", 9))
        subtitle.pack(pady=(0, 18))

        self.arc = tk.Canvas(left, width=230, height=230, bg="#06101C", highlightthickness=0)
        self.arc.pack(pady=8)

        self.stats = tk.Label(left, text="Initializing telemetry...", fg="#EAFBFF", bg="#06101C", justify="left", font=("Consolas", 10))
        self.stats.pack(padx=22, pady=18, anchor="w")

        actions = [
            ("System Status", "system status"),
            ("Screenshot", "take screenshot"),
            ("Open Chrome", "open chrome"),
            ("Calendar", "show calendar"),
            ("Memory", "what do you remember"),
            ("Voice Listen", "__listen__"),
        ]
        for text, command in actions:
            ttk.Button(
                left,
                text=text,
                style="Jarvis.TButton",
                command=lambda cmd=command: self.quick_action(cmd),
            ).pack(fill="x", padx=22, pady=5)

        main = tk.Frame(self.root, bg="#050A12")
        main.grid(row=0, column=1, sticky="nsew", padx=18, pady=18)
        main.grid_columnconfigure(0, weight=1)
        main.grid_rowconfigure(0, weight=1)

        self.chat = scrolledtext.ScrolledText(
            main,
            bg="#071421",
            fg="#EAFBFF",
            insertbackground="#00D4FF",
            relief="flat",
            wrap="word",
            font=("Segoe UI", 11),
        )
        self.chat.grid(row=0, column=0, sticky="nsew")
        self.chat.tag_config("user", foreground="#FFD166")
        self.chat.tag_config("jarvis", foreground="#00D4FF")
        self.chat.tag_config("system", foreground="#78A6B8")

        input_row = tk.Frame(main, bg="#050A12")
        input_row.grid(row=1, column=0, sticky="ew", pady=(12, 0))
        input_row.grid_columnconfigure(0, weight=1)
        self.entry = tk.Entry(
            input_row,
            bg="#0B2134",
            fg="#EAFBFF",
            insertbackground="#00D4FF",
            relief="flat",
            font=("Segoe UI", 12),
        )
        self.entry.grid(row=0, column=0, sticky="ew", ipady=10)
        self.entry.bind("<Return>", lambda _: self.submit())
        ttk.Button(input_row, text="Send", style="Jarvis.TButton", command=self.submit).grid(row=0, column=1, padx=(10, 0), ipady=7)
        ttk.Button(input_row, text="Speak", style="Jarvis.TButton", command=self.listen_once).grid(row=0, column=2, padx=(10, 0), ipady=7)

    def _animate_arc(self, phase: float = 0) -> None:
        self.arc.delete("all")
        center = 115
        radii = [88, 68, 44]
        for i, radius in enumerate(radii):
            color = ["#00D4FF", "#2EE6A6", "#FFFFFF"][i]
            start = (phase * (2 + i) * 40) % 360
            extent = 240 - i * 45
            self.arc.create_arc(
                center - radius,
                center - radius,
                center + radius,
                center + radius,
                start=start,
                extent=extent,
                style="arc",
                outline=color,
                width=3,
            )
        pulse = 18 + 6 * math.sin(phase)
        self.arc.create_oval(center - pulse, center - pulse, center + pulse, center + pulse, fill="#00D4FF", outline="")
        self.arc.create_text(center, center + 112, text="ONLINE", fill="#2EE6A6", font=("Consolas", 11, "bold"))
        self.root.after(70, lambda: self._animate_arc(phase + 0.1))

    def _update_stats(self) -> None:
        if psutil:
            cpu = psutil.cpu_percent(interval=None)
            mem = psutil.virtual_memory().percent
            disk = psutil.disk_usage("/").percent
            text = f"CPU       {cpu:5.1f}%\nMEMORY    {mem:5.1f}%\nDISK      {disk:5.1f}%\nVOICE     {'READY' if self.recognizer.available else 'OFFLINE'}"
        else:
            text = "Telemetry requires psutil\nVOICE     " + ("READY" if self.recognizer.available else "OFFLINE")
        self.stats.configure(text=text)
        self.root.after(2000, self._update_stats)

    def add_message(self, sender: str, message: str) -> None:
        tag = "jarvis" if sender.upper().startswith("J") else "user"
        self.chat.insert("end", f"{sender}: ", tag)
        self.chat.insert("end", f"{message}\n\n")
        self.chat.see("end")

    def submit(self) -> None:
        command = self.entry.get().strip()
        if not command:
            return
        self.entry.delete(0, "end")
        self.add_message("YOU", command)
        result = self.jarvis.process_command(command, speak=True)
        self.add_message("JARVIS", result.text)

    def quick_action(self, command: str) -> None:
        if command == "__listen__":
            self.listen_once()
            return
        self.add_message("YOU", command)
        result = self.jarvis.process_command(command, speak=True)
        self.add_message("JARVIS", result.text)

    def listen_once(self) -> None:
        if self._listening:
            return
        self._listening = True
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
        result = self.jarvis.process_command(text, speak=True)
        self.add_message("JARVIS", result.text)

    def run(self) -> None:
        self.root.mainloop()

    def close(self) -> None:
        self.jarvis.shutdown()
        self.root.destroy()
