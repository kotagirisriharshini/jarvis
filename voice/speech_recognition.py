import logging
import speech_recognition as sr
from typing import Tuple, Optional, List

logger = logging.getLogger("JARVIS.STT")

class STTService:
    """Speech-to-Text service using SpeechRecognition with microphone capture."""
    
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.energy_threshold = 300
        self.recognizer.pause_threshold = 0.8
        self.mic = None
        self.device_index = None
        self.device_name = None
        self._init_mic()

    @staticmethod
    def find_best_microphone_index(mics: List[str]) -> Tuple[Optional[int], Optional[str]]:
        """Auto-detect the best active hardware microphone device index."""
        if not mics:
            return None, None
            
        # 1. Prefer 'Microphone Array' or specific hardware microphone (excluding sound mappers)
        for i, name in enumerate(mics):
            n = name.lower()
            if "microphone array" in n or ("microphone" in n and "mapper" not in n and "primary" not in n):
                return i, name
                
        # 2. Fallback to first non-mapper input device
        for i, name in enumerate(mics):
            n = name.lower()
            if "mapper" not in n and "primary" not in n:
                return i, name

        # 3. Ultimate fallback to index 0
        return 0, mics[0]

    def _init_mic(self):
        try:
            mics = sr.Microphone.list_microphone_names()
            if mics:
                idx, name = self.find_best_microphone_index(mics)
                self.device_index = idx
                self.device_name = name
                self.mic = sr.Microphone(device_index=self.device_index)
                logger.info(f"Microphone initialized: Index {self.device_index} - '{self.device_name}'")
                # Calibrate ambient noise ONCE during initialization
                self.calibrate_ambient_noise(duration=0.5)
            else:
                logger.warning("No microphone devices detected.")
        except Exception as e:
            logger.error(f"Error setting up microphone: {e}")
            self.mic = None

    def calibrate_ambient_noise(self, duration: float = 0.5):
        """Calibrate ambient noise once so listening loop doesn't block on every phrase."""
        if self.mic:
            try:
                with self.mic as source:
                    self.recognizer.adjust_for_ambient_noise(source, duration=duration)
                    # Enforce reasonable bounds for energy threshold
                    if self.recognizer.energy_threshold < 150:
                        self.recognizer.energy_threshold = 150
                    elif self.recognizer.energy_threshold > 3000:
                        self.recognizer.energy_threshold = 1000
                    logger.info(f"Calibrated energy threshold: {self.recognizer.energy_threshold:.2f}")
            except Exception as e:
                logger.warning(f"Error calibrating ambient noise: {e}")

    def listen(self, phrase_time_limit: Optional[float] = 6.0, timeout: Optional[float] = 5.0) -> Tuple[str, Optional[sr.AudioData]]:
        """
        Listen for speech from microphone.
        Returns (recognized_text, raw_audio_data).
        """
        if self.mic is None:
            logger.warning("No microphone available. Using keyboard text input fallback.")
            try:
                text_input = input("User (type command): ").strip()
                return text_input.lower(), None
            except EOFError:
                return "", None

        with self.mic as source:
            try:
                logger.debug("Listening for audio input...")
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
                
                # Recognize using Google Speech API
                text = self.recognizer.recognize_google(audio)
                text_clean = text.strip().lower()
                logger.info(f"Speech Recognized: '{text_clean}'")
                print(f"User: {text}")
                return text_clean, audio

            except sr.WaitTimeoutError:
                logger.debug("Listening timed out waiting for phrase.")
                return "", None
            except sr.UnknownValueError:
                logger.debug("Speech was unintelligible.")
                return "", None
            except sr.RequestError as e:
                logger.warning(f"Google Speech Recognition request error (offline/service error): {e}")
                print(f"[JARVIS STT]: Could not reach Google Speech service ({e}). Please check connection.")
                return "", None
            except Exception as e:
                logger.error(f"Unexpected speech recognition error: {e}")
                return "", None

    def listen_text_only(self, timeout: float = 5.0) -> str:
        """Helper to get only clean recognized text."""
        text, _ = self.listen(timeout=timeout)
        return text
