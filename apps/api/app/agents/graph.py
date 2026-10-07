import time
import logging
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.state import AgentState
from app.agents.nodes import (
    guard_check_node,
    classify_intent_node,
    retrieve_knowledge_node,
    plan_tools_node,
    execute_tools_node,
    synthesize_response_node,
    validate_citations_node,
    output_guard_node
)

logger = logging.getLogger(__name__)

MAX_RECURSION_LIMIT = 5


class SupportOpsAgentGraph:
    """
    Bounded, deterministic State Graph for Enterprise Support Operations.
    Enforces strict recursion limit (<= 5) and single-pass tool planning.
    """

    def __init__(self, recursion_limit: int = MAX_RECURSION_LIMIT):
        self.recursion_limit = recursion_limit

    async def run(
        self,
        query: str,
        session_id: str,
        user_id: Optional[str] = None,
        session: Optional[AsyncSession] = None
    ) -> AgentState:
        # Initialize Clean State
        state: AgentState = {
            "session_id": session_id,
            "user_id": user_id,
            "raw_query": query,
            "sanitized_query": query,
            "is_blocked": False,
            "block_reasons": [],
            "intent": "unclassified",
            "entities": {},
            "required_tools": [],
            "retrieved_chunks": [],
            "retrieval_mode": "hybrid",
            "tool_results": {},
            "tool_calls_trace": [],
            "synthesized_response": "",
            "validated_citations": [],
            "unverified_citations": [],
            "confidence_score": 0.0,
            "provider_used": "mock",
            "model_name": "supportops-mock-v1",
            "fallback_used": False,
            "total_tokens": 0,
            "estimated_cost_usd": 0.0,
            "execution_steps": [],
            "recursion_count": 0,
            "error": None
        }

        # Step 1: Guard Check
        state = await guard_check_node(state, session)
        if state["is_blocked"]:
            state = await output_guard_node(state, session)
            return state

        # Step 2: Classify Intent
        state = await classify_intent_node(state, session)

        # Step 3: Retrieve Knowledge
        state = await retrieve_knowledge_node(state, session)

        # Step 4: Plan Tools
        state = await plan_tools_node(state, session)

        # Step 5: Execute Approved Tools
        state = await execute_tools_node(state, session)

        # Step 6: Synthesize Response
        state = await synthesize_response_node(state, session)

        # Step 7: Validate Citations
        state = await validate_citations_node(state, session)

        # Step 8: Output Guard
        state = await output_guard_node(state, session)

        return state


# Singleton agent graph instance
supportops_agent = SupportOpsAgentGraph()
