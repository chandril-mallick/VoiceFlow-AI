"""
VoiceFlow AI — Language Detector
Multi-strategy language detection combining Whisper and text-based analysis.
"""

import logging
from typing import Optional

from langdetect import detect as text_detect, DetectorFactory

from src.core.config import settings

logger = logging.getLogger(__name__)

# Make langdetect deterministic
DetectorFactory.seed = 42

SUPPORTED_LANGUAGES = {
    "en": "English",
    "hi": "Hindi",
    "bn": "Bengali",
}

# ISO 639-1 code mappings for edge cases
LANGUAGE_ALIASES = {
    "english": "en",
    "hindi": "hi",
    "bengali": "bn",
    "bangla": "bn",
    "हिन्दी": "hi",
    "বাংলা": "bn",
}


def detect_text_language(text: str) -> dict:
    """
    Detect language from text content using langdetect library.

    Returns:
        dict with language code, name, and confidence.
    """
    if not text or len(text.strip()) < 5:
        return {"language": "en", "language_name": "English", "confidence": 0.0}

    try:
        detected = text_detect(text)
        # Map to our supported set
        lang_code = detected if detected in SUPPORTED_LANGUAGES else "en"
        return {
            "language": lang_code,
            "language_name": SUPPORTED_LANGUAGES.get(lang_code, "English"),
            "confidence": 0.8 if lang_code == detected else 0.5,
        }
    except Exception as e:
        logger.warning("Text language detection failed: %s", e)
        return {"language": "en", "language_name": "English", "confidence": 0.0}


def merge_detection(
    whisper_result: dict,
    text_result: Optional[dict] = None,
) -> dict:
    """
    Merge language detection results from Whisper (audio) and text analysis.
    Whisper takes priority for spoken language; text confirms for written.
    """
    if not text_result:
        return {
            "language": whisper_result.get("language", "en"),
            "language_name": SUPPORTED_LANGUAGES.get(whisper_result.get("language", "en"), "English"),
            "confidence": whisper_result.get("language_confidence", 0.0),
            "method": "whisper",
        }

    whisper_lang = whisper_result.get("language", "en")
    whisper_conf = whisper_result.get("language_confidence", 0.0)
    text_lang = text_result.get("language", "en")
    text_conf = text_result.get("confidence", 0.0)

    # If both agree, high confidence
    if whisper_lang == text_lang:
        return {
            "language": whisper_lang,
            "language_name": SUPPORTED_LANGUAGES.get(whisper_lang, "English"),
            "confidence": max(whisper_conf, text_conf),
            "method": "consensus",
        }

    # If they disagree, prefer the one with higher confidence
    if whisper_conf >= text_conf:
        chosen = whisper_lang
        method = "whisper_priority"
    else:
        chosen = text_lang
        method = "text_priority"

    return {
        "language": chosen,
        "language_name": SUPPORTED_LANGUAGES.get(chosen, "English"),
        "confidence": max(whisper_conf, text_conf) * 0.8,  # Reduce confidence on disagreement
        "method": method,
    }


def should_switch_language(
    current_language: str,
    detected_language: str,
    confidence: float,
    consecutive_detections: int,
) -> bool:
    """
    Determine if the conversation should switch to a new language.
    Requires sustained detection to avoid false switches from code-mixing.
    """
    if detected_language == current_language:
        return False

    if detected_language not in SUPPORTED_LANGUAGES:
        return False

    # Require high confidence and multiple consecutive detections
    if confidence >= 0.85 and consecutive_detections >= 2:
        return True

    if confidence >= 0.70 and consecutive_detections >= 3:
        return True

    return False
