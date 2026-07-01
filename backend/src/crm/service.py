"""
VoiceFlow AI — CRM Service
Business logic for leads, analytics, and lead scoring.
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy import func, select, case
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.lead import Lead, LeadStatus
from src.models.conversation import Conversation, ConversationStatus
from src.models.appointment import Appointment, AppointmentStatus
from src.crm.schemas import DashboardStats

logger = logging.getLogger(__name__)


class CRMService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_dashboard_stats(self, tenant_id: UUID) -> DashboardStats:
        """Aggregate dashboard statistics for a tenant."""
        now = datetime.now(timezone.utc)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

        # Total leads
        total_leads_q = await self.db.execute(
            select(func.count(Lead.id)).where(Lead.tenant_id == tenant_id)
        )
        total_leads = total_leads_q.scalar() or 0

        # Leads today
        leads_today_q = await self.db.execute(
            select(func.count(Lead.id)).where(
                Lead.tenant_id == tenant_id,
                Lead.created_at >= today_start,
            )
        )
        leads_today = leads_today_q.scalar() or 0

        # Active conversations
        active_convos_q = await self.db.execute(
            select(func.count(Conversation.id)).where(
                Conversation.tenant_id == tenant_id,
                Conversation.status == ConversationStatus.ACTIVE,
            )
        )
        active_conversations = active_convos_q.scalar() or 0

        # Conversations today
        convos_today_q = await self.db.execute(
            select(func.count(Conversation.id)).where(
                Conversation.tenant_id == tenant_id,
                Conversation.started_at >= today_start,
            )
        )
        conversations_today = convos_today_q.scalar() or 0

        # Appointments booked
        appts_q = await self.db.execute(
            select(func.count(Appointment.id)).where(
                Appointment.tenant_id == tenant_id,
                Appointment.status == AppointmentStatus.SCHEDULED,
            )
        )
        appointments_booked = appts_q.scalar() or 0

        # Appointments today
        appts_today_q = await self.db.execute(
            select(func.count(Appointment.id)).where(
                Appointment.tenant_id == tenant_id,
                Appointment.created_at >= today_start,
            )
        )
        appointments_today = appts_today_q.scalar() or 0

        # Average lead score
        avg_score_q = await self.db.execute(
            select(func.avg(Lead.lead_score)).where(
                Lead.tenant_id == tenant_id,
                Lead.lead_score > 0,
            )
        )
        avg_lead_score = round(avg_score_q.scalar() or 0, 1)

        # Language distribution
        lang_q = await self.db.execute(
            select(Lead.language, func.count(Lead.id))
            .where(Lead.tenant_id == tenant_id)
            .group_by(Lead.language)
        )
        language_distribution = {
            lang or "unknown": count for lang, count in lang_q.all()
        }

        # Lead status distribution
        status_q = await self.db.execute(
            select(Lead.status, func.count(Lead.id))
            .where(Lead.tenant_id == tenant_id)
            .group_by(Lead.status)
        )
        lead_status_distribution = {
            status.value: count for status, count in status_q.all()
        }

        # Conversion rate
        closed_won = lead_status_distribution.get("closed_won", 0)
        conversion_rate = round((closed_won / total_leads * 100) if total_leads > 0 else 0, 1)

        return DashboardStats(
            total_leads=total_leads,
            leads_today=leads_today,
            active_conversations=active_conversations,
            conversations_today=conversations_today,
            appointments_booked=appointments_booked,
            appointments_today=appointments_today,
            avg_lead_score=avg_lead_score,
            language_distribution=language_distribution,
            lead_status_distribution=lead_status_distribution,
            conversion_rate=conversion_rate,
        )

    async def calculate_lead_score(self, lead: Lead) -> int:
        """Calculate lead score based on qualification data."""
        score = 0

        if lead.pain_points and len(lead.pain_points) > 0:
            score += min(len(lead.pain_points) * 10, 20)

        if lead.interested_services and len(lead.interested_services) > 0:
            score += min(len(lead.interested_services) * 10, 20)

        if lead.budget_range:
            score += 15

        if lead.timeline:
            score += 15

        if lead.meeting_time:
            score += 15

        if lead.email:
            score += 5

        if lead.phone:
            score += 5

        if lead.company:
            score += 5

        return min(score, 100)
