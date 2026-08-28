"""System control commands."""

from __future__ import annotations

import os
import platform
import random
import re
import subprocess
from typing import Any

from utils.helpers import human_bytes

try:
    import psutil  # type: ignore
except Exception:  # pragma: no cover
    psutil = None  # type: ignore

BUILTIN_JOKES = [
    "Why do programmers prefer dark mode? Because light attracts bugs, sir.",
    "I told my computer I needed a break, and it said no problem, I will go to sleep.",
    "Why did the developer go broke? Because he used up all his cache, sir.",
    "There are only two hard things in computing: cache invalidation, naming things, and off-by-one errors.",
    "I would tell you a UDP joke, but you might not get it, sir.",
    "Why was the JavaScript developer sad? Because he did not node how to express himself.",
    "A byte walked into a bar and ordered a bit. The bartender said, sorry, we do not serve halves.",
]


class SystemController:
    """Handle local system status and controls."""

    def __init__(self, config: Any) -> None:
        self.config = config

    def tell_joke(self) -> str:
        """Tell a joke via pyjokes when installed, with built-in fallbacks."""
        try:
            import pyjokes  # type: ignore

            return pyjokes.get_joke()
        except Exception:
            return random.choice(BUILTIN_JOKES)

    def status(self) -> dict[str, Any]:
        if not psutil:
            return {"platform": platform.platform(), "psutil": False}
        cpu = psutil.cpu_percent(interval=0.1)
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage("/")
        battery = psutil.sensors_battery() if hasattr(psutil, "sensors_battery") else None
        return {
            "platform": platform.platform(),
            "cpu_percent": cpu,
            "memory_percent": mem.percent,
            "memory_used": human_bytes(mem.used),
            "memory_total": human_bytes(mem.total),
            "disk_percent": disk.percent,
            "disk_free": human_bytes(disk.free),
            "battery_percent": battery.percent if battery else None,
            "power_plugged": battery.power_plugged if battery else None,
        }

    def describe_status(self) -> str:
        status = self.status()
        if not status.get("psutil", True):
            return f"System platform is {status['platform']}. Detailed metrics require psutil, sir."
        battery = ""
        if status.get("battery_percent") is not None:
            battery = f" Battery is at {status['battery_percent']} percent."
        return (
            f"CPU is at {status['cpu_percent']} percent, memory at {status['memory_percent']} percent, "
            f"and disk usage at {status['disk_percent']} percent.{battery}"
        )

    def _run_power_command(self, action: str) -> str:
        confirm = self.config.get("behavior.confirm_dangerous_actions", True)
        if confirm:
            return (
                f"{action.title()} is a dangerous power action. For safety, disable "
                "behavior.confirm_dangerous_actions in config or use your operating system confirmation."
            )
        system = platform.system()
        commands = {
            "shutdown": {
                "Windows": ["shutdown", "/s", "/t", "5"],
                "Linux": ["shutdown", "-h", "+1"],
                "Darwin": ["osascript", "-e", 'tell app "System Events" to shut down'],
            },
            "restart": {
                "Windows": ["shutdown", "/r", "/t", "5"],
                "Linux": ["shutdown", "-r", "+1"],
                "Darwin": ["osascript", "-e", 'tell app "System Events" to restart'],
            },
            "sleep": {
                "Windows": ["rundll32.exe", "powrprof.dll,SetSuspendState", "0,1,0"],
                "Linux": ["systemctl", "suspend"],
                "Darwin": ["pmset", "sleepnow"],
            },
        }
        cmd = commands[action].get(system)
        if not cmd:
            return f"{action.title()} is not supported on {system}, sir."
        subprocess.Popen(cmd)
        return f"Initiating {action}, sir."

    def set_volume(self, percent: int) -> str:
        percent = max(0, min(100, int(percent)))
        system = platform.system()
        try:
            if system == "Windows":
                # Uses simulated media keys as a no-extra-dependency fallback.
                import pyautogui  # type: ignore

                pyautogui.press("volumedown", presses=50)
                pyautogui.press("volumeup", presses=max(0, percent // 2))
            elif system == "Darwin":
                subprocess.run(
                    ["osascript", "-e", f"set volume output volume {percent}"], check=False
                )
            elif system == "Linux":
                subprocess.run(["amixer", "set", "Master", f"{percent}%"], check=False)
            return f"Volume set to {percent} percent, sir."
        except Exception:
            return "I could not adjust system volume on this machine, sir."

    def mute(self) -> str:
        try:
            system = platform.system()
            if system == "Windows":
                import pyautogui  # type: ignore

                pyautogui.press("volumemute")
            elif system == "Darwin":
                subprocess.run(["osascript", "-e", "set volume with output muted"], check=False)
            elif system == "Linux":
                subprocess.run(["amixer", "set", "Master", "toggle"], check=False)
            return "Audio mute toggled, sir."
        except Exception:
            return "I could not toggle mute, sir."

    def lock_screen(self) -> str:
        try:
            system = platform.system()
            if system == "Windows":
                subprocess.Popen(["rundll32.exe", "user32.dll,LockWorkStation"])
            elif system == "Darwin":
                subprocess.Popen(
                    ["/System/Library/CoreServices/Menu Extras/User.menu/Contents/Resources/CGSession", "-suspend"]
                )
            elif system == "Linux":
                subprocess.Popen(["loginctl", "lock-session"])
            return "Locking the workstation, sir."
        except Exception:
            return "I could not lock this workstation, sir."

    def process(self, command: str) -> dict[str, Any]:
        lower = command.lower()
        if "joke" in lower:
            return {"success": True, "response": self.tell_joke()}
        if any(term in lower for term in ["system status", "how's the system", "cpu", "battery", "memory"]):
            return {"success": True, "response": self.describe_status(), "data": self.status()}
        volume_match = re.search(r"volume (?:to )?(\d+)", lower)
        if volume_match:
            return {"success": True, "response": self.set_volume(int(volume_match.group(1)))}
        if "mute" in lower:
            return {"success": True, "response": self.mute()}
        if "lock" in lower and ("screen" in lower or "computer" in lower or "pc" in lower):
            return {"success": True, "response": self.lock_screen()}
        for action in ["shutdown", "restart", "sleep"]:
            if action in lower or (action == "shutdown" and "turn off" in lower):
                return {"success": True, "response": self._run_power_command(action)}
        return {"success": False, "response": "I did not find a system command, sir."}
