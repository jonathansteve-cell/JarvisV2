"""
Jarvis V2 - Modern UI
======================
A sleek, modern interface for Jarvis V2 with:
- Dark theme with orange accents
- Chat interface
- Voice controls
- System status panel
- Mode selection (Research, Roblox, Serious)
- Settings panel
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import time
from datetime import datetime
from typing import Any, Optional

# Color scheme
COLORS = {
    'bg': '#0a0a0a',
    'bg_secondary': '#121212',
    'bg_tertiary': '#1a1a1a',
    'panel': '#0d0d0d',
    'panel_border': '#2a2a2a',
    'accent': '#FF8C1A',
    'accent_dark': '#B4530A',
    'accent_light': '#FFB25E',
    'text': '#FFFFFF',
    'text_secondary': '#A0A0A0',
    'text_muted': '#666666',
    'success': '#38E07C',
    'error': '#E05555',
    'warning': '#FFA500',
    'input_bg': '#1a1a1a',
    'input_border': '#333333',
    'button_bg': '#FF8C1A',
    'button_hover': '#FFB25E',
    'button_text': '#000000',
}


class ModernButton(tk.Button):
    """Modern styled button with hover effects."""
    
    def __init__(self, master, **kwargs):
        self.default_bg = kwargs.get('bg', COLORS['button_bg'])
        self.hover_bg = kwargs.get('activebackground', COLORS['button_hover'])
        
        super().__init__(master, **kwargs)
        
        self.configure(
            relief='flat',
            borderwidth=0,
            cursor='hand2',
            font=('Segoe UI', 10, 'bold')
        )
        
        self.bind('<Enter>', self._on_enter)
        self.bind('<Leave>', self._on_leave)
    
    def _on_enter(self, e):
        self.configure(bg=self.hover_bg)
    
    def _on_leave(self, e):
        self.configure(bg=self.default_bg)


class ModernEntry(tk.Entry):
    """Modern styled entry with placeholder text."""
    
    def __init__(self, master, placeholder='', **kwargs):
        super().__init__(master, **kwargs)
        
        self.placeholder = placeholder
        self.placeholder_color = COLORS['text_muted']
        self.default_fg = kwargs.get('fg', COLORS['text'])
        
        self.configure(
            bg=COLORS['input_bg'],
            fg=self.default_fg,
            insertbackground=COLORS['accent'],
            relief='flat',
            borderwidth=2,
            highlightthickness=1,
            highlightcolor=COLORS['accent'],
            highlightbackground=COLORS['input_border'],
            font=('Segoe UI', 11)
        )
        
        self.bind('<FocusIn>', self._on_focus_in)
        self.bind('<FocusOut>', self._on_focus_out)
        
        self._show_placeholder()
    
    def _show_placeholder(self):
        if not self.get():
            self.insert(0, self.placeholder)
            self.configure(fg=self.placeholder_color)
    
    def _on_focus_in(self, e):
        if self.get() == self.placeholder:
            self.delete(0, tk.END)
            self.configure(fg=self.default_fg)
    
    def _on_focus_out(self, e):
        if not self.get():
            self._show_placeholder()


class StatusBar(tk.Frame):
    """Status bar showing system information."""
    
    def __init__(self, master, **kwargs):
        super().__init__(master, bg=COLORS['panel'], **kwargs)
        
        self.configure(height=30)
        self.pack_propagate(False)
        
        # Status indicators
        self.indicators = {}
        
        # AI Status
        self.indicators['ai'] = tk.Label(
            self,
            text='● AI: Online',
            fg=COLORS['success'],
            bg=COLORS['panel'],
            font=('Segoe UI', 9)
        )
        self.indicators['ai'].pack(side='left', padx=10)
        
        # Voice Status
        self.indicators['voice'] = tk.Label(
            self,
            text='● Voice: Ready',
            fg=COLORS['success'],
            bg=COLORS['panel'],
            font=('Segoe UI', 9)
        )
        self.indicators['voice'].pack(side='left', padx=10)
        
        # Time
        self.time_label = tk.Label(
            self,
            text='',
            fg=COLORS['text_secondary'],
            bg=COLORS['panel'],
            font=('Segoe UI', 9)
        )
        self.time_label.pack(side='right', padx=10)
        
        # Update time
        self._update_time()
    
    def _update_time(self):
        current_time = datetime.now().strftime('%H:%M:%S')
        self.time_label.configure(text=current_time)
        self.after(1000, self._update_time)
    
    def update_status(self, key: str, text: str, color: str = None):
        if key in self.indicators:
            if color:
                self.indicators[key].configure(fg=color)
            self.indicators[key].configure(text=f'● {text}')


class ChatPanel(tk.Frame):
    """Chat panel with message history and input."""
    
    def __init__(self, master, on_send=None, **kwargs):
        super().__init__(master, bg=COLORS['bg'], **kwargs)
        
        self.on_send = on_send
        
        # Header
        header = tk.Frame(self, bg=COLORS['bg_secondary'], height=50)
        header.pack(fill='x')
        header.pack_propagate(False)
        
        tk.Label(
            header,
            text='💬 Chat',
            fg=COLORS['accent'],
            bg=COLORS['bg_secondary'],
            font=('Segoe UI', 14, 'bold')
        ).pack(side='left', padx=15)
        
        # Chat history
        self.chat_history = scrolledtext.ScrolledText(
            self,
            bg=COLORS['bg'],
            fg=COLORS['text'],
            insertbackground=COLORS['accent'],
            relief='flat',
            wrap='word',
            font=('Segoe UI', 11),
            state='disabled'
        )
        self.chat_history.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Configure tags
        self.chat_history.tag_config('user', foreground=COLORS['accent_light'])
        self.chat_history.tag_config('jarvis', foreground=COLORS['accent'])
        self.chat_history.tag_config('system', foreground=COLORS['text_muted'])
        self.chat_history.tag_config('error', foreground=COLORS['error'])
        
        # Input area
        input_frame = tk.Frame(self, bg=COLORS['bg'])
        input_frame.pack(fill='x', padx=10, pady=(0, 10))
        
        self.input_entry = ModernEntry(
            input_frame,
            placeholder='Type a message...',
            fg=COLORS['text']
        )
        self.input_entry.pack(side='left', fill='x', expand=True, ipady=8, padx=(0, 10))
        self.input_entry.bind('<Return>', lambda e: self._send_message())
        
        # Send button
        send_btn = ModernButton(
            input_frame,
            text='Send',
            bg=COLORS['button_bg'],
            fg=COLORS['button_text'],
            activebackground=COLORS['button_hover'],
            command=self._send_message,
            width=8
        )
        send_btn.pack(side='right', ipady=5)
        
        # Voice button
        voice_btn = ModernButton(
            input_frame,
            text='🎤',
            bg=COLORS['bg_tertiary'],
            fg=COLORS['text'],
            activebackground=COLORS['panel_border'],
            command=self._voice_input,
            width=3
        )
        voice_btn.pack(side='right', padx=(0, 5), ipady=5)
    
    def _send_message(self):
        message = self.input_entry.get().strip()
        if message and message != self.input_entry.placeholder:
            self.add_message('You', message, 'user')
            self.input_entry.delete(0, tk.END)
            
            if self.on_send:
                threading.Thread(target=self.on_send, args=(message,), daemon=True).start()
    
    def _voice_input(self):
        self.add_message('System', 'Listening...', 'system')
        # Voice input will be handled by the main application
    
    def add_message(self, sender: str, message: str, tag: str = 'jarvis'):
        self.chat_history.configure(state='normal')
        self.chat_history.insert('end', f'{sender}: ', tag)
        self.chat_history.insert('end', f'{message}\n\n')
        self.chat_history.see('end')
        self.chat_history.configure(state='disabled')


class ModePanel(tk.Frame):
    """Panel for selecting different modes."""
    
    def __init__(self, master, on_mode_select=None, **kwargs):
        super().__init__(master, bg=COLORS['bg_secondary'], **kwargs)
        
        self.on_mode_select = on_mode_select
        self.selected_mode = None
        
        # Header
        tk.Label(
            self,
            text='🎮 Modes',
            fg=COLORS['accent'],
            bg=COLORS['bg_secondary'],
            font=('Segoe UI', 12, 'bold')
        ).pack(anchor='w', padx=15, pady=(15, 10))
        
        # Mode buttons
        modes = [
            ('🔬 Research', 'research', 'Automated topic research'),
            ('🎮 Roblox Grind', 'roblox', 'Automated Roblox grinding'),
            ('💼 Serious Mode', 'serious', 'Productivity workspaces'),
            ('🎤 Voice Only', 'voice', 'Voice-only mode'),
        ]
        
        for name, mode_id, description in modes:
            self._create_mode_button(name, mode_id, description)
    
    def _create_mode_button(self, name: str, mode_id: str, description: str):
        frame = tk.Frame(self, bg=COLORS['bg_tertiary'], cursor='hand2')
        frame.pack(fill='x', padx=15, pady=5)
        
        # Mode name
        tk.Label(
            frame,
            text=name,
            fg=COLORS['text'],
            bg=COLORS['bg_tertiary'],
            font=('Segoe UI', 10, 'bold')
        ).pack(anchor='w', padx=10, pady=(10, 2))
        
        # Description
        tk.Label(
            frame,
            text=description,
            fg=COLORS['text_muted'],
            bg=COLORS['bg_tertiary'],
            font=('Segoe UI', 9)
        ).pack(anchor='w', padx=10, pady=(0, 10))
        
        # Bind click
        frame.bind('<Button-1>', lambda e, m=mode_id: self._select_mode(m))
        for child in frame.winfo_children():
            child.bind('<Button-1>', lambda e, m=mode_id: self._select_mode(m))
    
    def _select_mode(self, mode_id: str):
        self.selected_mode = mode_id
        if self.on_mode_select:
            self.on_mode_select(mode_id)


class SystemPanel(tk.Frame):
    """Panel showing system information."""
    
    def __init__(self, master, **kwargs):
        super().__init__(master, bg=COLORS['bg_secondary'], **kwargs)
        
        # Header
        tk.Label(
            self,
            text='📊 System',
            fg=COLORS['accent'],
            bg=COLORS['bg_secondary'],
            font=('Segoe UI', 12, 'bold')
        ).pack(anchor='w', padx=15, pady=(15, 10))
        
        # System info
        self.info_labels = {}
        
        info_items = [
            ('cpu', 'CPU: ---%'),
            ('memory', 'Memory: ---%'),
            ('disk', 'Disk: ---%'),
            ('battery', 'Battery: ---%'),
        ]
        
        for key, text in info_items:
            frame = tk.Frame(self, bg=COLORS['bg_tertiary'])
            frame.pack(fill='x', padx=15, pady=3)
            
            label = tk.Label(
                frame,
                text=text,
                fg=COLORS['text'],
                bg=COLORS['bg_tertiary'],
                font=('Segoe UI', 10)
            )
            label.pack(anchor='w', padx=10, pady=8)
            
            self.info_labels[key] = label
        
        # Progress bars
        self.progress_bars = {}
        
        for key in ['cpu', 'memory', 'disk']:
            progress = ttk.Progressbar(
                self,
                length=200,
                mode='determinate',
                style='Custom.Horizontal.TProgressbar'
            )
            progress.pack(padx=15, pady=(0, 10))
            self.progress_bars[key] = progress
        
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        style.configure(
            'Custom.Horizontal.TProgressbar',
            background=COLORS['accent'],
            troughcolor=COLORS['bg_tertiary']
        )
    
    def update_stats(self, stats: dict):
        for key, value in stats.items():
            if key in self.info_labels:
                if value is not None:
                    self.info_labels[key].configure(text=f'{key.upper()}: {value:.0f}%')
                    if key in self.progress_bars:
                        self.progress_bars[key]['value'] = value
                else:
                    self.info_labels[key].configure(text=f'{key.upper()}: N/A')


class SettingsPanel(tk.Frame):
    """Settings panel for configuration."""
    
    def __init__(self, master, **kwargs):
        super().__init__(master, bg=COLORS['bg_secondary'], **kwargs)
        
        # Header
        tk.Label(
            self,
            text='⚙ Settings',
            fg=COLORS['accent'],
            bg=COLORS['bg_secondary'],
            font=('Segoe UI', 12, 'bold')
        ).pack(anchor='w', padx=15, pady=(15, 10))
        
        # Settings options
        settings = [
            ('Voice Profile', 'Dark Synthetic'),
            ('TTS Engine', 'Auto'),
            ('Speak Responses', 'Enabled'),
            ('Remember Conversations', 'Enabled'),
        ]
        
        for name, value in settings:
            frame = tk.Frame(self, bg=COLORS['bg_tertiary'])
            frame.pack(fill='x', padx=15, pady=3)
            
            tk.Label(
                frame,
                text=name,
                fg=COLORS['text'],
                bg=COLORS['bg_tertiary'],
                font=('Segoe UI', 10)
            ).pack(side='left', padx=10, pady=8)
            
            tk.Label(
                frame,
                text=value,
                fg=COLORS['text_muted'],
                bg=COLORS['bg_tertiary'],
                font=('Segoe UI', 10)
            ).pack(side='right', padx=10, pady=8)
        
        # API Status
        tk.Label(
            self,
            text='🔑 API Status',
            fg=COLORS['accent'],
            bg=COLORS['bg_secondary'],
            font=('Segoe UI', 12, 'bold')
        ).pack(anchor='w', padx=15, pady=(20, 10))
        
        apis = [
            ('Groq AI', 'Not configured'),
            ('Email', 'Not configured'),
            ('Spotify', 'Not configured'),
        ]
        
        for name, status in apis:
            frame = tk.Frame(self, bg=COLORS['bg_tertiary'])
            frame.pack(fill='x', padx=15, pady=3)
            
            tk.Label(
                frame,
                text=name,
                fg=COLORS['text'],
                bg=COLORS['bg_tertiary'],
                font=('Segoe UI', 10)
            ).pack(side='left', padx=10, pady=8)
            
            color = COLORS['success'] if status == 'Connected' else COLORS['text_muted']
            tk.Label(
                frame,
                text=status,
                fg=color,
                bg=COLORS['bg_tertiary'],
                font=('Segoe UI', 10)
            ).pack(side='right', padx=10, pady=8)


class ModernJarvisUI:
    """Main modern UI for Jarvis V2."""
    
    def __init__(self, jarvis=None):
        self.jarvis = jarvis
        
        # Create main window
        self.root = tk.Tk()
        self.root.title('Jarvis V2 - AI Assistant')
        self.root.geometry('1200x800')
        self.root.configure(bg=COLORS['bg'])
        self.root.minsize(1000, 600)
        
        # Center window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (1200 // 2)
        y = (self.root.winfo_screenheight() // 2) - (800 // 2)
        self.root.geometry(f'+{x}+{y}')
        
        # Build UI
        self._build_header()
        self._build_main_content()
        self._build_status_bar()
        
        # Initialize
        self._update_system_stats()
    
    def _build_header(self):
        """Build the header bar."""
        header = tk.Frame(self.root, bg=COLORS['bg_secondary'], height=60)
        header.pack(fill='x')
        header.pack_propagate(False)
        
        # Logo
        logo_frame = tk.Frame(header, bg=COLORS['accent'], width=40, height=40)
        logo_frame.pack(side='left', padx=15, pady=10)
        logo_frame.pack_propagate(False)
        
        tk.Label(
            logo_frame,
            text='J',
            fg=COLORS['bg'],
            bg=COLORS['accent'],
            font=('Segoe UI', 20, 'bold')
        ).pack(expand=True)
        
        # Title
        tk.Label(
            header,
            text='J.A.R.V.I.S V2',
            fg=COLORS['accent'],
            bg=COLORS['bg_secondary'],
            font=('Segoe UI', 16, 'bold')
        ).pack(side='left', padx=10)
        
        # Navigation buttons
        nav_frame = tk.Frame(header, bg=COLORS['bg_secondary'])
        nav_frame.pack(side='left', padx=20)
        
        nav_buttons = [
            ('💬 Chat', 'chat'),
            ('📊 Dashboard', 'dashboard'),
            ('⚙ Settings', 'settings'),
        ]
        
        for text, view in nav_buttons:
            btn = tk.Button(
                nav_frame,
                text=text,
                fg=COLORS['text'],
                bg=COLORS['bg_secondary'],
                activebackground=COLORS['bg_tertiary'],
                relief='flat',
                font=('Segoe UI', 10),
                cursor='hand2',
                command=lambda v=view: self._switch_view(v)
            )
            btn.pack(side='left', padx=5)
        
        # User info
        user_frame = tk.Frame(header, bg=COLORS['bg_secondary'])
        user_frame.pack(side='right', padx=15)
        
        tk.Label(
            user_frame,
            text='👤 User',
            fg=COLORS['text_secondary'],
            bg=COLORS['bg_secondary'],
            font=('Segoe UI', 10)
        ).pack(side='left')
    
    def _build_main_content(self):
        """Build the main content area."""
        # Main container
        self.main_container = tk.Frame(self.root, bg=COLORS['bg'])
        self.main_container.pack(fill='both', expand=True)
        
        # Left sidebar
        self.sidebar = tk.Frame(self.main_container, bg=COLORS['bg_secondary'], width=250)
        self.sidebar.pack(side='left', fill='y')
        self.sidebar.pack_propagate(False)
        
        # Mode panel
        self.mode_panel = ModePanel(self.sidebar, on_mode_select=self._on_mode_select)
        self.mode_panel.pack(fill='x', pady=(0, 10))
        
        # System panel
        self.system_panel = SystemPanel(self.sidebar)
        self.system_panel.pack(fill='x', pady=(0, 10))
        
        # Settings panel
        self.settings_panel = SettingsPanel(self.sidebar)
        self.settings_panel.pack(fill='x', pady=(0, 10))
        
        # Right content area
        self.content_area = tk.Frame(self.main_container, bg=COLORS['bg'])
        self.content_area.pack(side='right', fill='both', expand=True)
        
        # Chat panel (default view)
        self.chat_panel = ChatPanel(self.content_area, on_send=self._on_send_message)
        self.chat_panel.pack(fill='both', expand=True)
        
        # Welcome message
        self.chat_panel.add_message(
            'Jarvis',
            'Welcome to Jarvis V2! How can I assist you today?',
            'jarvis'
        )
    
    def _build_status_bar(self):
        """Build the status bar."""
        self.status_bar = StatusBar(self.root)
        self.status_bar.pack(side='bottom', fill='x')
    
    def _switch_view(self, view: str):
        """Switch between different views."""
        # This would switch between chat, dashboard, settings views
        pass
    
    def _on_mode_select(self, mode: str):
        """Handle mode selection."""
        mode_messages = {
            'research': 'Research mode activated. What topic would you like to research?',
            'roblox': 'Roblox Grind mode activated. Which game would you like to play?',
            'serious': 'Serious Mode activated. Which workspace would you like to open?',
            'voice': 'Voice-only mode activated. Listening for commands...',
        }
        
        if mode in mode_messages:
            self.chat_panel.add_message('System', mode_messages[mode], 'system')
    
    def _on_send_message(self, message: str):
        """Handle sent messages."""
        if self.jarvis:
            result = self.jarvis.process_command(message, speak=False)
            self.root.after(0, lambda: self.chat_panel.add_message(
                'Jarvis', result.text, 'jarvis'
            ))
        else:
            # Demo response
            self.root.after(500, lambda: self.chat_panel.add_message(
                'Jarvis',
                f'I received your message: "{message}". Jarvis V2 is ready to assist!',
                'jarvis'
            ))
    
    def _update_system_stats(self):
        """Update system statistics."""
        try:
            import psutil
            
            stats = {
                'cpu': psutil.cpu_percent(),
                'memory': psutil.virtual_memory().percent,
                'disk': psutil.disk_usage('/').percent,
            }
            
            battery = psutil.sensors_battery()
            if battery:
                stats['battery'] = battery.percent
            
            self.system_panel.update_stats(stats)
            
            # Update status bar
            self.status_bar.update_status('ai', 'AI: Online', COLORS['success'])
            self.status_bar.update_status('voice', 'Voice: Ready', COLORS['success'])
            
        except ImportError:
            pass
        
        # Update every 2 seconds
        self.root.after(2000, self._update_system_stats)
    
    def run(self):
        """Run the application."""
        self.root.mainloop()


def create_modern_ui(jarvis=None):
    """Create and run the modern UI."""
    ui = ModernJarvisUI(jarvis)
    ui.run()


if __name__ == '__main__':
    create_modern_ui()
