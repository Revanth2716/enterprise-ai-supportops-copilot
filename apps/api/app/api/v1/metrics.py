from fastapi import APIRouter, Response, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.db.session import get_db
from app.db.models import AgentRun, LLMCall
from app.observability.prometheus import get_prometheus_metrics

router = APIRouter(tags=["Metrics"])


@router.get("/metrics")
async def prometheus_metrics():
    """Returns standard Prometheus scrape format."""
    return Response(content=get_prometheus_metrics(), media_type="text/plain; version=0.0.4; charset=utf-8")


@router.get("/api/v1/metrics")
async def json_metrics(session: AsyncSession = Depends(get_db)):
    """Returns application summary telemetry in structured JSON."""
    runs_count = 0
    total_tokens = 0
    total_cost = 0.0

    try:
        r_stmt = select(func.count(AgentRun.id)).select_from(AgentRun)
        runs_res = await session.execute(r_stmt)
        runs_count = runs_res.scalar_one() or 0

        t_stmt = select(func.sum(LLMCall.total_tokens)).select_from(LLMCall)
        t_res = await session.execute(t_stmt)
        total_tokens = t_res.scalar_one() or 0

        c_stmt = select(func.sum(LLMCall.estimated_cost_usd)).select_from(LLMCall)
        c_res = await session.execute(c_stmt)
        total_cost = float(c_res.scalar_one() or 0.0)
    except Exception:
        pass

    return {
        "status": "operational",
        "total_agent_runs": runs_count,
        "total_tokens_consumed": total_tokens,
        "total_estimated_cost_usd": round(total_cost, 6),
        "cost_model": "Zero-Cost Local Default ($0.00 in mock mode)",
        "active_provider": "MockProvider (Deterministic $0.00)"
    }
