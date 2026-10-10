import datetime
import logging
from typing import Tuple, Optional

from config import NOTES_DIR, NOTES_FILE
from voice.text_to_speech import speak

logger = logging.getLogger("JARVIS.Notes")

class NoteManager:
    """Manages recording and reading text voice notes."""

    def __init__(self):
        NOTES_DIR.mkdir(parents=True, exist_ok=True)

    def add_note(self, note_text: str, speaker_role: str = "Boss") -> Tuple[bool, str]:
        """Append timestamped note entry to notes.txt."""
        if not note_text:
            msg = f"Sorry {speaker_role}, the note content was empty."
            speak(msg)
            return False, msg

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        formatted_entry = f"[{timestamp}]\n{note_text.strip()}\n\n"

        logger.info(f"Saving note: '{note_text}'")

        try:
            with open(NOTES_FILE, "a", encoding="utf-8") as f:
                f.write(formatted_entry)
            
            msg = f"Your note has been saved, {speaker_role}."
            speak(msg)
            return True, msg

        except Exception as e:
            logger.error(f"Error saving note: {e}")
            msg = f"Sorry {speaker_role}, I couldn't save your note."
            speak(msg)
            return False, msg

    def read_notes(self, speaker_role: str = "Boss") -> Tuple[bool, str]:
        """Read saved notes aloud or return text summary."""
        if not NOTES_FILE.exists() or NOTES_FILE.stat().st_size == 0:
            msg = f"You have no saved notes, {speaker_role}."
            speak(msg)
            return True, msg

        try:
            with open(NOTES_FILE, "r", encoding="utf-8") as f:
                content = f.read().strip()

            lines = content.split("\n\n")
            recent_notes = lines[-3:]  # Read up to last 3 notes
            
            msg = f"{speaker_role}, here are your most recent notes: " + " ".join(recent_notes)
            speak(msg)
            return True, msg

        except Exception as e:
            logger.error(f"Error reading notes: {e}")
            msg = f"Sorry {speaker_role}, I couldn't read your notes file."
            speak(msg)
            return False, msg
