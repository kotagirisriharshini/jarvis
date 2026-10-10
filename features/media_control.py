import logging
import pyautogui
import ctypes
from typing import Tuple

from voice.text_to_speech import speak

logger = logging.getLogger("JARVIS.MediaControl")

# Windows Virtual Key Codes for Media Keys
VK_VOLUME_MUTE = 0xAD
VK_VOLUME_DOWN = 0xAE
VK_VOLUME_UP = 0xAF
VK_MEDIA_NEXT_TRACK = 0xB0
VK_MEDIA_PREV_TRACK = 0xB1
VK_MEDIA_STOP = 0xB2
VK_MEDIA_PLAY_PAUSE = 0xB3

def _send_win_key(vk_code: int):
    """Send Windows keybd_event virtual key stroke."""
    ctypes.windll.user32.keybd_event(vk_code, 0, 0, 0)
    ctypes.windll.user32.keybd_event(vk_code, 0, 2, 0)

def control_media(action: str, speaker_role: str = "Boss") -> Tuple[bool, str]:
    """Execute system media control operation."""
    clean_action = action.lower().strip()
    logger.info(f"Media control action: '{clean_action}'")

    try:
        if clean_action in ["play", "pause", "play_pause"]:
            _send_win_key(VK_MEDIA_PLAY_PAUSE)
            msg = "Toggled playback."
        elif clean_action == "next":
            _send_win_key(VK_MEDIA_NEXT_TRACK)
            msg = "Playing next track."
        elif clean_action == "previous":
            _send_win_key(VK_MEDIA_PREV_TRACK)
            msg = "Playing previous track."
        elif clean_action == "volume_up":
            for _ in range(5):
                _send_win_key(VK_VOLUME_UP)
            msg = "Increased volume."
        elif clean_action == "volume_down":
            for _ in range(5):
                _send_win_key(VK_VOLUME_DOWN)
            msg = "Decreased volume."
        elif clean_action == "mute":
            _send_win_key(VK_VOLUME_MUTE)
            msg = "Muted audio."
        else:
            msg = f"Sorry {speaker_role}, unknown media action."
            speak(msg)
            return False, msg

        speak(msg)
        return True, msg

    except Exception as e:
        logger.error(f"Error performing media action '{action}': {e}")
        # Fallback to pyautogui key presses
        try:
            if clean_action in ["play", "pause"]:
                pyautogui.press("playpause")
            elif clean_action == "next":
                pyautogui.press("nexttrack")
            elif clean_action == "previous":
                pyautogui.press("prevtrack")
            elif clean_action == "volume_up":
                pyautogui.press("volumeup")
            elif clean_action == "volume_down":
                pyautogui.press("volumedown")
            elif clean_action == "mute":
                pyautogui.press("volumemute")
            msg = f"Media command executed."
            speak(msg)
            return True, msg
        except Exception as inner_e:
            msg = f"Sorry {speaker_role}, media key stroke could not be sent."
            speak(msg)
            return False, msg
