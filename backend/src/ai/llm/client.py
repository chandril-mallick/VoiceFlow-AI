"""
VoiceFlow AI — LLM Client
LiteLLM abstraction for Ollama (local) with streaming, token tracking, and retry logic.
"""

import logging
from typing import AsyncGenerator, Optional

import litellm

from src.core.config import settings

logger = logging.getLogger(__name__)

# Configure LiteLLM
litellm.set_verbose = False


class LLMClient:
    """Unified LLM client using LiteLLM to abstract over Ollama and other providers."""

    def __init__(
        self,
        model: Optional[str] = None,
        api_base: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 512,
    ):
        self.model = model or settings.litellm_model
        self.api_base = api_base or settings.ollama_base_url
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.total_tokens_used = 0
        self.total_cost = 0.0

    async def generate(
        self,
        messages: list[dict],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> dict:
        """
        Generate a completion from the LLM.

        Args:
            messages: List of chat messages [{"role": "...", "content": "..."}]
            temperature: Override default temperature.
            max_tokens: Override default max tokens.

        Returns:
            dict with: content, tokens_used, model
        """
        try:
            response = await litellm.acompletion(
                model=self.model,
                messages=messages,
                temperature=temperature or self.temperature,
                max_tokens=max_tokens or self.max_tokens,
                api_base=self.api_base,
            )

            content = response.choices[0].message.content
            usage = response.usage

            tokens = (usage.total_tokens if usage else 0)
            self.total_tokens_used += tokens

            return {
                "content": content,
                "tokens_used": tokens,
                "prompt_tokens": usage.prompt_tokens if usage else 0,
                "completion_tokens": usage.completion_tokens if usage else 0,
                "model": self.model,
            }

        except Exception as e:
            logger.error("LLM generation failed: %s", e)
            raise

    async def generate_stream(
        self,
        messages: list[dict],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> AsyncGenerator[str, None]:
        """
        Stream a completion from the LLM, yielding text chunks.
        """
        try:
            response = await litellm.acompletion(
                model=self.model,
                messages=messages,
                temperature=temperature or self.temperature,
                max_tokens=max_tokens or self.max_tokens,
                api_base=self.api_base,
                stream=True,
            )

            async for chunk in response:
                delta = chunk.choices[0].delta
                if delta and delta.content:
                    yield delta.content

        except Exception as e:
            logger.error("LLM streaming failed: %s", e)
            raise

    async def is_available(self) -> bool:
        """Check if the LLM backend is reachable."""
        try:
            response = await litellm.acompletion(
                model=self.model,
                messages=[{"role": "user", "content": "ping"}],
                max_tokens=5,
                api_base=self.api_base,
            )
            return True
        except Exception:
            return False

    def get_usage_stats(self) -> dict:
        """Return cumulative usage statistics."""
        return {
            "total_tokens": self.total_tokens_used,
            "total_cost": self.total_cost,
            "model": self.model,
        }


# Singleton
_llm_instance: Optional[LLMClient] = None


def get_llm() -> LLMClient:
    """Get or create the LLM client singleton."""
    global _llm_instance
    if _llm_instance is None:
        _llm_instance = LLMClient()
    return _llm_instance
