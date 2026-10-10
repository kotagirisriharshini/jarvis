import unittest
from pathlib import Path
from config import NOTES_FILE, NOTES_DIR
from features.notes import NoteManager
from features.reminders import ReminderManager
from features.email_writer import generate_email_draft
from features.applications import resolve_app_executable
from features.youtube import extract_top_video_id, play_on_youtube
from features.spotify import play_on_spotify
from features.weather import get_weather
from voice.speech_recognition import STTService

class TestFeatures(unittest.TestCase):

    def test_best_microphone_index_selection(self):
        sample_mics = [
            "Microsoft Sound Mapper - Input",
            "Microphone Array (2- Realtek(R) Audio)",
            "Speakers (2- Realtek(R) Audio)"
        ]
        idx, name = STTService.find_best_microphone_index(sample_mics)
        self.assertEqual(idx, 1)
        self.assertEqual(name, "Microphone Array (2- Realtek(R) Audio)")

    def test_chrome_resolution(self):
        resolved = resolve_app_executable("chrome")
        self.assertIsNotNone(resolved)
        self.assertTrue(Path(resolved).exists(), f"Resolved Chrome path does not exist: {resolved}")

    def test_youtube_extraction(self):
        video_id = extract_top_video_id("Believer")
        self.assertTrue(len(video_id) == 11, f"Invalid YouTube video ID extracted: '{video_id}'")
        
        success, msg = play_on_youtube("Python tutorial", "Boss")
        self.assertTrue(success)
        self.assertIn("Python tutorial", msg)

    def test_spotify_feature(self):
        # 1. Play song
        success, msg = play_on_spotify("Perfect", "Boss")
        self.assertTrue(success)
        self.assertIn("Perfect", msg)
        self.assertIn("You may need to press Play", msg)

        # 2. Open homepage
        success_home, msg_home = play_on_spotify("", "Boss")
        self.assertTrue(success_home)
        self.assertIn("Opening Spotify Web Player", msg_home)

        # 3. Search Spotify
        success_search, msg_search = play_on_spotify("search for Believer", "Boss")
        self.assertTrue(success_search)
        self.assertIn("Searching Spotify for Believer", msg_search)

    def test_seminar_permission_email(self):
        success, msg = generate_email_draft("seminar permission", "Boss")
        self.assertTrue(success)
        self.assertIn("seminar permission", msg)
        
        draft_files = list(NOTES_DIR.glob("email_draft_*.txt"))
        self.assertGreater(len(draft_files), 0)
        latest_draft = draft_files[-1]
        with open(latest_draft, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("Subject: Request for Permission to Attend Seminar / Workshop", content)

    def test_assignment_extension_email(self):
        success, msg = generate_email_draft("assignment extension", "Boss")
        self.assertTrue(success)
        self.assertIn("assignment extension", msg)
        
        draft_files = list(NOTES_DIR.glob("email_draft_*.txt"))
        self.assertGreater(len(draft_files), 0)
        latest_draft = draft_files[-1]
        with open(latest_draft, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("Subject: Request for Extension of Assignment Submission Date", content)

    def test_notes_manager(self):
        manager = NoteManager()
        success, msg = manager.add_note("Test DBMS assignment note", "Boss")
        self.assertTrue(success)
        self.assertTrue(NOTES_FILE.exists())
        
        with open(NOTES_FILE, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("Test DBMS assignment note", content)

    def test_reminder_parser(self):
        manager = ReminderManager()
        secs, task = manager.parse_time_duration("remind me in 10 minutes to study DBMS")
        self.assertEqual(secs, 600)
        self.assertEqual(task, "study dbms")

    def test_weather_feature(self):
        success, msg = get_weather("Hyderabad", "Boss")
        self.assertTrue(success)
        self.assertIn("Hyderabad", msg)
        self.assertIn("temperature", msg.lower())

if __name__ == "__main__":
    unittest.main()
