"""
VoiceFlow AI — Models Package
Import all models so Alembic and SQLAlchemy discover them.
"""

from src.models.base import Base
from src.models.tenant import Tenant
from src.models.user import User, UserRole
from src.models.lead import Lead, LeadStatus
from src.models.conversation import Conversation, ConversationMessage, ConversationStatus, MessageRole
from src.models.knowledge import KnowledgeDocument, ProcessingStatus
from src.models.appointment import Appointment, AppointmentStatus, CalendarProvider
from src.models.integration import Integration, WebhookEndpoint, IntegrationProvider
from src.models.audit import AuditLog

__all__ = [
    "Base",
    "Tenant",
    "User", "UserRole",
    "Lead", "LeadStatus",
    "Conversation", "ConversationMessage", "ConversationStatus", "MessageRole",
    "KnowledgeDocument", "ProcessingStatus",
    "Appointment", "AppointmentStatus", "CalendarProvider",
    "Integration", "WebhookEndpoint", "IntegrationProvider",
    "AuditLog",
]
