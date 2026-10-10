import os
import logging
import numpy as np
from scipy.signal import welch
from scipy.fftpack import dct
from typing import Tuple, Optional
import speech_recognition as sr

from config import BOSS_PROFILE_FILE, SPEAKER_THRESHOLD, AUDIO_SAMPLE_RATE, ENROLLMENT_SAMPLES, VOICE_PROFILES_DIR
from voice.text_to_speech import speak

logger = logging.getLogger("JARVIS.SpeakerRecognition")

# Security Disclaimer Notice
SECURITY_DISCLAIMER = (
    "Voice recognition is for personalization and demonstration purposes "
    "and should not be considered secure authentication."
)

FEATURE_VECTOR_DIM = 42

def _hz_to_mel(hz: float) -> float:
    return 2595.0 * np.log10(1.0 + hz / 700.0)

def _mel_to_hz(mel: float) -> float:
    return 700.0 * (10.0 ** (mel / 2595.0) - 1.0)

def _get_mel_filterbank(num_filters: int = 20, nfft: int = 512, sample_rate: int = 16000) -> np.ndarray:
    low_mel = _hz_to_mel(100.0)
    high_mel = _hz_to_mel(sample_rate / 2.0)
    mels = np.linspace(low_mel, high_mel, num_filters + 2)
    bin_pts = np.floor((nfft + 1) * _mel_to_hz(mels) / sample_rate).astype(int)
    fbank = np.zeros((num_filters, int(nfft // 2 + 1)))
    for m in range(1, num_filters + 1):
        for k in range(bin_pts[m - 1], bin_pts[m]):
            fbank[m - 1, k] = (k - bin_pts[m - 1]) / max(1, bin_pts[m] - bin_pts[m - 1])
        for k in range(bin_pts[m], bin_pts[m + 1]):
            fbank[m - 1, k] = (bin_pts[m + 1] - k) / max(1, bin_pts[m + 1] - bin_pts[m])
    return fbank

def _extract_pitch_f0(audio_array: np.ndarray, sample_rate: int = 16000) -> Tuple[float, float]:
    """
    Extract fundamental pitch F0 (Hz) median and std across voiced speech frames using autocorrelation.
    Returns (f0_median, f0_std).
    """
    win_len = int(sample_rate * 0.030)  # 30ms window
    shift = int(sample_rate * 0.015)    # 15ms shift
    min_lag = int(sample_rate / 400.0)  # Max pitch 400 Hz (~40 samples @ 16kHz)
    max_lag = int(sample_rate / 60.0)   # Min pitch 60 Hz (~266 samples @ 16kHz)
    
    max_amp = np.max(np.abs(audio_array))
    if max_amp == 0:
        return 0.0, 0.0

    energy_thresh = max_amp * 0.05
    pitches = []

    for start in range(0, len(audio_array) - win_len, shift):
        frame = audio_array[start : start + win_len]
        if np.max(np.abs(frame)) < energy_thresh:
            continue
        
        frame_centered = frame - np.mean(frame)
        n_fft = 2 ** int(np.ceil(np.log2(2 * win_len)))
        fft_f = np.fft.rfft(frame_centered, n=n_fft)
        autocorr = np.fft.irfft(fft_f * np.conj(fft_f))[:win_len]
        
        if autocorr[0] <= 1e-8:
            continue
            
        autocorr_norm = autocorr / autocorr[0]
        
        if max_lag < len(autocorr_norm):
            search_region = autocorr_norm[min_lag:max_lag]
            if len(search_region) > 0:
                best_lag = min_lag + np.argmax(search_region)
                peak_val = autocorr_norm[best_lag]
                if peak_val > 0.25:
                    f0 = sample_rate / float(best_lag)
                    pitches.append(f0)

    if not pitches:
        return 0.0, 0.0

    return float(np.median(pitches)), float(np.std(pitches))

class SpeakerRecognizer:
    """
    Modular acoustic feature extractor and speaker classifier for Boss identification.
    Uses multi-block normalized sub-vector pipeline:
      - Block 1: Zero-mean MFCC means (12 dims)
      - Block 2: MFCC standard deviations (12 dims)
      - Block 3: Delta MFCC means (12 dims)
      - Block 4: Pitch F0 & Spectral distribution stats (6 dims)
    Total dimension: 42. Prevents C1 energy bias domination.
    """

    def __init__(self):
        VOICE_PROFILES_DIR.mkdir(parents=True, exist_ok=True)
        self.boss_profile: Optional[np.ndarray] = None
        self.load_profile()

    def extract_features(self, pcm_data: bytes, sample_rate: int = 16000) -> Optional[np.ndarray]:
        """
        Extract robust 42-dimensional multi-block normalized acoustic feature vector.
        """
        if not pcm_data:
            return None
        
        try:
            audio_array = np.frombuffer(pcm_data, dtype=np.int16).astype(np.float32)
            if len(audio_array) < sample_rate * 0.2:
                return None

            max_amp = np.max(np.abs(audio_array))
            if max_amp == 0:
                return None

            win_len = int(sample_rate * 0.025)
            shift = int(sample_rate * 0.010)
            energy_thresh = max_amp * 0.05
            
            fbank = _get_mel_filterbank(num_filters=20, nfft=512, sample_rate=sample_rate)
            freqs = np.fft.rfftfreq(512, 1.0 / sample_rate)
            
            mfccs = []
            centroids = []
            bandwidths = []
            
            for start in range(0, len(audio_array) - win_len, shift):
                frame = audio_array[start : start + win_len]
                if np.max(np.abs(frame)) < energy_thresh:
                    continue
                
                w_frame = frame * np.hanning(win_len)
                mag = np.abs(np.fft.rfft(w_frame, n=512))
                sum_mag = np.sum(mag) + 1e-12
                
                centroid = np.sum(freqs * mag) / sum_mag
                centroids.append(centroid)
                
                bandwidth = np.sqrt(np.sum(((freqs - centroid) ** 2) * mag) / sum_mag)
                bandwidths.append(bandwidth)
                
                mel_energy = np.dot(fbank, mag) + 1e-12
                log_mel = np.log(mel_energy)
                
                # Dropping C0 energy constant, taking C1..C12
                mfcc = dct(log_mel, type=2, norm='ortho')[1:13]
                mfccs.append(mfcc)
                
            if not mfccs:
                return None
                
            mfccs_arr = np.array(mfccs)  # (T, 12)
            
            # Delta MFCCs
            if len(mfccs_arr) >= 3:
                delta_mfccs = mfccs_arr[2:] - mfccs_arr[:-2]
            else:
                delta_mfccs = np.zeros_like(mfccs_arr)

            # Pitch F0 stats
            f0_median, f0_std = _extract_pitch_f0(audio_array, sample_rate=sample_rate)
            zcr = np.mean(np.diff(np.signbit(audio_array)))

            # Block 1: Zero-mean MFCC Means (12 dims)
            b1 = np.mean(mfccs_arr, axis=0)
            b1 = b1 - np.mean(b1)  # Remove static offset bias
            norm1 = np.linalg.norm(b1)
            if norm1 > 0:
                b1 = b1 / norm1

            # Block 2: MFCC Standard Deviations (12 dims)
            b2 = np.std(mfccs_arr, axis=0)
            norm2 = np.linalg.norm(b2)
            if norm2 > 0:
                b2 = b2 / norm2

            # Block 3: Delta MFCC Means (12 dims)
            b3 = np.mean(delta_mfccs, axis=0)
            norm3 = np.linalg.norm(b3)
            if norm3 > 0:
                b3 = b3 / norm3

            # Block 4: Pitch & Spectral features (6 dims)
            norm_f0_median = (f0_median - 150.0) / 100.0
            norm_f0_std = f0_std / 50.0
            norm_centroid_mean = (np.mean(centroids) - 2000.0) / 1500.0
            norm_centroid_std = np.std(centroids) / 1000.0
            norm_bw_mean = (np.mean(bandwidths) - 1500.0) / 1000.0
            norm_zcr = (zcr - 0.1) / 0.1
            
            b4 = np.array([norm_f0_median, norm_f0_std, norm_centroid_mean, norm_centroid_std, norm_bw_mean, norm_zcr], dtype=np.float32)
            norm4 = np.linalg.norm(b4)
            if norm4 > 0:
                b4 = b4 / norm4

            combined_vector = np.concatenate([b1, b2, b3, b4])
            
            final_norm = np.linalg.norm(combined_vector)
            if final_norm > 0:
                combined_vector = combined_vector / final_norm

            return combined_vector

        except Exception as e:
            logger.error(f"Error extracting speaker features: {e}")
            return None

    def save_profile(self, feature_vector: np.ndarray) -> bool:
        """Save Boss voice profile to disk."""
        try:
            np.save(BOSS_PROFILE_FILE, feature_vector)
            self.boss_profile = feature_vector
            logger.info(f"Boss voice profile saved to {BOSS_PROFILE_FILE}")
            return True
        except Exception as e:
            logger.error(f"Failed to save Boss voice profile: {e}")
            return False

    def load_profile(self) -> bool:
        """Load stored Boss voice profile and validate dimension compatibility."""
        if BOSS_PROFILE_FILE.exists():
            try:
                profile = np.load(BOSS_PROFILE_FILE)
                if profile.shape != (FEATURE_VECTOR_DIM,):
                    logger.warning(
                        f"Boss profile shape {profile.shape} is incompatible with current feature pipeline shape ({FEATURE_VECTOR_DIM},). "
                        "Profile requires re-enrollment via python main.py --setup."
                    )
                    self.boss_profile = None
                    return False

                self.boss_profile = profile
                logger.info(f"Boss voice profile loaded from {BOSS_PROFILE_FILE} (dim: {FEATURE_VECTOR_DIM})")
                return True
            except Exception as e:
                logger.error(f"Failed to load Boss profile: {e}")
                self.boss_profile = None
        else:
            logger.info("No Boss voice profile found.")
            self.boss_profile = None
        return False

    def is_enrolled(self) -> bool:
        """Check if Boss voice profile is currently enrolled."""
        return self.boss_profile is not None

    def classify_speaker(self, audio_data: Optional[sr.AudioData]) -> Tuple[str, float]:
        """
        Classify speaker as 'Boss' or 'Unknown'.
        Returns (speaker_label, similarity_score).
        Never fails open. Treats un-enrolled, missing, or low confidence audio as 'Unknown'.
        """
        if not self.is_enrolled():
            logger.debug("No Boss profile registered or profile shape incompatible. Treating speaker as 'Unknown'.")
            return "Unknown", 0.0

        if audio_data is None:
            logger.debug("No audio data provided. Treating speaker as 'Unknown'.")
            return "Unknown", 0.0

        try:
            pcm_bytes = audio_data.get_raw_data(convert_rate=AUDIO_SAMPLE_RATE, convert_width=2)
            features = self.extract_features(pcm_bytes, sample_rate=AUDIO_SAMPLE_RATE)
            
            if features is None:
                logger.debug("Audio snippet too short for feature extraction. Treating speaker as 'Unknown'.")
                return "Unknown", 0.0

            if self.boss_profile.shape != features.shape:
                logger.error(
                    f"Shape mismatch: features shape {features.shape} != boss_profile shape {self.boss_profile.shape}. "
                    "Re-enrollment required."
                )
                return "Unknown", 0.0

            # Compute Cosine Similarity between feature vectors
            dot_product = np.dot(features, self.boss_profile)
            norm_a = np.linalg.norm(features)
            norm_b = np.linalg.norm(self.boss_profile)

            if norm_a == 0 or norm_b == 0:
                similarity = 0.0
            else:
                similarity = float(dot_product / (norm_a * norm_b))

            logger.info(f"Speaker verification similarity score: {similarity:.4f} (Threshold: {SPEAKER_THRESHOLD})")

            if similarity >= SPEAKER_THRESHOLD:
                return "Boss", similarity
            else:
                return "Unknown", similarity

        except Exception as e:
            logger.error(f"Error classifying speaker: {e}")
            return "Unknown", 0.0

    def enroll_interactive(self, stt_service) -> bool:
        """Interactive CLI Voice Enrollment Wizard for registering Boss voice."""
        speak("Starting Boss Voice Enrollment process.")
        speak("I will record 3 audio samples. Please read the sentences on screen.")
        print("\n" + "=" * 50)
        print("    BOSS VOICE ENROLLMENT WIZARD")
        print(f"DISCLAIMER: {SECURITY_DISCLAIMER}")
        print("=" * 50 + "\n")

        sentences = [
            "Hello JARVIS, I am your Boss and main system operator.",
            "Today is a great day to build voice recognition software.",
            "JARVIS, activate all desktop systems and standby for commands."
        ]

        vectors = []
        for i, sentence in enumerate(sentences, 1):
            prompt_msg = f"Sample {i} of {ENROLLMENT_SAMPLES}: Please say out loud:"
            print(f"\n- {prompt_msg}")
            print(f"   \"{sentence}\"")
            speak(f"Sample {i}. Please say: {sentence}")
            
            sample_captured = False
            for attempt in range(3):
                print(f"[RECORDING] Listening for sample (attempt {attempt + 1})...")
                _, audio = stt_service.listen(phrase_time_limit=6.0, timeout=8.0)
                
                if audio is not None:
                    pcm_bytes = audio.get_raw_data(convert_rate=AUDIO_SAMPLE_RATE, convert_width=2)
                    vec = self.extract_features(pcm_bytes, sample_rate=AUDIO_SAMPLE_RATE)
                    if vec is not None:
                        vectors.append(vec)
                        print("[OK] Sample captured successfully.")
                        sample_captured = True
                        break
                    else:
                        print("[WARNING] Sample audio was unclear or silent. Retrying...")
                        speak("Sample was unclear. Please speak clearly into the microphone.")
                else:
                    print("[WARNING] Speech not detected. Retrying...")
                    speak("I did not hear you. Please try again.")

            if not sample_captured:
                print(f"[ERROR] Failed to capture valid audio for sample {i}.")

        if len(vectors) == ENROLLMENT_SAMPLES:
            mean_vector = np.mean(vectors, axis=0)
            norm = np.linalg.norm(mean_vector)
            if norm > 0:
                mean_vector = mean_vector / norm
            
            success = self.save_profile(mean_vector)
            if success:
                print("\n[SUCCESS] Boss Voice Profile created and saved successfully!")
                speak("Boss Voice Profile created and saved successfully.")
                return True
            
        print("\n[ERROR] Enrollment failed to capture sufficient valid voice samples.")
        speak("Enrollment failed to capture voice samples.")
        return False

