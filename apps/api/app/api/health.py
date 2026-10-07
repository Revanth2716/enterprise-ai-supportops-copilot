from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.db.session import get_db
from app.rag.embeddings import embedder
from app.config import settings

router = APIRouter(tags=["Health"])


@router.get("/health")
async def healthcheck(session: AsyncSession = Depends(get_db)):
    db_status = "connected"
    try:
        await session.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    return {
        "status": "healthy" if "unhealthy" not in db_status else "degraded",
        "app_name": settings.APP_NAME,
        "environment": settings.APP_ENV,
        "database": db_status,
        "provider": settings.AI_PROVIDER,
        "embedder": {
            "model": embedder.model_name,
            "is_available": embedder.is_available,
            "fallback_mode": "lexical" if not embedder.is_available else "none"
        }
    }
