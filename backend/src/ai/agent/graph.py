"""
VoiceFlow AI — LangGraph Sales Agent Graph
Stateful conversation graph implementing the full sales flow.
"""

import logging
from typing import Optional

from langchain_core.messages import HumanMessage
from langgraph.graph import END, StateGraph

from src.ai.agent.state import ConversationState
from src.ai.agent.nodes import (
    greeting_node,
    language_detection_node,
    business_intro_node,
    understand_customer_node,
    pain_point_discovery_node,
    recommend_services_node,
    budget_qualification_node,
    timeline_qualification_node,
    book_meeting_node,
    send_followup_node,
    save_crm_node,
    end_call_node,
    determine_next_stage,
)

logger = logging.getLogger(__name__)


def build_sales_graph() -> StateGraph:
    """
    Build the LangGraph state machine for the sales conversation.

    Flow:
    greeting → understand_customer → pain_point_discovery → recommend_services
    → budget_qualification → timeline_qualification → book_meeting
    → send_followup → save_crm → end_call
    """
    graph = StateGraph(ConversationState)

    # ── Add all nodes ──
    graph.add_node("greeting", greeting_node)
    graph.add_node("language_detection", language_detection_node)
    graph.add_node("business_intro", business_intro_node)
    graph.add_node("understand_customer", understand_customer_node)
    graph.add_node("pain_point_discovery", pain_point_discovery_node)
    graph.add_node("recommend_services", recommend_services_node)
    graph.add_node("budget_qualification", budget_qualification_node)
    graph.add_node("timeline_qualification", timeline_qualification_node)
    graph.add_node("book_meeting", book_meeting_node)
    graph.add_node("send_followup", send_followup_node)
    graph.add_node("save_crm", save_crm_node)
    graph.add_node("end_call", end_call_node)

    # ── Set entry point ──
    graph.set_entry_point("greeting")

    # ── Add conditional edges (router-based flow) ──
    for node_name in [
        "greeting", "language_detection", "business_intro",
        "understand_customer", "pain_point_discovery", "recommend_services",
        "budget_qualification", "timeline_qualification", "book_meeting",
        "send_followup", "save_crm",
    ]:
        graph.add_conditional_edges(
            node_name,
            determine_next_stage,
            {
                "greeting": "greeting",
                "language_detection": "language_detection",
                "business_intro": "business_intro",
                "understand_customer": "understand_customer",
                "pain_point_discovery": "pain_point_discovery",
                "recommend_services": "recommend_services",
                "budget_qualification": "budget_qualification",
                "timeline_qualification": "timeline_qualification",
                "book_meeting": "book_meeting",
                "send_followup": "send_followup",
                "save_crm": "save_crm",
                "end_call": "end_call",
            }
        )

    # end_call → END
    graph.add_edge("end_call", END)

    return graph


# Compile the graph once
_compiled_graph = None


def get_compiled_graph():
    """Get or compile the sales conversation graph."""
    global _compiled_graph
    if _compiled_graph is None:
        graph = build_sales_graph()
        _compiled_graph = graph.compile()
        logger.info("✅ Sales conversation graph compiled")
    return _compiled_graph


class SalesAgent:
    """
    High-level interface for the sales conversation agent.
    Manages state across turns and provides a simple API.
    """

    def __init__(
        self,
        tenant_id: str,
        company_name: str,
        services: list[str],
        agent_name: str = "AI Assistant",
        company_context: str = "",
        custom_prompts: dict = None,
        language: str = "en",
    ):
        self.graph = get_compiled_graph()
        self.state = ConversationState(
            tenant_id=tenant_id,
            company_name=company_name,
            services=services,
            agent_name=agent_name,
            company_context=company_context,
            custom_prompts=custom_prompts or {},
            language=language,
        )
        self._initialized = False

    async def start(self) -> str:
        """Start the conversation with a greeting."""
        result = await self.graph.ainvoke(self.state)
        self.state = result
        self._initialized = True

        # Return the last AI message
        for msg in reversed(self.state.messages):
            if hasattr(msg, "content") and not isinstance(msg, HumanMessage):
                return msg.content
        return ""

    async def respond(self, user_message: str) -> str:
        """
        Process a user message and generate a response.

        Args:
            user_message: The customer's spoken/typed message.

        Returns:
            The AI agent's response text.
        """
        if not self._initialized:
            return await self.start()

        # Add user message to state
        self.state.messages.append(HumanMessage(content=user_message))
        self.state.turn_count += 1

        # Run the graph for one step
        result = await self.graph.ainvoke(self.state)
        self.state = result

        # Return the last AI message
        for msg in reversed(self.state.messages):
            if hasattr(msg, "content") and not isinstance(msg, HumanMessage):
                return msg.content
        return ""

    @property
    def is_ended(self) -> bool:
        return self.state.should_end

    @property
    def current_stage(self) -> str:
        return self.state.current_stage

    @property
    def lead_data(self) -> dict:
        return self.state.to_lead_data()

    @property
    def usage_stats(self) -> dict:
        return {
            "tokens_used": self.state.tokens_used,
            "turn_count": self.state.turn_count,
            "stages_visited": self.state.current_stage,
        }
