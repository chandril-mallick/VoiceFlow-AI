"""
VoiceFlow AI — LangGraph Agent Node Implementations
Each node handles a specific stage of the sales conversation.
"""

import json
import logging
from typing import Any

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from src.ai.agent.state import ConversationState
from src.ai.llm.client import get_llm
from src.ai.llm.prompts import build_system_prompt, OBJECTION_HANDLING_PROMPT

logger = logging.getLogger(__name__)


async def _call_llm(state: ConversationState, stage: str) -> str:
    """Helper: build prompt and call the LLM for a given stage."""
    system_prompt = build_system_prompt(
        company_name=state.company_name,
        services=state.services,
        stage=stage,
        language=state.language,
        company_context=state.company_context or state.rag_context,
        agent_name=state.agent_name,
        custom_prompts=state.custom_prompts,
    )

    # Build messages for LLM
    messages = [{"role": "system", "content": system_prompt}]

    # Add conversation history (last 10 turns for context window management)
    for msg in state.messages[-10:]:
        if isinstance(msg, HumanMessage):
            messages.append({"role": "user", "content": msg.content})
        elif isinstance(msg, AIMessage):
            messages.append({"role": "assistant", "content": msg.content})

    llm = get_llm()
    result = await llm.generate(messages)
    state.tokens_used += result.get("tokens_used", 0)
    return result["content"]


async def greeting_node(state: ConversationState) -> dict:
    """Generate a warm greeting to start the conversation."""
    response = await _call_llm(state, "greeting")
    state.turn_count += 1
    return {
        "messages": [AIMessage(content=response)],
        "current_stage": "greeting",
        "previous_stage": "",
        "turn_count": state.turn_count,
        "tokens_used": state.tokens_used,
    }


async def language_detection_node(state: ConversationState) -> dict:
    """Process language detection results and adapt."""
    return {
        "current_stage": "language_detection",
        "previous_stage": state.current_stage,
    }


async def business_intro_node(state: ConversationState) -> dict:
    """Introduce the company and its services."""
    response = await _call_llm(state, "business_intro")
    state.turn_count += 1
    return {
        "messages": [AIMessage(content=response)],
        "current_stage": "business_intro",
        "previous_stage": state.current_stage,
        "turn_count": state.turn_count,
        "tokens_used": state.tokens_used,
    }


async def understand_customer_node(state: ConversationState) -> dict:
    """Ask about the customer's business and needs."""
    response = await _call_llm(state, "understand_customer")
    state.turn_count += 1
    return {
        "messages": [AIMessage(content=response)],
        "current_stage": "understand_customer",
        "previous_stage": state.current_stage,
        "turn_count": state.turn_count,
        "tokens_used": state.tokens_used,
    }


async def pain_point_discovery_node(state: ConversationState) -> dict:
    """Discover customer pain points and challenges."""
    response = await _call_llm(state, "pain_point_discovery")
    state.turn_count += 1
    return {
        "messages": [AIMessage(content=response)],
        "current_stage": "pain_point_discovery",
        "previous_stage": state.current_stage,
        "turn_count": state.turn_count,
        "tokens_used": state.tokens_used,
    }


async def recommend_services_node(state: ConversationState) -> dict:
    """Recommend relevant services based on discovered pain points."""
    response = await _call_llm(state, "recommend_services")
    state.turn_count += 1
    return {
        "messages": [AIMessage(content=response)],
        "current_stage": "recommend_services",
        "previous_stage": state.current_stage,
        "turn_count": state.turn_count,
        "tokens_used": state.tokens_used,
    }


async def budget_qualification_node(state: ConversationState) -> dict:
    """Explore the customer's budget."""
    response = await _call_llm(state, "budget_qualification")
    state.turn_count += 1
    return {
        "messages": [AIMessage(content=response)],
        "current_stage": "budget_qualification",
        "previous_stage": state.current_stage,
        "turn_count": state.turn_count,
        "tokens_used": state.tokens_used,
    }


async def timeline_qualification_node(state: ConversationState) -> dict:
    """Understand the customer's timeline."""
    response = await _call_llm(state, "timeline_qualification")
    state.turn_count += 1
    return {
        "messages": [AIMessage(content=response)],
        "current_stage": "timeline_qualification",
        "previous_stage": state.current_stage,
        "turn_count": state.turn_count,
        "tokens_used": state.tokens_used,
    }


async def book_meeting_node(state: ConversationState) -> dict:
    """Offer to schedule a meeting."""
    response = await _call_llm(state, "book_meeting")
    state.turn_count += 1
    return {
        "messages": [AIMessage(content=response)],
        "current_stage": "book_meeting",
        "previous_stage": state.current_stage,
        "turn_count": state.turn_count,
        "tokens_used": state.tokens_used,
    }


async def send_followup_node(state: ConversationState) -> dict:
    """Confirm and send follow-up communications."""
    response = await _call_llm(state, "send_followup")
    state.turn_count += 1
    return {
        "messages": [AIMessage(content=response)],
        "current_stage": "send_followup",
        "previous_stage": state.current_stage,
        "followup_sent": True,
        "turn_count": state.turn_count,
        "tokens_used": state.tokens_used,
    }


async def save_crm_node(state: ConversationState) -> dict:
    """Save conversation data to CRM (internal node)."""
    return {
        "current_stage": "save_crm",
        "previous_stage": state.current_stage,
    }


async def end_call_node(state: ConversationState) -> dict:
    """End the conversation gracefully."""
    response = await _call_llm(state, "end_call")
    state.turn_count += 1
    return {
        "messages": [AIMessage(content=response)],
        "current_stage": "end_call",
        "previous_stage": state.current_stage,
        "should_end": True,
        "turn_count": state.turn_count,
        "tokens_used": state.tokens_used,
    }


def determine_next_stage(state: ConversationState) -> str:
    """
    Router function: determine the next conversation stage based on current state.
    This drives the conversation flow through the graph.
    """
    current = state.current_stage
    turn = state.turn_count

    # If should end, go to end
    if state.should_end:
        return "end_call"

    # Natural flow progression
    stage_flow = {
        "greeting": "understand_customer",
        "language_detection": "business_intro",
        "business_intro": "understand_customer",
        "understand_customer": "pain_point_discovery" if turn >= 3 else "understand_customer",
        "pain_point_discovery": "recommend_services" if state.pain_points else "pain_point_discovery",
        "recommend_services": "budget_qualification" if state.interested_services else "recommend_services",
        "budget_qualification": "timeline_qualification" if state.budget_range else "budget_qualification",
        "timeline_qualification": "book_meeting" if state.timeline else "timeline_qualification",
        "book_meeting": "send_followup" if state.meeting_booked else "book_meeting",
        "send_followup": "save_crm",
        "save_crm": "end_call",
    }

    # Advance stages based on turn count to avoid getting stuck
    if turn >= 15:
        if current in ("understand_customer", "pain_point_discovery"):
            return "recommend_services"
        if current in ("recommend_services", "budget_qualification"):
            return "book_meeting"
        if current == "book_meeting":
            return "end_call"

    return stage_flow.get(current, "end_call")
