import re
import requests
import urllib.parse
import webbrowser
import logging
from typing import Tuple

from voice.text_to_speech import speak

logger = logging.getLogger("JARVIS.YouTube")

def extract_top_video_id(query: str) -> str:
    """
    Query YouTube search results and extract top video ID.
    Returns 11-character video ID string or empty string if scraping fails.
    """
    try:
        encoded_query = urllib.parse.quote_plus(query)
        search_url = f"https://www.youtube.com/results?search_query={encoded_query}"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        
        response = requests.get(search_url, headers=headers, timeout=5)
        if response.status_code == 200:
            html = response.text
            # Search for watch?v= video ID patterns in HTML/JSON data
            video_ids = re.findall(r'/watch\?v=([\w-]{11})', html)
            if not video_ids:
                video_ids = re.findall(r'"videoId":"([\w-]{11})"', html)
            
            if video_ids:
                top_id = video_ids[0]
                logger.info(f"Extracted top YouTube video ID: '{top_id}' for query: '{query}'")
                return top_id
    except Exception as e:
        logger.warning(f"Failed to extract YouTube video ID for '{query}': {e}")
    
    return ""

def play_on_youtube(query: str, speaker_role: str = "Boss") -> Tuple[bool, str]:
    """
    Search and play requested video/content on YouTube.
    Opens the actual video watch page directly (youtube.com/watch?v=...) when possible.
    Includes transparent spoken response regarding browser autoplay.
    """
    clean_query = query.strip() if query else "trending music"
    
    # Remove phrases like 'on youtube', 'youtube', 'play', 'search for'
    clean_query = re.sub(r"\b(on youtube|youtube|play|search for)\b", "", clean_query, flags=re.IGNORECASE).strip()
    if not clean_query:
        clean_query = "trending music"

    logger.info(f"YouTube play request for: '{clean_query}'")

    try:
        top_video_id = extract_top_video_id(clean_query)
        
        if top_video_id:
            watch_url = f"https://www.youtube.com/watch?v={top_video_id}"
            logger.info(f"Opening YouTube watch page: {watch_url}")
            webbrowser.open(watch_url)
            
            msg = f"Playing {clean_query} on YouTube. Note that your browser may require one click to start playback."
            speak(msg)
            return True, msg
        else:
            # Fallback to search results page if video ID could not be extracted
            encoded_query = urllib.parse.quote_plus(clean_query)
            search_url = f"https://www.youtube.com/results?search_query={encoded_query}"
            logger.info(f"Opening YouTube search fallback: {search_url}")
            webbrowser.open(search_url)
            
            msg = f"Searching YouTube for {clean_query}. The browser may require one click to select a video."
            speak(msg)
            return True, msg

    except Exception as e:
        logger.error(f"YouTube playback error for '{clean_query}': {e}")
        msg = f"Sorry {speaker_role}, I encountered an issue opening YouTube."
        speak(msg)
        return False, msg
