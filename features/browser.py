import socket
import urllib.parse
import webbrowser
import logging
from typing import Tuple

from config import WEBSITES
from voice.text_to_speech import speak

logger = logging.getLogger("JARVIS.Browser")

def open_website(site_key: str, speaker_role: str = "Boss") -> Tuple[bool, str]:
    """Open predefined website or raw URL in default system browser."""
    if not site_key:
        msg = f"Sorry {speaker_role}, please specify a website."
        speak(msg)
        return False, msg

    clean_key = site_key.lower().strip()
    url = WEBSITES.get(clean_key)
    
    if not url:
        if clean_key.startswith("http://") or clean_key.startswith("https://"):
            url = clean_key
        else:
            url = f"https://www.{clean_key}.com"

    try:
        logger.info(f"Opening browser URL: {url}")
        webbrowser.open(url)
        msg = f"Opening {site_key}."
        speak(msg)
        return True, msg
    except Exception as e:
        logger.error(f"Error opening website {site_key}: {e}")
        msg = f"Sorry {speaker_role}, I couldn't open {site_key}."
        speak(msg)
        return False, msg

def search_google(query: str, speaker_role: str = "Boss") -> Tuple[bool, str]:
    """Execute Google Search in default browser."""
    if not query:
        msg = f"What would you like me to search for on Google, {speaker_role}?"
        speak(msg)
        return False, msg

    try:
        encoded_query = urllib.parse.quote_plus(query)
        search_url = f"https://www.google.com/search?q={encoded_query}"
        logger.info(f"Performing Google search for: '{query}' ({search_url})")
        webbrowser.open(search_url)
        msg = f"Searching Google for {query}."
        speak(msg)
        return True, msg
    except Exception as e:
        logger.error(f"Google search error: {e}")
        msg = f"Sorry {speaker_role}, I couldn't complete the Google search."
        speak(msg)
        return False, msg

def check_internet_connection(speaker_role: str = "Boss") -> Tuple[bool, str]:
    """Perform lightweight socket test to check internet connectivity."""
    logger.info("Checking internet connectivity...")
    try:
        # Ping Google Public DNS on port 53
        socket.setdefaulttimeout(3)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(("8.8.8.8", 53))
        msg = f"Yes {speaker_role}, your internet connection is active."
        speak(msg)
        return True, msg
    except Exception:
        msg = f"{speaker_role}, it looks like you're currently offline."
        speak(msg)
        return False, msg
