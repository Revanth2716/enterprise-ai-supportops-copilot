import pytest
from app.rag.chunker import DocumentChunker
from app.rag.fusion import reciprocal_rank_fusion
from app.rag.retriever import hybrid_retriever


def test_chunker_splits_markdown_sections():
    chunker = DocumentChunker(chunk_size=200, chunk_overlap=20)
    markdown = """# Section 1
This is the first paragraph with some details.

## Section 2
This is the second section discussing billing and payments.
"""
    chunks = chunker.chunk_markdown("doc-1", "Billing Policy", "billing", markdown)
    assert len(chunks) >= 2
    assert chunks[0]["document_title"] == "Billing Policy"
    assert "Section 1" in chunks[0]["section_title"] or "General" in chunks[0]["section_title"]


def test_reciprocal_rank_fusion_scoring():
    sem_results = [
        {"chunk_id": "c1", "title": "Doc 1"},
        {"chunk_id": "c2", "title": "Doc 2"},
    ]
    lex_results = [
        {"chunk_id": "c2", "title": "Doc 2"},
        {"chunk_id": "c3", "title": "Doc 3"},
    ]
    fused = reciprocal_rank_fusion(sem_results, lex_results, k=60, top_n=3)
    assert len(fused) == 3
    # c2 was present in both, so it should rank top
    assert fused[0]["chunk_id"] == "c2"
    assert fused[0]["rrf_score"] > fused[1]["rrf_score"]


@pytest.mark.asyncio
async def test_retriever_search_with_lexical_fallback(db_session):
    res = await hybrid_retriever.search("duplicate charge invoice", db_session, top_k=2)
    assert "chunks" in res
    assert len(res["chunks"]) > 0
    # Every returned chunk must have a citation token
    for c in res["chunks"]:
        assert "citation_token" in c
        assert "[Doc:" in c["citation_token"]
