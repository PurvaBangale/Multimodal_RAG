"""Context formatting helpers for grounded answer generation."""

from __future__ import annotations


def _location_label(metadata: dict) -> str:
    """Choose the most useful citation location label for a chunk."""

    if metadata.get("type") == "audio" and metadata.get("timestamp"):
        return str(metadata["timestamp"])

    if metadata.get("page") is not None:
        return f"Page {metadata['page']}"

    return "Unknown location"


def build_context(query: str, chunks: list[dict]) -> dict:
    """Format reranked chunks into an LLM-ready context block plus source cards."""

    context_sections: list[str] = []
    sources: list[dict] = []

    for index, chunk in enumerate(chunks, start=1):
        ref = f"[{index}]"
        metadata = dict(chunk.get("metadata", {}))
        location = _location_label(metadata)
        source_name = str(metadata.get("source", "Unknown source"))
        source_type = str(metadata.get("type", "unknown"))
        text = str(chunk.get("text", "")).strip()
        score = float(chunk.get("rerank_score", chunk.get("rrf_score", chunk.get("score", 0.0))))

        context_sections.append(f"{ref} Source: {source_name} ({location})\n{text}")
        sources.append(
            {
                "ref": ref,
                "source": source_name,
                "type": source_type,
                "location": location,
                "text_snippet": text[:200],
                "score": score,
            }
        )

    return {
        "query": query,
        "context_text": "\n\n".join(context_sections),
        "sources": sources,
    }
