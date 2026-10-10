import re
import logging
from dataclasses import dataclass
from typing import Optional, Dict, Any

logger = logging.getLogger("JARVIS.CommandProcessor")

@dataclass
class CommandIntent:
    intent_type: str
    parameter: Optional[str] = None
    requires_confirmation: bool = False
    raw_text: str = ""
    is_sensitive: bool = False

class CommandProcessor:
    """Parses raw text speech input into structured CommandIntents."""

    def parse(self, text: str) -> CommandIntent:
        if not text:
            return CommandIntent(intent_type="UNKNOWN", raw_text=text)

        clean_text = text.lower().strip()
        logger.info(f"Parsing command: '{clean_text}'")

        # 1. Standby / Exit / Sleep
        if any(w in clean_text for w in ["go to sleep", "standby", "sleep mode"]):
            return CommandIntent(intent_type="STANDBY", raw_text=text)
        if any(w in clean_text for w in ["exit", "shutdown jarvis", "stop jarvis", "goodbye", "quit"]):
            return CommandIntent(intent_type="EXIT", raw_text=text)

        # 2. Dangerous System Operations (Requires confirmation & Sensitive)
        if any(cmd in clean_text for cmd in ["shutdown computer", "shutdown system", "restart computer", "restart system"]):
            return CommandIntent(intent_type="SYSTEM_SHUTDOWN", parameter=clean_text, requires_confirmation=True, is_sensitive=True, raw_text=text)

        # 3. Sensitive Commands Detection (Passes, Credentials, API Keys, Security Settings, Private Files, File Deletion, Sending Email)
        if any(k in clean_text for k in ["password", "passwords", "credential", "credentials", "api key", "api keys", "secret", "secrets"]):
            return CommandIntent(intent_type="ACCESS_PASSWORDS", parameter=clean_text, is_sensitive=True, raw_text=text)

        if any(k in clean_text for k in ["security setting", "security settings", "change password", "auth config", "authentication config", "security config", "change authentication"]):
            return CommandIntent(intent_type="SECURITY_SETTINGS", parameter=clean_text, is_sensitive=True, raw_text=text)

        if any(k in clean_text for k in ["private file", "private files", "sensitive file", "sensitive files", "confidential file", "access private", "access sensitive"]):
            return CommandIntent(intent_type="ACCESS_SENSITIVE_FILES", parameter=clean_text, is_sensitive=True, raw_text=text)

        if any(k in clean_text for k in ["delete file", "delete files", "delete important", "delete database", "delete all notes"]):
            return CommandIntent(intent_type="DELETE_FILES", parameter=clean_text, is_sensitive=True, raw_text=text)

        if any(k in clean_text for k in ["send email", "send an email", "automatically send email", "send message"]):
            return CommandIntent(intent_type="SEND_EMAIL", parameter=clean_text, is_sensitive=True, raw_text=text)

        # 4. Email Writer Intent (Drafting without sending - Normal Command)
        if "email" in clean_text:
            topic = clean_text
            prefixes = [
                r"^i need to write an email (asking for|for|about)?",
                r"^i need an email (asking for|for|about)?",
                r"^i need a",
                r"^write an email (asking for|for|about)?",
                r"^write a",
                r"^draft an email (asking for|for|about)?",
                r"^draft a",
                r"^create an email (asking for|for|about)?",
                r"^create a",
                r"^email (asking for|for|about)?"
            ]
            for p in prefixes:
                topic = re.sub(p, "", topic, flags=re.IGNORECASE).strip()

            if topic.endswith("email"):
                topic = topic[:-5].strip()

            topic = re.sub(r"^(asking for|for|about)\s+", "", topic, flags=re.IGNORECASE).strip()
            return CommandIntent(intent_type="EMAIL_DRAFT", parameter=topic if topic else "general college request", raw_text=text)

        # 4. Spotify Intent (Natural matching)
        if "spotify" in clean_text:
            if clean_text in ["open spotify", "launch spotify", "spotify", "open spotify web player"]:
                return CommandIntent(intent_type="SPOTIFY_PLAY", parameter="", raw_text=text)

            if "search spotify for" in clean_text or clean_text.startswith("spotify search"):
                q = re.sub(r"^(search spotify for|spotify search)\s+", "", clean_text, flags=re.IGNORECASE).strip()
                q = re.sub(r"\b(on spotify|in spotify|spotify)\b", "", q, flags=re.IGNORECASE).strip()
                return CommandIntent(intent_type="SPOTIFY_PLAY", parameter=f"search for {q}" if q else "", raw_text=text)

            spotify_patterns = [
                r"play (.*?) (?:on|in) spotify",
                r"spotify play (.*)",
                r"play (.*)",
                r"spotify (.*)"
            ]
            for pattern in spotify_patterns:
                match = re.search(pattern, clean_text)
                if match:
                    query = match.group(1)
                    query = re.sub(r"\b(on spotify|in spotify|spotify|play|search for)\b", "", query, flags=re.IGNORECASE).strip()
                    return CommandIntent(intent_type="SPOTIFY_PLAY", parameter=query if query else "", raw_text=text)
            return CommandIntent(intent_type="SPOTIFY_PLAY", parameter="", raw_text=text)

        # 5. YouTube Launch / Open Website vs YouTube Playback & Search
        if "youtube" in clean_text:
            open_yt_phrases = ["open youtube", "open youtube homepage", "launch youtube", "go to youtube", "youtube homepage"]
            if clean_text in open_yt_phrases or clean_text.startswith("open youtube") or clean_text.startswith("launch youtube"):
                return CommandIntent(intent_type="OPEN_WEBSITE", parameter="youtube", raw_text=text)

            youtube_patterns = [
                r"play (.*?) (?:on|in) youtube",
                r"search youtube for (.*)",
                r"youtube search (.*)",
                r"play (.*)"
            ]
            for pattern in youtube_patterns:
                match = re.search(pattern, clean_text)
                if match:
                    query = match.group(1)
                    query = re.sub(r"\b(on youtube|in youtube|youtube|play|search for)\b", "", query, flags=re.IGNORECASE).strip()
                    if query and query not in ["open", "homepage"]:
                        return CommandIntent(intent_type="YOUTUBE_SEARCH", parameter=query, raw_text=text)
            return CommandIntent(intent_type="OPEN_WEBSITE", parameter="youtube", raw_text=text)

        # Generic "Play [song / video]" without platform specified -> Default YouTube Playback
        if clean_text.startswith("play "):
            query = clean_text.replace("play ", "", 1).strip()
            # If not a media control like "play music"
            if query not in ["music", "pause"]:
                return CommandIntent(intent_type="YOUTUBE_SEARCH", parameter=query, raw_text=text)

        # 6. Weather Intent (Flexible location matching)
        if "weather" in clean_text:
            city = None
            weather_patterns = [
                r"weather in (.*)",
                r"weather of (.*)",
                r"weather for (.*)",
                r"weather at (.*)",
                r"weather (.*)"
            ]
            for pattern in weather_patterns:
                match = re.search(pattern, clean_text)
                if match:
                    extracted = match.group(1).replace("what's the", "").replace("what is the", "").replace("how is the", "").strip()
                    if extracted and extracted not in ["today", "now", "like"]:
                        city = extracted
                        break
            return CommandIntent(intent_type="WEATHER", parameter=city, raw_text=text)

        # 7. Google Search
        google_patterns = [
            r"search google for (.*)",
            r"search for (.*)",
            r"google (.*)"
        ]
        if "google" in clean_text or "search for" in clean_text:
            for pattern in google_patterns:
                match = re.search(pattern, clean_text)
                if match:
                    query = match.group(1).replace("on google", "").replace("google", "").strip()
                    if query:
                        return CommandIntent(intent_type="GOOGLE_SEARCH", parameter=query, raw_text=text)

        # 8. Open Website
        website_keywords = ["youtube", "google", "gmail", "github", "instagram", "chatgpt", "linkedin"]
        if "open" in clean_text:
            for site in website_keywords:
                if site in clean_text:
                    return CommandIntent(intent_type="OPEN_WEBSITE", parameter=site, raw_text=text)

        # 9. Open / Close Applications
        if clean_text.startswith("open "):
            target = clean_text.replace("open ", "", 1).strip()
            # Check if target is a special folder
            if target in ["downloads", "documents", "desktop", "pictures", "project folder", "my project folder"]:
                return CommandIntent(intent_type="OPEN_FOLDER", parameter=target, raw_text=text)
            return CommandIntent(intent_type="OPEN_APP", parameter=target, raw_text=text)

        if clean_text.startswith("close "):
            target = clean_text.replace("close ", "", 1).strip()
            return CommandIntent(intent_type="CLOSE_APP", parameter=target, raw_text=text)

        # 10. Time and Date
        if any(phrase in clean_text for phrase in ["what time", "tell me the time", "current time", "time is it"]):
            return CommandIntent(intent_type="GET_TIME", raw_text=text)
        if any(phrase in clean_text for phrase in ["today's date", "what date", "what day is today", "current date"]):
            return CommandIntent(intent_type="GET_DATE", raw_text=text)

        # 11. Calculator & Math
        math_keywords = ["calculate", "plus", "minus", "multiplied by", "divided by", "times"]
        if any(k in clean_text for k in math_keywords) or re.search(r"\d+\s*[\+\-\*/]\s*\d+", clean_text):
            expr = clean_text.replace("calculate", "").strip()
            return CommandIntent(intent_type="CALCULATE", parameter=expr, raw_text=text)

        # 12. Battery & System Info
        if any(k in clean_text for k in ["battery percentage", "how much battery", "battery status", "battery"]):
            return CommandIntent(intent_type="BATTERY_STATUS", raw_text=text)
        if any(k in clean_text for k in ["cpu usage", "ram usage", "storage", "system info", "system information"]):
            return CommandIntent(intent_type="SYSTEM_INFO", parameter=clean_text, raw_text=text)

        # 13. Screenshot
        if any(k in clean_text for k in ["screenshot", "capture screen", "capture my screen", "take a screenshot"]):
            return CommandIntent(intent_type="TAKE_SCREENSHOT", raw_text=text)

        # 14. Notes
        if "note" in clean_text or "write down" in clean_text:
            note_content = clean_text.replace("take a note", "").replace("take note", "").replace("note", "").strip()
            return CommandIntent(intent_type="TAKE_NOTE", parameter=note_content if note_content else None, raw_text=text)

        # 15. Reminders
        if "remind" in clean_text:
            return CommandIntent(intent_type="SET_REMINDER", parameter=clean_text, raw_text=text)

        # 16. Media Controls
        media_map = {
            "pause music": "pause",
            "stop music": "pause",
            "play music": "play",
            "resume music": "play",
            "next song": "next",
            "previous song": "previous",
            "increase volume": "volume_up",
            "volume up": "volume_up",
            "decrease volume": "volume_down",
            "volume down": "volume_down",
            "mute": "mute",
            "unmute": "mute"
        }
        for k, action in media_map.items():
            if k in clean_text:
                return CommandIntent(intent_type="MEDIA_CONTROL", parameter=action, raw_text=text)

        # 17. Internet Connection Check
        if any(k in clean_text for k in ["internet", "connection", "check internet", "am i connected"]):
            return CommandIntent(intent_type="CHECK_INTERNET", raw_text=text)

        # 18. Identity / General Q&A / Jokes
        if any(k in clean_text for k in ["who are you", "what is your name"]):
            return CommandIntent(intent_type="QNA_IDENTITY", raw_text=text)
        if any(k in clean_text for k in ["who created you", "who made you"]):
            return CommandIntent(intent_type="QNA_CREATOR", raw_text=text)
        if any(k in clean_text for k in ["are you intelligent", "are you smart"]):
            return CommandIntent(intent_type="QNA_INTELLIGENCE", raw_text=text)
        if "joke" in clean_text:
            return CommandIntent(intent_type="JOKE", raw_text=text)

        # 19. Basic Greetings & Thanks
        if any(k in clean_text for k in ["hello", "hey", "hi", "how are you"]):
            return CommandIntent(intent_type="GREETING", raw_text=text)
        if any(k in clean_text for k in ["thank you", "thanks"]):
            return CommandIntent(intent_type="THANK_YOU", raw_text=text)

        return CommandIntent(intent_type="UNKNOWN", raw_text=text)
