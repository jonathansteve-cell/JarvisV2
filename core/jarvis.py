"""Main J.A.R.V.I.S V2 orchestrator."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from core.config_manager import ConfigManager
from modules.application_manager import ApplicationManager
from modules.automation_controller import AutomationController
from modules.calendar_controller import CalendarController
from modules.email_controller import EmailController
from modules.file_manager import FileManager
from modules.memory_controller import MemoryController
from modules.phone_controller import PhoneController
from modules.power_controller import PowerController
from modules.productivity_controller import ProductivityController
from modules.screenshot_manager import ScreenshotManager
from modules.smart_home_controller import SmartHomeController
from modules.socialmedia_controller import SocialMediaController
from modules.spotify_controller import SpotifyController
from modules.system_controller import SystemController
from modules.web_controller import WebController
from modules.whatsapp_controller import WhatsAppController
from modules.window_manager import WindowManager
from modules.word_controller import WordController
from modules.zoom_controller import ZoomController
from personality.response_generator import ResponseGenerator
from utils.helpers import normalize_command, remove_wake_word
from voice.text_to_speech import TextToSpeech

logger = logging.getLogger(__name__)


@dataclass
class JarvisResponse:
    """A normalized result from Jarvis."""

    text: str
    success: bool = True
    intent: str = "unknown"
    data: dict[str, Any] | list[Any] | None = None
    provider: str = "local"
    spoken: bool = False
    debug: dict[str, Any] = field(default_factory=dict)


class Jarvis:
    """All-in-one assistant controller.

    The controller routes natural-language text from voice, GUI, or CLI into modules. Modules return
    plain text that can be spoken by the TTS engine. Secrets are read only from environment variables
    or local .env files and are never committed to the repository.
    """

    def __init__(self, config_path: str = "config/config.json", voice_output: bool | None = None) -> None:
        self.config = ConfigManager(config_path)
        if voice_output is not None:
            self.config.set("behavior.speak_responses", voice_output, save=False)

        self.memory = MemoryController(self.config)
        self.ai = ResponseGenerator(self.config, memory=self.memory)
        self.tts = TextToSpeech(self.config)
        self.automation = AutomationController(self.config)

        self.modules: list[tuple[str, Any, list[str]]] = [
            ("power", PowerController(self.config), ["wake", "turn on pc", "turn on computer"]),
            ("memory", self.memory, ["remember", "forget", "memory", "my name is", "call me", "i prefer", "i like"]),
            ("productivity", ProductivityController(self.config), ["remind", "note", "task", "timer"]),
            ("email", EmailController(self.config), ["email", "inbox"]),
            ("whatsapp", WhatsAppController(self.config), ["whatsapp"]),
            ("phone", PhoneController(self.config), ["call", "phone"]),
            ("spotify", SpotifyController(self.config), ["spotify", "play song", "pause music", "next song", "now playing"]),
            ("calendar", CalendarController(self.config), ["calendar", "schedule", "meeting"]),
            ("zoom", ZoomController(self.config), ["zoom", "join meeting", "video", "mute"]),
            ("word", WordController(self.config), ["word", "document"]),
            ("social", SocialMediaController(self.config), ["tweet", "twitter", "linkedin"]),
            ("smart_home", SmartHomeController(self.config), ["light", "thermostat", "door", "smart home"]),
            ("screenshot", ScreenshotManager(self.config), ["screenshot", "screen shot", "capture screen"]),
            ("system", SystemController(self.config), ["system", "cpu", "battery", "memory", "volume", "mute", "lock", "sleep", "shutdown", "restart"]),
            ("window", WindowManager(self.config), ["window", "maximize", "minimize", "tile", "snap"]),
            ("file", FileManager(self.config), ["folder", "file", "documents", "downloads", "desktop", "find", "locate"]),
            ("web", WebController(self.config), ["google", "search", "weather", "news", "wikipedia", "open youtube", "open github", "open gmail"]),
            ("application", ApplicationManager(self.config), ["open", "launch", "start", "run", "close", "quit", "running apps"]),
        ]

    def boot_message(self) -> str:
        return self.ai.greeting()

    def clean_command(self, command: str) -> str:
        wake_words = self.config.get("voice.wake_words", ["hey jarvis", "jarvis"])
        return remove_wake_word(command, wake_words).strip()

    def _should_try(self, normalized: str, keywords: list[str]) -> bool:
        return any(keyword in normalized for keyword in keywords)

    def _run_module(self, intent: str, module: Any, command: str) -> JarvisResponse | None:
        try:
            result = module.process(command)
        except Exception as exc:
            logger.exception("Module %s failed", intent)
            return JarvisResponse(text=f"The {intent} module encountered an error: {exc}", success=False, intent=intent)
        if result and result.get("success"):
            return JarvisResponse(
                text=result.get("response", "Done, sir."),
                success=True,
                intent=intent,
                data=result.get("data"),
            )
        return None

    def _route_single(self, command: str) -> JarvisResponse:
        normalized = normalize_command(command)
        if not normalized:
            return JarvisResponse(text="I did not hear a command, sir.", success=False, intent="empty")

        # Routines first.
        routine = self.automation.process_routine(command, lambda item: self.process_command(item, speak=False))
        if routine.get("success"):
            return JarvisResponse(text=routine["response"], success=True, intent="automation")

        for intent, module, keywords in self.modules:
            if self._should_try(normalized, keywords):
                response = self._run_module(intent, module, command)
                if response:
                    return response

        learned = self.memory.learn_from_command(command)
        if learned:
            return JarvisResponse(text=learned, success=True, intent="memory")

        ai_result = self.ai.generate(command, context=self.memory.memory_context())
        return JarvisResponse(
            text=ai_result.text,
            success=ai_result.success,
            intent="ai_chat",
            provider=ai_result.provider,
        )

    def process_command(self, command: str, speak: bool | None = None) -> JarvisResponse:
        """Process a command and optionally speak the final response."""
        raw_command = command or ""
        command = self.clean_command(raw_command)
        normalized = normalize_command(command)

        # Explicit command chains, e.g. "open chrome then volume 40".
        chain_parts = self.automation.split_chain(command)
        if len(chain_parts) > 1:
            responses = [self.process_command(part, speak=False) for part in chain_parts]
            text = " ".join(response.text for response in responses)
            result = JarvisResponse(text=text, success=all(r.success for r in responses), intent="command_chain")
        else:
            result = self._route_single(command)

        self.memory.log_interaction(command, result.intent, result.success)
        self.memory.save_conversation(command, result.text)

        if speak is None:
            speak = bool(self.config.get("behavior.speak_responses", True))
        if speak:
            self.tts.speak(result.text, blocking=False)
            result.spoken = True

        logger.info("Command processed intent=%s success=%s", result.intent, result.success)
        result.debug["normalized"] = normalized
        return result

    def shutdown(self) -> None:
        self.tts.stop()
