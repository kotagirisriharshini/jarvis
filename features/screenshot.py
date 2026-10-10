import datetime
import logging
from PIL import ImageGrab
import pyautogui
from typing import Tuple

from config import SCREENSHOTS_DIR
from voice.text_to_speech import speak

logger = logging.getLogger("JARVIS.Screenshot")

def take_screenshot(speaker_role: str = "Boss") -> Tuple[bool, str]:
    """Capture full screen and save PNG image in screenshots directory."""
    SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = SCREENSHOTS_DIR / f"screenshot_{timestamp}.png"

    logger.info(f"Capturing screenshot to {filepath}")

    try:
        # Capture screen using ImageGrab or pyautogui
        try:
            image = ImageGrab.grab()
            image.save(filepath)
        except Exception:
            pyautogui.screenshot(str(filepath))

        msg = f"Screenshot captured and saved to screenshots directory, {speaker_role}."
        speak(msg)
        return True, msg

    except Exception as e:
        logger.error(f"Error capturing screenshot: {e}")
        msg = f"Sorry {speaker_role}, I couldn't capture the screen."
        speak(msg)
        return False, msg
