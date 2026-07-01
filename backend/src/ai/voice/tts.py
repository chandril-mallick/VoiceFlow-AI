"""
VoiceFlow AI — Text-to-Speech (Piper TTS)
Multilingual offline TTS with dynamic language switching.
"""

import io
import logging
import subprocess
import wave
from pathlib import Path
from typing import Optional

from src.core.config import settings

logger = logging.getLogger(__name__)


class TextToSpeech:
    """Piper TTS with multilingual support (English, Hindi, Bengali)."""

    VOICE_MAP = {
        "en": settings.piper_voice_en,
        "hi": settings.piper_voice_hi,
        "bn": settings.piper_voice_bn,
    }

    def __init__(self):
        self.data_dir = Path(settings.piper_data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self._available_voices: dict[str, bool] = {}
        self._check_voices()

    def _check_voices(self):
        """Check which voice models are available locally."""
        for lang, voice_name in self.VOICE_MAP.items():
            model_path = self.data_dir / f"{voice_name}.onnx"
            available = model_path.exists()
            self._available_voices[lang] = available
            if available:
                logger.info("✅ Voice available: %s (%s)", lang, voice_name)
            else:
                logger.warning("⚠️ Voice not found: %s (%s) — will use fallback", lang, voice_name)

    def synthesize(
        self,
        text: str,
        language: str = "en",
        speed: float = 1.0,
        sample_rate: int = 22050,
    ) -> bytes:
        """
        Convert text to speech audio.

        Args:
            text: Text to synthesize.
            language: Language code (en/hi/bn).
            speed: Speaking rate multiplier (0.5-2.0).
            sample_rate: Output sample rate.

        Returns:
            WAV audio bytes.
        """
        if not text.strip():
            return self._empty_wav(sample_rate)

        voice_name = self.VOICE_MAP.get(language, self.VOICE_MAP["en"])
        model_path = self.data_dir / f"{voice_name}.onnx"

        if not model_path.exists():
            # Fallback to English if the requested language model isn't available
            logger.warning("Voice model not found for %s, falling back to English", language)
            voice_name = self.VOICE_MAP["en"]
            model_path = self.data_dir / f"{voice_name}.onnx"

            if not model_path.exists():
                logger.error("No voice models available! Returning silence.")
                return self._empty_wav(sample_rate)

        try:
            # Use piper CLI for synthesis
            cmd = [
                "piper",
                "--model", str(model_path),
                "--output-raw",
                "--length-scale", str(1.0 / speed),
            ]

            process = subprocess.run(
                cmd,
                input=text.encode("utf-8"),
                capture_output=True,
                timeout=30,
            )

            if process.returncode != 0:
                logger.error("Piper TTS failed: %s", process.stderr.decode())
                return self._empty_wav(sample_rate)

            raw_audio = process.stdout
            return self._raw_to_wav(raw_audio, sample_rate=sample_rate)

        except FileNotFoundError:
            logger.error("Piper TTS not installed. Install with: pip install piper-tts")
            return self._empty_wav(sample_rate)
        except subprocess.TimeoutExpired:
            logger.error("Piper TTS timed out for text: %s...", text[:50])
            return self._empty_wav(sample_rate)
        except Exception as e:
            logger.error("TTS error: %s", e)
            return self._empty_wav(sample_rate)

    def synthesize_streaming(self, text: str, language: str = "en", speed: float = 1.0):
        """
        Stream synthesized audio in chunks.
        Yields chunks of raw PCM audio data.
        """
        voice_name = self.VOICE_MAP.get(language, self.VOICE_MAP["en"])
        model_path = self.data_dir / f"{voice_name}.onnx"

        if not model_path.exists():
            voice_name = self.VOICE_MAP["en"]
            model_path = self.data_dir / f"{voice_name}.onnx"

        if not model_path.exists():
            return

        # Split text into sentences for streaming
        sentences = self._split_sentences(text)

        for sentence in sentences:
            if sentence.strip():
                audio = self.synthesize(sentence, language, speed)
                if audio:
                    yield audio

    def _split_sentences(self, text: str) -> list[str]:
        """Split text into sentences for streaming synthesis."""
        import re
        # Split on sentence-ending punctuation
        sentences = re.split(r'(?<=[.!?।॥])\s+', text)
        return [s.strip() for s in sentences if s.strip()]

    def _raw_to_wav(self, raw_audio: bytes, sample_rate: int = 22050, channels: int = 1, sample_width: int = 2) -> bytes:
        """Convert raw PCM bytes to WAV format."""
        buf = io.BytesIO()
        with wave.open(buf, "wb") as wf:
            wf.setnchannels(channels)
            wf.setsampwidth(sample_width)
            wf.setframerate(sample_rate)
            wf.writeframes(raw_audio)
        return buf.getvalue()

    def _empty_wav(self, sample_rate: int = 22050) -> bytes:
        """Return a silent WAV file (0.5 seconds of silence)."""
        import struct
        num_samples = int(sample_rate * 0.5)
        silence = struct.pack(f"<{num_samples}h", *([0] * num_samples))
        return self._raw_to_wav(silence, sample_rate)

    @property
    def available_languages(self) -> list[str]:
        """Return list of languages with available voice models."""
        return [lang for lang, available in self._available_voices.items() if available]


# Singleton
_tts_instance: Optional[TextToSpeech] = None


def get_tts() -> TextToSpeech:
    """Get or create the TTS singleton."""
    global _tts_instance
    if _tts_instance is None:
        _tts_instance = TextToSpeech()
    return _tts_instance
