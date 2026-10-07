import uuid
import time
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.db.models import AgentRun, AgentStep, ToolCall, LLMCall
from app.agents.graph import supportops_agent
from app.observability.prometheus import (
    TOOL_CALLS_TOTAL,
    LLM_TOKENS_TOTAL,
    ESTIMATED_COST_USD_TOTAL,
    GUARDRAIL_BLOCKS_TOTAL
)

router = APIRouter(prefix="/chat", tags=["Chat"])


class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=2000, description="Customer support inquiry")
    session_id: Optional[str] = Field(default=None, description="Client session identifier")
    user_id: Optional[str] = Field(default=None, description="Operator user identifier")


class CitationItem(BaseModel):
    citation_token: str
    document_title: Optional[str] = None
    chunk_id: Optional[str] = None
    content_excerpt: Optional[str] = None


class ToolCallItem(BaseModel):
    tool_name: str
    source: str
    success: bool
    parameters: Dict[str, Any]
    duration_ms: int
    result_summary: str


class ExecutionStepItem(BaseModel):
    step_order: int
    step_name: str
    status: str
    duration_ms: int
    details: Dict[str, Any]


class ChatMetrics(BaseModel):
    total_duration_ms: int
    total_tokens: int
    estimated_cost_usd: float
    provider: str
    model: str
    fallback_used: bool


class ChatResponse(BaseModel):
    run_id: str
    session_id: str
    query: str
    status: str
    response: str
    confidence_score: float
    retrieval_mode: str
    citations: List[CitationItem]
    tool_calls: List[ToolCallItem]
    execution_trace: List[ExecutionStepItem]
    metrics: ChatMetrics


@router.post("", response_model=ChatResponse)
async def process_chat(
    req: ChatRequest,
    session: AsyncSession = Depends(get_db)
):
    start_time = time.perf_counter()
    session_id = req.session_id or f"sess-{uuid.uuid4().hex[:8]}"
    run_id = f"run-{uuid.uuid4().hex[:12]}"

    # Execute Bounded LangGraph Workflow
    state = await supportops_agent.run(
        query=req.query,
        session_id=session_id,
        user_id=req.user_id,
        session=session
    )

    total_duration_ms = int((time.perf_counter() - start_time) * 1000)
    run_status = "GUARD_BLOCKED" if state["is_blocked"] else ("FAILED" if state["error"] else "SUCCESS")

    # Update Prometheus metrics
    if state["is_blocked"]:
        for reason in state["block_reasons"]:
            GUARDRAIL_BLOCKS_TOTAL.labels(reason=reason).inc()

    for tc in state["tool_calls_trace"]:
        TOOL_CALLS_TOTAL.labels(tool=tc["tool_name"], success=str(tc["success"]).lower()).inc()

    LLM_TOKENS_TOTAL.labels(type="total", provider=state["provider_used"]).inc(state["total_tokens"])
    ESTIMATED_COST_USD_TOTAL.inc(state["estimated_cost_usd"])

    # Persist Run to Database
    try:
        agent_run = AgentRun(
            id=run_id,
            user_id=req.user_id,
            session_id=session_id,
            user_query=req.query,
            sanitized_query=state["sanitized_query"],
            status=run_status,
            final_response=state["synthesized_response"],
            confidence_score=state["confidence_score"],
            total_duration_ms=total_duration_ms,
            total_tokens=state["total_tokens"],
            estimated_cost_usd=state["estimated_cost_usd"],
            provider_used=state["provider_used"],
            fallback_occurred=state["fallback_used"]
        )
        session.add(agent_run)

        # Persist Steps
        for s in state["execution_steps"]:
            step_record = AgentStep(
                run_id=run_id,
                step_order=s["step_order"],
                step_name=s["step_name"],
                status=s["status"],
                duration_ms=s["duration_ms"],
                details=s["details"]
            )
            session.add(step_record)

        # Persist Tool Calls
        for tc in state["tool_calls_trace"]:
            tool_record = ToolCall(
                run_id=run_id,
                tool_name=tc["tool_name"],
                source=tc["source"],
                input_parameters=tc["parameters"],
                output_result={"summary": tc["result_summary"]},
                duration_ms=tc["duration_ms"],
                success=tc["success"]
            )
            session.add(tool_record)

        # Persist LLM call
        llm_record = LLMCall(
            run_id=run_id,
            provider=state["provider_used"],
            model_name=state["model_name"],
            total_tokens=state["total_tokens"],
            latency_ms=total_duration_ms,
            estimated_cost_usd=state["estimated_cost_usd"],
            status="SUCCESS" if not state["is_blocked"] else "BLOCKED",
            fallback_used=state["fallback_used"]
        )
        session.add(llm_record)

        await session.commit()
    except Exception as e:
        await session.rollback()
        # Non-blocking persistence warning to guarantee API response
        pass

    return ChatResponse(
        run_id=run_id,
        session_id=session_id,
        query=req.query,
        status=run_status,
        response=state["synthesized_response"],
        confidence_score=state["confidence_score"],
        retrieval_mode=state["retrieval_mode"],
        citations=[CitationItem(**c) for c in state["validated_citations"]],
        tool_calls=[ToolCallItem(**t) for t in state["tool_calls_trace"]],
        execution_trace=[ExecutionStepItem(**st) for st in state["execution_steps"]],
        metrics=ChatMetrics(
            total_duration_ms=total_duration_ms,
            total_tokens=state["total_tokens"],
            estimated_cost_usd=state["estimated_cost_usd"],
            provider=state["provider_used"],
            model=state["model_name"],
            fallback_used=state["fallback_used"]
        )
    )
