import os
import platform
import datetime
import logging
import psutil
from typing import Tuple

from voice.text_to_speech import speak

logger = logging.getLogger("JARVIS.SystemInfo")

def get_current_time() -> str:
    """Return formatted spoken current time string."""
    now = datetime.datetime.now()
    time_str = now.strftime("%I:%M %p")
    # Remove leading zero in hour for natural speech
    if time_str.startswith("0"):
        time_str = time_str[1:]
    msg = f"The current time is {time_str}."
    speak(msg)
    return msg

def get_current_date() -> str:
    """Return formatted spoken date string."""
    now = datetime.datetime.now()
    day_name = now.strftime("%A")
    month_name = now.strftime("%B")
    day_num = now.day
    
    # Ordinal suffix for day number
    if 11 <= day_num <= 13:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(day_num % 10, "th")
        
    date_str = f"{day_name}, {month_name} {day_num}{suffix}, {now.year}"
    msg = f"Today is {date_str}."
    speak(msg)
    return msg

def get_battery_status(speaker_role: str = "Boss") -> Tuple[bool, str]:
    """Retrieve system battery percentage and charging status using psutil."""
    try:
        battery = psutil.sensors_battery()
        if battery is None:
            msg = f"{speaker_role}, your device does not have a battery sensor or power status is unavailable."
            speak(msg)
            return False, msg

        percent = int(battery.percent)
        is_plugged = battery.power_plugged

        if is_plugged:
            msg = f"{speaker_role}, your battery is at {percent} percent and the charger is connected."
        else:
            msg = f"{speaker_role}, your battery is at {percent} percent."

        speak(msg)
        return True, msg

    except Exception as e:
        logger.error(f"Error checking battery status: {e}")
        msg = f"Sorry {speaker_role}, I couldn't retrieve battery information."
        speak(msg)
        return False, msg

def get_system_metrics(speaker_role: str = "Boss") -> Tuple[bool, str]:
    """Retrieve CPU usage, RAM utilization, Disk storage, and OS info."""
    try:
        cpu_usage = psutil.cpu_percent(interval=0.5)
        ram = psutil.virtual_memory()
        disk = psutil.disk_usage('C:\\' if os.name == 'nt' else '/')
        os_info = f"{platform.system()} {platform.release()}"

        ram_used_gb = ram.used / (1024 ** 3)
        ram_total_gb = ram.total / (1024 ** 3)
        disk_free_gb = disk.free / (1024 ** 3)

        msg = (
            f"{speaker_role}, CPU usage is currently at {cpu_usage:.1f} percent. "
            f"RAM usage is {ram.percent:.1f} percent, using {ram_used_gb:.1f} of {ram_total_gb:.1f} gigabytes. "
            f"Storage has {disk_free_gb:.1f} gigabytes free on operating system drive {os_info}."
        )
        
        speak(msg)
        return True, msg

    except Exception as e:
        logger.error(f"Error checking system info: {e}")
        msg = f"Sorry {speaker_role}, I couldn't retrieve system diagnostic metrics."
        speak(msg)
        return False, msg
