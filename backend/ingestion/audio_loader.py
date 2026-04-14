"""Audio transcription helpers."""

from __future__ import annotations

from pathlib import Path

import whisper

from config import WHISPER_MODEL

# Load the Whisper model once at import time so repeated uploads reuse the same model in memory.
AUDIO_MODEL = whisper.load_model(WHISPER_MODEL)


def _format_timestamp(seconds: float) -> str:
    """Convert raw seconds into a readable HH:MM:SS label."""

    # Round down to a whole number of seconds because segment times do not need millisecond precision here.
    total_seconds = int(seconds)

    # Convert the total seconds into hours, minutes, and seconds.
    hours, remainder = divmod(total_seconds, 3600)
    minutes, secs = divmod(remainder, 60)

    # Always include all three fields so timestamps are visually consistent in citations.
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def extract_text_from_audio(file_path: str) -> list[dict]:
    """Transcribe an audio file and return one record per Whisper segment."""

    # Keep the source label compact for citations and UI display.
    source_name = Path(file_path).name

    try:
        # Run local transcription with Whisper and ask it to return timestamped segments.
        result = AUDIO_MODEL.transcribe(file_path)
    except Exception as exc:
        # Re-raise with the file name to make debugging failed uploads much easier.
        raise RuntimeError(f"Failed to transcribe audio '{source_name}': {exc}") from exc

    # Build one searchable record per segment so users can trace answers back to a moment in the audio.
    segments: list[dict] = []

    # Iterate over Whisper's segment list, skipping segments that contain no useful text.
    for segment in result.get("segments", []):
        # Normalize the segment text so downstream chunking starts from clean strings.
        segment_text = str(segment.get("text", "")).strip()

        if not segment_text:
            continue

        # Store the text together with a formatted timestamp for later citations.
        segments.append(
            {
                "text": segment_text,
                "timestamp": _format_timestamp(float(segment.get("start", 0))),
                "source": source_name,
                "type": "audio",
            }
        )

    return segments
