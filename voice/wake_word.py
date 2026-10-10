import logging
from typing import Tuple, Optional
from config import WAKE_WORDS, STANDBY_COMMANDS
from voice.speech_recognition import STTService

logger = logging.getLogger("JARVIS.WakeWord")

class WakeWordDetector:
    """Detects wake words ('Hey JARVIS', 'JARVIS') to transition assistant from standby to active."""

    def __init__(self, stt_service: STTService):
        self.stt = stt_service

    def contains_wake_word(self, text: str) -> bool:
        """Check if input string contains any registered wake word."""
        if not text:
            return False
        text_lower = text.lower()
        return any(wake_word in text_lower for wake_word in WAKE_WORDS)

    def extract_command_after_wake_word(self, text: str) -> str:
        """Extract the command following the wake word, if any."""
        if not text:
            return ""
        text_lower = text.lower()
        for wake_word in WAKE_WORDS:
            if wake_word in text_lower:
                parts = text_lower.split(wake_word, 1)
                if len(parts) > 1 and parts[1].strip():
                    return parts[1].strip()
        return ""

    def is_standby_command(self, text: str) -> bool:
        """Check if command requests standby/sleep mode."""
        if not text:
            return False
        text_lower = text.lower()
        return any(cmd in text_lower for cmd in STANDBY_COMMANDS)

    def listen_for_wake_word(self, timeout: float = 3.0) -> Tuple[bool, str, Optional[object]]:
        """
        Listen for spoken wake word.
        Returns (is_detected, leftover_command, raw_audio).
        """
        text, audio = self.stt.listen(phrase_time_limit=4.0, timeout=timeout)
        if self.contains_wake_word(text):
            command = self.extract_command_after_wake_word(text)
            logger.info(f"Wake word detected! Leftover command: '{command}'")
            return True, command, audio
        return False, "", audio
