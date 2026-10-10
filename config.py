import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
LOG_DIR = BASE_DIR / "logs"

NOTES_DIR = DATA_DIR / "notes"
SCREENSHOTS_DIR = DATA_DIR / "screenshots"
REMINDERS_DIR = DATA_DIR / "reminders"
VOICE_PROFILES_DIR = DATA_DIR / "voice_profiles"

LOG_FILE = LOG_DIR / "jarvis.log"
BOSS_PROFILE_FILE = VOICE_PROFILES_DIR / "boss_profile.npy"
NOTES_FILE = NOTES_DIR / "notes.txt"
REMINDERS_FILE = REMINDERS_DIR / "reminders.json"

# Assistant Config
ASSISTANT_NAME = "JARVIS"
WAKE_WORDS = ["hey jarvis", "jarvis"]
STANDBY_COMMANDS = ["go to sleep", "standby", "sleep mode"]
EXIT_COMMANDS = ["exit", "shutdown jarvis", "stop jarvis", "goodbye", "quit"]

# Text-to-Speech Settings
TTS_RATE = 175
TTS_VOLUME = 1.0
# Preferred voice: 0 for David (male), 1 for Zira (female)
TTS_VOICE_INDEX = 0

# Voice / Speaker Recognition Settings
SPEAKER_THRESHOLD = 0.55  # Cosine distance / similarity threshold for Boss verification
AUDIO_SAMPLE_RATE = 16000
ENROLLMENT_SAMPLES = 3
ENROLLMENT_DURATION = 4.0  # seconds per sample

# Safety Settings
CONFIRMATION_REQUIRED_COMMANDS = ["shutdown system", "restart system", "delete all notes"]

# Application Executables / Commands Mapping (Windows)
APPLICATIONS = {
    "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "google chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "notepad": "notepad.exe",
    "calculator": "calc.exe",
    "vs code": "code",
    "vscode": "code",
    "visual studio code": "code",
    "command prompt": "cmd.exe",
    "cmd": "cmd.exe",
    "file explorer": "explorer.exe",
    "explorer": "explorer.exe",
    "settings": "ms-settings:",
    "whatsapp": "whatsapp:",
    "spotify": "spotify.exe",
}

# Websites Mapping
WEBSITES = {
    "youtube": "https://www.youtube.com",
    "google": "https://www.google.com",
    "gmail": "https://mail.google.com",
    "github": "https://www.github.com",
    "instagram": "https://www.instagram.com",
    "chatgpt": "https://chatgpt.com",
    "linkedin": "https://www.linkedin.com",
}

# Ensure required directories exist
def ensure_directories():
    for directory in [DATA_DIR, LOG_DIR, NOTES_DIR, SCREENSHOTS_DIR, REMINDERS_DIR, VOICE_PROFILES_DIR]:
        directory.mkdir(parents=True, exist_ok=True)
