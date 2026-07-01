"""
VoiceFlow AI — Conversation & Message Models
Stores voice conversations with transcripts, recordings, and AI metrics.
"""

import enum
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, TimestampMixin, UUIDMixin


class ConversationStatus(str, enum.Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    ABANDONED = "abandoned"
    FAILED = "failed"


class MessageRole(str, enum.Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class Conversation(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "conversations"

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    lead_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("leads.id", ondelete="SET NULL"), nullable=True, index=True
    )

    # Conversation metadata
    agent_type: Mapped[str] = mapped_column(String(50), default="sales", nullable=False)
    language_detected: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    languages_used: Mapped[Optional[list]] = mapped_column(JSON, nullable=True, default=list)
    duration_seconds: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Transcript stored as JSON array of messages
    transcript: Mapped[Optional[list]] = mapped_column(JSON, nullable=True, default=list)

    # AI-generated summary
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Recording
    recording_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Cost tracking
    ai_cost: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    tokens_used: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Lead impact
    lead_score_delta: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Conversation stage reached
    final_stage: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Status
    status: Mapped[ConversationStatus] = mapped_column(
        Enum(ConversationStatus), default=ConversationStatus.ACTIVE, nullable=False, index=True
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    ended_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    tenant = relationship("Tenant", back_populates="conversations")
    lead = relationship("Lead", back_populates="conversations")
    messages = relationship("ConversationMessage", back_populates="conversation", cascade="all, delete-orphan",
                            order_by="ConversationMessage.timestamp")

    def __repr__(self) -> str:
        return f"<Conversation {self.id} ({self.status.value})>"


class ConversationMessage(Base, UUIDMixin):
    __tablename__ = "conversation_messages"

    conversation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    role: Mapped[MessageRole] = mapped_column(Enum(MessageRole), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    language: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    audio_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    # Relationships
    conversation = relationship("Conversation", back_populates="messages")

    def __repr__(self) -> str:
        return f"<Message {self.role.value} @ {self.timestamp}>"
