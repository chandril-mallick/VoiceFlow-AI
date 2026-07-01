"""
VoiceFlow AI — Application Configuration
Pydantic Settings loaded from environment variables / .env file.
"""

from functools import lru_cache
from typing import List

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Application ──
    app_name: str = "VoiceFlow AI"
    app_env: str = "development"
    debug: bool = True
    secret_key: str = "change-me-to-a-random-64-char-string"
    api_base_url: str = "http://localhost:8000"
    frontend_url: str = "http://localhost:3000"

    # ── Database ──
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "voiceflow"
    postgres_user: str = "voiceflow"
    postgres_password: str = "voiceflow_secret_2024"

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def database_url_sync(self) -> str:
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    # ── Redis ──
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_password: str = ""
    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"

    # ── Qdrant ──
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    qdrant_grpc_port: int = 6334

    @property
    def qdrant_url(self) -> str:
        return f"http://{self.qdrant_host}:{self.qdrant_port}"

    # ── Ollama ──
    ollama_host: str = "localhost"
    ollama_port: int = 11434
    ollama_model: str = "llama3.1:8b"
    ollama_embed_model: str = "nomic-embed-text"

    @property
    def ollama_base_url(self) -> str:
        return f"http://{self.ollama_host}:{self.ollama_port}"

    # ── LiteLLM ──
    litellm_model: str = "ollama/llama3.1:8b"

    # ── Whisper STT ──
    whisper_model_size: str = "base"
    whisper_device: str = "cpu"
    whisper_compute_type: str = "int8"
    whisper_language: str = "auto"

    # ── Piper TTS ──
    piper_voice_en: str = "en_US-lessac-medium"
    piper_voice_hi: str = "hi_IN-swara-medium"
    piper_voice_bn: str = "bn_BD-default-medium"
    piper_data_dir: str = "/app/data/piper-voices"

    # ── JWT ──
    jwt_secret_key: str = "change-me-to-another-random-64-char-string"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7

    # ── SMTP ──
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from_email: str = "noreply@voiceflow.ai"
    smtp_use_tls: bool = True

    # ── WhatsApp ──
    whatsapp_api_url: str = "https://graph.facebook.com/v18.0"
    whatsapp_phone_number_id: str = ""
    whatsapp_access_token: str = ""
    whatsapp_verify_token: str = ""

    # ── Google Calendar ──
    google_client_id: str = ""
    google_client_secret: str = ""
    google_redirect_uri: str = "http://localhost:8000/api/v1/integrations/google/callback"

    # ── Zoom ──
    zoom_client_id: str = ""
    zoom_client_secret: str = ""

    # ── Slack ──
    slack_webhook_url: str = ""
    slack_bot_token: str = ""

    # ── Discord ──
    discord_webhook_url: str = ""

    # ── External CRM ──
    hubspot_api_key: str = ""
    zoho_client_id: str = ""
    zoho_client_secret: str = ""

    # ── CORS ──
    cors_origins: str = "http://localhost:3000,http://localhost:8000"

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.cors_origins.split(",")]

    # ── Rate Limiting ──
    rate_limit_per_minute: int = 60

    # ── File Storage ──
    upload_dir: str = "/app/uploads"
    recordings_dir: str = "/app/recordings"
    max_upload_size_mb: int = 50


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
