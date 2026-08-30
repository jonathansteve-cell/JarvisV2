"""
Jarvis V2 - Login Dialog
=========================
Login dialog for returning users.

Features:
- Username/password login
- Remember me option
- New user registration link
- Error handling
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Any, Optional

from core.user_manager import UserManager, get_user_manager

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


class LoginDialog:
    """
    Login dialog for Jarvis V2.

    Features:
    - Clean, modern interface
    - Username/password authentication
    - Error handling
    - New user registration option
    """

    def __init__(self, on_login: Optional[callable] = None, on_register: Optional[callable] = None):
        self.on_login = on_login
        self.on_register = on_register

        self.user_manager = get_user_manager()
        self.result = False

        self.root = tk.Tk()
        self.root.title("Jarvis V2 - Login")
        self.root.geometry("400x500")
        self.root.configure(bg=BG)
        self.root.resizable(False, False)

        # Center window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (400 // 2)
        y = (self.root.winfo_screenheight() // 2) - (500 // 2)
        self.root.geometry(f"+{x}+{y}")

        self._build_ui()

    def _build_ui(self):
        """Build the login UI."""
        # Header
        header = tk.Frame(self.root, bg=PANEL, height=100)
        header.pack(fill="x")
        header.pack_propagate(False)

        # Logo
        logo_frame = tk.Frame(header, bg=ORANGE, width=60, height=60)
        logo_frame.pack(expand=True)
        logo_frame.pack_propagate(False)
        tk.Label(
            logo_frame,
            text="J",
            fg=BG,
            bg=ORANGE,
            font=("Segoe UI", 32, "bold"),
        ).pack(expand=True)

        tk.Label(
            header,
            text="J.A.R.V.I.S V2",
            fg=ORANGE,
            bg=PANEL,
            font=("Segoe UI", 16, "bold"),
        ).pack()

        # Login form
        form_frame = tk.Frame(self.root, bg=BG)
        form_frame.pack(fill="both", expand=True, padx=40, pady=30)

        tk.Label(
            form_frame,
            text="Welcome Back",
            fg=TEXT,
            bg=BG,
            font=("Segoe UI", 18, "bold"),
        ).pack(anchor="w")

        tk.Label(
            form_frame,
            text="Sign in to continue",
            fg=MUTED,
            bg=BG,
            font=("Segoe UI", 10),
        ).pack(anchor="w", pady=(5, 25))

        # Username
        tk.Label(
            form_frame,
            text="Username",
            fg=TEXT,
            bg=BG,
            font=("Segoe UI", 10),
        ).pack(anchor="w")

        self.username_entry = tk.Entry(
            form_frame,
            bg=INPUT_BG,
            fg=TEXT,
            insertbackground=ORANGE,
            font=("Segoe UI", 12),
            relief="flat",
        )
        self.username_entry.pack(fill="x", ipady=10, pady=(5, 15))
        self.username_entry.focus_set()

        # Password
        tk.Label(
            form_frame,
            text="Password",
            fg=TEXT,
            bg=BG,
            font=("Segoe UI", 10),
        ).pack(anchor="w")

        password_frame = tk.Frame(form_frame, bg=BG)
        password_frame.pack(fill="x", pady=(5, 15))

        self.password_entry = tk.Entry(
            password_frame,
            bg=INPUT_BG,
            fg=TEXT,
            insertbackground=ORANGE,
            font=("Segoe UI", 12),
            relief="flat",
            show="•",
        )
        self.password_entry.pack(side="left", fill="x", expand=True, ipady=10)

        # Show/hide password button
        self.show_password = False
        self.toggle_btn = tk.Button(
            password_frame,
            text="👁",
            bg=INPUT_BG,
            fg=MUTED,
            font=("Segoe UI", 10),
            relief="flat",
            cursor="hand2",
            command=self._toggle_password,
        )
        self.toggle_btn.pack(side="right", padx=(5, 0))

        # Error label
        self.error_label = tk.Label(
            form_frame,
            text="",
            fg=RED,
            bg=BG,
            font=("Segoe UI", 9),
        )
        self.error_label.pack(anchor="w", pady=(0, 10))

        # Login button
        self.login_btn = tk.Button(
            form_frame,
            text="Sign In",
            bg=ORANGE,
            fg=BG,
            font=("Segoe UI", 12, "bold"),
            relief="flat",
            cursor="hand2",
            command=self._login,
        )
        self.login_btn.pack(fill="x", ipady=10)

        # Bind Enter key
        self.root.bind("<Return>", lambda e: self._login())

        # Divider
        divider_frame = tk.Frame(form_frame, bg=BG)
        divider_frame.pack(fill="x", pady=20)

        tk.Frame(divider_frame, bg=MUTED, height=1).pack(side="left", fill="x", expand=True)
        tk.Label(
            divider_frame,
            text="  OR  ",
            fg=MUTED,
            bg=BG,
            font=("Segoe UI", 9),
        ).pack(side="left")
        tk.Frame(divider_frame, bg=MUTED, height=1).pack(side="left", fill="x", expand=True)

        # Register button
        register_btn = tk.Button(
            form_frame,
            text="Create New Account",
            bg=PANEL,
            fg=TEXT,
            font=("Segoe UI", 11),
            relief="flat",
            cursor="hand2",
            command=self._register,
        )
        register_btn.pack(fill="x", ipady=8)

    def _toggle_password(self):
        """Toggle password visibility."""
        self.show_password = not self.show_password
        if self.show_password:
            self.password_entry.config(show="")
            self.toggle_btn.config(text="🔒")
        else:
            self.password_entry.config(show="•")
            self.toggle_btn.config(text="👁")

    def _login(self):
        """Handle login."""
        username = self.username_entry.get().strip()
        password = self.password_entry.get()

        if not username:
            self.error_label.config(text="Please enter your username")
            self.username_entry.focus_set()
            return

        if not password:
            self.error_label.config(text="Please enter your password")
            self.password_entry.focus_set()
            return

        # Disable button during login
        self.login_btn.config(state="disabled", text="Signing in...")
        self.root.update()

        success, message = self.user_manager.login(username, password)

        if success:
            self.result = True
            if self.on_login:
                self.on_login()
            self.root.destroy()
        else:
            self.error_label.config(text=message)
            self.login_btn.config(state="normal", text="Sign In")
            self.password_entry.delete(0, "end")
            self.password_entry.focus_set()

    def _register(self):
        """Handle registration."""
        if self.on_register:
            self.on_register()
        self.root.destroy()

    def run(self) -> bool:
        """Run the dialog and return result."""
        self.root.mainloop()
        return self.result


def show_login_dialog(
    on_login: Optional[callable] = None,
    on_register: Optional[callable] = None,
) -> bool:
    """
    Show the login dialog.

    Returns:
        True if login was successful, False otherwise
    """
    dialog = LoginDialog(on_login=on_login, on_register=on_register)
    return dialog.run()
