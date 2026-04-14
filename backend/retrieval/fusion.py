"""Hybrid result fusion."""

from __future__ import annotations

import asyncio

from retrieval.bm25_search import bm25_search
from retrieval.semantic_search import semantic_search


def reciprocal_rank_fusion(results_list: list[list[dict]], k: int = 60) -> list[dict]:
    """Merge ranked results using Reciprocal Rank Fusion (RRF)."""

    # RRF adds 1 / (k + rank) for each appearance of a document across ranked lists.
    # The standard default k=60 softens the effect of small rank changes while still rewarding consistent hits.
    fused_scores: dict[str, float] = {}
    fused_records: dict[str, dict] = {}

    for result_group in results_list:
        for rank, chunk in enumerate(result_group, start=1):
            chunk_id = chunk["chunk_id"]
            fused_scores[chunk_id] = fused_scores.get(chunk_id, 0.0) + (1.0 / (k + rank))

            if chunk_id not in fused_records:
                fused_records[chunk_id] = dict(chunk)

    merged_results: list[dict] = []

    for chunk_id, chunk in fused_records.items():
        chunk_copy = dict(chunk)
        chunk_copy["rrf_score"] = fused_scores[chunk_id]
        merged_results.append(chunk_copy)

    merged_results.sort(key=lambda item: item["rrf_score"], reverse=True)
    return merged_results


async def hybrid_search(query: str, query_embedding: list[float], top_k: int) -> list[dict]:
    """Run semantic and BM25 search together, then fuse the results."""

    semantic_task = asyncio.to_thread(semantic_search, query_embedding, top_k)
    bm25_task = asyncio.to_thread(bm25_search, query, top_k)
    semantic_results, bm25_results = await asyncio.gather(semantic_task, bm25_task)
    fused_results = reciprocal_rank_fusion([semantic_results, bm25_results])
    return fused_results[:top_k]
