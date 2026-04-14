"""Cross-encoder reranking."""

from __future__ import annotations

from sentence_transformers import CrossEncoder

from config import RERANKER_MODEL

# Load the reranker once because it is an expensive model to initialize repeatedly.
RERANKER_MODEL_INSTANCE = CrossEncoder(RERANKER_MODEL)


def rerank(query: str, candidates: list[dict], top_k: int) -> list[dict]:
    """Score candidate chunks with a cross-encoder and keep the best ones."""

    if not candidates:
        return []

    # Create query-document pairs because cross-encoders score each pair jointly.
    pairs = [(query, candidate["text"]) for candidate in candidates]

    # Predict one relevance score per pair.
    scores = RERANKER_MODEL_INSTANCE.predict(pairs, show_progress_bar=False)

    reranked_candidates: list[dict] = []

    for candidate, score in zip(candidates, scores):
        candidate_copy = dict(candidate)
        candidate_copy["rerank_score"] = float(score)
        reranked_candidates.append(candidate_copy)

    reranked_candidates.sort(key=lambda item: item["rerank_score"], reverse=True)
    return reranked_candidates[:top_k]
