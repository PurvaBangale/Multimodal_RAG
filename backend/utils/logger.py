"""Simple timestamped logger for backend events."""

from __future__ import annotations

from datetime import datetime


def log(level: str, message: str) -> None:
    """Print a log line with a timestamp and severity level."""

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{level.upper()}] {message}")
