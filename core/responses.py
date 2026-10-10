import random
import datetime
import pyjokes

# Boss Greetings by Time of Day
BOSS_GREETINGS = {
    "morning": ["Good morning, Boss.", "Good morning, Boss. All systems online.", "Welcome back, Boss. Ready for commands."],
    "afternoon": ["Good afternoon, Boss.", "Good afternoon, Boss. How may I assist you?", "At your service, Boss."],
    "evening": ["Good evening, Boss.", "Good evening, Boss. Systems operational.", "Welcome back, Boss."],
    "night": ["Good night, Boss.", "Good evening, Boss. Running late night diagnostics.", "At your service, Boss."]
}

OTHER_GREETINGS = [
    "Hello. How can I help you?",
    "Hello. How may I assist you today?",
    "Greetings. What can I do for you?"
]

PREDEFINED_ANSWERS = {
    "identity": "I am J.A.R.V.I.S., your personal intelligent voice assistant.",
    "creator": "I was created as a Python voice assistant project, inspired by Iron Man.",
    "intelligence": "I'm constantly learning and expanding my system capabilities, Boss.",
    "thanks": ["You're welcome, Boss.", "Happy to help, Boss.", "Anytime, Boss.", "My pleasure."],
    "thanks_other": ["You're welcome.", "Glad to help.", "Happy to assist."]
}

def get_time_period() -> str:
    """Determine current time period (morning, afternoon, evening, night)."""
    hour = datetime.datetime.now().hour
    if 5 <= hour < 12:
        return "morning"
    elif 12 <= hour < 17:
        return "afternoon"
    elif 17 <= hour < 22:
        return "evening"
    else:
        return "night"

def get_greeting(speaker_role: str = "Boss") -> str:
    """Generate time-aware greeting based on speaker role."""
    if speaker_role.lower() == "boss":
        period = get_time_period()
        return random.choice(BOSS_GREETINGS[period])
    else:
        return random.choice(OTHER_GREETINGS)

def get_joke() -> str:
    """Return a joke using pyjokes or a standard fallback."""
    try:
        joke = pyjokes.get_joke(category="neutral")
        return joke
    except Exception:
        fallback_jokes = [
            "Why do programmers prefer dark mode? Because light attracts bugs!",
            "There are 10 types of people in the world: those who understand binary, and those who don't.",
            "Why did the Python developer sell his house? Because he had too many indentation errors!"
        ]
        return random.choice(fallback_jokes)
