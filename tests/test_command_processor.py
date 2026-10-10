import unittest
from core.command_processor import CommandProcessor

class TestCommandProcessor(unittest.TestCase):

    def setUp(self):
        self.processor = CommandProcessor()

    def test_open_app(self):
        intent = self.processor.parse("open chrome")
        self.assertEqual(intent.intent_type, "OPEN_APP")
        self.assertEqual(intent.parameter, "chrome")

    def test_close_app(self):
        intent = self.processor.parse("close notepad")
        self.assertEqual(intent.intent_type, "CLOSE_APP")
        self.assertEqual(intent.parameter, "notepad")

    def test_youtube_search(self):
        intent1 = self.processor.parse("play python tutorial on youtube")
        self.assertEqual(intent1.intent_type, "YOUTUBE_SEARCH")
        self.assertIn("python tutorial", intent1.parameter)

        intent2 = self.processor.parse("play believer")
        self.assertEqual(intent2.intent_type, "YOUTUBE_SEARCH")
        self.assertEqual(intent2.parameter, "believer")

        intent3 = self.processor.parse("play python tutorial")
        self.assertEqual(intent3.intent_type, "YOUTUBE_SEARCH")
        self.assertEqual(intent3.parameter, "python tutorial")

        intent4 = self.processor.parse("search youtube for dbms tutorials")
        self.assertEqual(intent4.intent_type, "YOUTUBE_SEARCH")
        self.assertIn("dbms tutorials", intent4.parameter)

    def test_youtube_open_homepage(self):
        intent1 = self.processor.parse("open youtube")
        self.assertEqual(intent1.intent_type, "OPEN_WEBSITE")
        self.assertEqual(intent1.parameter, "youtube")

        intent2 = self.processor.parse("open youtube homepage")
        self.assertEqual(intent2.intent_type, "OPEN_WEBSITE")
        self.assertEqual(intent2.parameter, "youtube")

        intent3 = self.processor.parse("play bigg boss promo on youtube")
        self.assertEqual(intent3.intent_type, "YOUTUBE_SEARCH")
        self.assertEqual(intent3.parameter, "bigg boss promo")

    def test_spotify_intents(self):
        # Song extraction
        intent1 = self.processor.parse("play perfect on spotify")
        self.assertEqual(intent1.intent_type, "SPOTIFY_PLAY")
        self.assertEqual(intent1.parameter, "perfect")
        self.assertNotEqual(intent1.intent_type, "YOUTUBE_SEARCH")

        intent2 = self.processor.parse("play Perfect in spotify")
        self.assertEqual(intent2.intent_type, "SPOTIFY_PLAY")
        self.assertEqual(intent2.parameter, "perfect")

        intent3 = self.processor.parse("spotify play Perfect")
        self.assertEqual(intent3.intent_type, "SPOTIFY_PLAY")
        self.assertEqual(intent3.parameter, "perfect")

        # Artist + Song extraction
        intent4 = self.processor.parse("play perfect by ed sheeran on spotify")
        self.assertEqual(intent4.intent_type, "SPOTIFY_PLAY")
        self.assertEqual(intent4.parameter, "perfect by ed sheeran")

        # Open Spotify homepage
        intent5 = self.processor.parse("open spotify")
        self.assertEqual(intent5.intent_type, "SPOTIFY_PLAY")
        self.assertEqual(intent5.parameter, "")

        intent6 = self.processor.parse("launch spotify")
        self.assertEqual(intent6.intent_type, "SPOTIFY_PLAY")
        self.assertEqual(intent6.parameter, "")

        # Search Spotify for ...
        intent7 = self.processor.parse("search spotify for ed sheeran")
        self.assertEqual(intent7.intent_type, "SPOTIFY_PLAY")
        self.assertIn("search for ed sheeran", intent7.parameter)

        # Empty / Malformed
        intent8 = self.processor.parse("spotify")
        self.assertEqual(intent8.intent_type, "SPOTIFY_PLAY")
        self.assertEqual(intent8.parameter, "")

    def test_email_writer_intents(self):
        email_phrases = [
            "Write an email for sick leave for college",
            "Write an email for seminar permission",
            "Email for seminar permission",
            "Create an email for seminar permission",
            "I need an email for seminar permission",
            "Write a seminar permission email",
            "I need to write an email asking for seminar permission",
            "Write an email for assignment extension",
            "Email for assignment extension",
            "I need an assignment extension email",
            "Create an assignment extension email"
        ]
        for phrase in email_phrases:
            intent = self.processor.parse(phrase)
            self.assertEqual(intent.intent_type, "EMAIL_DRAFT", f"Failed for phrase: '{phrase}'")
            self.assertTrue(len(intent.parameter) > 0, f"Empty topic for phrase: '{phrase}'")

    def test_weather_intents(self):
        intent1 = self.processor.parse("what's the weather in hyderabad")
        self.assertEqual(intent1.intent_type, "WEATHER")
        self.assertEqual(intent1.parameter, "hyderabad")

        intent2 = self.processor.parse("weather in karimnagar")
        self.assertEqual(intent2.intent_type, "WEATHER")
        self.assertEqual(intent2.parameter, "karimnagar")

        intent3 = self.processor.parse("weather in london")
        self.assertEqual(intent3.intent_type, "WEATHER")
        self.assertEqual(intent3.parameter, "london")

    def test_google_search(self):
        intent = self.processor.parse("search google for artificial intelligence")
        self.assertEqual(intent.intent_type, "GOOGLE_SEARCH")
        self.assertEqual(intent.parameter, "artificial intelligence")

    def test_time_and_date(self):
        intent_time = self.processor.parse("what time is it")
        self.assertEqual(intent_time.intent_type, "GET_TIME")
        
        intent_date = self.processor.parse("what is today's date")
        self.assertEqual(intent_date.intent_type, "GET_DATE")

    def test_calculator_intent(self):
        intent = self.processor.parse("calculate 25 plus 50")
        self.assertEqual(intent.intent_type, "CALCULATE")
        self.assertIn("25 plus 50", intent.parameter)

    def test_battery_and_system(self):
        intent_bat = self.processor.parse("what is my battery percentage")
        self.assertEqual(intent_bat.intent_type, "BATTERY_STATUS")

        intent_sys = self.processor.parse("what is my cpu usage")
        self.assertEqual(intent_sys.intent_type, "SYSTEM_INFO")

    def test_screenshot(self):
        intent = self.processor.parse("take a screenshot")
        self.assertEqual(intent.intent_type, "TAKE_SCREENSHOT")

    def test_safety_guard(self):
        intent = self.processor.parse("shutdown system")
        self.assertEqual(intent.intent_type, "SYSTEM_SHUTDOWN")
        self.assertTrue(intent.requires_confirmation)

if __name__ == "__main__":
    unittest.main()
