"""
VoiceFlow AI — Tenant Model
Each tenant is a separate business with its own branding, config, and data.
"""

import uuid
from typing import Optional

from sqlalchemy import Boolean, String, Text
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, TimestampMixin, UUIDMixin


class Tenant(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "tenants"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    logo_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    website: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Branding configuration
    branding_config: Mapped[Optional[dict]] = mapped_column(
        JSON, nullable=True, default=dict,
        comment="Colors, fonts, and visual identity"
    )

    # Subscription
    subscription_plan: Mapped[str] = mapped_column(
        String(50), default="free", nullable=False
    )

    # Phone configuration
    phone_config: Mapped[Optional[dict]] = mapped_column(
        JSON, nullable=True, default=dict,
        comment="Phone numbers, telephony provider config"
    )

    # AI personality and prompts
    ai_personality: Mapped[Optional[dict]] = mapped_column(
        JSON, nullable=True, default=dict,
        comment="AI voice style, tone, behavior settings"
    )
    custom_prompts: Mapped[Optional[dict]] = mapped_column(
        JSON, nullable=True, default=dict,
        comment="Custom system prompts per conversation stage"
    )

    # Configurable services offered by this business
    services: Mapped[Optional[dict]] = mapped_column(
        JSON, nullable=True, default=list,
        comment="List of services this business offers"
    )

    # Voice config
    voice_config: Mapped[Optional[dict]] = mapped_column(
        JSON, nullable=True, default=dict,
        comment="TTS voice selection per language, speed, pitch"
    )

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    users = relationship("User", back_populates="tenant", cascade="all, delete-orphan")
    leads = relationship("Lead", back_populates="tenant", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="tenant", cascade="all, delete-orphan")
    knowledge_documents = relationship("KnowledgeDocument", back_populates="tenant", cascade="all, delete-orphan")
    integrations = relationship("Integration", back_populates="tenant", cascade="all, delete-orphan")
    webhook_endpoints = relationship("WebhookEndpoint", back_populates="tenant", cascade="all, delete-orphan")
    appointments = relationship("Appointment", back_populates="tenant", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Tenant {self.slug}>"
