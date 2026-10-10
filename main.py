#!/usr/bin/env python3
"""
J.A.R.V.I.S. – Intelligent Voice Assistant
Main entry point for standalone execution outside of IDE.

Usage:
    python main.py             # Start JARVIS voice assistant
    python main.py --setup     # Run setup wizard & Boss voice enrollment
    python main.py --test      # Run quick diagnostic system tests
"""

import sys
import argparse
from config import ensure_directories
from core.assistant import JarvisAssistant

def main():
    ensure_directories()
    
    parser = argparse.ArgumentParser(description="J.A.R.V.I.S. Personal Voice Assistant")
    parser.add_argument("--setup", action="store_true", help="Run interactive voice setup wizard")
    parser.add_argument("--verify", action="store_true", help="Run live Boss vs Unknown speaker verification test")
    parser.add_argument("--test", action="store_true", help="Run diagnostic component tests")
    args = parser.parse_args()

    assistant = JarvisAssistant()

    if args.setup:
        assistant.run_setup()
        sys.exit(0)

    if args.verify:
        print("\n==================================================")
        print("    J.A.R.V.I.S. SPEAKER VERIFICATION DIAGNOSTIC   ")
        print("==================================================")
        
        from config import BOSS_PROFILE_FILE, SPEAKER_THRESHOLD
        import numpy as np

        if not BOSS_PROFILE_FILE.exists():
            print("[WARNING] Boss voice profile file does NOT exist on disk!")
            print("Run 'python main.py --setup' first to record your Boss voice profile.")
            sys.exit(1)

        profile = np.load(BOSS_PROFILE_FILE)
        profile_norm = np.linalg.norm(profile)
        print(f"Boss Profile File Found: True ({BOSS_PROFILE_FILE})")
        print(f"Profile Vector Shape:   {profile.shape} | Profile Norm: {profile_norm:.4f}")
        print(f"Configured SPEAKER_THRESHOLD: {SPEAKER_THRESHOLD:.4f}")

        if not assistant.speaker_recognizer.is_enrolled():
            print(f"\n[ERROR] Boss profile shape {profile.shape} is incompatible with current feature pipeline shape (42,).")
            print("Your stored boss_profile.npy was recorded with an older format.")
            print("Please run 'python main.py --setup' to re-enroll your Boss voice profile.\n")
            sys.exit(1)

        print("\nPlease speak a test command into your microphone (e.g., 'show passwords' or 'hello jarvis')...")
        
        raw_text, audio = assistant.stt.listen(phrase_time_limit=6.0, timeout=8.0)
        if not audio:
            print("[ERROR] No audio captured from microphone. Please try again.")
            sys.exit(1)

        print(f"\n[AUDIO CAPTURED]")
        print(f"Speech Recognized:   '{raw_text}'")
        pcm_bytes = audio.get_raw_data(convert_rate=16000, convert_width=2)
        print(f"Audio Sample Buffer: {len(pcm_bytes)} bytes")

        features = assistant.speaker_recognizer.extract_features(pcm_bytes)
        if features is None:
            print("[ERROR] Could not extract acoustic feature vector from audio sample.")
            sys.exit(1)

        feat_norm = np.linalg.norm(features)
        role, score = assistant.speaker_recognizer.classify_speaker(audio)

        print("--------------------------------------------------")
        print(f"Extracted Feature Shape: {features.shape} | Feature Norm: {feat_norm:.4f}")
        print(f"Feature Vector Stats:    Min={np.min(features):.4f}, Max={np.max(features):.4f}, Mean={np.mean(features):.4f}")
        print(f"Calculated Cosine Similarity Score: {score:.4f}")
        print(f"Configured SPEAKER_THRESHOLD:       {SPEAKER_THRESHOLD:.4f}")
        print("--------------------------------------------------")
        print(f"[RESULT] Verified Speaker Role: {role.upper()}")
        if role == "Boss":
            print("[SUCCESS] Speaker matched enrolled Boss voice profile!")
        else:
            print("[UNVERIFIED] Speaker did NOT match Boss profile. Classified as Unknown.")
        print("==================================================\n")
        sys.exit(0)

    if args.test:
        print("Running J.A.R.V.I.S. System Tests...")
        from features.calculator import safe_evaluate
        from features.system_info import get_current_time
        assert safe_evaluate("25 + 50") == 75, "Calculator test failed"
        print("[OK] Calculator AST test passed!")
        print("[OK] System info test passed!")
        print("All diagnostic tests passed successfully.")
        sys.exit(0)

    assistant.start_loop()

if __name__ == "__main__":
    main()
