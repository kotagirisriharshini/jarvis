import os
import shutil
import subprocess
import logging
import psutil
from pathlib import Path
from typing import Tuple, Optional

from config import APPLICATIONS
from voice.text_to_speech import speak

logger = logging.getLogger("JARVIS.Applications")

def resolve_app_executable(app_name: str) -> Optional[str]:
    """
    Resolve application executable path on Windows.
    Checks configured map, common installation directories, and system PATH.
    """
    clean_name = app_name.lower().strip()
    configured_target = APPLICATIONS.get(clean_name, clean_name)

    # 1. If configured target exists directly on disk
    if os.path.exists(configured_target):
        return configured_target

    # 2. Check common installation directories for Chrome
    if "chrome" in clean_name:
        chrome_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe"),
            shutil.which("chrome"),
            shutil.which("chrome.exe")
        ]
        for p in chrome_paths:
            if p and os.path.exists(p):
                return p

    # 3. Check system PATH via shutil.which
    which_path = shutil.which(configured_target)
    if which_path:
        return which_path

    which_exe = shutil.which(f"{configured_target}.exe")
    if which_exe:
        return which_exe

    # 4. Check general Program Files and AppData locations
    program_files = [
        os.environ.get("ProgramFiles", r"C:\Program Files"),
        os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)"),
        os.environ.get("LocalAppData", os.path.expanduser(r"~\AppData\Local"))
    ]
    for pf in program_files:
        candidate = Path(pf) / configured_target
        if candidate.exists():
            return str(candidate)

    return None

def open_application(app_name: str, speaker_role: str = "Boss") -> Tuple[bool, str]:
    """
    Open configured application by alias or executable name.
    Uses safe Windows subprocess invocation without shell parsing issues for paths with spaces.
    """
    if not app_name:
        msg = f"Sorry {speaker_role}, please specify an application name."
        speak(msg)
        return False, msg

    clean_name = app_name.lower().strip()
    target = APPLICATIONS.get(clean_name, clean_name)

    logger.info(f"Attempting to open application: '{app_name}' (target: '{target}')")

    try:
        # Protocol URL launch (e.g. settings: or whatsapp:)
        if target.startswith("ms-") or target.endswith(":"):
            os.system(f'start "" "{target}"')
            msg = f"Opening {app_name}."
            speak(msg)
            return True, msg

        # Resolve actual executable path
        resolved_exe = resolve_app_executable(clean_name)
        if resolved_exe:
            logger.info(f"Launching resolved executable: '{resolved_exe}'")
            # Pass resolved path as single list item WITHOUT shell=True to handle spaces cleanly
            subprocess.Popen([resolved_exe])
            msg = f"Opening {app_name}."
            speak(msg)
            return True, msg

        # Fallback to system command launch if path wasn't explicitly resolved
        logger.info(f"Attempting fallback launch for command string: '{target}'")
        if " " in target:
            # Safely quote target command if it contains spaces
            subprocess.Popen(f'"{target}"', shell=True)
        else:
            subprocess.Popen([target])

        msg = f"Opening {app_name}."
        speak(msg)
        return True, msg

    except Exception as e:
        logger.error(f"Error opening application {app_name}: {e}")
        msg = f"Sorry {speaker_role}, I couldn't find or open that application."
        speak(msg)
        return False, msg

def close_application(app_name: str, speaker_role: str = "Boss") -> Tuple[bool, str]:
    """
    Close running process for configured application.
    Uses safe process matching by executable name.
    """
    if not app_name:
        msg = f"Sorry {speaker_role}, please specify an application to close."
        speak(msg)
        return False, msg

    clean_name = app_name.lower().strip()
    target_path = APPLICATIONS.get(clean_name, clean_name)
    exe_name = os.path.basename(target_path).lower()

    if not exe_name.endswith(".exe"):
        exe_name += ".exe"

    logger.info(f"Attempting to close process: '{exe_name}' for alias '{app_name}'")
    closed_count = 0

    try:
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                pname = proc.info['name'].lower()
                if pname == exe_name or clean_name in pname:
                    proc.terminate()
                    closed_count += 1
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        if closed_count > 0:
            msg = f"Closed {app_name}."
            speak(msg)
            return True, msg
        else:
            msg = f"Sorry {speaker_role}, {app_name} does not appear to be running."
            speak(msg)
            return False, msg

    except Exception as e:
        logger.error(f"Error closing application {app_name}: {e}")
        msg = f"Sorry {speaker_role}, I encountered an issue closing that application."
        speak(msg)
        return False, msg
