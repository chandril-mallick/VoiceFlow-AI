"""
VoiceFlow AI — LangGraph Agent Tools
Tools available to the sales agent for CRM, scheduling, and knowledge base access.
"""

import json
import logging
from datetime import datetime, timezone
from typing import Optional

from langchain_core.tools import tool

logger = logging.getLogger(__name__)


@tool
def search_knowledge_base(query: str, tenant_id: str = "") -> str:
    """Search the company's knowledge base (documents, FAQs, pricing) for relevant information.
    Use this when a customer asks about specific products, services, pricing, or company details."""
    # This will be wired to the RAG retriever at runtime
    return f"[Knowledge base search for: {query}]"


@tool
def score_lead(
    pain_points: list[str],
    interested_services: list[str],
    has_budget: bool,
    has_timeline: bool,
    is_decision_maker: bool,
    meeting_booked: bool,
) -> str:
    """Calculate a lead score (0-100) based on qualification criteria."""
    score = 0

    if pain_points:
        score += min(len(pain_points) * 10, 20)
    if interested_services:
        score += min(len(interested_services) * 10, 20)
    if has_budget:
        score += 15
    if has_timeline:
        score += 15
    if is_decision_maker:
        score += 10
    if meeting_booked:
        score += 15

    # Cap at 100
    score = min(score, 100)

    return json.dumps({
        "score": score,
        "breakdown": {
            "pain_points": min(len(pain_points) * 10, 20),
            "services_interest": min(len(interested_services) * 10, 20),
            "budget_discussed": 15 if has_budget else 0,
            "timeline_defined": 15 if has_timeline else 0,
            "decision_maker": 10 if is_decision_maker else 0,
            "meeting_booked": 15 if meeting_booked else 0,
        }
    })


@tool
def book_appointment(
    customer_name: str,
    customer_email: str,
    preferred_time: str,
    topic: str,
    duration_minutes: int = 30,
) -> str:
    """Book a meeting/appointment with the customer.
    Use when the customer agrees to schedule a call or meeting."""
    # Will be connected to calendar integration at runtime
    return json.dumps({
        "status": "booked",
        "customer": customer_name,
        "email": customer_email,
        "time": preferred_time,
        "topic": topic,
        "duration": duration_minutes,
        "meeting_link": "https://meet.google.com/pending",
    })


@tool
def send_whatsapp_message(phone: str, message: str) -> str:
    """Send a WhatsApp follow-up message to the customer.
    Use after booking a meeting or when the customer requests follow-up via WhatsApp."""
    # Will be connected to WhatsApp integration at runtime
    return json.dumps({
        "status": "queued",
        "phone": phone,
        "message_preview": message[:100],
    })


@tool
def send_email_followup(email: str, subject: str, body: str) -> str:
    """Send an email follow-up to the customer.
    Use after the conversation to send a summary or meeting confirmation."""
    # Will be connected to email integration at runtime
    return json.dumps({
        "status": "queued",
        "email": email,
        "subject": subject,
    })


@tool
def get_available_time_slots(date: str = "") -> str:
    """Get available meeting time slots for booking.
    Use when the customer wants to schedule a meeting and needs options."""
    # Will be connected to calendar integration at runtime
    return json.dumps({
        "available_slots": [
            "Tomorrow 10:00 AM",
            "Tomorrow 2:00 PM",
            "Day after tomorrow 11:00 AM",
            "Day after tomorrow 3:00 PM",
        ],
        "timezone": "IST",
    })


# All tools available to the agent
AGENT_TOOLS = [
    search_knowledge_base,
    score_lead,
    book_appointment,
    send_whatsapp_message,
    send_email_followup,
    get_available_time_slots,
]
