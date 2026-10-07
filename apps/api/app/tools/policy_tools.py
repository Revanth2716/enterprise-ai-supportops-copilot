from typing import Optional, Dict, Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import KnowledgeDocument, DocumentChunk


async def lookup_policy(
    category: str,
    session: AsyncSession
) -> Dict[str, Any]:
    """
    Direct category lookup for enterprise policies (billing, refund, sla, security).
    """
    category_clean = category.strip().lower()
    stmt = (
        select(KnowledgeDocument)
        .where(KnowledgeDocument.category.ilike(f"%{category_clean}%"))
    )
    res = await session.execute(stmt)
    doc = res.scalars().first()

    if not doc:
        return {
            "found": False,
            "message": f"No policy document found under category '{category}'."
        }

    # Fetch top chunks
    chunk_stmt = (
        select(DocumentChunk)
        .where(DocumentChunk.document_id == doc.id)
        .order_by(DocumentChunk.chunk_index)
        .limit(3)
    )
    c_res = await session.execute(chunk_stmt)
    chunks = c_res.scalars().all()

    return {
        "found": True,
        "document_title": doc.title,
        "category": doc.category,
        "version": doc.version,
        "key_excerpts": [
            {
                "chunk_index": c.chunk_index,
                "content": c.content,
                "citation_token": f"[Doc:{doc.title}#C{c.chunk_index}]"
            }
            for c in chunks
        ]
    }
