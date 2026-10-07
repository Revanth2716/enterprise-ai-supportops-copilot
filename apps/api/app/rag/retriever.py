import logging
from typing import List, Dict, Any, Optional
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.rag.embeddings import embedder
from app.rag.fusion import reciprocal_rank_fusion
from app.db.models import DocumentChunk, KnowledgeDocument

logger = logging.getLogger(__name__)


class HybridRetriever:
    """
    Production-grade hybrid retriever combining FastEmbed 384-d semantic vectors,
    PostgreSQL full-text lexical search, and Reciprocal Rank Fusion.
    Gracefully degrades to pure lexical search if semantic model is unavailable.
    """

    def __init__(self):
        self.embedder = embedder

    async def search(
        self,
        query: str,
        session: AsyncSession,
        top_k: int = 3,
        category: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Executes hybrid retrieval and returns top-k chunks with citation metadata.
        """
        semantic_results: List[Dict[str, Any]] = []
        lexical_results: List[Dict[str, Any]] = []
        retrieval_mode = "hybrid"

        # 1. Attempt Semantic Retrieval
        if self.embedder.is_available:
            query_vector = self.embedder.embed_query(query)
            if query_vector:
                semantic_results = await self._vector_search(query_vector, session, top_k * 2, category)
        else:
            retrieval_mode = "lexical_fallback"
            logger.info("retrieving_in_lexical_fallback_mode", extra={"reason": "fastembed_offline"})

        # 2. Execute Lexical Retrieval
        lexical_results = await self._lexical_search(query, session, top_k * 2, category)

        # 3. Combine Rankings
        if semantic_results and lexical_results:
            final_chunks = reciprocal_rank_fusion(semantic_results, lexical_results, k=60, top_n=top_k)
        elif semantic_results:
            final_chunks = semantic_results[:top_k]
            retrieval_mode = "semantic_only"
        else:
            final_chunks = lexical_results[:top_k]
            retrieval_mode = "lexical_fallback"

        # Format citations
        for chunk in final_chunks:
            title = chunk.get("document_title", "Knowledge Manual")
            idx = chunk.get("chunk_index", 1)
            chunk["citation_token"] = f"[Doc:{title}#C{idx}]"

        return {
            "retrieval_mode": retrieval_mode,
            "query": query,
            "total_retrieved": len(final_chunks),
            "chunks": final_chunks
        }

    async def _vector_search(
        self,
        query_vector: List[float],
        session: AsyncSession,
        limit: int,
        category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        try:
            # Query pgvector cosine distance
            stmt = (
                select(
                    DocumentChunk.id,
                    DocumentChunk.document_id,
                    DocumentChunk.chunk_index,
                    DocumentChunk.content,
                    KnowledgeDocument.title.label("document_title"),
                    KnowledgeDocument.category,
                    DocumentChunk.embedding.cosine_distance(query_vector).label("distance")
                )
                .join(KnowledgeDocument, DocumentChunk.document_id == KnowledgeDocument.id)
                .order_by("distance")
                .limit(limit)
            )
            if category:
                stmt = stmt.where(KnowledgeDocument.category == category)

            res = await session.execute(stmt)
            rows = res.all()
            return [
                {
                    "chunk_id": row.id,
                    "document_id": row.document_id,
                    "document_title": row.document_title,
                    "category": row.category,
                    "chunk_index": row.chunk_index,
                    "content": row.content,
                    "similarity_score": round(1.0 - float(row.distance or 0.0), 4)
                }
                for row in rows
            ]
        except Exception as e:
            logger.warning("vector_search_failed_skipping_to_lexical", extra={"error": str(e)})
            return []

    async def _lexical_search(
        self,
        query: str,
        session: AsyncSession,
        limit: int,
        category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        try:
            import re
            from sqlalchemy import or_

            stopwords = {
                "why", "what", "how", "who", "when", "where", "was", "were", "is", "are",
                "the", "and", "for", "our", "says", "their", "with", "from", "that", "this",
                "find", "check", "draft", "response", "tell", "show", "get", "about",
                "does", "have", "been", "would", "could", "should"
            }
            raw_words = [w.lower() for w in re.findall(r'[a-zA-Z0-9\-_]+', query)]
            base_kws = [w for w in raw_words if len(w) > 2 and w not in stopwords]
            if not base_kws:
                base_kws = [w for w in raw_words if len(w) > 2]

            # Generate stemmed variants
            search_terms = set(base_kws)
            for w in base_kws:
                if w.endswith("ies") and len(w) > 4:
                    search_terms.add(w[:-3] + "y")
                elif w.endswith("ed") and len(w) > 3:
                    search_terms.add(w[:-2])
                    search_terms.add(w[:-1])
                elif w.endswith("ing") and len(w) > 4:
                    search_terms.add(w[:-3])
                elif w.endswith("s") and len(w) > 3:
                    search_terms.add(w[:-1])

            stmt = (
                select(
                    DocumentChunk.id,
                    DocumentChunk.document_id,
                    DocumentChunk.chunk_index,
                    DocumentChunk.content,
                    KnowledgeDocument.title.label("document_title"),
                    KnowledgeDocument.category
                )
                .join(KnowledgeDocument, DocumentChunk.document_id == KnowledgeDocument.id)
            )

            conditions = []
            for kw in list(search_terms)[:12]:
                conditions.append(DocumentChunk.content.ilike(f"%{kw}%"))
                conditions.append(KnowledgeDocument.title.ilike(f"%{kw}%"))

            if conditions:
                stmt = stmt.where(or_(*conditions))
            if category:
                stmt = stmt.where(KnowledgeDocument.category == category)

            stmt = stmt.limit(limit)
            res = await session.execute(stmt)
            rows = res.all()

            # If no rows found with category filter, try category fallback or unconstrained search
            if not rows:
                if category:
                    cat_stmt = (
                        select(
                            DocumentChunk.id,
                            DocumentChunk.document_id,
                            DocumentChunk.chunk_index,
                            DocumentChunk.content,
                            KnowledgeDocument.title.label("document_title"),
                            KnowledgeDocument.category
                        )
                        .join(KnowledgeDocument, DocumentChunk.document_id == KnowledgeDocument.id)
                        .where(KnowledgeDocument.category == category)
                        .limit(limit)
                    )
                    cat_res = await session.execute(cat_stmt)
                    rows = cat_res.all()

                if not rows and conditions:
                    unconstrained_stmt = (
                        select(
                            DocumentChunk.id,
                            DocumentChunk.document_id,
                            DocumentChunk.chunk_index,
                            DocumentChunk.content,
                            KnowledgeDocument.title.label("document_title"),
                            KnowledgeDocument.category
                        )
                        .join(KnowledgeDocument, DocumentChunk.document_id == KnowledgeDocument.id)
                        .where(or_(*conditions))
                        .limit(limit)
                    )
                    unres = await session.execute(unconstrained_stmt)
                    rows = unres.all()

            return [
                {
                    "chunk_id": row.id,
                    "document_id": row.document_id,
                    "document_title": row.document_title,
                    "category": row.category,
                    "chunk_index": row.chunk_index,
                    "content": row.content,
                    "similarity_score": 0.85
                }
                for row in rows
            ]
        except Exception as e:
            logger.error("lexical_search_error", extra={"error": str(e)})
            return []


# Singleton retriever
hybrid_retriever = HybridRetriever()
