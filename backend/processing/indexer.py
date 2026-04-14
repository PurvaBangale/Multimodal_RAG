"""ChromaDB indexing helpers."""

from __future__ import annotations

from typing import Any

import chromadb

from config import CHROMA_PERSIST_DIR

# Create one persistent client so all parts of the app share the same local vector store.
CHROMA_CLIENT = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)

# Use a stable collection name so indexing and retrieval always talk to the same dataset.
COLLECTION_NAME = "rag_collection"

# Create the collection if it does not exist yet, or load the existing one from disk.
COLLECTION = CHROMA_CLIENT.get_or_create_collection(name=COLLECTION_NAME)


def _flatten_metadata(chunk: dict[str, Any]) -> dict[str, Any]:
    """Keep only Chroma-friendly scalar metadata values."""

    flat_metadata: dict[str, Any] = {}

    for key, value in chunk.items():
        if key in {"embedding", "text"}:
            continue

        if isinstance(value, (str, int, float, bool)) or value is None:
            flat_metadata[key] = value
        else:
            flat_metadata[key] = str(value)

    return flat_metadata


def get_collection():
    """Return the active Chroma collection."""

    global COLLECTION
    COLLECTION = CHROMA_CLIENT.get_or_create_collection(name=COLLECTION_NAME)
    return COLLECTION


def index_chunks(chunks: list[dict]) -> int:
    """Upsert embedded chunks into ChromaDB."""

    if not chunks:
        return 0

    # Build the parallel lists Chroma expects for ids, vectors, documents, and metadata.
    ids = [str(chunk["chunk_id"]) for chunk in chunks]
    embeddings = [list(chunk["embedding"]) for chunk in chunks]
    documents = [str(chunk["text"]) for chunk in chunks]
    metadatas = [_flatten_metadata(chunk) for chunk in chunks]

    get_collection().upsert(ids=ids, embeddings=embeddings, documents=documents, metadatas=metadatas)
    return len(chunks)


def get_all_chunks() -> list[dict]:
    """Read every stored chunk back out of ChromaDB."""

    stored = get_collection().get(include=["documents", "metadatas"])
    ids = stored.get("ids", [])
    documents = stored.get("documents", [])
    metadatas = stored.get("metadatas", [])

    all_chunks: list[dict] = []

    for chunk_id, document, metadata in zip(ids, documents, metadatas):
        all_chunks.append(
            {
                "chunk_id": chunk_id,
                "text": document,
                "metadata": metadata or {},
            }
        )

    return all_chunks


def reset_collection():
    """Delete and recreate the Chroma collection."""

    global COLLECTION

    try:
        CHROMA_CLIENT.delete_collection(name=COLLECTION_NAME)
    except Exception:
        # Ignore missing-collection errors so reset stays idempotent.
        pass

    COLLECTION = CHROMA_CLIENT.get_or_create_collection(name=COLLECTION_NAME)
    return COLLECTION
