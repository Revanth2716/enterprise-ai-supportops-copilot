import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.observability.logger import setup_structured_logging
from app.observability.middleware import RequestTracingMiddleware
from app.api.health import router as health_router
from app.api.v1.chat import router as chat_router
from app.api.v1.runs import router as runs_router
from app.api.v1.knowledge import router as knowledge_router
from app.api.v1.evaluations import router as evals_router
from app.api.v1.metrics import router as metrics_router

# Setup structured logging
setup_structured_logging(settings.LOG_LEVEL)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("supportops_copilot_starting_up", extra={"env": settings.APP_ENV, "provider": settings.AI_PROVIDER})
    # Auto-seed on startup if needed
    try:
        from db.seed.seed_data import seed_all
        await seed_all()
    except Exception as e:
        logger.warning("auto_seeding_skipped_or_failed", extra={"error": str(e)})

    yield
    logger.info("supportops_copilot_shutting_down")


app = FastAPI(
    title=settings.APP_NAME,
    description="Enterprise AI SupportOps Copilot API with bounded LangGraph orchestration, hybrid RAG, guardrails, and MCP.",
    version="2026.1.0",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request Tracing & Observability Middleware
app.add_middleware(RequestTracingMiddleware)

# Include API Routers
app.include_router(health_router)
app.include_router(chat_router, prefix="/api/v1")
app.include_router(runs_router, prefix="/api/v1")
app.include_router(knowledge_router, prefix="/api/v1")
app.include_router(evals_router, prefix="/api/v1")
app.include_router(metrics_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.API_HOST, port=settings.API_PORT, reload=settings.DEBUG)
