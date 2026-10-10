import re
import urllib.parse
import webbrowser
import logging
from typing import Tuple

from voice.text_to_speech import speak

logger = logging.getLogger("JARVIS.Spotify")

def play_on_spotify(query: str = "", speaker_role: str = "Boss") -> Tuple[bool, str]:
    """
    Search and open requested track/artist or homepage on Spotify Web Player in default browser.
    Does not attempt desktop app URI deep-links or credential automation.
    """
    raw_query = query.strip() if query else ""

    # 1. Open Spotify Homepage (e.g. "open spotify", "launch spotify")
    if not raw_query or raw_query.lower() in ["open", "launch", "homepage"]:
        try:
            web_url = "https://open.spotify.com/"
            logger.info("Opening Spotify Web Player homepage...")
            webbrowser.open(web_url)
            msg = "Opening Spotify Web Player."
            speak(msg)
            return True, msg
        except Exception as e:
            logger.error(f"Error opening Spotify Web Player homepage: {e}")
            msg = f"Sorry {speaker_role}, I couldn't open Spotify Web Player."
            speak(msg)
            return False, msg

    # 2. Determine if command is search-only vs play request
    is_search_only = raw_query.lower().startswith("search for ") or "search spotify" in raw_query.lower()

    clean_query = re.sub(r"^(search for|search spotify for|spotify search|play)\s+", "", raw_query, flags=re.IGNORECASE).strip()
    clean_query = re.sub(r"\b(on spotify|in spotify|spotify)\b", "", clean_query, flags=re.IGNORECASE).strip()
    clean_query = re.sub(r"\s+", " ", clean_query).strip()

    if not clean_query:
        try:
            web_url = "https://open.spotify.com/"
            webbrowser.open(web_url)
            msg = "Opening Spotify Web Player."
            speak(msg)
            return True, msg
        except Exception as e:
            logger.error(f"Error opening Spotify Web Player: {e}")
            msg = f"Sorry {speaker_role}, I couldn't open Spotify."
            speak(msg)
            return False, msg

    encoded_query = urllib.parse.quote(clean_query)
    web_url = f"https://open.spotify.com/search/{encoded_query}"

    try:
        logger.info(f"Opening Spotify Web Player search URL: {web_url}")
        webbrowser.open(web_url)

        if is_search_only:
            msg = f"Searching Spotify for {clean_query}."
        else:
            msg = f"I opened {clean_query} on Spotify. You may need to press Play."

        speak(msg)
        return True, msg

    except Exception as e:
        logger.error(f"Spotify Web Player search error for '{clean_query}': {e}")
        msg = f"Sorry {speaker_role}, I couldn't open Spotify for {clean_query}."
        speak(msg)
        return False, msg
