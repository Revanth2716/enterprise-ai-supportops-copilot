from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.db.session import get_db
from app.db.models import KnowledgeDocument, DocumentChunk

router = APIRouter(prefix="/knowledge", tags=["Knowledge"])


@router.get("")
async def list_knowledge_documents(session: AsyncSession = Depends(get_db)):
    stmt = (
        select(
            KnowledgeDocument.id,
            KnowledgeDocument.title,
            KnowledgeDocument.category,
            KnowledgeDocument.version,
            func.count(DocumentChunk.id).label("chunk_count")
        )
        .outerjoin(DocumentChunk, KnowledgeDocument.id == DocumentChunk.document_id)
        .group_by(KnowledgeDocument.id)
    )
    res = await session.execute(stmt)
    rows = res.all()

    return {
        "total_documents": len(rows),
        "documents": [
            {
                "id": r.id,
                "title": r.title,
                "category": r.category,
                "version": r.version,
                "chunk_count": r.chunk_count
            }
            for r in rows
        ]
    }
