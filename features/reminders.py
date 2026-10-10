import re
import json
import threading
import datetime
import logging
from typing import Tuple, List, Dict, Any

from config import REMINDERS_DIR, REMINDERS_FILE
from voice.text_to_speech import speak

logger = logging.getLogger("JARVIS.Reminders")

class ReminderManager:
    """Schedules local timers and spoken reminder alerts."""

    def __init__(self):
        REMINDERS_DIR.mkdir(parents=True, exist_ok=True)
        self.active_timers: List[threading.Timer] = []

    def parse_time_duration(self, text: str) -> Tuple[int, str]:
        """
        Extract duration in seconds and target task from text phrase.
        Example: "remind me in 10 minutes to study DBMS" -> (600, "study DBMS")
        """
        text_lower = text.lower()
        
        # Regex patterns for minutes / seconds / hours
        sec_match = re.search(r"in (\d+)\s*(seconds|second|secs|sec)", text_lower)
        min_match = re.search(r"in (\d+)\s*(minutes|minute|mins|min)", text_lower)
        hr_match = re.search(r"in (\d+)\s*(hours|hour|hrs|hr)", text_lower)

        seconds = 0
        if sec_match:
            seconds = int(sec_match.group(1))
        elif min_match:
            seconds = int(min_match.group(1)) * 60
        elif hr_match:
            seconds = int(hr_match.group(1)) * 3600
        else:
            # Default to 60 seconds if no time parsed
            seconds = 60

        # Extract task description after 'to ' or 'for '
        task = "your reminder"
        if " to " in text_lower:
            task = text_lower.split(" to ", 1)[1].strip()
        elif " for " in text_lower:
            task = text_lower.split(" for ", 1)[1].strip()

        return seconds, task

    def trigger_reminder(self, task_description: str, speaker_role: str = "Boss"):
        """Trigger spoken alert when timer expires."""
        alert_msg = f"Reminder alert for {speaker_role}: It is time to {task_description}."
        logger.info(f"Reminder triggered: '{task_description}'")
        speak(alert_msg)

    def set_reminder(self, command_text: str, speaker_role: str = "Boss") -> Tuple[bool, str]:
        """Schedule a timer for the requested reminder."""
        seconds, task = self.parse_time_duration(command_text)

        if seconds <= 0:
            msg = f"Sorry {speaker_role}, I couldn't parse the time duration for the reminder."
            speak(msg)
            return False, msg

        # Format human-readable delay
        delay_desc = f"{seconds // 60} minutes" if seconds >= 60 else f"{seconds} seconds"

        # Launch background timer thread
        timer = threading.Timer(seconds, self.trigger_reminder, args=[task, speaker_role])
        timer.daemon = True
        timer.start()
        self.active_timers.append(timer)

        # Save reminder to json file
        self._save_to_json(task, seconds)

        msg = f"Reminder set for {delay_desc} from now to {task}, {speaker_role}."
        speak(msg)
        return True, msg

    def _save_to_json(self, task: str, seconds: int):
        """Save reminder entry to data/reminders/reminders.json."""
        try:
            reminders = []
            if REMINDERS_FILE.exists():
                try:
                    with open(REMINDERS_FILE, "r", encoding="utf-8") as f:
                        reminders = json.load(f)
                except Exception:
                    reminders = []

            due_time = (datetime.datetime.now() + datetime.timedelta(seconds=seconds)).isoformat()
            reminders.append({"task": task, "due_time": due_time, "created_at": datetime.datetime.now().isoformat()})

            with open(REMINDERS_FILE, "w", encoding="utf-8") as f:
                json.dump(reminders, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save reminder JSON: {e}")
