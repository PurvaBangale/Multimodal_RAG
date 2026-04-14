"""PDF ingestion helpers."""

from __future__ import annotations

from pathlib import Path

import fitz


def extract_text_from_pdf(file_path: str) -> list[dict]:
    """Extract text page by page from a PDF file."""

    # Capture only the file name so source labels stay clean in the UI and citations.
    source_name = Path(file_path).name

    # Prepare a list that will hold one record per page with extracted text.
    extracted_pages: list[dict] = []

    try:
        # Open the PDF with PyMuPDF so we can iterate through each page.
        with fitz.open(file_path) as pdf_document:
            # Enumerate pages starting at 1 so page numbers match what users see in the PDF viewer.
            for page_number, page in enumerate(pdf_document, start=1):
                # Read plain text from the current page and trim leading/trailing whitespace.
                page_text = page.get_text("text").strip()

                # Skip empty pages so the index does not fill with useless blank chunks.
                if not page_text:
                    continue

                # Store the extracted text together with metadata needed later for citations.
                extracted_pages.append(
                    {
                        "text": page_text,
                        "page": page_number,
                        "source": source_name,
                        "type": "document",
                    }
                )
    except Exception as exc:
        # Raise a clear runtime error so the API can return a helpful message to the user.
        raise RuntimeError(f"Failed to extract text from PDF '{source_name}': {exc}") from exc

    return extracted_pages
