import os
import subprocess
import logging
from pathlib import Path
from typing import Tuple

from config import BASE_DIR
from voice.text_to_speech import speak

logger = logging.getLogger("JARVIS.FileManager")

def open_folder(folder_name: str, speaker_role: str = "Boss") -> Tuple[bool, str]:
    """Open safe configured user system folders in File Explorer."""
    clean_name = folder_name.lower().strip()
    home = Path.home()

    folders_map = {
        "downloads": home / "Downloads",
        "documents": home / "Documents",
        "desktop": home / "Desktop",
        "pictures": home / "Pictures",
        "project folder": BASE_DIR,
        "my project folder": BASE_DIR,
    }

    target_path = folders_map.get(clean_name)
    if not target_path or not target_path.exists():
        msg = f"Sorry {speaker_role}, I couldn't find the {folder_name} folder."
        speak(msg)
        return False, msg

    logger.info(f"Opening folder: {target_path}")

    try:
        if os.name == "nt":
            os.startfile(str(target_path))
        else:
            subprocess.Popen(["xdg-open", str(target_path)])
            
        msg = f"Opening {folder_name}."
        speak(msg)
        return True, msg

    except Exception as e:
        logger.error(f"Error opening folder '{folder_name}': {e}")
        msg = f"Sorry {speaker_role}, I couldn't open {folder_name}."
        speak(msg)
        return False, msg
