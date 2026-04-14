"""Vector similarity search."""

from __future__ import annotations

from processing.indexer import get_collection


def semantic_search(query_embedding: list[float], top_k: int) -> list[dict]:
    """Run vector similarity search against ChromaDB."""

    collection = get_collection()

    if collection.count() == 0:
        return []

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )

    ids = results.get("ids", [[]])[0]
    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    formatted_results: list[dict] = []

    for chunk_id, text, metadata, distance in zip(ids, documents, metadatas, distances):
        formatted_results.append(
            {
                "chunk_id": chunk_id,
                "text": text,
                "metadata": metadata or {},
                "score": max(0.0, 1 - float(distance)),
            }
        )

    return formatted_results
