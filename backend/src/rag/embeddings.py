"""
VoiceFlow AI — Embedding Model
Uses Ollama embeddings (nomic-embed-text) for local vector generation.
"""

import logging
from typing import Optional

from langchain_community.embeddings import OllamaEmbeddings

from src.core.config import settings

logger = logging.getLogger(__name__)

_embedding_instance = None


def get_embedding_function(
    model: Optional[str] = None,
    base_url: Optional[str] = None,
) -> OllamaEmbeddings:
    """
    Get or create the embedding model instance.
    Uses Ollama's nomic-embed-text by default for fully local operation.
    """
    global _embedding_instance

    if _embedding_instance is None:
        _embedding_instance = OllamaEmbeddings(
            model=model or settings.ollama_embed_model,
            base_url=base_url or settings.ollama_base_url,
        )
        logger.info(
            "✅ Embedding model initialized: %s @ %s",
            model or settings.ollama_embed_model,
            base_url or settings.ollama_base_url,
        )

    return _embedding_instance
