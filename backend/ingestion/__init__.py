"""Unified file ingestion entry points."""

from __future__ import annotations

from pathlib import Path

from .audio_loader import extract_text_from_audio
from .document_loader import extract_text_from_pdf
from .image_loader import extract_text_from_image


def ingest_file(file_path: str) -> list[dict]:
    """Route a file to the correct loader based on its extension."""

    # Normalize the extension to lower-case so .PDF and .pdf are treated the same.
    extension = Path(file_path).suffix.lower()

    if extension == ".pdf":
        return extract_text_from_pdf(file_path)

    if extension in {".png", ".jpg", ".jpeg"}:
        return extract_text_from_image(file_path)

    if extension in {".mp3", ".wav", ".m4a"}:
        return extract_text_from_audio(file_path)

    # Reject anything else early so unsupported files never reach the heavy models.
    raise ValueError(f"Unsupported file format: {extension}")
