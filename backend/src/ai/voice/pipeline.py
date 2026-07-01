"""
VoiceFlow AI — Voice Pipeline Orchestrator
End-to-end: Audio → STT → Language Detection → LLM Agent → TTS → Audio
"""

import logging
import io
import wave
from datetime import datetime, timezone
from typing import Optional

import numpy as np
import soundfile as sf

from src.ai.voice.stt import get_stt
from src.ai.voice.tts import get_tts
from src.ai.voice.language_detector import detect_text_language, merge_detection, should_switch_language
from src.ai.agent.graph import SalesAgent

logger = logging.getLogger(__name__)


class VoicePipeline:
    """
    Orchestrates the full voice conversation pipeline:
    1. Receive audio → STT (Faster Whisper)
    2. Detect language
    3. Generate response (LangGraph Sales Agent)
    4. Convert response to speech (Piper TTS)
    5. Return audio + metadata
    """

    def __init__(
        self,
        tenant_id: str,
        company_name: str,
        services: list[str],
        agent_name: str = "AI Assistant",
        company_context: str = "",
        custom_prompts: dict = None,
        initial_language: str = "en",
    ):
        self.stt = get_stt()
        self.tts = get_tts()
        self.agent = SalesAgent(
            tenant_id=tenant_id,
            company_name=company_name,
            services=services,
            agent_name=agent_name,
            company_context=company_context,
            custom_prompts=custom_prompts,
            language=initial_language,
        )
        self.current_language = initial_language
        self.consecutive_lang_detections = 0
        self.last_detected_language = initial_language
        self.started_at = datetime.now(timezone.utc)
        self.transcript: list[dict] = []

    async def start_conversation(self) -> dict:
        """Start the conversation — generate initial greeting audio."""
        greeting_text = await self.agent.start()

        # Generate greeting audio
        greeting_audio = self.tts.synthesize(greeting_text, self.current_language)

        self.transcript.append({
            "role": "assistant",
            "content": greeting_text,
            "language": self.current_language,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

        return {
            "text": greeting_text,
            "audio": greeting_audio,
            "language": self.current_language,
            "stage": self.agent.current_stage,
        }

    async def process_audio(self, audio_bytes: bytes, sample_rate: int = 16000) -> dict:
        """
        Process incoming audio and return response audio.

        Args:
            audio_bytes: Raw audio bytes (PCM 16-bit or WAV).
            sample_rate: Input audio sample rate.

        Returns:
            dict with: text, audio, language, stage, transcript_entry
        """
        # 1. Convert audio bytes to numpy array
        audio_array = self._bytes_to_array(audio_bytes, sample_rate)

        if audio_array is None or len(audio_array) < 1600:  # < 0.1 second
            return {
                "text": "",
                "audio": b"",
                "language": self.current_language,
                "stage": self.agent.current_stage,
                "is_silence": True,
            }

        # 2. STT — Transcribe audio
        stt_result = self.stt.transcribe(audio_array, language=None)  # Auto-detect

        user_text = stt_result["text"].strip()
        if not user_text:
            return {
                "text": "",
                "audio": b"",
                "language": self.current_language,
                "stage": self.agent.current_stage,
                "is_silence": True,
            }

        # 3. Language detection
        text_lang = detect_text_language(user_text)
        lang_result = merge_detection(stt_result, text_lang)
        detected_lang = lang_result["language"]

        # Check if we should switch language
        if detected_lang == self.last_detected_language:
            self.consecutive_lang_detections += 1
        else:
            self.consecutive_lang_detections = 1
            self.last_detected_language = detected_lang

        if should_switch_language(
            self.current_language,
            detected_lang,
            lang_result["confidence"],
            self.consecutive_lang_detections,
        ):
            logger.info("🔄 Language switch: %s → %s", self.current_language, detected_lang)
            self.current_language = detected_lang
            self.agent.state.language = detected_lang

        # Record user turn
        self.transcript.append({
            "role": "user",
            "content": user_text,
            "language": detected_lang,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

        # 4. Generate agent response
        response_text = await self.agent.respond(user_text)

        # Record assistant turn
        self.transcript.append({
            "role": "assistant",
            "content": response_text,
            "language": self.current_language,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })

        # 5. TTS — Convert response to audio
        response_audio = self.tts.synthesize(response_text, self.current_language)

        return {
            "user_text": user_text,
            "text": response_text,
            "audio": response_audio,
            "language": self.current_language,
            "language_confidence": lang_result["confidence"],
            "stage": self.agent.current_stage,
            "is_ended": self.agent.is_ended,
            "turn_count": self.agent.state.turn_count,
        }

    def _bytes_to_array(self, audio_bytes: bytes, sample_rate: int = 16000) -> Optional[np.ndarray]:
        """Convert raw audio bytes to float32 numpy array."""
        try:
            # Try to read as WAV first
            buf = io.BytesIO(audio_bytes)
            try:
                data, sr = sf.read(buf)
                if len(data.shape) > 1:
                    data = data.mean(axis=1)  # Convert stereo to mono
                return data.astype(np.float32)
            except Exception:
                pass

            # Fall back to raw PCM 16-bit
            audio_array = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32)
            audio_array /= 32768.0  # Normalize to [-1, 1]
            return audio_array

        except Exception as e:
            logger.error("Failed to convert audio bytes: %s", e)
            return None

    @property
    def conversation_summary(self) -> dict:
        """Get a summary of the conversation so far."""
        duration = (datetime.now(timezone.utc) - self.started_at).total_seconds()
        return {
            "duration_seconds": int(duration),
            "turn_count": self.agent.state.turn_count,
            "language": self.current_language,
            "stage": self.agent.current_stage,
            "lead_data": self.agent.lead_data,
            "tokens_used": self.agent.state.tokens_used,
            "transcript": self.transcript,
            "is_ended": self.agent.is_ended,
        }
