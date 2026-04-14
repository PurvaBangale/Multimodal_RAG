"""Keyword search with BM25."""

from __future__ import annotations

from rank_bm25 import BM25Okapi

from processing.indexer import get_all_chunks

# Keep the BM25 index in memory so repeated queries do not rebuild it unnecessarily.
_bm25_cache = {"index": None, "chunks": None, "dirty": True}


def invalidate_bm25_cache() -> None:
    """Mark the in-memory BM25 index as stale after ingestion or reset."""

    _bm25_cache["dirty"] = True


def build_bm25_index() -> tuple[BM25Okapi | None, list[dict]]:
    """Build or reuse a BM25 index from all stored chunks."""

    if not _bm25_cache["dirty"] and _bm25_cache["index"] is not None and _bm25_cache["chunks"] is not None:
        return _bm25_cache["index"], _bm25_cache["chunks"]

    all_chunks = get_all_chunks()

    if not all_chunks:
        _bm25_cache["index"] = None
        _bm25_cache["chunks"] = []
        _bm25_cache["dirty"] = False
        return None, []

    tokenized_corpus = [chunk["text"].lower().split() for chunk in all_chunks]
    bm25_index = BM25Okapi(tokenized_corpus)

    _bm25_cache["index"] = bm25_index
    _bm25_cache["chunks"] = all_chunks
    _bm25_cache["dirty"] = False

    return bm25_index, all_chunks


def bm25_search(query: str, top_k: int) -> list[dict]:
    """Run keyword search over the cached BM25 index."""

    bm25_index, all_chunks = build_bm25_index()

    if bm25_index is None or not all_chunks:
        return []

    tokenized_query = query.lower().split()
    scores = bm25_index.get_scores(tokenized_query)

    ranked_pairs = sorted(
        zip(all_chunks, scores),
        key=lambda item: float(item[1]),
        reverse=True,
    )[:top_k]

    results: list[dict] = []

    for chunk, score in ranked_pairs:
        results.append(
            {
                "chunk_id": chunk["chunk_id"],
                "text": chunk["text"],
                "metadata": chunk["metadata"],
                "score": float(score),
            }
        )

    return results
