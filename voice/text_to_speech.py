import threading
import pyttsx3
import logging
from typing import List, Dict, Any

from config import TTS_RATE, TTS_VOLUME, TTS_VOICE_INDEX

logger = logging.getLogger("JARVIS.TTS")

class TTSService:
    """Centralized Text-to-Speech service wrapping pyttsx3."""
    
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(TTSService, cls).__new__(cls)
                cls._instance._init_engine()
            return cls._instance

    def _init_engine(self):
        try:
            self.engine = pyttsx3.init()
            self.set_rate(TTS_RATE)
            self.set_volume(TTS_VOLUME)
            voices = self.get_voices()
            if voices and len(voices) > TTS_VOICE_INDEX:
                self.set_voice(voices[TTS_VOICE_INDEX]["id"])
            logger.info("TTS engine initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize TTS engine: {e}")
            self.engine = None

    def speak(self, text: str) -> None:
        """Speak the given text aloud synchronously with log output."""
        if not text:
            return
        
        print(f"\n[JARVIS]: {text}")
        logger.info(f"Speaking: '{text}'")

        if not self.engine:
            return

        with self._lock:
            try:
                # Re-initialize or run loop safely
                self.engine.say(text)
                self.engine.runAndWait()
            except Exception as e:
                logger.error(f"TTS speak error: {e}")
                # Re-init engine in case of COM lockup
                try:
                    self.engine = pyttsx3.init()
                    self.engine.say(text)
                    self.engine.runAndWait()
                except Exception as inner_e:
                    logger.error(f"TTS re-init speak failed: {inner_e}")

    def set_rate(self, rate: int) -> None:
        """Set speaking speed rate."""
        if self.engine:
            try:
                self.engine.setProperty('rate', rate)
            except Exception as e:
                logger.error(f"Error setting TTS rate: {e}")

    def set_volume(self, volume: float) -> None:
        """Set TTS volume (0.0 to 1.0)."""
        if self.engine:
            try:
                self.engine.setProperty('volume', max(0.0, min(1.0, volume)))
            except Exception as e:
                logger.error(f"Error setting TTS volume: {e}")

    def set_voice(self, voice_id: str) -> None:
        """Set TTS voice ID."""
        if self.engine:
            try:
                self.engine.setProperty('voice', voice_id)
            except Exception as e:
                logger.error(f"Error setting TTS voice: {e}")

    def get_voices(self) -> List[Dict[str, Any]]:
        """Get list of available voices."""
        voices_info = []
        if self.engine:
            try:
                voices = self.engine.getProperty('voices')
                for v in voices:
                    voices_info.append({
                        "id": v.id,
                        "name": v.name,
                        "languages": getattr(v, 'languages', [])
                    })
            except Exception as e:
                logger.error(f"Error getting voices: {e}")
        return voices_info


# Global helper functions for convenient project-wide usage
_tts_service = None

def get_tts_service() -> TTSService:
    global _tts_service
    if _tts_service is None:
        _tts_service = TTSService()
    return _tts_service

def speak(text: str) -> None:
    get_tts_service().speak(text)

def set_voice(voice_id: str) -> None:
    get_tts_service().set_voice(voice_id)

def set_rate(rate: int) -> None:
    get_tts_service().set_rate(rate)

def set_volume(volume: float) -> None:
    get_tts_service().set_volume(volume)
