"""Image OCR helpers."""

from __future__ import annotations

from pathlib import Path

import easyocr

# Load the OCR model once because model startup is slow and repeated loads waste a lot of time.
OCR_READER = easyocr.Reader(["en"], gpu=False, verbose=False)


def extract_text_from_image(file_path: str) -> list[dict]:
    """Extract a single block of OCR text from an image file."""

    # Keep only the base file name for user-facing source references.
    source_name = Path(file_path).name

    try:
        # Ask EasyOCR to return only the recognized text strings without bounding boxes or scores.
        text_blocks = OCR_READER.readtext(file_path, detail=0, paragraph=True)

        # Join all detected text fragments into one searchable string for the image.
        image_text = " ".join(block.strip() for block in text_blocks if block and block.strip()).strip()
    except Exception as exc:
        # Surface OCR failures with context so the caller can report the real cause.
        raise RuntimeError(f"Failed to extract text from image '{source_name}': {exc}") from exc

    # Return one record for the whole image so downstream processing can treat it like any other document.
    return [
        {
            "text": image_text,
            "page": 1,
            "source": source_name,
            "type": "image",
        }
    ]
