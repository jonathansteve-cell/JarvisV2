"""
Jarvis V2 - GUI Setup Wizard
==============================
Graphical setup wizard for first-run configuration.

Features:
- Welcome screen with branding
- User registration form
- API key configuration
- Voice settings
- Progress tracking
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Any, Optional

from core.user_manager import UserManager, get_user_manager
from core.api_manager import APIManager, APIProvider
from core.api_validator import APIValidator
from core.secure_env import SecureEnvManager

# Color scheme
BG = "#050505"
PANEL = "#0C0C0C"
ORANGE = "#FF8C1A"
ORANGE_BRIGHT = "#FFB25E"
TEXT = "#F5EDE0"
MUTED = "#9A8F7F"
GREEN = "#38E07C"
RED = "#E05555"
INPUT_BG = "#120A03"


class SetupWizardGUI:
    """
    GUI Setup Wizard for Jarvis V2.

    Guides users through:
    1. Welcome screen
    2. User registration
    3. API configuration
    4. Voice settings
    5. Completion
    """

    def __init__(self, on_complete: Optional[callable] = None):
        self.on_complete = on_complete

        self.user_manager = get_user_manager()
        self.env_manager = SecureEnvManager()
        self.api_manager = APIManager()
        self.validator = APIValidator()

        self.root = tk.Tk()
        self.root.title("Jarvis V2 - Setup Wizard")
        self.root.geometry("700x600")
        self.root.configure(bg=BG)
        self.root.resizable(False, False)

        # Center window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (700 // 2)
        y = (self.root.winfo_screenheight() // 2) - (600 // 2)
        self.root.geometry(f"+{x}+{y}")

        self.current_step = 0
        self.steps = [
            self._build_welcome_step,
            self._build_register_step,
            self._build_api_step,
            self._build_voice_step,
            self._build_complete_step,
        ]

        self._build_ui()
        self._show_step(0)

    def _build_ui(self):
        """Build the main UI structure."""
        # Header
        header = tk.Frame(self.root, bg=PANEL, height=80)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(
            header,
            text="J.A.R.V.I.S V2",
            fg=ORANGE,
            bg=PANEL,
            font=("Segoe UI", 24, "bold"),
        ).pack(expand=True)

        # Progress bar
        progress_frame = tk.Frame(self.root, bg=BG, height=30)
        progress_frame.pack(fill="x", padx=40, pady=(20, 0))

        self.progress_label = tk.Label(
            progress_frame,
            text="Step 1 of 5",
            fg=MUTED,
            bg=BG,
            font=("Segoe UI", 10),
        )
        self.progress_label.pack()

        self.progress_bar = ttk.Progressbar(
            progress_frame,
            length=600,
            mode="determinate",
            style="Solar.Horizontal.TProgressbar",
        )
        self.progress_bar.pack(pady=(5, 0))

        # Content area
        self.content_frame = tk.Frame(self.root, bg=BG)
        self.content_frame.pack(fill="both", expand=True, padx=40, pady=20)

        # Navigation buttons
        nav_frame = tk.Frame(self.root, bg=BG, height=60)
        nav_frame.pack(fill="x", padx=40, pady=(0, 20))

        self.back_btn = tk.Button(
            nav_frame,
            text="← Back",
            command=self._prev_step,
            bg=PANEL,
            fg=TEXT,
            font=("Segoe UI", 11),
            relief="flat",
            cursor="hand2",
            state="disabled",
        )
        self.back_btn.pack(side="left")

        self.next_btn = tk.Button(
            nav_frame,
            text="Next →",
            command=self._next_step,
            bg=ORANGE,
            fg=BG,
            font=("Segoe UI", 11, "bold"),
            relief="flat",
            cursor="hand2",
        )
        self.next_btn.pack(side="right")

        # Configure styles
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Solar.Horizontal.TProgressbar",
            background=ORANGE,
            troughcolor=PANEL,
        )

    def _show_step(self, step: int):
        """Show a specific step."""
        # Clear content
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        # Update progress
        self.current_step = step
        self.progress_label.config(text=f"Step {step + 1} of {len(self.steps)}")
        self.progress_bar["value"] = (step + 1) / len(self.steps) * 100

        # Update navigation buttons
        self.back_btn.config(state="normal" if step > 0 else "disabled")

        if step == len(self.steps) - 1:
            self.next_btn.config(text="Finish ✓", command=self._finish)
        else:
            self.next_btn.config(text="Next →", command=self._next_step)

        # Build step content
        self.steps[step]()

    def _next_step(self):
        """Go to next step."""
        if self.current_step < len(self.steps) - 1:
            # Validate current step
            if self._validate_step():
                self._show_step(self.current_step + 1)

    def _prev_step(self):
        """Go to previous step."""
        if self.current_step > 0:
            self._show_step(self.current_step - 1)

    def _validate_step(self) -> bool:
        """Validate the current step before proceeding."""
        if self.current_step == 1:  # Registration step
            username = self.username_entry.get().strip()
            password = self.password_entry.get()
            confirm = self.confirm_entry.get()

            if not username:
                messagebox.showerror("Error", "Username cannot be empty")
                return False
            if len(username) < 3:
                messagebox.showerror("Error", "Username must be at least 3 characters")
                return False
            if len(password) < 8:
                messagebox.showerror("Error", "Password must be at least 8 characters")
                return False
            if password != confirm:
                messagebox.showerror("Error", "Passwords do not match")
                return False

        return True

    def _build_welcome_step(self):
        """Build the welcome step."""
        frame = tk.Frame(self.content_frame, bg=BG)
        frame.pack(expand=True)

        # Logo/Icon placeholder
        logo_frame = tk.Frame(frame, bg=ORANGE, width=100, height=100)
        logo_frame.pack(pady=(0, 20))
        logo_frame.pack_propagate(False)
        tk.Label(
            logo_frame,
            text="J",
            fg=BG,
            bg=ORANGE,
            font=("Segoe UI", 48, "bold"),
        ).pack(expand=True)

        tk.Label(
            frame,
            text="Welcome to Jarvis V2",
            fg=TEXT,
            bg=BG,
            font=("Segoe UI", 20, "bold"),
        ).pack()

        tk.Label(
            frame,
            text="Your All-in-One Desktop AI Assistant",
            fg=ORANGE,
            bg=BG,
            font=("Segoe UI", 12),
        ).pack(pady=(5, 20))

        features = [
            "✓ Voice Control & AI Conversations",
            "✓ 19 Built-in Modules",
            "✓ Solar Core HUD Interface",
            "✓ Smart Home Integration",
            "✓ Music & Media Control",
        ]

        for feature in features:
            tk.Label(
                frame,
                text=feature,
                fg=TEXT,
                bg=BG,
                font=("Segoe UI", 11),
            ).pack(anchor="w", padx=100)

        tk.Label(
            frame,
            text="\nThis wizard will guide you through the setup process.",
            fg=MUTED,
            bg=BG,
            font=("Segoe UI", 10),
        ).pack(pady=(20, 0))

    def _build_register_step(self):
        """Build the registration step."""
        frame = tk.Frame(self.content_frame, bg=BG)
        frame.pack(expand=True)

        tk.Label(
            frame,
            text="Create Your Account",
            fg=TEXT,
            bg=BG,
            font=("Segoe UI", 16, "bold"),
        ).pack(anchor="w")

        tk.Label(
            frame,
            text="Choose a username and password to personalize your experience.",
            fg=MUTED,
            bg=BG,
            font=("Segoe UI", 10),
        ).pack(anchor="w", pady=(5, 20))

        # Username
        tk.Label(
            frame,
            text="Username",
            fg=TEXT,
            bg=BG,
            font=("Segoe UI", 10),
        ).pack(anchor="w")

        self.username_entry = tk.Entry(
            frame,
            bg=INPUT_BG,
            fg=TEXT,
            insertbackground=ORANGE,
            font=("Segoe UI", 11),
            relief="flat",
        )
        self.username_entry.pack(fill="x", ipady=8, pady=(2, 10))

        # Display Name
        tk.Label(
            frame,
            text="Display Name (optional)",
            fg=TEXT,
            bg=BG,
            font=("Segoe UI", 10),
        ).pack(anchor="w")

        self.displayname_entry = tk.Entry(
            frame,
            bg=INPUT_BG,
            fg=TEXT,
            insertbackground=ORANGE,
            font=("Segoe UI", 11),
            relief="flat",
        )
        self.displayname_entry.pack(fill="x", ipady=8, pady=(2, 10))

        # Email
        tk.Label(
            frame,
            text="Email (optional)",
            fg=TEXT,
            bg=BG,
            font=("Segoe UI", 10),
        ).pack(anchor="w")

        self.email_entry = tk.Entry(
            frame,
            bg=INPUT_BG,
            fg=TEXT,
            insertbackground=ORANGE,
            font=("Segoe UI", 11),
            relief="flat",
        )
        self.email_entry.pack(fill="x", ipady=8, pady=(2, 10))

        # Password
        tk.Label(
            frame,
            text="Password (min 8 characters)",
            fg=TEXT,
            bg=BG,
            font=("Segoe UI", 10),
        ).pack(anchor="w")

        self.password_entry = tk.Entry(
            frame,
            bg=INPUT_BG,
            fg=TEXT,
            insertbackground=ORANGE,
            font=("Segoe UI", 11),
            relief="flat",
            show="•",
        )
        self.password_entry.pack(fill="x", ipady=8, pady=(2, 10))

        # Confirm Password
        tk.Label(
            frame,
            text="Confirm Password",
            fg=TEXT,
            bg=BG,
            font=("Segoe UI", 10),
        ).pack(anchor="w")

        self.confirm_entry = tk.Entry(
            frame,
            bg=INPUT_BG,
            fg=TEXT,
            insertbackground=ORANGE,
            font=("Segoe UI", 11),
            relief="flat",
            show="•",
        )
        self.confirm_entry.pack(fill="x", ipady=8, pady=(2, 10))

    def _build_api_step(self):
        """Build the API configuration step."""
        frame = tk.Frame(self.content_frame, bg=BG)
        frame.pack(expand=True)

        tk.Label(
            frame,
            text="Configure API Keys",
            fg=TEXT,
            bg=BG,
            font=("Segoe UI", 16, "bold"),
        ).pack(anchor="w")

        tk.Label(
            frame,
            text="Add your API keys to unlock full functionality. You can skip this and add later.",
            fg=MUTED,
            bg=BG,
            font=("Segoe UI", 10),
        ).pack(anchor="w", pady=(5, 20))

        # Groq AI
        groq_frame = tk.LabelFrame(
            frame,
            text=" Groq AI (Recommended) ",
            fg=ORANGE,
            bg=PANEL,
            font=("Segoe UI", 10, "bold"),
        )
        groq_frame.pack(fill="x", pady=(0, 10))

        tk.Label(
            groq_frame,
            text="Fast AI inference - Get key at: console.groq.com",
            fg=MUTED,
            bg=PANEL,
            font=("Segoe UI", 9),
        ).pack(anchor="w", padx=10, pady=(5, 0))

        self.groq_entry = tk.Entry(
            groq_frame,
            bg=INPUT_BG,
            fg=TEXT,
            insertbackground=ORANGE,
            font=("Segoe UI", 10),
            relief="flat",
        )
        self.groq_entry.pack(fill="x", padx=10, pady=(5, 10), ipady=6)

        # Email
        email_frame = tk.LabelFrame(
            frame,
            text=" Email (Optional) ",
            fg=ORANGE,
            bg=PANEL,
            font=("Segoe UI", 10, "bold"),
        )
        email_frame.pack(fill="x", pady=(0, 10))

        tk.Label(
            email_frame,
            text="Gmail with App Password - Get at: myaccount.google.com/apppasswords",
            fg=MUTED,
            bg=PANEL,
            font=("Segoe UI", 9),
        ).pack(anchor="w", padx=10, pady=(5, 0))

        email_input_frame = tk.Frame(email_frame, bg=PANEL)
        email_input_frame.pack(fill="x", padx=10, pady=(5, 10))

        self.email_api_entry = tk.Entry(
            email_input_frame,
            bg=INPUT_BG,
            fg=TEXT,
            insertbackground=ORANGE,
            font=("Segoe UI", 10),
            relief="flat",
        )
        self.email_api_entry.pack(side="left", fill="x", expand=True, ipady=6)

        self.email_pass_entry = tk.Entry(
            email_input_frame,
            bg=INPUT_BG,
            fg=TEXT,
            insertbackground=ORANGE,
            font=("Segoe UI", 10),
            relief="flat",
            show="•",
        )
        self.email_pass_entry.pack(side="right", fill="x", expand=True, ipady=6, padx=(10, 0))

        # Skip note
        tk.Label(
            frame,
            text="💡 You can configure more APIs later in Settings",
            fg=MUTED,
            bg=BG,
            font=("Segoe UI", 9),
        ).pack(anchor="w", pady=(10, 0))

    def _build_voice_step(self):
        """Build the voice settings step."""
        frame = tk.Frame(self.content_frame, bg=BG)
        frame.pack(expand=True)

        tk.Label(
            frame,
            text="Voice Settings",
            fg=TEXT,
            bg=BG,
            font=("Segoe UI", 16, "bold"),
        ).pack(anchor="w")

        tk.Label(
            frame,
            text="Choose how Jarvis sounds when speaking.",
            fg=MUTED,
            bg=BG,
            font=("Segoe UI", 10),
        ).pack(anchor="w", pady=(5, 20))

        # Voice Profile
        tk.Label(
            frame,
            text="Voice Profile",
            fg=TEXT,
            bg=BG,
            font=("Segoe UI", 11, "bold"),
        ).pack(anchor="w", pady=(0, 10))

        self.voice_var = tk.StringVar(value="dark_synthetic")

        profiles = [
            ("dark_synthetic", "Dark Synthetic", "Slow, low, commanding voice"),
            ("jarvis_classic", "Jarvis Classic", "Calm, polite, professional"),
            ("fast_operator", "Fast Operator", "Brisk, mission-control pace"),
            ("gentle", "Gentle", "Softer, quieter voice"),
        ]

        for value, name, desc in profiles:
            profile_frame = tk.Frame(frame, bg=PANEL, cursor="hand2")
            profile_frame.pack(fill="x", pady=2)

            radio = tk.Radiobutton(
                profile_frame,
                text="",
                variable=self.voice_var,
                value=value,
                bg=PANEL,
                selectcolor=ORANGE,
                activebackground=PANEL,
            )
            radio.pack(side="left", padx=(10, 5))

            info_frame = tk.Frame(profile_frame, bg=PANEL)
            info_frame.pack(side="left", fill="x", expand=True, pady=8)

            tk.Label(
                info_frame,
                text=name,
                fg=TEXT,
                bg=PANEL,
                font=("Segoe UI", 10, "bold"),
            ).pack(anchor="w")

            tk.Label(
                info_frame,
                text=desc,
                fg=MUTED,
                bg=PANEL,
                font=("Segoe UI", 9),
            ).pack(anchor="w")

        # TTS Engine
        tk.Label(
            frame,
            text="\nTTS Engine",
            fg=TEXT,
            bg=BG,
            font=("Segoe UI", 11, "bold"),
        ).pack(anchor="w", pady=(10, 10))

        self.engine_var = tk.StringVar(value="auto")

        engines = [
            ("auto", "Auto", "Best available engine"),
            ("edge", "Edge Neural", "Natural voice, requires internet"),
            ("pyttsx3", "pyttsx3", "Offline, robotic voice"),
        ]

        for value, name, desc in engines:
            engine_frame = tk.Frame(frame, bg=PANEL, cursor="hand2")
            engine_frame.pack(fill="x", pady=2)

            radio = tk.Radiobutton(
                engine_frame,
                text="",
                variable=self.engine_var,
                value=value,
                bg=PANEL,
                selectcolor=ORANGE,
                activebackground=PANEL,
            )
            radio.pack(side="left", padx=(10, 5))

            info_frame = tk.Frame(engine_frame, bg=PANEL)
            info_frame.pack(side="left", fill="x", expand=True, pady=8)

            tk.Label(
                info_frame,
                text=name,
                fg=TEXT,
                bg=PANEL,
                font=("Segoe UI", 10, "bold"),
            ).pack(anchor="w")

            tk.Label(
                info_frame,
                text=desc,
                fg=MUTED,
                bg=PANEL,
                font=("Segoe UI", 9),
            ).pack(anchor="w")

    def _build_complete_step(self):
        """Build the completion step."""
        frame = tk.Frame(self.content_frame, bg=BG)
        frame.pack(expand=True)

        # Success icon
        success_frame = tk.Frame(frame, bg=GREEN, width=80, height=80)
        success_frame.pack(pady=(0, 20))
        success_frame.pack_propagate(False)
        tk.Label(
            success_frame,
            text="✓",
            fg=BG,
            bg=GREEN,
            font=("Segoe UI", 40, "bold"),
        ).pack(expand=True)

        tk.Label(
            frame,
            text="Setup Complete!",
            fg=TEXT,
            bg=BG,
            font=("Segoe UI", 20, "bold"),
        ).pack()

        tk.Label(
            frame,
            text="Your Jarvis V2 is ready to use.",
            fg=ORANGE,
            bg=BG,
            font=("Segoe UI", 12),
        ).pack(pady=(5, 30))

        # Quick start guide
        guide_frame = tk.Frame(frame, bg=PANEL, padx=20, pady=15)
        guide_frame.pack(fill="x")

        tk.Label(
            guide_frame,
            text="Quick Start Guide",
            fg=ORANGE,
            bg=PANEL,
            font=("Segoe UI", 11, "bold"),
        ).pack(anchor="w")

        tips = [
            "• Type commands in the chat box",
            "• Click SPEAK for voice commands",
            "• Say 'Hey Jarvis' to activate voice",
            "• Try: 'What can you do?'",
            "• Try: 'System status'",
        ]

        for tip in tips:
            tk.Label(
                guide_frame,
                text=tip,
                fg=TEXT,
                bg=PANEL,
                font=("Segoe UI", 10),
            ).pack(anchor="w", pady=1)

    def _save_settings(self):
        """Save all settings from the wizard."""
        # Register user
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        display_name = self.displayname_entry.get().strip() or username
        email = self.email_entry.get().strip() or None

        success, message = self.user_manager.register_user(
            username=username,
            password=password,
            display_name=display_name,
            email=email,
        )

        if success:
            self.user_manager.login(username, password)

        # Save API keys
        groq_key = self.groq_entry.get().strip()
        if groq_key:
            self.env_manager.set("GROQ_API_KEY", groq_key)

        email_addr = self.email_api_entry.get().strip()
        email_pass = self.email_pass_entry.get().strip()
        if email_addr and email_pass:
            self.env_manager.set("JARVIS_EMAIL_ADDRESS", email_addr, save=False)
            self.env_manager.set("JARVIS_EMAIL_APP_PASSWORD", email_pass, save=False)
            self.env_manager.save(self.env_manager.load())

        # Save voice preferences
        self.user_manager.set_preference("voice_profile", self.voice_var.get())
        self.user_manager.set_preference("tts_engine", self.engine_var.get())

    def _finish(self):
        """Finish the wizard."""
        self._save_settings()

        if self.on_complete:
            self.on_complete()

        self.root.destroy()

    def run(self):
        """Run the wizard."""
        self.root.mainloop()


def run_setup_wizard_gui(on_complete: Optional[callable] = None) -> bool:
    """Run the GUI setup wizard if needed."""
    user_manager = get_user_manager()

    if user_manager.is_first_run():
        wizard = SetupWizardGUI(on_complete=on_complete)
        wizard.run()
        return user_manager.is_logged_in()

    return True
