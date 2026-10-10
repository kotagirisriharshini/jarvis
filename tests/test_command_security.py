import unittest
from unittest.mock import patch, MagicMock
import numpy as np

from core.command_processor import CommandProcessor, CommandIntent
from core.assistant import JarvisAssistant
from voice.speaker_recognition import SpeakerRecognizer

class TestCommandSecurity(unittest.TestCase):

    def setUp(self):
        self.processor = CommandProcessor()
        self.assistant = JarvisAssistant()

    def test_sensitive_command_intent_parsing(self):
        """Verify sensitive vs normal command intent classification."""
        # Normal commands
        normal_phrases = [
            "what's the weather in hyderabad",
            "calculate 25 plus 50",
            "play believer on youtube",
            "play perfect on spotify",
            "open chrome",
            "write an email for sick leave for college",
            "what time is it",
            "take a note"
        ]
        for phrase in normal_phrases:
            intent = self.processor.parse(phrase)
            self.assertFalse(intent.is_sensitive, f"Phrase incorrectly marked as sensitive: '{phrase}'")

        # Sensitive commands
        sensitive_phrases = [
            "show my passwords",
            "view api keys and secrets",
            "open security settings",
            "access private files",
            "delete all notes",
            "delete important files",
            "send email to professor",
            "shutdown computer"
        ]
        for phrase in sensitive_phrases:
            intent = self.processor.parse(phrase)
            self.assertTrue(intent.is_sensitive, f"Phrase incorrectly marked as normal: '{phrase}'")

    @patch("core.assistant.speak")
    def test_case_a_unknown_speaker_normal_command(self, mock_speak):
        """A. Unknown speaker + normal command -> command is allowed."""
        intent = self.processor.parse("what's the weather in hyderabad")
        self.assertFalse(intent.is_sensitive)
        
        result = self.assistant.handle_intent(intent, role="Unknown")
        self.assertTrue(result)
        # Should not reject with security error
        for call_arg in mock_speak.call_args_list:
            spoken_text = call_arg[0][0]
            self.assertNotIn("Boss verification is required", spoken_text)

    @patch("core.assistant.speak")
    def test_case_b_unknown_speaker_sensitive_command(self, mock_speak):
        """B. Unknown speaker + sensitive command -> command is rejected."""
        intent = self.processor.parse("show my passwords")
        self.assertTrue(intent.is_sensitive)
        
        result = self.assistant.handle_intent(intent, role="Unknown")
        self.assertTrue(result)
        
        # Verify rejection response spoken
        mock_speak.assert_called_with("Sorry, Boss verification is required for this command.")

    @patch("core.assistant.speak")
    def test_case_c_boss_speaker_normal_command(self, mock_speak):
        """C. Boss speaker + normal command -> command is allowed."""
        intent = self.processor.parse("calculate 10 plus 20")
        self.assertFalse(intent.is_sensitive)
        
        result = self.assistant.handle_intent(intent, role="Boss")
        self.assertTrue(result)
        for call_arg in mock_speak.call_args_list:
            spoken_text = call_arg[0][0]
            self.assertNotIn("Boss verification is required", spoken_text)

    @patch("core.assistant.speak")
    def test_case_d_boss_speaker_sensitive_command(self, mock_speak):
        """D. Boss speaker + sensitive command -> command is allowed after verification."""
        intent = self.processor.parse("open security settings")
        self.assertTrue(intent.is_sensitive)
        
        result = self.assistant.handle_intent(intent, role="Boss")
        self.assertTrue(result)
        
        # Should execute sensitive handler for Boss
        mock_speak.assert_called_with("Opening system security settings for Boss.")

    @patch("core.assistant.speak")
    def test_case_e_uncertain_speaker_verification(self, mock_speak):
        """E. Failed/uncertain speaker verification -> command is rejected."""
        recognizer = SpeakerRecognizer()
        
        # Simulate uncertain audio (low similarity or short audio)
        role, score = recognizer.classify_speaker(audio_data=None)
        self.assertEqual(role, "Unknown")
        self.assertEqual(score, 0.0)
        
        intent = self.processor.parse("delete important files")
        self.assertTrue(intent.is_sensitive)
        
        # Execute with resolved role from uncertain verification
        result = self.assistant.handle_intent(intent, role=role)
        self.assertTrue(result)
        mock_speak.assert_called_with("Sorry, Boss verification is required for this command.")

    def test_speaker_verification_threshold_decision_boundary(self):
        """Verify speaker classification above threshold yields Boss and below threshold yields Unknown."""
        recognizer = SpeakerRecognizer()
        mock_profile = np.ones(42) / np.sqrt(42)
        recognizer.boss_profile = mock_profile

        # 1. High similarity (> threshold 0.55) -> Boss
        high_sim_features = mock_profile * 0.9 + np.zeros(42) * 0.1
        high_sim_features = high_sim_features / np.linalg.norm(high_sim_features)
        
        with patch.object(recognizer, "is_enrolled", return_value=True), \
             patch.object(recognizer, "extract_features", return_value=high_sim_features):
            mock_audio = MagicMock()
            mock_audio.get_raw_data.return_value = b"\x00" * 3200
            role, score = recognizer.classify_speaker(mock_audio)
            self.assertEqual(role, "Boss")
            self.assertGreaterEqual(score, 0.55)

        # 2. Low similarity (< threshold 0.55) -> Unknown
        low_sim_features = np.array([-1.0 if i % 2 == 0 else 1.0 for i in range(42)], dtype=np.float32)
        low_sim_features = low_sim_features / np.linalg.norm(low_sim_features)
        
        with patch.object(recognizer, "is_enrolled", return_value=True), \
             patch.object(recognizer, "extract_features", return_value=low_sim_features):
            mock_audio = MagicMock()
            mock_audio.get_raw_data.return_value = b"\x00" * 3200
            role, score = recognizer.classify_speaker(mock_audio)
            self.assertEqual(role, "Unknown")
            self.assertLess(score, 0.55)

    def test_speaker_recognizer_never_fails_open(self):
        """Verify SpeakerRecognizer never defaults to Boss without valid profile and score."""
        recognizer = SpeakerRecognizer()
        
        # Unenrolled / null input returns Unknown
        with patch.object(recognizer, "is_enrolled", return_value=False):
            role, score = recognizer.classify_speaker(None)
            self.assertEqual(role, "Unknown")
            self.assertEqual(score, 0.0)

        # Enrolled but null audio returns Unknown
        with patch.object(recognizer, "is_enrolled", return_value=True):
            role, score = recognizer.classify_speaker(None)
            self.assertEqual(role, "Unknown")
            self.assertEqual(score, 0.0)

if __name__ == "__main__":
    unittest.main()
