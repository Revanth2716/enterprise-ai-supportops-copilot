from typing import List, Dict, Any
from collections import defaultdict


def reciprocal_rank_fusion(
    semantic_results: List[Dict[str, Any]],
    lexical_results: List[Dict[str, Any]],
    k: int = 60,
    top_n: int = 3
) -> List[Dict[str, Any]]:
    """
    Combines semantic and lexical search rankings using Reciprocal Rank Fusion (RRF).
    score(doc) = sum(1 / (k + rank)) across available rankers.
    """
    scores: Dict[str, float] = defaultdict(float)
    doc_lookup: Dict[str, Dict[str, Any]] = {}

    # 1. Process Semantic Ranks
    for rank, doc in enumerate(semantic_results, start=1):
        doc_id = doc["chunk_id"]
        doc_lookup[doc_id] = doc
        scores[doc_id] += 1.0 / (k + rank)

    # 2. Process Lexical Ranks
    for rank, doc in enumerate(lexical_results, start=1):
        doc_id = doc["chunk_id"]
        if doc_id not in doc_lookup:
            doc_lookup[doc_id] = doc
        scores[doc_id] += 1.0 / (k + rank)

    # 3. Sort by fused RRF score descending
    sorted_doc_ids = sorted(scores.keys(), key=lambda did: scores[did], reverse=True)

    fused_results = []
    for did in sorted_doc_ids[:top_n]:
        item = dict(doc_lookup[did])
        item["rrf_score"] = round(scores[did], 5)
        fused_results.append(item)

    return fused_results
