"""
Jarvis V2 - Settings Dialog
=============================
Settings and configuration dialog.

Features:
- User profile management
- API key configuration
- Voice settings
- Application preferences
- Security settings
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
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


class SettingsDialog:
    """
    Settings dialog for Jarvis V2.

    Features:
    - Tabbed interface
    - User profile settings
    - API configuration
    - Voice settings
    - Application preferences
    """

    def __init__(self, parent: Optional[tk.Tk] = None):
        self.parent = parent

        self.user_manager = get_user_manager()
        self.env_manager = SecureEnvManager()
        self.api_manager = APIManager()
        self.validator = APIValidator()

        self.root = tk.Toplevel(parent) if parent else tk.Tk()
        self.root.title("Jarvis V2 - Settings")
        self.root.geometry("800x600")
        self.root.configure(bg=BG)
        self.root.resizable(True, True)

        # Center window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (800 // 2)
        y = (self.root.winfo_screenheight() // 2) - (600 // 2)
        self.root.geometry(f"+{x}+{y}")

        self._build_ui()
        self._load_settings()

    def _build_ui(self):
        """Build the settings UI."""
        # Header
        header = tk.Frame(self.root, bg=PANEL, height=60)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(
            header,
            text="⚙ Settings",
            fg=ORANGE,
            bg=PANEL,
            font=("Segoe UI", 16, "bold"),
        ).pack(side="left", padx=20)

        # Close button
        close_btn = tk.Button(
            header,
            text="✕",
            bg=PANEL,
            fg=MUTED,
            font=("Segoe UI", 14),
            relief="flat",
            cursor="hand2",
            command=self.root.destroy,
        )
        close_btn.pack(side="right", padx=20)

        # Main content with tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # Configure tab style
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TNotebook", background=BG)
        style.configure("TNotebook.Tab", background=PANEL, foreground=TEXT)
        style.map("TNotebook.Tab", background=[("selected", ORANGE)])
        style.map("TNotebook.Tab", foreground=[("selected", BG)])

        # Create tabs
        self._build_profile_tab()
        self._build_api_tab()
        self._build_voice_tab()
        self._build_preferences_tab()
        self._build_security_tab()

        # Save button
        save_frame = tk.Frame(self.root, bg=BG)
        save_frame.pack(fill="x", padx=10, pady=(0, 10))

        tk.Button(
            save_frame,
            text="Save Changes",
            bg=ORANGE,
            fg=BG,
            font=("Segoe UI", 11, "bold"),
            relief="flat",
            cursor="hand2",
            command=self._save_settings,
        ).pack(side="right", padx=5, ipady=5, ipadx=20)

        tk.Button(
            save_frame,
            text="Cancel",
            bg=PANEL,
            fg=TEXT,
            font=("Segoe UI", 11),
            relief="flat",
            cursor="hand2",
            command=self.root.destroy,
        ).pack(side="right", padx=5, ipady=5, ipadx=20)

    def _build_profile_tab(self):
        """Build the profile settings tab."""
        tab = tk.Frame(self.notebook, bg=BG)
        self.notebook.add(tab, text="  Profile  ")

        # Scrollable frame
        canvas = tk.Canvas(tab, bg=BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(tab, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=BG)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Profile section
        profile_frame = tk.LabelFrame(
            scrollable_frame,
            text=" User Profile ",
            fg=ORANGE,
            bg=PANEL,
            font=("Segoe UI", 11, "bold"),
        )
        profile_frame.pack(fill="x", padx=20, pady=20)

        # Username (read-only)
        tk.Label(
            profile_frame,
            text="Username",
            fg=TEXT,
            bg=PANEL,
            font=("Segoe UI", 10),
        ).pack(anchor="w", padx=15, pady=(15, 5))

        self.username_label = tk.Label(
            profile_frame,
            text="",
            fg=MUTED,
            bg=PANEL,
            font=("Segoe UI", 10),
        )
        self.username_label.pack(anchor="w", padx=15)

        # Display Name
        tk.Label(
            profile_frame,
            text="Display Name",
            fg=TEXT,
            bg=PANEL,
            font=("Segoe UI", 10),
        ).pack(anchor="w", padx=15, pady=(15, 5))

        self.displayname_entry = tk.Entry(
            profile_frame,
            bg=INPUT_BG,
            fg=TEXT,
            insertbackground=ORANGE,
            font=("Segoe UI", 10),
            relief="flat",
        )
        self.displayname_entry.pack(fill="x", padx=15, ipady=6, pady=(0, 15))

        # Email
        tk.Label(
            profile_frame,
            text="Email",
            fg=TEXT,
            bg=PANEL,
            font=("Segoe UI", 10),
        ).pack(anchor="w", padx=15, pady=(0, 5))

        self.email_entry = tk.Entry(
            profile_frame,
            bg=INPUT_BG,
            fg=TEXT,
            insertbackground=ORANGE,
            font=("Segoe UI", 10),
            relief="flat",
        )
        self.email_entry.pack(fill="x", padx=15, ipady=6, pady=(0, 15))

        # Owner Name (how Jarvis addresses you)
        tk.Label(
            profile_frame,
            text="How should Jarvis address you?",
            fg=TEXT,
            bg=PANEL,
            font=("Segoe UI", 10),
        ).pack(anchor="w", padx=15, pady=(0, 5))

        self.ownername_entry = tk.Entry(
            profile_frame,
            bg=INPUT_BG,
            fg=TEXT,
            insertbackground=ORANGE,
            font=("Segoe UI", 10),
            relief="flat",
        )
        self.ownername_entry.pack(fill="x", padx=15, ipady=6, pady=(0, 15))

        self.ownername_entry.insert(0, "sir")

    def _build_api_tab(self):
        """Build the API configuration tab."""
        tab = tk.Frame(self.notebook, bg=BG)
        self.notebook.add(tab, text="  API Keys  ")

        # Scrollable frame
        canvas = tk.Canvas(tab, bg=BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(tab, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=BG)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Groq AI
        groq_frame = tk.LabelFrame(
            scrollable_frame,
            text=" Groq AI (Recommended) ",
            fg=ORANGE,
            bg=PANEL,
            font=("Segoe UI", 11, "bold"),
        )
        groq_frame.pack(fill="x", padx=20, pady=(20, 10))

        tk.Label(
            groq_frame,
            text="Fast AI inference - Get key at: console.groq.com",
            fg=MUTED,
            bg=PANEL,
            font=("Segoe UI", 9),
        ).pack(anchor="w", padx=15, pady=(10, 5))

        self.groq_entry = tk.Entry(
            groq_frame,
            bg=INPUT_BG,
            fg=TEXT,
            insertbackground=ORANGE,
            font=("Segoe UI", 10),
            relief="flat",
        )
        self.groq_entry.pack(fill="x", padx=15, ipady=6, pady=(0, 10))

        # OpenAI
        openai_frame = tk.LabelFrame(
            scrollable_frame,
            text=" OpenAI (Alternative) ",
            fg=ORANGE,
            bg=PANEL,
            font=("Segoe UI", 11, "bold"),
        )
        openai_frame.pack(fill="x", padx=20, pady=10)

        tk.Label(
            openai_frame,
            text="GPT-4 and other models - Get key at: platform.openai.com",
            fg=MUTED,
            bg=PANEL,
            font=("Segoe UI", 9),
        ).pack(anchor="w", padx=15, pady=(10, 5))

        self.openai_entry = tk.Entry(
            openai_frame,
            bg=INPUT_BG,
            fg=TEXT,
            insertbackground=ORANGE,
            font=("Segoe UI", 10),
            relief="flat",
        )
        self.openai_entry.pack(fill="x", padx=15, ipady=6, pady=(0, 10))

        # Email
        email_frame = tk.LabelFrame(
            scrollable_frame,
            text=" Email (Gmail) ",
            fg=ORANGE,
            bg=PANEL,
            font=("Segoe UI", 11, "bold"),
        )
        email_frame.pack(fill="x", padx=20, pady=10)

        tk.Label(
            email_frame,
            text="Requires 2FA enabled - Get App Password at: myaccount.google.com/apppasswords",
            fg=MUTED,
            bg=PANEL,
            font=("Segoe UI", 9),
        ).pack(anchor="w", padx=15, pady=(10, 5))

        tk.Label(
            email_frame,
            text="Email Address",
            fg=TEXT,
            bg=PANEL,
            font=("Segoe UI", 10),
        ).pack(anchor="w", padx=15, pady=(5, 2))

        self.email_addr_entry = tk.Entry(
            email_frame,
            bg=INPUT_BG,
            fg=TEXT,
            insertbackground=ORANGE,
            font=("Segoe UI", 10),
            relief="flat",
        )
        self.email_addr_entry.pack(fill="x", padx=15, ipady=6, pady=(0, 10))

        tk.Label(
            email_frame,
            text="App Password",
            fg=TEXT,
            bg=PANEL,
            font=("Segoe UI", 10),
        ).pack(anchor="w", padx=15, pady=(0, 2))

        self.email_pass_entry = tk.Entry(
            email_frame,
            bg=INPUT_BG,
            fg=TEXT,
            insertbackground=ORANGE,
            font=("Segoe UI", 10),
            relief="flat",
            show="•",
        )
        self.email_pass_entry.pack(fill="x", padx=15, ipady=6, pady=(0, 15))

        # Twilio
        twilio_frame = tk.LabelFrame(
            scrollable_frame,
            text=" Twilio (WhatsApp & Phone) ",
            fg=ORANGE,
            bg=PANEL,
            font=("Segoe UI", 11, "bold"),
        )
        twilio_frame.pack(fill="x", padx=20, pady=10)

        tk.Label(
            twilio_frame,
            text="Get credentials at: console.twilio.com",
            fg=MUTED,
            bg=PANEL,
            font=("Segoe UI", 9),
        ).pack(anchor="w", padx=15, pady=(10, 5))

        tk.Label(
            twilio_frame,
            text="Account SID",
            fg=TEXT,
            bg=PANEL,
            font=("Segoe UI", 10),
        ).pack(anchor="w", padx=15, pady=(5, 2))

        self.twilio_sid_entry = tk.Entry(
            twilio_frame,
            bg=INPUT_BG,
            fg=TEXT,
            insertbackground=ORANGE,
            font=("Segoe UI", 10),
            relief="flat",
        )
        self.twilio_sid_entry.pack(fill="x", padx=15, ipady=6, pady=(0, 10))

        tk.Label(
            twilio_frame,
            text="Auth Token",
            fg=TEXT,
            bg=PANEL,
            font=("Segoe UI", 10),
        ).pack(anchor="w", padx=15, pady=(0, 2))

        self.twilio_token_entry = tk.Entry(
            twilio_frame,
            bg=INPUT_BG,
            fg=TEXT,
            insertbackground=ORANGE,
            font=("Segoe UI", 10),
            relief="flat",
            show="•",
        )
        self.twilio_token_entry.pack(fill="x", padx=15, ipady=6, pady=(0, 15))

        # Spotify
        spotify_frame = tk.LabelFrame(
            scrollable_frame,
            text=" Spotify ",
            fg=ORANGE,
            bg=PANEL,
            font=("Segoe UI", 11, "bold"),
        )
        spotify_frame.pack(fill="x", padx=20, pady=10)

        tk.Label(
            spotify_frame,
            text="Get credentials at: developer.spotify.com/dashboard",
            fg=MUTED,
            bg=PANEL,
            font=("Segoe UI", 9),
        ).pack(anchor="w", padx=15, pady=(10, 5))

        tk.Label(
            spotify_frame,
            text="Client ID",
            fg=TEXT,
            bg=PANEL,
            font=("Segoe UI", 10),
        ).pack(anchor="w", padx=15, pady=(5, 2))

        self.spotify_id_entry = tk.Entry(
            spotify_frame,
            bg=INPUT_BG,
            fg=TEXT,
            insertbackground=ORANGE,
            font=("Segoe UI", 10),
            relief="flat",
        )
        self.spotify_id_entry.pack(fill="x", padx=15, ipady=6, pady=(0, 10))

        tk.Label(
            spotify_frame,
            text="Client Secret",
            fg=TEXT,
            bg=PANEL,
            font=("Segoe UI", 10),
        ).pack(anchor="w", padx=15, pady=(0, 2))

        self.spotify_secret_entry = tk.Entry(
            spotify_frame,
            bg=INPUT_BG,
            fg=TEXT,
            insertbackground=ORANGE,
            font=("Segoe UI", 10),
            relief="flat",
            show="•",
        )
        self.spotify_secret_entry.pack(fill="x", padx=15, ipady=6, pady=(0, 15))

    def _build_voice_tab(self):
        """Build the voice settings tab."""
        tab = tk.Frame(self.notebook, bg=BG)
        self.notebook.add(tab, text="  Voice  ")

        # Voice Profile
        profile_frame = tk.LabelFrame(
            tab,
            text=" Voice Profile ",
            fg=ORANGE,
            bg=PANEL,
            font=("Segoe UI", 11, "bold"),
        )
        profile_frame.pack(fill="x", padx=20, pady=20)

        self.voice_var = tk.StringVar(value="dark_synthetic")

        profiles = [
            ("dark_synthetic", "Dark Synthetic", "Slow, low, commanding voice"),
            ("jarvis_classic", "Jarvis Classic", "Calm, polite, professional"),
            ("fast_operator", "Fast Operator", "Brisk, mission-control pace"),
            ("gentle", "Gentle", "Softer, quieter voice"),
        ]

        for value, name, desc in profiles:
            profile_option = tk.Frame(profile_frame, bg=PANEL, cursor="hand2")
            profile_option.pack(fill="x", padx=15, pady=5)

            radio = tk.Radiobutton(
                profile_option,
                text="",
                variable=self.voice_var,
                value=value,
                bg=PANEL,
                selectcolor=ORANGE,
                activebackground=PANEL,
            )
            radio.pack(side="left")

            info_frame = tk.Frame(profile_option, bg=PANEL)
            info_frame.pack(side="left", fill="x", expand=True, padx=10)

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
        engine_frame = tk.LabelFrame(
            tab,
            text=" TTS Engine ",
            fg=ORANGE,
            bg=PANEL,
            font=("Segoe UI", 11, "bold"),
        )
        engine_frame.pack(fill="x", padx=20, pady=10)

        self.engine_var = tk.StringVar(value="auto")

        engines = [
            ("auto", "Auto", "Best available engine"),
            ("edge", "Edge Neural", "Natural voice, requires internet"),
            ("pyttsx3", "pyttsx3", "Offline, robotic voice"),
            ("system", "System", "OS default voice"),
        ]

        for value, name, desc in engines:
            engine_option = tk.Frame(engine_frame, bg=PANEL, cursor="hand2")
            engine_option.pack(fill="x", padx=15, pady=5)

            radio = tk.Radiobutton(
                engine_option,
                text="",
                variable=self.engine_var,
                value=value,
                bg=PANEL,
                selectcolor=ORANGE,
                activebackground=PANEL,
            )
            radio.pack(side="left")

            info_frame = tk.Frame(engine_option, bg=PANEL)
            info_frame.pack(side="left", fill="x", expand=True, padx=10)

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

    def _build_preferences_tab(self):
        """Build the preferences tab."""
        tab = tk.Frame(self.notebook, bg=BG)
        self.notebook.add(tab, text="  Preferences  ")

        # General
        general_frame = tk.LabelFrame(
            tab,
            text=" General ",
            fg=ORANGE,
            bg=PANEL,
            font=("Segoe UI", 11, "bold"),
        )
        general_frame.pack(fill="x", padx=20, pady=20)

        # Speak responses
        self.speak_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            general_frame,
            text="Speak responses aloud",
            variable=self.speak_var,
            bg=PANEL,
            fg=TEXT,
            selectcolor=ORANGE,
            activebackground=PANEL,
            font=("Segoe UI", 10),
        ).pack(anchor="w", padx=15, pady=10)

        # Remember conversations
        self.remember_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            general_frame,
            text="Remember conversations",
            variable=self.remember_var,
            bg=PANEL,
            fg=TEXT,
            selectcolor=ORANGE,
            activebackground=PANEL,
            font=("Segoe UI", 10),
        ).pack(anchor="w", padx=15, pady=10)

        # Learning enabled
        self.learning_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            general_frame,
            text="Enable learning from interactions",
            variable=self.learning_var,
            bg=PANEL,
            fg=TEXT,
            selectcolor=ORANGE,
            activebackground=PANEL,
            font=("Segoe UI", 10),
        ).pack(anchor="w", padx=15, pady=10)

        # Confirm dangerous actions
        self.confirm_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            general_frame,
            text="Confirm dangerous actions (shutdown, restart)",
            variable=self.confirm_var,
            bg=PANEL,
            fg=TEXT,
            selectcolor=ORANGE,
            activebackground=PANEL,
            font=("Segoe UI", 10),
        ).pack(anchor="w", padx=15, pady=(10, 15))

        # UI Settings
        ui_frame = tk.LabelFrame(
            tab,
            text=" Interface ",
            fg=ORANGE,
            bg=PANEL,
            font=("Segoe UI", 11, "bold"),
        )
        ui_frame.pack(fill="x", padx=20, pady=10)

        # Transparency
        tk.Label(
            ui_frame,
            text="Window Transparency",
            fg=TEXT,
            bg=PANEL,
            font=("Segoe UI", 10),
        ).pack(anchor="w", padx=15, pady=(15, 5))

        self.transparency_var = tk.DoubleVar(value=0.98)
        transparency_scale = tk.Scale(
            ui_frame,
            from_=0.5,
            to=1.0,
            resolution=0.01,
            orient="horizontal",
            variable=self.transparency_var,
            bg=PANEL,
            fg=TEXT,
            highlightthickness=0,
            troughcolor=INPUT_BG,
        )
        transparency_scale.pack(fill="x", padx=15, pady=(0, 15))

    def _build_security_tab(self):
        """Build the security tab."""
        tab = tk.Frame(self.notebook, bg=BG)
        self.notebook.add(tab, text="  Security  ")

        # Change Password
        password_frame = tk.LabelFrame(
            tab,
            text=" Change Password ",
            fg=ORANGE,
            bg=PANEL,
            font=("Segoe UI", 11, "bold"),
        )
        password_frame.pack(fill="x", padx=20, pady=20)

        tk.Label(
            password_frame,
            text="Current Password",
            fg=TEXT,
            bg=PANEL,
            font=("Segoe UI", 10),
        ).pack(anchor="w", padx=15, pady=(15, 5))

        self.current_pass_entry = tk.Entry(
            password_frame,
            bg=INPUT_BG,
            fg=TEXT,
            insertbackground=ORANGE,
            font=("Segoe UI", 10),
            relief="flat",
            show="•",
        )
        self.current_pass_entry.pack(fill="x", padx=15, ipady=6, pady=(0, 10))

        tk.Label(
            password_frame,
            text="New Password",
            fg=TEXT,
            bg=PANEL,
            font=("Segoe UI", 10),
        ).pack(anchor="w", padx=15, pady=(0, 5))

        self.new_pass_entry = tk.Entry(
            password_frame,
            bg=INPUT_BG,
            fg=TEXT,
            insertbackground=ORANGE,
            font=("Segoe UI", 10),
            relief="flat",
            show="•",
        )
        self.new_pass_entry.pack(fill="x", padx=15, ipady=6, pady=(0, 10))

        tk.Label(
            password_frame,
            text="Confirm New Password",
            fg=TEXT,
            bg=PANEL,
            font=("Segoe UI", 10),
        ).pack(anchor="w", padx=15, pady=(0, 5))

        self.confirm_pass_entry = tk.Entry(
            password_frame,
            bg=INPUT_BG,
            fg=TEXT,
            insertbackground=ORANGE,
            font=("Segoe UI", 10),
            relief="flat",
            show="•",
        )
        self.confirm_pass_entry.pack(fill="x", padx=15, ipady=6, pady=(0, 10))

        tk.Button(
            password_frame,
            text="Change Password",
            bg=ORANGE,
            fg=BG,
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            cursor="hand2",
            command=self._change_password,
        ).pack(anchor="w", padx=15, pady=(0, 15))

        # Logout
        logout_frame = tk.LabelFrame(
            tab,
            text=" Session ",
            fg=ORANGE,
            bg=PANEL,
            font=("Segoe UI", 11, "bold"),
        )
        logout_frame.pack(fill="x", padx=20, pady=10)

        tk.Button(
            logout_frame,
            text="Logout",
            bg=RED,
            fg=TEXT,
            font=("Segoe UI", 10),
            relief="flat",
            cursor="hand2",
            command=self._logout,
        ).pack(anchor="w", padx=15, pady=15)

    def _load_settings(self):
        """Load current settings into the UI."""
        # Profile
        user = self.user_manager.get_current_user()
        if user:
            self.username_label.config(text=user.get("username", ""))
            self.displayname_entry.insert(0, user.get("display_name", ""))
            self.email_entry.insert(0, user.get("email", "") or "")

        # Owner name
        owner_name = self.user_manager.get_preference("owner_name", "sir")
        self.ownername_entry.insert(0, owner_name)

        # API keys
        groq_key = self.env_manager.get("GROQ_API_KEY", "")
        if groq_key and not groq_key.startswith("your_"):
            self.groq_entry.insert(0, groq_key)

        openai_key = self.env_manager.get("OPENAI_API_KEY", "")
        if openai_key and not openai_key.startswith("your_"):
            self.openai_entry.insert(0, openai_key)

        email_addr = self.env_manager.get("JARVIS_EMAIL_ADDRESS", "")
        if email_addr:
            self.email_addr_entry.insert(0, email_addr)

        email_pass = self.env_manager.get("JARVIS_EMAIL_APP_PASSWORD", "")
        if email_pass:
            self.email_pass_entry.insert(0, email_pass)

        twilio_sid = self.env_manager.get("TWILIO_ACCOUNT_SID", "")
        if twilio_sid:
            self.twilio_sid_entry.insert(0, twilio_sid)

        twilio_token = self.env_manager.get("TWILIO_AUTH_TOKEN", "")
        if twilio_token:
            self.twilio_token_entry.insert(0, twilio_token)

        spotify_id = self.env_manager.get("SPOTIFY_CLIENT_ID", "")
        if spotify_id:
            self.spotify_id_entry.insert(0, spotify_id)

        spotify_secret = self.env_manager.get("SPOTIFY_CLIENT_SECRET", "")
        if spotify_secret:
            self.spotify_secret_entry.insert(0, spotify_secret)

        # Voice
        voice_profile = self.user_manager.get_preference("voice_profile", "dark_synthetic")
        self.voice_var.set(voice_profile)

        tts_engine = self.user_manager.get_preference("tts_engine", "auto")
        self.engine_var.set(tts_engine)

        # Preferences
        self.speak_var.set(self.user_manager.get_preference("speak_responses", True))
        self.remember_var.set(self.user_manager.get_preference("remember_conversations", True))
        self.learning_var.set(self.user_manager.get_preference("learning_enabled", True))
        self.confirm_var.set(self.user_manager.get_preference("confirm_dangerous_actions", True))

        transparency = self.user_manager.get_preference("transparency", 0.98)
        self.transparency_var.set(transparency)

    def _save_settings(self):
        """Save all settings."""
        # Profile
        display_name = self.displayname_entry.get().strip()
        email = self.email_entry.get().strip()
        owner_name = self.ownername_entry.get().strip()

        if display_name:
            self.user_manager.update_profile(display_name=display_name)
        if email:
            self.user_manager.update_profile(email=email)

        self.user_manager.set_preference("owner_name", owner_name)

        # API keys
        groq_key = self.groq_entry.get().strip()
        if groq_key:
            self.env_manager.set("GROQ_API_KEY", groq_key)

        openai_key = self.openai_entry.get().strip()
        if openai_key:
            self.env_manager.set("OPENAI_API_KEY", openai_key)

        email_addr = self.email_addr_entry.get().strip()
        email_pass = self.email_pass_entry.get().strip()
        if email_addr and email_pass:
            self.env_manager.set("JARVIS_EMAIL_ADDRESS", email_addr, save=False)
            self.env_manager.set("JARVIS_EMAIL_APP_PASSWORD", email_pass, save=False)

        twilio_sid = self.twilio_sid_entry.get().strip()
        twilio_token = self.twilio_token_entry.get().strip()
        if twilio_sid and twilio_token:
            self.env_manager.set("TWILIO_ACCOUNT_SID", twilio_sid, save=False)
            self.env_manager.set("TWILIO_AUTH_TOKEN", twilio_token, save=False)

        spotify_id = self.spotify_id_entry.get().strip()
        spotify_secret = self.spotify_secret_entry.get().strip()
        if spotify_id and spotify_secret:
            self.env_manager.set("SPOTIFY_CLIENT_ID", spotify_id, save=False)
            self.env_manager.set("SPOTIFY_CLIENT_SECRET", spotify_secret, save=False)

        self.env_manager.save(self.env_manager.load())

        # Voice
        self.user_manager.set_preference("voice_profile", self.voice_var.get())
        self.user_manager.set_preference("tts_engine", self.engine_var.get())

        # Preferences
        self.user_manager.set_preference("speak_responses", self.speak_var.get())
        self.user_manager.set_preference("remember_conversations", self.remember_var.get())
        self.user_manager.set_preference("learning_enabled", self.learning_var.get())
        self.user_manager.set_preference("confirm_dangerous_actions", self.confirm_var.get())
        self.user_manager.set_preference("transparency", self.transparency_var.get())

        messagebox.showinfo("Success", "Settings saved successfully!")
        self.root.destroy()

    def _change_password(self):
        """Change user password."""
        current = self.current_pass_entry.get()
        new = self.new_pass_entry.get()
        confirm = self.confirm_pass_entry.get()

        if not current or not new or not confirm:
            messagebox.showerror("Error", "Please fill in all password fields")
            return

        if new != confirm:
            messagebox.showerror("Error", "New passwords do not match")
            return

        if len(new) < 8:
            messagebox.showerror("Error", "New password must be at least 8 characters")
            return

        success, message = self.user_manager.change_password(current, new)
        if success:
            messagebox.showinfo("Success", message)
            self.current_pass_entry.delete(0, "end")
            self.new_pass_entry.delete(0, "end")
            self.confirm_pass_entry.delete(0, "end")
        else:
            messagebox.showerror("Error", message)

    def _logout(self):
        """Logout current user."""
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.user_manager.logout()
            self.root.destroy()

    def run(self):
        """Run the settings dialog."""
        self.root.mainloop()


def show_settings_dialog(parent: Optional[tk.Tk] = None):
    """Show the settings dialog."""
    dialog = SettingsDialog(parent=parent)
    dialog.run()
