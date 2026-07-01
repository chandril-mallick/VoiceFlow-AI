"""
VoiceFlow AI — CRM Schemas
Pydantic models for leads, conversations, appointments, and analytics.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


# ── Lead Schemas ──

class LeadCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    company: Optional[str] = None
    industry: Optional[str] = None
    language: Optional[str] = "en"
    source: Optional[str] = "manual"


class LeadUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    company: Optional[str] = None
    industry: Optional[str] = None
    pain_points: Optional[list[str]] = None
    interested_services: Optional[list[str]] = None
    budget_range: Optional[str] = None
    timeline: Optional[str] = None
    lead_score: Optional[int] = None
    status: Optional[str] = None
    assigned_agent_id: Optional[UUID] = None


class LeadResponse(BaseModel):
    id: UUID
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    company: Optional[str] = None
    industry: Optional[str] = None
    language: Optional[str] = None
    pain_points: Optional[list] = None
    interested_services: Optional[list] = None
    budget_range: Optional[str] = None
    timeline: Optional[str] = None
    lead_score: int
    meeting_time: Optional[datetime] = None
    conversation_summary: Optional[str] = None
    status: str
    source: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ── Conversation Schemas ──

class ConversationResponse(BaseModel):
    id: UUID
    lead_id: Optional[UUID] = None
    agent_type: str
    language_detected: Optional[str] = None
    languages_used: Optional[list] = None
    duration_seconds: Optional[int] = None
    summary: Optional[str] = None
    recording_url: Optional[str] = None
    ai_cost: float
    tokens_used: int
    lead_score_delta: int
    final_stage: Optional[str] = None
    status: str
    started_at: datetime
    ended_at: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Appointment Schemas ──

class AppointmentCreate(BaseModel):
    lead_id: UUID
    title: str
    description: Optional[str] = None
    scheduled_at: datetime
    duration_minutes: int = 30
    calendar_provider: str = "manual"


class AppointmentResponse(BaseModel):
    id: UUID
    lead_id: UUID
    title: str
    description: Optional[str] = None
    scheduled_at: datetime
    duration_minutes: int
    meeting_link: Optional[str] = None
    calendar_provider: str
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Analytics ──

class DashboardStats(BaseModel):
    total_leads: int = 0
    leads_today: int = 0
    active_conversations: int = 0
    conversations_today: int = 0
    appointments_booked: int = 0
    appointments_today: int = 0
    avg_lead_score: float = 0.0
    total_revenue: float = 0.0
    language_distribution: dict = {}
    lead_status_distribution: dict = {}
    conversion_rate: float = 0.0
