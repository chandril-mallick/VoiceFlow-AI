"""
VoiceFlow AI — Speech-to-Text (Faster Whisper)
Multilingual transcription with automatic language detection.
"""

import logging
from typing import Optional

import numpy as np

from src.core.config import settings

logger = logging.getLogger(__name__)

# Lazy-load the model to avoid startup cost
_model = None


def _get_model():
    """Lazily load the Faster Whisper model."""
    global _model
    if _model is None:
        from faster_whisper import WhisperModel

        logger.info(
            "Loading Whisper model: %s (device=%s, compute=%s)",
            settings.whisper_model_size,
            settings.whisper_device,
            settings.whisper_compute_type,
        )
        _model = WhisperModel(
            settings.whisper_model_size,
            device=settings.whisper_device,
            compute_type=settings.whisper_compute_type,
        )
        logger.info("✅ Whisper model loaded successfully")
    return _model


class SpeechToText:
    """Faster Whisper STT with multilingual support (Bengali, Hindi, English)."""

    SUPPORTED_LANGUAGES = {"en": "English", "hi": "Hindi", "bn": "Bengali"}

    def __init__(self):
        self.model = _get_model()

    def transcribe(
        self,
        audio_data: np.ndarray,
        language: Optional[str] = None,
        sample_rate: int = 16000,
    ) -> dict:
        """
        Transcribe audio data to text.

        Args:
            audio_data: NumPy array of audio samples (float32, mono).
            language: Force language code (en/hi/bn) or None for auto-detect.
            sample_rate: Audio sample rate (default 16kHz).

        Returns:
            dict with keys: text, language, language_confidence, segments
        """
        # Ensure float32
        if audio_data.dtype != np.float32:
            audio_data = audio_data.astype(np.float32)

        # Normalize if needed
        max_val = np.max(np.abs(audio_data))
        if max_val > 1.0:
            audio_data = audio_data / max_val

        # Determine language setting
        lang = language if language in self.SUPPORTED_LANGUAGES else None

        segments, info = self.model.transcribe(
            audio_data,
            language=lang,
            beam_size=5,
            vad_filter=True,
            vad_parameters=dict(
                min_silence_duration_ms=500,
                speech_pad_ms=200,
            ),
            word_timestamps=True,
        )

        # Collect segments
        text_parts = []
        segment_list = []
        for segment in segments:
            text_parts.append(segment.text.strip())
            segment_list.append({
                "start": segment.start,
                "end": segment.end,
                "text": segment.text.strip(),
                "words": [
                    {"word": w.word, "start": w.start, "end": w.end, "probability": w.probability}
                    for w in (segment.words or [])
                ],
            })

        detected_language = info.language if info.language in self.SUPPORTED_LANGUAGES else "en"

        return {
            "text": " ".join(text_parts),
            "language": detected_language,
            "language_name": self.SUPPORTED_LANGUAGES.get(detected_language, "English"),
            "language_confidence": round(info.language_probability, 3),
            "duration": info.duration,
            "segments": segment_list,
        }

    def detect_language(self, audio_data: np.ndarray) -> dict:
        """Detect the spoken language from audio without full transcription."""
        if audio_data.dtype != np.float32:
            audio_data = audio_data.astype(np.float32)

        # Use only first 30 seconds for detection
        max_samples = 30 * 16000
        if len(audio_data) > max_samples:
            audio_data = audio_data[:max_samples]

        _, info = self.model.transcribe(audio_data, beam_size=1)

        return {
            "language": info.language,
            "language_name": self.SUPPORTED_LANGUAGES.get(info.language, info.language),
            "confidence": round(info.language_probability, 3),
        }


# Singleton instance
_stt_instance: Optional[SpeechToText] = None


def get_stt() -> SpeechToText:
    """Get or create the STT singleton."""
    global _stt_instance
    if _stt_instance is None:
        _stt_instance = SpeechToText()
    return _stt_instance
