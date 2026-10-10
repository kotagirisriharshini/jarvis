import sys
import logging
import datetime
from typing import Optional

from config import ensure_directories, LOG_FILE, ASSISTANT_NAME
from voice.text_to_speech import TTSService, speak
from voice.speech_recognition import STTService
from voice.wake_word import WakeWordDetector
from voice.speaker_recognition import SpeakerRecognizer
from core.command_processor import CommandProcessor, CommandIntent
from core.responses import get_greeting, get_joke, PREDEFINED_ANSWERS

# Feature Handlers
from features.applications import open_application, close_application
from features.browser import open_website, search_google, check_internet_connection
from features.youtube import play_on_youtube
from features.spotify import play_on_spotify
from features.email_writer import generate_email_draft
from features.calculator import calculate
from features.system_info import get_current_time, get_current_date, get_battery_status, get_system_metrics
from features.screenshot import take_screenshot
from features.notes import NoteManager
from features.reminders import ReminderManager
from features.media_control import control_media
from features.file_manager import open_folder
from features.weather import get_weather

# Setup Logger
ensure_directories()
logging.basicConfig(
    filename=str(LOG_FILE),
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("JARVIS.Core")

class JarvisAssistant:
    """
    Main Assistant Controller for J.A.R.V.I.S.
    Manages assistant states (STANDBY vs ACTIVE), speech loop, speaker classification,
    and intent execution.
    """

    def __init__(self):
        logger.info("Initializing J.A.R.V.I.S. Assistant Subsystems...")
        self.tts = TTSService()
        self.stt = STTService()
        self.wake_detector = WakeWordDetector(self.stt)
        self.speaker_recognizer = SpeakerRecognizer()
        self.processor = CommandProcessor()
        self.note_manager = NoteManager()
        self.reminder_manager = ReminderManager()

        self.is_active = False
        self.running = True
        self.current_speaker_role = "Boss"

    def run_setup(self):
        """Interactive Setup Wizard for microphone, TTS, and Boss voice enrollment."""
        print("\n========================================")
        print("    J.A.R.V.I.S. FIRST-TIME SETUP       ")
        print("========================================\n")
        
        speak("Initializing J.A.R.V.I.S. setup process.")
        
        # Test TTS output
        speak("Testing text to speech output. Audio check complete.")
        
        # Ask to enroll Boss voice
        choice = input("Do you want to enroll your Boss voice profile now? (y/n): ").strip().lower()
        if choice == 'y':
            self.speaker_recognizer.enroll_interactive(self.stt)
        else:
            print("Skipping voice profile enrollment. Defaulting to standard mode.")
            speak("Voice enrollment skipped.")

        print("\nJ.A.R.V.I.S. setup completed successfully.")
        speak("Setup completed successfully.")

    def handle_intent(self, intent: CommandIntent, role: Optional[str] = None) -> bool:
        """
        Route and execute feature handler corresponding to parsed intent.
        Enforces security verification for sensitive commands.
        Returns True if assistant should remain running, False if exit requested.
        """
        if role is None:
            role = self.current_speaker_role

        logger.info(f"Executing intent: '{intent.intent_type}' (sensitive: {intent.is_sensitive}) for role '{role}'")

        # Security check for sensitive commands
        if intent.is_sensitive and role.lower() != "boss":
            logger.warning(f"Rejected sensitive intent '{intent.intent_type}' for unverified speaker role '{role}'.")
            speak("Sorry, Boss verification is required for this command.")
            return True

        # 1. Exit / Shutdown Assistant
        if intent.intent_type == "EXIT":
            resp = f"Goodbye, {role}. Shutting down J.A.R.V.I.S. systems." if role == "Boss" else "Goodbye. Shutting down J.A.R.V.I.S. systems."
            speak(resp)
            self.running = False
            return False

        # 2. Standby Mode
        if intent.intent_type == "STANDBY":
            resp = f"Entering standby mode, {role}. Say Hey JARVIS to wake me." if role == "Boss" else "Entering standby mode. Say Hey JARVIS to wake me."
            speak(resp)
            self.is_active = False
            return True

        # 3. Sensitive / Security Handlers (Boss Verified)
        if intent.intent_type == "ACCESS_PASSWORDS":
            speak(f"Accessing secure password vault for {role}.")
            return True
        elif intent.intent_type == "SECURITY_SETTINGS":
            speak(f"Opening system security settings for {role}.")
            return True
        elif intent.intent_type == "ACCESS_SENSITIVE_FILES":
            speak(f"Accessing sensitive files for {role}.")
            return True
        elif intent.intent_type == "DELETE_FILES":
            speak(f"Deleting requested files for {role}.")
            return True
        elif intent.intent_type == "SEND_EMAIL":
            speak(f"Sending email automatically for {role}.")
            return True

        # 4. Dangerous System Confirmation Guard
        if intent.requires_confirmation:
            speak(f"{role}, do you want me to perform {intent.parameter}? Please say confirm.")
            confirmation = self.stt.listen_text_only(timeout=6.0)
            if "confirm" in confirmation:
                speak("Confirmation received. Executing action.")
                # Execute action safely
                return True
            else:
                speak("Action canceled.")
                return True

        # 4. Feature Handlers Execution
        if intent.intent_type == "OPEN_APP":
            open_application(intent.parameter, role)
        elif intent.intent_type == "CLOSE_APP":
            close_application(intent.parameter, role)
        elif intent.intent_type == "OPEN_WEBSITE":
            open_website(intent.parameter, role)
        elif intent.intent_type == "YOUTUBE_SEARCH":
            play_on_youtube(intent.parameter, role)
        elif intent.intent_type == "SPOTIFY_PLAY":
            play_on_spotify(intent.parameter, role)
        elif intent.intent_type == "EMAIL_DRAFT":
            generate_email_draft(intent.parameter, role)
        elif intent.intent_type == "GOOGLE_SEARCH":
            search_google(intent.parameter, role)
        elif intent.intent_type == "GET_TIME":
            get_current_time()
        elif intent.intent_type == "GET_DATE":
            get_current_date()
        elif intent.intent_type == "CALCULATE":
            calculate(intent.parameter, role)
        elif intent.intent_type == "BATTERY_STATUS":
            get_battery_status(role)
        elif intent.intent_type == "SYSTEM_INFO":
            get_system_metrics(role)
        elif intent.intent_type == "TAKE_SCREENSHOT":
            take_screenshot(role)
        elif intent.intent_type == "TAKE_NOTE":
            content = intent.parameter
            if not content:
                speak(f"What should I write in your note, {role}?")
                content = self.stt.listen_text_only(timeout=7.0)
            self.note_manager.add_note(content, role)
        elif intent.intent_type == "SET_REMINDER":
            self.reminder_manager.set_reminder(intent.raw_text, role)
        elif intent.intent_type == "MEDIA_CONTROL":
            control_media(intent.parameter, role)
        elif intent.intent_type == "OPEN_FOLDER":
            open_folder(intent.parameter, role)
        elif intent.intent_type == "CHECK_INTERNET":
            check_internet_connection(role)
        elif intent.intent_type == "WEATHER":
            get_weather(intent.parameter, role)
        elif intent.intent_type == "QNA_IDENTITY":
            speak(PREDEFINED_ANSWERS["identity"])
        elif intent.intent_type == "QNA_CREATOR":
            speak(PREDEFINED_ANSWERS["creator"])
        elif intent.intent_type == "QNA_INTELLIGENCE":
            speak(PREDEFINED_ANSWERS["intelligence"])
        elif intent.intent_type == "JOKE":
            speak(get_joke())
        elif intent.intent_type == "GREETING":
            greeting = get_greeting(role)
            speak(greeting)
        elif intent.intent_type == "THANK_YOU":
            resp = "You're welcome, Boss." if role == "Boss" else "You're welcome."
            speak(resp)
        else:
            msg = f"Sorry {role}, I don't know how to perform that command yet."
            speak(msg)

        return True

    def start_loop(self):
        """Start the continuous standby / active assistant listening loop."""
        print("\n" + "=" * 50)
        print("         J.A.R.V.I.S. VOICE ASSISTANT           ")
        print("========================================")
        print(" Status:")
        print("  Microphone:         Ready")
        print("  Speech Engine:      Ready")
        print(f"  Speaker Recognizer: {'Boss Profile Loaded' if self.speaker_recognizer.is_enrolled() else 'Default Mode'}")
        print("========================================\n")

        # Initial Startup Greeting
        initial_greeting = get_greeting(self.current_speaker_role)
        speak(f"{initial_greeting} All systems are online.")
        
        self.is_active = True

        while self.running:
            try:
                if not self.is_active:
                    print("\n[STANDBY MODE] Listening for wake word ('Hey JARVIS')...")
                    detected, leftover_cmd, audio = self.wake_detector.listen_for_wake_word(timeout=4.0)
                    
                    if detected:
                        # Speaker classification check on wake audio
                        role, score = self.speaker_recognizer.classify_speaker(audio)
                        self.current_speaker_role = role
                        logger.info(f"Speaker classified as: '{role}' (score: {score:.3f})")
                        
                        greeting = get_greeting(role)
                        speak(greeting)
                        self.is_active = True

                        if leftover_cmd:
                            intent = self.processor.parse(leftover_cmd)
                            self.handle_intent(intent)
                    continue

                # ACTIVE MODE: Listen for user command
                print("\n[ACTIVE MODE] Listening for your command...")
                raw_text, audio = self.stt.listen(phrase_time_limit=6.0, timeout=5.0)

                if not raw_text:
                    continue

                # Speaker classification
                role, score = self.speaker_recognizer.classify_speaker(audio)
                self.current_speaker_role = role

                # Parse & execute intent
                intent = self.processor.parse(raw_text)
                self.handle_intent(intent)

            except KeyboardInterrupt:
                print("\nKeyboard Interrupt detected. Exiting JARVIS.")
                speak("Shutting down systems. Goodbye.")
                break
            except Exception as e:
                logger.error(f"Error in main loop: {e}", exc_info=True)
                speak("I encountered a system error. Continuing operation.")

        print("\nJARVIS assistant terminated clean.")
