"""Text chunking helpers."""

from __future__ import annotations

import re
from collections import defaultdict

from config import CHUNK_OVERLAP, CHUNK_SIZE


def _normalize_text(text: str) -> str:
    """Collapse repeated whitespace so chunks stay compact and readable."""

    return re.sub(r"\s+", " ", text).strip()


def _split_text(text: str) -> list[str]:
    """Split text with a sliding window and drop very short noise chunks."""

    # Clean the source text before chunking so chunk boundaries are based on meaningful characters.
    normalized_text = _normalize_text(text)

    # Return early when the input has no usable text after normalization.
    if not normalized_text:
        return []

    # Keep a list of chunk strings created by the sliding window.
    chunks: list[str] = []

    # Start at the beginning of the text and move forward by chunk_size - overlap each round.
    start = 0
    step = max(CHUNK_SIZE - CHUNK_OVERLAP, 1)

    while start < len(normalized_text):
        # Cut out the current chunk window.
        chunk_text = normalized_text[start : start + CHUNK_SIZE].strip()

        # Keep only chunks that are large enough to carry meaningful context.
        if len(chunk_text) >= 50:
            chunks.append(chunk_text)

        # Advance by the configured step size so adjacent chunks overlap.
        start += step

    return chunks


def chunk_documents(documents: list[dict]) -> list[dict]:
    """Split input documents into overlapping chunks while preserving metadata."""

    # Group chunks by source first so we can assign unique source-wide chunk indexes.
    per_source_records: dict[str, list[dict]] = defaultdict(list)

    for document in documents:
        # Extract and clean the source text for the current document or segment.
        source_text = str(document.get("text", ""))

        # Split the text into chunk strings using the configured windowing rules.
        split_chunks = _split_text(source_text)

        for chunk_text in split_chunks:
            # Preserve every original metadata field, then replace text with the chunk text.
            chunk_record = dict(document)
            chunk_record["text"] = chunk_text
            per_source_records[str(document.get("source", "unknown"))].append(chunk_record)

    # Flatten the grouped records back into one list with stable source-wide IDs.
    final_chunks: list[dict] = []

    for source_name, source_chunks in per_source_records.items():
        total_chunks = len(source_chunks)

        for chunk_index, chunk in enumerate(source_chunks):
            chunk["chunk_index"] = chunk_index
            chunk["chunk_id"] = f"{source_name}_chunk_{chunk_index}"
            chunk["total_chunks"] = total_chunks
            final_chunks.append(chunk)

    return final_chunks
