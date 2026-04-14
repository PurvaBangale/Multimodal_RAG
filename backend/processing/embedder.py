"""Embedding helpers."""

from __future__ import annotations

import hashlib

from sentence_transformers import SentenceTransformer

from config import EMBEDDING_MODEL

# Load the embedding model once so every request can reuse the same model instance.
EMBEDDING_MODEL_INSTANCE = SentenceTransformer(EMBEDDING_MODEL)

# Cache previously computed embeddings so repeated uploads or queries avoid duplicate model work.
_EMBEDDING_CACHE: dict[str, list[float]] = {}


def _text_cache_key(text: str) -> str:
    """Generate a stable hash key for cache lookups."""

    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def embed_chunks(chunks: list[dict]) -> list[dict]:
    """Attach embeddings to chunk dictionaries."""

    # Separate cached texts from uncached texts so we only run the model on new content.
    uncached_texts: list[str] = []
    uncached_keys: list[str] = []

    for chunk in chunks:
        key = _text_cache_key(chunk["text"])
        if key not in _EMBEDDING_CACHE:
            uncached_keys.append(key)
            uncached_texts.append(chunk["text"])

    if uncached_texts:
        # Encode new chunk texts in batches for better throughput on CPU.
        uncached_embeddings = EMBEDDING_MODEL_INSTANCE.encode(
            uncached_texts,
            batch_size=64,
            normalize_embeddings=True,
            convert_to_numpy=True,
            show_progress_bar=False,
        )

        for key, embedding in zip(uncached_keys, uncached_embeddings):
            _EMBEDDING_CACHE[key] = embedding.tolist()

    # Copy each chunk so callers keep their original data untouched.
    embedded_chunks: list[dict] = []

    for chunk in chunks:
        chunk_copy = dict(chunk)
        chunk_copy["embedding"] = _EMBEDDING_CACHE[_text_cache_key(chunk["text"])]
        embedded_chunks.append(chunk_copy)

    return embedded_chunks


def embed_query(query: str) -> list[float]:
    """Embed a single query string."""

    key = _text_cache_key(query)

    if key not in _EMBEDDING_CACHE:
        query_embedding = EMBEDDING_MODEL_INSTANCE.encode(
            [query],
            batch_size=1,
            normalize_embeddings=True,
            convert_to_numpy=True,
            show_progress_bar=False,
        )[0]
        _EMBEDDING_CACHE[key] = query_embedding.tolist()

    return _EMBEDDING_CACHE[key]
