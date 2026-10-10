# J.A.R.V.I.S. – Intelligent Desktop Voice Assistant

J.A.R.V.I.S. is a modular, lightweight Python-based desktop voice assistant inspired by Iron Man's artificial intelligence assistant. It accepts spoken commands, recognizes whether the speaker is the registered **"Boss"** or another user, provides text-to-speech audio responses, and performs useful desktop automation tasks on Windows.

> **CRITICAL REQUIREMENT**: J.A.R.V.I.S. runs completely independently of Antigravity IDE. It can be started directly from any standard Windows Command Prompt or PowerShell environment.

---

## 🌟 Key Features

1. **Continuous Voice Input & Wake Word Detection**:
   - Listens continuously for wake words (`"Hey JARVIS"` or `"JARVIS"`).
   - Features a lightweight standby mode (`"Go to sleep"`) and wake listener.
2. **Boss Speaker Recognition & Personalized Greetings**:
   - Interactive enrollment wizard to register the Boss voice profile (`python main.py --setup`).
   - Acoustic spectral feature extraction comparing speakers against `data/voice_profiles/boss_profile.npy`.
   - Time-aware greetings (Morning, Afternoon, Evening, Night) customized for "Boss" vs "Other".
3. **Text-to-Speech (TTS)**:
   - Centralized offline speech output (`pyttsx3`) with configurable speed, volume, and voice selection.
4. **Spotify Integration**:
   - Open Spotify and search songs/artists (`"Play Perfect on Spotify"`, `"Open Spotify"`).
   - Never requests or stores Spotify account passwords.
5. **Email Draft Generator**:
   - Generates formal college/work email drafts (`"Write an email for sick leave for college"`, `"Write an email for seminar permission"`).
   - Opens draft in Windows Notepad with placeholders filled for user review. Never sends emails automatically.
6. **Enhanced Weather Reporting**:
   - Arbitrary location weather queries (`"What's the weather in Hyderabad?"`, `"Weather in Karimnagar"`).
   - Reports temperature, weather condition, feels-like temperature, humidity, and wind speed via OpenWeatherMap API (or `wttr.in` fallback).
7. **YouTube Search & Playback**:
   - Natural playback commands (`"Play Believer"`, `"Play Python tutorial on YouTube"`).
8. **Application Management**:
   - Open Windows applications (`Chrome`, `VS Code`, `Notepad`, `Calculator`, `File Explorer`, `CMD`, `Settings`, `WhatsApp`, `Spotify`).
   - Safely terminate running configured processes by process name (`psutil`).
9. **Safe AST Calculator**:
   - Evaluates math expressions (`"Calculate 25 plus 50"`, `"100 divided by 4"`) safely via AST parsing without using `eval()`.
10. **System Diagnostics & Battery**:
    - Check battery percentage & charger status (`"What's my battery percentage?"`).
    - Check CPU usage, RAM utilization, storage space, and OS information.
11. **Screenshots & Voice Notes**:
    - Capture screen and save timestamped image (`data/screenshots/screenshot_YYYYMMDD_HHMMSS.png`).
    - Record voice notes saved with date/time stamps in `data/notes/notes.txt`.
12. **Threaded Voice Reminders**:
    - Schedule local background reminders (`"Remind me in 10 minutes to study DBMS"`).
13. **Windows Media Controls**:
    - Play, pause, next track, previous track, volume up/down, mute.
14. **Safety Confirmation Safeguards**:
    - High-risk operations (such as system shutdown) require explicit voice confirmation (`"Please say confirm"`).

---

## 🏗️ Project Architecture

```
JARVIS/
├── main.py                     # Entry point & CLI launcher
├── config.py                   # Central configuration & paths
├── requirements.txt            # Python dependencies
├── README.md                   # Documentation
├── .env.example                # Template for environment variables
├── .gitignore                  # Git exclusions
├── JARVIS.spec                 # PyInstaller packaging specification
│
├── core/                       # Assistant core logic
│   ├── assistant.py            # Assistant controller & loop manager
│   ├── command_processor.py    # Intent parsing & safety guards
│   └── responses.py            # Time-aware response generator
│
├── voice/                      # Voice & audio processing
│   ├── text_to_speech.py       # Offline pyttsx3 TTS engine
│   ├── speech_recognition.py   # Speech-to-text audio capture
│   ├── wake_word.py            # Wake-word listener ("Hey JARVIS")
│   └── speaker_recognition.py  # Boss voice enrollment & acoustic feature verifier
│
├── features/                   # Task & system automation handlers
│   ├── applications.py         # App launcher & safe process termination
│   ├── browser.py              # Website opener & Google search
│   ├── youtube.py              # YouTube query search
│   ├── spotify.py              # Spotify player launch & song query search
│   ├── email_writer.py        # Formal email draft generator & Notepad opener
│   ├── calculator.py           # Safe AST math parser
│   ├── system_info.py          # Battery, CPU, RAM & storage diagnostic metrics
│   ├── screenshot.py           # Screen capture
│   ├── notes.py                # Voice notes logger
│   ├── reminders.py            # Threaded timer reminders
│   ├── media_control.py        # Windows media key simulation
│   ├── file_manager.py         # System folder navigator
│   └── weather.py              # Enhanced weather reporting (wttr.in / OpenWeatherMap)
│
├── data/                       # Persistent local storage
│   ├── notes/
│   ├── screenshots/
│   ├── reminders/
│   └── voice_profiles/
│
├── logs/
│   └── jarvis.log              # Technical event log
│
└── tests/                      # Automated unit test suite
    ├── test_command_processor.py
    ├── test_calculator.py
    └── test_features.py
```

---

## 💻 System Requirements & Installation

### Requirements
- **Operating System**: Windows 10 or 11 (64-bit)
- **Python**: Python 3.10 to 3.13
- **Audio Hardware**: Functional microphone and speakers/headphones

### 1. Clone or Download Project
Navigate to your desired workspace folder:
```powershell
cd C:\Users\harsh\.gemini\antigravity\scratch\JARVIS
```

### 2. Create Virtual Environment (Recommended)
```powershell
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies
```powershell
pip install -r requirements.txt
```

---

## 🎙️ Boss Voice Enrollment (First-Time Setup)

Run the interactive setup wizard to register your Boss voice profile:

```powershell
python main.py --setup
```

1. The setup wizard will test audio output.
2. It will prompt you to record 3 short voice samples.
3. Acoustic feature vectors are stored locally in `data/voice_profiles/boss_profile.npy`.

> ⚠️ **SECURITY DISCLAIMER**: Speaker recognition is implemented for personalization ("Boss" vs "Other") and demonstration purposes. It should not be considered a secure biometric authentication mechanism.

---

## 🚀 Running JARVIS Outside Antigravity IDE

You do **NOT** need Antigravity IDE open to run JARVIS.

1. Open **Command Prompt** (`cmd.exe`) or **PowerShell**.
2. Navigate to the project directory:
   ```powershell
   cd C:\Users\harsh\.gemini\antigravity\scratch\JARVIS
   ```
3. Activate virtual environment (if created):
   ```powershell
   venv\Scripts\activate
   ```
4. Start J.A.R.V.I.S.:
   ```powershell
   python main.py
   ```

---

## 🗣️ Supported Spoken Commands

| Category | Example Voice Commands |
| :--- | :--- |
| **Wake Word** | `"Hey JARVIS"`, `"JARVIS"` |
| **Spotify** | `"Play Perfect on Spotify"`, `"Open Spotify"`, `"Play Believer on Spotify"` |
| **Email Writer** | `"Write an email for sick leave for college"`, `"Write an email for leave request to HOD"`, `"Write an email for seminar permission"`, `"Write an email for assignment extension"` |
| **Weather** | `"What's the weather in Hyderabad?"`, `"Weather in Karimnagar"`, `"What's the weather in Delhi?"`, `"Weather in London"` |
| **YouTube** | `"Play Believer"`, `"Play Python tutorial on YouTube"`, `"Search YouTube for DBMS tutorials"` |
| **Applications** | `"Open Chrome"`, `"Open VS Code"`, `"Open Notepad"`, `"Close Notepad"` |
| **Websites** | `"Open YouTube"`, `"Open Google"`, `"Open GitHub"`, `"Open ChatGPT"` |
| **Google Search** | `"Search Google for artificial intelligence"`, `"Search for DBMS normalization"` |
| **Time & Date** | `"What time is it?"`, `"What is today's date?"` |
| **Calculator** | `"Calculate 25 plus 50"`, `"What is 100 divided by 4?"` |
| **Battery & System**| `"What's my battery percentage?"`, `"What's my CPU usage?"`, `"System info"` |
| **Screenshot** | `"Take a screenshot"`, `"Capture my screen"` |
| **Voice Notes** | `"Take a note"`, `"Read my notes"` |
| **Reminders** | `"Remind me in 10 minutes to study DBMS"` |
| **Media Controls** | `"Play music"`, `"Pause music"`, `"Next song"`, `"Volume up"`, `"Mute"` |
| **Files & Folders** | `"Open Downloads"`, `"Open Documents"`, `"Open Desktop"` |
| **Internet Check** | `"Check my internet"` |
| **Standby & Exit** | `"Go to sleep"`, `"Shutdown JARVIS"`, `"Exit"` |

---

## 🧪 Running Unit Tests

Run the automated test suite to verify system integrity:

```powershell
python -m unittest discover -s tests -p "test_*.py"
```

Or run diagnostic checks:
```powershell
python main.py --test
```

---

## 📦 Building Standalone Executable (.exe)

To bundle J.A.R.V.I.S. into a standalone Windows `.exe` using PyInstaller:

1. Install PyInstaller:
   ```powershell
   pip install pyinstaller
   ```
2. Build executable using provided `JARVIS.spec`:
   ```powershell
   pyinstaller JARVIS.spec
   ```
3. The compiled binary will be available in `dist/JARVIS.exe`.

---

## 🔧 Troubleshooting

- **Microphone Not Detected**: Ensure your default Windows recording device is enabled in Windows Sound Settings (`mmsys.cpl`).
- **Offline Speech Recognition**: If internet is disconnected, JARVIS falls back to command line prompt or local audio capture.
- **Permission Errors**: Run Command Prompt or PowerShell as Administrator if Windows app execution is restricted.
