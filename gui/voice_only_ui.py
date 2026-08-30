"""
Jarvis V2 - Voice-Only 3D Interface
=====================================
A futuristic voice-only AI interface with:
- Central 3D holographic display
- Right-side project listings
- Voice-only interaction
- Animated visual effects
"""

from __future__ import annotations

import math
import tkinter as tk
from tkinter import ttk
import threading
import time
import random
from datetime import datetime
from typing import Any, Optional, List, Dict

# Color scheme - Futuristic Dark Theme
COLORS = {
    'bg': '#000000',
    'bg_secondary': '#0a0a0a',
    'accent': '#00d4ff',  # Cyan/Blue accent
    'accent_secondary': '#0099cc',
    'accent_glow': '#00ffff',
    'text': '#ffffff',
    'text_secondary': '#888888',
    'text_muted': '#444444',
    'success': '#00ff88',
    'warning': '#ffaa00',
    'error': '#ff4444',
    'hologram': '#00d4ff',
    'hologram_dim': '#003344',
    'grid': '#111111',
    'particle': '#00d4ff',
}


class Particle:
    """Represents a floating particle in the 3D space."""
    
    def __init__(self, canvas: tk.Canvas, x: float, y: float, size: float = 2):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.size = size
        self.speed_x = random.uniform(-0.5, 0.5)
        self.speed_y = random.uniform(-0.5, 0.5)
        self.life = random.uniform(100, 300)
        self.max_life = self.life
        self.id = None
    
    def update(self):
        """Update particle position and life."""
        self.x += self.speed_x
        self.y += self.speed_y
        self.life -= 1
        
        # Wrap around screen
        if self.x < 0:
            self.x = self.canvas.winfo_width()
        elif self.x > self.canvas.winfo_width():
            self.x = 0
        if self.y < 0:
            self.y = self.canvas.winfo_height()
        elif self.y > self.canvas.winfo_height():
            self.y = 0
        
        return self.life > 0
    
    def draw(self):
        """Draw the particle."""
        if self.id:
            self.canvas.delete(self.id)
        
        alpha = int(255 * (self.life / self.max_life))
        color = f'#{0:02x}{alpha:02x}{alpha:02x}'
        
        self.id = self.canvas.create_oval(
            self.x - self.size, self.y - self.size,
            self.x + self.size, self.y + self.size,
            fill=color, outline=''
        )


class HolographicDisplay:
    """Central 3D holographic display with animations."""
    
    def __init__(self, canvas: tk.Canvas, width: int, height: int):
        self.canvas = canvas
        self.width = width
        self.height = height
        self.center_x = width // 2
        self.center_y = height // 2
        
        # Animation state
        self.angle = 0
        self.pulse = 0
        self.pulse_direction = 1
        self.particles: List[Particle] = []
        self.rings = []
        self.scan_beams = []
        
        # Initialize particles
        for _ in range(50):
            x = random.randint(0, width)
            y = random.randint(0, height)
            self.particles.append(Particle(canvas, x, y, random.uniform(1, 3)))
        
        # Initialize rings
        for i in range(4):
            self.rings.append({
                'radius': 80 + i * 40,
                'speed': 0.5 + i * 0.2,
                'angle': i * 45,
                'direction': 1 if i % 2 == 0 else -1
            })
        
        # Initialize scan beams
        for i in range(8):
            self.scan_beams.append({
                'angle': i * 45,
                'speed': 1 + random.uniform(0, 0.5)
            })
    
    def update(self):
        """Update all animations."""
        self.angle += 0.5
        self.pulse += 0.02 * self.pulse_direction
        
        if self.pulse > 1:
            self.pulse_direction = -1
        elif self.pulse < 0:
            self.pulse_direction = 1
        
        # Update particles
        self.particles = [p for p in self.particles if p.update()]
        
        # Add new particles
        while len(self.particles) < 50:
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            self.particles.append(Particle(self.canvas, x, y, random.uniform(1, 3)))
        
        # Update rings
        for ring in self.rings:
            ring['angle'] += ring['speed'] * ring['direction']
        
        # Update scan beams
        for beam in self.scan_beams:
            beam['angle'] += beam['speed']
    
    def draw(self):
        """Draw the holographic display."""
        # Clear canvas
        self.canvas.delete('all')
        
        # Draw grid background
        self._draw_grid()
        
        # Draw particles
        for particle in self.particles:
            particle.draw()
        
        # Draw outer glow
        self._draw_outer_glow()
        
        # Draw rings
        self._draw_rings()
        
        # Draw scan beams
        self._draw_scan_beams()
        
        # Draw center core
        self._draw_center_core()
        
        # Draw status text
        self._draw_status_text()
    
    def _draw_grid(self):
        """Draw background grid."""
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        
        # Vertical lines
        for x in range(0, width, 50):
            self.canvas.create_line(x, 0, x, height, fill=COLORS['grid'], width=1)
        
        # Horizontal lines
        for y in range(0, height, 50):
            self.canvas.create_line(0, y, width, y, fill=COLORS['grid'], width=1)
    
    def _draw_outer_glow(self):
        """Draw outer glow effect."""
        pulse_size = 200 + self.pulse * 20
        
        # Outer glow layers
        for i in range(3):
            size = pulse_size + i * 30
            alpha = 50 - i * 15
            color = f'#{0:02x}{alpha:02x}{alpha:02x}'
            
            self.canvas.create_oval(
                self.center_x - size, self.center_y - size,
                self.center_x + size, self.center_y + size,
                outline=color, width=2
            )
    
    def _draw_rings(self):
        """Draw rotating rings."""
        for ring in self.rings:
            radius = ring['radius']
            angle = ring['angle']
            
            # Calculate ring points
            points = []
            for i in range(0, 360, 10):
                rad = math.radians(i + angle)
                x = self.center_x + radius * math.cos(rad)
                y = self.center_y + radius * math.sin(rad)
                points.extend([x, y])
            
            # Draw ring
            if len(points) >= 4:
                self.canvas.create_line(
                    points, fill=COLORS['hologram'], width=2, smooth=True
                )
    
    def _draw_scan_beams(self):
        """Draw scanning beams."""
        for beam in self.scan_beams:
            angle = beam['angle']
            rad = math.radians(angle)
            
            # Calculate beam endpoint
            length = 150 + self.pulse * 30
            end_x = self.center_x + length * math.cos(rad)
            end_y = self.center_y + length * math.sin(rad)
            
            # Draw beam
            self.canvas.create_line(
                self.center_x, self.center_y, end_x, end_y,
                fill=COLORS['accent'], width=1, dash=(4, 4)
            )
    
    def _draw_center_core(self):
        """Draw the central core."""
        # Core glow
        core_size = 40 + self.pulse * 10
        
        # Outer core
        self.canvas.create_oval(
            self.center_x - core_size, self.center_y - core_size,
            self.center_x + core_size, self.center_y + core_size,
            fill=COLORS['hologram_dim'], outline=COLORS['accent'], width=2
        )
        
        # Inner core
        inner_size = 20 + self.pulse * 5
        self.canvas.create_oval(
            self.center_x - inner_size, self.center_y - inner_size,
            self.center_x + inner_size, self.center_y + inner_size,
            fill=COLORS['accent'], outline=''
        )
        
        # Core text
        self.canvas.create_text(
            self.center_x, self.center_y,
            text='J', fill=COLORS['text'], font=('Segoe UI', 24, 'bold')
        )
    
    def _draw_status_text(self):
        """Draw status text around the display."""
        # Top status
        self.canvas.create_text(
            self.center_x, 30,
            text='J.A.R.V.I.S V2 - VOICE MODE',
            fill=COLORS['accent'], font=('Segoe UI', 14, 'bold')
        )
        
        # Bottom status
        status = 'LISTENING...' if self.pulse > 0.5 else 'STANDBY'
        self.canvas.create_text(
            self.center_x, self.height - 30,
            text=status,
            fill=COLORS['text_secondary'], font=('Segoe UI', 10)
        )
        
        # Side indicators
        indicators = [
            ('AI: ONLINE', 50, COLORS['success']),
            ('VOICE: ACTIVE', 70, COLORS['accent']),
            ('MEMORY: OK', 90, COLORS['success']),
        ]
        
        for text, y, color in indicators:
            self.canvas.create_text(
                20, y, text=text, fill=color,
                font=('Consolas', 9), anchor='w'
            )


class ProjectListing:
    """Represents a 3D project listing item."""
    
    def __init__(self, name: str, description: str, status: str = 'active'):
        self.name = name
        self.description = description
        self.status = status
        self.hover = False


class ProjectPanel:
    """Right-side panel showing 3D project listings."""
    
    def __init__(self, parent: tk.Frame):
        self.parent = parent
        self.projects: List[ProjectListing] = []
        self.selected_project = None
        
        # Sample projects
        self._load_sample_projects()
        
        # Build UI
        self._build_ui()
    
    def _load_sample_projects(self):
        """Load sample projects."""
        self.projects = [
            ProjectListing('Research AI', 'Machine Learning Research', 'active'),
            ProjectListing('Roblox Grind', 'Automated Gaming Session', 'idle'),
            ProjectListing('Study Mode', 'Productivity Workspace', 'active'),
            ProjectListing('Web Scraper', 'Data Collection Tool', 'idle'),
            ProjectListing('Voice Assistant', 'Natural Language Processing', 'active'),
            ProjectListing('Home Automation', 'Smart Home Control', 'idle'),
            ProjectListing('Music Player', 'Spotify Integration', 'active'),
            ProjectListing('Email Manager', 'Automated Email Processing', 'idle'),
        ]
    
    def _build_ui(self):
        """Build the project panel UI."""
        # Header
        header = tk.Frame(self.parent, bg=COLORS['bg_secondary'])
        header.pack(fill='x', padx=10, pady=(10, 5))
        
        tk.Label(
            header,
            text='📁 PROJECTS',
            fg=COLORS['accent'],
            bg=COLORS['bg_secondary'],
            font=('Segoe UI', 12, 'bold')
        ).pack(anchor='w', padx=10, pady=10)
        
        # Project list
        self.list_frame = tk.Frame(self.parent, bg=COLORS['bg'])
        self.list_frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(self.list_frame)
        scrollbar.pack(side='right', fill='y')
        
        # Canvas for project items
        self.canvas = tk.Canvas(
            self.list_frame,
            bg=COLORS['bg'],
            highlightthickness=0,
            yscrollcommand=scrollbar.set
        )
        self.canvas.pack(fill='both', expand=True)
        scrollbar.config(command=self.canvas.yview)
        
        # Draw projects
        self._draw_projects()
    
    def _draw_projects(self):
        """Draw project items."""
        self.canvas.delete('all')
        
        y = 10
        for i, project in enumerate(self.projects):
            self._draw_project_item(project, y, i)
            y += 80
    
    def _draw_project_item(self, project: ProjectListing, y: int, index: int):
        """Draw a single project item."""
        # Background
        bg_color = COLORS['bg_secondary'] if index % 2 == 0 else COLORS['bg']
        
        # Status color
        if project.status == 'active':
            status_color = COLORS['success']
        elif project.status == 'idle':
            status_color = COLORS['text_muted']
        else:
            status_color = COLORS['warning']
        
        # Draw background
        self.canvas.create_rectangle(
            10, y, 230, y + 70,
            fill=bg_color, outline=COLORS['grid']
        )
        
        # Draw status indicator
        self.canvas.create_oval(
            20, y + 25, 30, y + 35,
            fill=status_color, outline=''
        )
        
        # Draw project name
        self.canvas.create_text(
            40, y + 20,
            text=project.name,
            fill=COLORS['text'],
            font=('Segoe UI', 10, 'bold'),
            anchor='w'
        )
        
        # Draw description
        self.canvas.create_text(
            40, y + 45,
            text=project.description,
            fill=COLORS['text_secondary'],
            font=('Segoe UI', 8),
            anchor='w'
        )
        
        # Draw status text
        self.canvas.create_text(
            220, y + 30,
            text=project.status.upper(),
            fill=status_color,
            font=('Consolas', 8),
            anchor='e'
        )
        
        # Bind click
        self.canvas.tag_bind(
            self.canvas.create_rectangle(10, y, 230, y + 70, fill='', outline=''),
            '<Button-1>',
            lambda e, p=project: self._select_project(p)
        )
    
    def _select_project(self, project: ProjectListing):
        """Select a project."""
        self.selected_project = project
        # Trigger project selection callback
        print(f"Selected project: {project.name}")


class VoiceVisualizer:
    """Voice input visualizer."""
    
    def __init__(self, canvas: tk.Canvas, x: int, y: int, width: int, height: int):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        
        # Audio levels (simulated)
        self.levels = [0] * 20
        self.target_levels = [0] * 20
        self.is_listening = False
    
    def update(self):
        """Update voice visualization."""
        if self.is_listening:
            # Generate random audio levels
            for i in range(len(self.target_levels)):
                self.target_levels[i] = random.uniform(0.3, 1.0)
        else:
            # Set to zero
            for i in range(len(self.target_levels)):
                self.target_levels[i] = 0
        
        # Smooth transition
        for i in range(len(self.levels)):
            self.levels[i] += (self.target_levels[i] - self.levels[i]) * 0.3
    
    def draw(self):
        """Draw voice visualization."""
        bar_width = self.width // len(self.levels)
        
        for i, level in enumerate(self.levels):
            x = self.x + i * bar_width
            bar_height = int(level * self.height)
            
            # Color based on level
            if level > 0.7:
                color = COLORS['accent']
            elif level > 0.3:
                color = COLORS['accent_secondary']
            else:
                color = COLORS['hologram_dim']
            
            # Draw bar
            self.canvas.create_rectangle(
                x, self.y + self.height - bar_height,
                x + bar_width - 2, self.y + self.height,
                fill=color, outline=''
            )


class VoiceOnlyUI:
    """Main voice-only 3D interface."""
    
    def __init__(self, jarvis=None):
        self.jarvis = jarvis
        
        # Create main window
        self.root = tk.Tk()
        self.root.title('Jarvis V2 - Voice AI')
        self.root.geometry('1400x900')
        self.root.configure(bg=COLORS['bg'])
        self.root.minsize(1200, 700)
        
        # Center window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (1400 // 2)
        y = (self.root.winfo_screenheight() // 2) - (900 // 2)
        self.root.geometry(f'+{x}+{y}')
        
        # Build UI
        self._build_header()
        self._build_main_content()
        self._build_footer()
        
        # Initialize components
        self.holographic_display = None
        self.voice_visualizer = None
        self.project_panel = None
        
        # Animation state
        self.is_listening = False
        self.animation_running = True
        
        # Start animation loop
        self._animate()
    
    def _build_header(self):
        """Build the header."""
        header = tk.Frame(self.root, bg=COLORS['bg_secondary'], height=50)
        header.pack(fill='x')
        header.pack_propagate(False)
        
        # Logo
        logo_frame = tk.Frame(header, bg=COLORS['accent'], width=35, height=35)
        logo_frame.pack(side='left', padx=15, pady=7)
        logo_frame.pack_propagate(False)
        
        tk.Label(
            logo_frame,
            text='J',
            fg=COLORS['bg'],
            bg=COLORS['accent'],
            font=('Segoe UI', 18, 'bold')
        ).pack(expand=True)
        
        # Title
        tk.Label(
            header,
            text='J.A.R.V.I.S V2',
            fg=COLORS['accent'],
            bg=COLORS['bg_secondary'],
            font=('Segoe UI', 14, 'bold')
        ).pack(side='left', padx=10)
        
        # Subtitle
        tk.Label(
            header,
            text='VOICE AI ASSISTANT',
            fg=COLORS['text_secondary'],
            bg=COLORS['bg_secondary'],
            font=('Segoe UI', 10)
        ).pack(side='left', padx=10)
        
        # Status indicators
        status_frame = tk.Frame(header, bg=COLORS['bg_secondary'])
        status_frame.pack(side='right', padx=15)
        
        self.status_indicators = {}
        
        indicators = [
            ('ai', 'AI: ONLINE', COLORS['success']),
            ('voice', 'VOICE: READY', COLORS['accent']),
            ('memory', 'MEMORY: OK', COLORS['success']),
        ]
        
        for key, text, color in indicators:
            label = tk.Label(
                status_frame,
                text=f'● {text}',
                fg=color,
                bg=COLORS['bg_secondary'],
                font=('Consolas', 9)
            )
            label.pack(side='left', padx=10)
            self.status_indicators[key] = label
    
    def _build_main_content(self):
        """Build the main content area."""
        # Main container
        main_container = tk.Frame(self.root, bg=COLORS['bg'])
        main_container.pack(fill='both', expand=True)
        
        # Left panel - Holographic display
        left_panel = tk.Frame(main_container, bg=COLORS['bg'])
        left_panel.pack(side='left', fill='both', expand=True)
        
        # Create canvas for holographic display
        self.holo_canvas = tk.Canvas(
            left_panel,
            bg=COLORS['bg'],
            highlightthickness=0
        )
        self.holo_canvas.pack(fill='both', expand=True)
        
        # Initialize holographic display
        self.root.update_idletasks()
        width = self.holo_canvas.winfo_width()
        height = self.holo_canvas.winfo_height()
        
        if width > 0 and height > 0:
            self.holographic_display = HolographicDisplay(
                self.holo_canvas, width, height
            )
        
        # Right panel - Projects
        right_panel = tk.Frame(
            main_container,
            bg=COLORS['bg_secondary'],
            width=250
        )
        right_panel.pack(side='right', fill='y')
        right_panel.pack_propagate(False)
        
        # Initialize project panel
        self.project_panel = ProjectPanel(right_panel)
        
        # Voice visualizer at bottom of holographic display
        self.voice_canvas = tk.Canvas(
            left_panel,
            bg=COLORS['bg'],
            height=60,
            highlightthickness=0
        )
        self.voice_canvas.pack(fill='x', side='bottom')
        
        # Initialize voice visualizer
        self.voice_visualizer = VoiceVisualizer(
            self.voice_canvas, 50, 10, 300, 40
        )
    
    def _build_footer(self):
        """Build the footer."""
        footer = tk.Frame(self.root, bg=COLORS['bg_secondary'], height=40)
        footer.pack(fill='x', side='bottom')
        footer.pack_propagate(False)
        
        # Voice control button
        self.voice_btn = tk.Button(
            footer,
            text='🎤 START LISTENING',
            fg=COLORS['text'],
            bg=COLORS['accent'],
            activebackground=COLORS['accent_secondary'],
            font=('Segoe UI', 10, 'bold'),
            relief='flat',
            cursor='hand2',
            command=self._toggle_listening
        )
        self.voice_btn.pack(side='left', padx=15, pady=5, ipady=5)
        
        # Mode buttons
        modes = [
            ('🔬 Research', 'research'),
            ('🎮 Roblox', 'roblox'),
            ('💼 Serious', 'serious'),
        ]
        
        for text, mode in modes:
            btn = tk.Button(
                footer,
                text=text,
                fg=COLORS['text'],
                bg=COLORS['bg_secondary'],
                activebackground=COLORS['grid'],
                font=('Segoe UI', 9),
                relief='flat',
                cursor='hand2',
                command=lambda m=mode: self._activate_mode(m)
            )
            btn.pack(side='left', padx=5, pady=5, ipady=3)
        
        # Time display
        self.time_label = tk.Label(
            footer,
            text='',
            fg=COLORS['text_secondary'],
            bg=COLORS['bg_secondary'],
            font=('Consolas', 10)
        )
        self.time_label.pack(side='right', padx=15)
        
        # Update time
        self._update_time()
    
    def _animate(self):
        """Main animation loop."""
        if not self.animation_running:
            return
        
        # Update holographic display
        if self.holographic_display:
            self.holographic_display.update()
            self.holographic_display.draw()
        
        # Update voice visualizer
        if self.voice_visualizer:
            self.voice_visualizer.update()
            self.voice_visualizer.draw()
        
        # Schedule next frame
        self.root.after(33, self._animate)  # ~30 FPS
    
    def _update_time(self):
        """Update time display."""
        current_time = datetime.now().strftime('%H:%M:%S')
        self.time_label.configure(text=current_time)
        self.root.after(1000, self._update_time)
    
    def _toggle_listening(self):
        """Toggle voice listening."""
        self.is_listening = not self.is_listening
        
        if self.is_listening:
            self.voice_btn.configure(
                text='⏹ STOP LISTENING',
                bg=COLORS['error']
            )
            if self.voice_visualizer:
                self.voice_visualizer.is_listening = True
            
            # Update status
            self.status_indicators['voice'].configure(
                text='● VOICE: LISTENING',
                fg=COLORS['accent']
            )
        else:
            self.voice_btn.configure(
                text='🎤 START LISTENING',
                bg=COLORS['accent']
            )
            if self.voice_visualizer:
                self.voice_visualizer.is_listening = False
            
            # Update status
            self.status_indicators['voice'].configure(
                text='● VOICE: READY',
                fg=COLORS['accent']
            )
    
    def _activate_mode(self, mode: str):
        """Activate a specific mode."""
        mode_messages = {
            'research': 'Research mode activated. Speak your topic...',
            'roblox': 'Roblox Grind mode activated. Select a game...',
            'serious': 'Serious Mode activated. Choose a workspace...',
        }
        
        if mode in mode_messages:
            print(f"Mode activated: {mode}")
            # Here you would integrate with the actual mode controllers
    
    def run(self):
        """Run the application."""
        self.root.mainloop()
    
    def stop(self):
        """Stop the application."""
        self.animation_running = False
        self.root.destroy()


def create_voice_only_ui(jarvis=None):
    """Create and run the voice-only UI."""
    ui = VoiceOnlyUI(jarvis)
    ui.run()


if __name__ == '__main__':
    create_voice_only_ui()
