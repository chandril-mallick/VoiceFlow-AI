"""
VoiceFlow AI — LangGraph Agent State
Defines the conversation state schema passed between graph nodes.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Annotated, Any, Optional
from uuid import UUID

from langgraph.graph.message import add_messages


@dataclass
class ConversationState:
    """State object that flows through the LangGraph sales conversation."""

    # ── Core identifiers ──
    conversation_id: str = ""
    tenant_id: str = ""
    lead_id: str = ""

    # ── Conversation messages (LangGraph managed) ──
    messages: Annotated[list, add_messages] = field(default_factory=list)

    # ── Current stage in the sales flow ──
    current_stage: str = "greeting"
    previous_stage: str = ""

    # ── Language ──
    language: str = "en"
    language_name: str = "English"
    language_confidence: float = 0.0
    language_switch_count: int = 0
    consecutive_language_detections: int = 0

    # ── Lead information (gathered during conversation) ──
    customer_name: str = ""
    customer_company: str = ""
    customer_industry: str = ""
    customer_email: str = ""
    customer_phone: str = ""

    # ── Discovery ──
    pain_points: list[str] = field(default_factory=list)
    interested_services: list[str] = field(default_factory=list)
    budget_range: str = ""
    timeline: str = ""

    # ── Qualification ──
    lead_score: int = 0
    is_decision_maker: bool = False
    objections: list[str] = field(default_factory=list)

    # ── Meeting ──
    meeting_booked: bool = False
    meeting_time: str = ""
    meeting_link: str = ""

    # ── Follow-up ──
    followup_sent: bool = False
    followup_method: str = ""  # email / whatsapp

    # ── Tenant config (injected at start) ──
    company_name: str = ""
    services: list[str] = field(default_factory=list)
    company_context: str = ""
    agent_name: str = "AI Assistant"
    custom_prompts: dict = field(default_factory=dict)

    # ── Metrics ──
    tokens_used: int = 0
    turn_count: int = 0
    started_at: str = ""

    # ── Control flags ──
    should_end: bool = False
    error: str = ""
    rag_context: str = ""

    def to_lead_data(self) -> dict:
        """Extract lead-relevant fields for CRM storage."""
        return {
            "name": self.customer_name,
            "phone": self.customer_phone,
            "email": self.customer_email,
            "company": self.customer_company,
            "industry": self.customer_industry,
            "language": self.language,
            "pain_points": self.pain_points,
            "interested_services": self.interested_services,
            "budget_range": self.budget_range,
            "timeline": self.timeline,
            "lead_score": self.lead_score,
            "meeting_time": self.meeting_time,
        }
