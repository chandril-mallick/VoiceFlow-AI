"""
VoiceFlow AI — Lead Model
CRM lead entity with scoring, qualification, and conversation tracking.
"""

import enum
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, TimestampMixin, UUIDMixin


class LeadStatus(str, enum.Enum):
    NEW = "new"
    CONTACTED = "contacted"
    QUALIFIED = "qualified"
    MEETING_BOOKED = "meeting_booked"
    PROPOSAL_SENT = "proposal_sent"
    NEGOTIATION = "negotiation"
    CLOSED_WON = "closed_won"
    CLOSED_LOST = "closed_lost"


class Lead(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "leads"

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Contact information
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, index=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    company: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    industry: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Conversation insights
    language: Mapped[Optional[str]] = mapped_column(String(10), nullable=True, comment="Primary language: en/hi/bn")
    pain_points: Mapped[Optional[list]] = mapped_column(JSON, nullable=True, default=list)
    interested_services: Mapped[Optional[list]] = mapped_column(JSON, nullable=True, default=list)

    # Qualification
    budget_range: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    timeline: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    lead_score: Mapped[int] = mapped_column(Integer, default=0, nullable=False, comment="0-100 score")

    # Meeting
    meeting_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Summary
    conversation_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Status tracking
    status: Mapped[LeadStatus] = mapped_column(
        Enum(LeadStatus), default=LeadStatus.NEW, nullable=False, index=True
    )
    source: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, default="voice_agent")

    # Assignment
    assigned_agent_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    # Relationships
    tenant = relationship("Tenant", back_populates="leads")
    assigned_agent = relationship("User", back_populates="assigned_leads", foreign_keys=[assigned_agent_id])
    conversations = relationship("Conversation", back_populates="lead", cascade="all, delete-orphan")
    appointments = relationship("Appointment", back_populates="lead", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Lead {self.name} ({self.status.value})>"
