"""
VoiceFlow AI — Integration & Webhook Models
Third-party service configs and outgoing webhook endpoints.
"""

import enum
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base, TimestampMixin, UUIDMixin


class IntegrationProvider(str, enum.Enum):
    GOOGLE_CALENDAR = "google_calendar"
    ZOOM = "zoom"
    WHATSAPP = "whatsapp"
    SMTP_EMAIL = "smtp_email"
    HUBSPOT = "hubspot"
    ZOHO = "zoho"
    SLACK = "slack"
    DISCORD = "discord"


class Integration(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "integrations"

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )

    provider: Mapped[IntegrationProvider] = mapped_column(
        Enum(IntegrationProvider), nullable=False
    )
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)

    # Encrypted configuration (API keys, tokens, etc.)
    config: Mapped[Optional[dict]] = mapped_column(
        JSON, nullable=True, default=dict,
        comment="Encrypted integration credentials and settings"
    )

    is_active: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    last_synced: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    tenant = relationship("Tenant", back_populates="integrations")

    def __repr__(self) -> str:
        return f"<Integration {self.provider.value} ({self.tenant_id})>"


class WebhookEndpoint(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "webhook_endpoints"

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True
    )

    url: Mapped[str] = mapped_column(String(500), nullable=False)
    events: Mapped[list] = mapped_column(
        JSON, nullable=False, default=list,
        comment="List of event types to trigger: lead.created, conversation.completed, etc."
    )
    secret: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True, comment="HMAC signing secret"
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    last_triggered: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    failure_count: Mapped[int] = mapped_column(default=0, nullable=False)

    # Relationships
    tenant = relationship("Tenant", back_populates="webhook_endpoints")

    def __repr__(self) -> str:
        return f"<WebhookEndpoint {self.url}>"
