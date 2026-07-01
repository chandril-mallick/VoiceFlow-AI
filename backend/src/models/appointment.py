"""
VoiceFlow AI — Appointment Model
Meeting bookings linked to leads with calendar integration.
"""

import enum
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, TimestampMixin, UUIDMixin


class AppointmentStatus(str, enum.Enum):
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"


class CalendarProvider(str, enum.Enum):
    GOOGLE = "google"
    ZOOM = "zoom"
    MANUAL = "manual"


class Appointment(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "appointments"

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )
    lead_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("leads.id", ondelete="CASCADE"), nullable=False, index=True
    )

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    scheduled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    duration_minutes: Mapped[int] = mapped_column(Integer, default=30, nullable=False)
    meeting_link: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    calendar_provider: Mapped[CalendarProvider] = mapped_column(
        Enum(CalendarProvider), default=CalendarProvider.MANUAL, nullable=False
    )
    calendar_event_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    status: Mapped[AppointmentStatus] = mapped_column(
        Enum(AppointmentStatus), default=AppointmentStatus.SCHEDULED, nullable=False, index=True
    )

    # Relationships
    tenant = relationship("Tenant", back_populates="appointments")
    lead = relationship("Lead", back_populates="appointments")

    def __repr__(self) -> str:
        return f"<Appointment {self.title} @ {self.scheduled_at}>"
