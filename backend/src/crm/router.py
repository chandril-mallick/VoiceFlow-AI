"""
VoiceFlow AI — CRM Router
API endpoints for leads, conversations, appointments, and analytics.
"""

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.auth.dependencies import get_current_user, get_current_tenant_id
from src.crm.schemas import (
    AppointmentCreate, AppointmentResponse,
    DashboardStats,
    LeadCreate, LeadResponse, LeadUpdate,
    ConversationResponse,
)
from src.crm.service import CRMService
from src.models.lead import Lead, LeadStatus
from src.models.conversation import Conversation
from src.models.appointment import Appointment
from src.models.user import User

router = APIRouter(tags=["CRM"])


# ── Leads ──

@router.get("/leads", response_model=list[LeadResponse])
async def list_leads(
    status_filter: Optional[str] = Query(None, alias="status"),
    search: Optional[str] = Query(None),
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
    user: User = Depends(get_current_user),
):
    """List all leads with optional filtering."""
    query = select(Lead).where(Lead.tenant_id == tenant_id)

    if status_filter:
        try:
            query = query.where(Lead.status == LeadStatus(status_filter))
        except ValueError:
            pass

    if search:
        query = query.where(
            Lead.name.ilike(f"%{search}%") |
            Lead.email.ilike(f"%{search}%") |
            Lead.company.ilike(f"%{search}%")
        )

    query = query.order_by(desc(Lead.created_at)).limit(limit).offset(offset)
    result = await db.execute(query)
    leads = result.scalars().all()
    return [LeadResponse.model_validate(lead) for lead in leads]


@router.post("/leads", response_model=LeadResponse, status_code=status.HTTP_201_CREATED)
async def create_lead(
    data: LeadCreate,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
    user: User = Depends(get_current_user),
):
    """Create a new lead."""
    lead = Lead(
        tenant_id=tenant_id,
        name=data.name,
        phone=data.phone,
        email=data.email,
        company=data.company,
        industry=data.industry,
        language=data.language,
        source=data.source,
    )
    db.add(lead)
    await db.flush()
    return LeadResponse.model_validate(lead)


@router.get("/leads/{lead_id}", response_model=LeadResponse)
async def get_lead(
    lead_id: UUID,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
    user: User = Depends(get_current_user),
):
    """Get a single lead by ID."""
    result = await db.execute(
        select(Lead).where(Lead.id == lead_id, Lead.tenant_id == tenant_id)
    )
    lead = result.scalar_one_or_none()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return LeadResponse.model_validate(lead)


@router.put("/leads/{lead_id}", response_model=LeadResponse)
async def update_lead(
    lead_id: UUID,
    data: LeadUpdate,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
    user: User = Depends(get_current_user),
):
    """Update a lead."""
    result = await db.execute(
        select(Lead).where(Lead.id == lead_id, Lead.tenant_id == tenant_id)
    )
    lead = result.scalar_one_or_none()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if key == "status":
            value = LeadStatus(value)
        setattr(lead, key, value)

    lead.updated_at = datetime.now(timezone.utc)
    await db.flush()
    return LeadResponse.model_validate(lead)


@router.delete("/leads/{lead_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_lead(
    lead_id: UUID,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
    user: User = Depends(get_current_user),
):
    """Delete a lead."""
    result = await db.execute(
        select(Lead).where(Lead.id == lead_id, Lead.tenant_id == tenant_id)
    )
    lead = result.scalar_one_or_none()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    await db.delete(lead)


# ── Conversations ──

@router.get("/conversations", response_model=list[ConversationResponse])
async def list_conversations(
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
    user: User = Depends(get_current_user),
):
    """List all conversations."""
    result = await db.execute(
        select(Conversation)
        .where(Conversation.tenant_id == tenant_id)
        .order_by(desc(Conversation.started_at))
        .limit(limit).offset(offset)
    )
    convos = result.scalars().all()
    return [ConversationResponse.model_validate(c) for c in convos]


@router.get("/conversations/{conversation_id}")
async def get_conversation(
    conversation_id: UUID,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
    user: User = Depends(get_current_user),
):
    """Get a single conversation with full transcript."""
    result = await db.execute(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.tenant_id == tenant_id,
        )
    )
    convo = result.scalar_one_or_none()
    if not convo:
        raise HTTPException(status_code=404, detail="Conversation not found")

    return {
        **ConversationResponse.model_validate(convo).model_dump(),
        "transcript": convo.transcript,
    }


# ── Appointments ──

@router.post("/appointments", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
async def create_appointment(
    data: AppointmentCreate,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
    user: User = Depends(get_current_user),
):
    """Book an appointment."""
    appointment = Appointment(
        tenant_id=tenant_id,
        lead_id=data.lead_id,
        title=data.title,
        description=data.description,
        scheduled_at=data.scheduled_at,
        duration_minutes=data.duration_minutes,
    )
    db.add(appointment)
    await db.flush()
    return AppointmentResponse.model_validate(appointment)


@router.get("/appointments", response_model=list[AppointmentResponse])
async def list_appointments(
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
    user: User = Depends(get_current_user),
):
    """List all appointments."""
    result = await db.execute(
        select(Appointment)
        .where(Appointment.tenant_id == tenant_id)
        .order_by(Appointment.scheduled_at)
    )
    appts = result.scalars().all()
    return [AppointmentResponse.model_validate(a) for a in appts]


# ── Analytics ──

@router.get("/analytics/dashboard", response_model=DashboardStats)
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
    user: User = Depends(get_current_user),
):
    """Get dashboard analytics."""
    service = CRMService(db)
    return await service.get_dashboard_stats(tenant_id)
