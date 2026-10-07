from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.db.session import get_db
from app.db.models import AgentRun, AgentStep, ToolCall

router = APIRouter(prefix="/runs", tags=["Runs"])


@router.get("/{run_id}")
async def get_run_details(run_id: str, session: AsyncSession = Depends(get_db)):
    stmt = (
        select(AgentRun)
        .where(AgentRun.id == run_id)
        .options(
            selectinload(AgentRun.steps),
            selectinload(AgentRun.tool_calls)
        )
    )
    res = await session.execute(stmt)
    run = res.scalar_one_or_none()

    if not run:
        raise HTTPException(status_code=404, detail=f"Run {run_id} not found.")

    return {
        "run_id": run.id,
        "session_id": run.session_id,
        "query": run.user_query,
        "status": run.status,
        "final_response": run.final_response,
        "confidence_score": float(run.confidence_score or 0.0),
        "total_duration_ms": run.total_duration_ms,
        "total_tokens": run.total_tokens,
        "estimated_cost_usd": float(run.estimated_cost_usd or 0.0),
        "provider_used": run.provider_used,
        "fallback_occurred": run.fallback_occurred,
        "created_at": run.created_at.isoformat() if run.created_at else None,
        "steps": [
            {
                "step_order": s.step_order,
                "step_name": s.step_name,
                "status": s.status,
                "duration_ms": s.duration_ms,
                "details": s.details
            }
            for s in sorted(run.steps, key=lambda x: x.step_order)
        ],
        "tool_calls": [
            {
                "tool_name": tc.tool_name,
                "source": tc.source,
                "input_parameters": tc.input_parameters,
                "output_result": tc.output_result,
                "duration_ms": tc.duration_ms,
                "success": tc.success
            }
            for tc in run.tool_calls
        ]
    }
