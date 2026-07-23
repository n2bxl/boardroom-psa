# core/date_utils.py

from __future__ import annotations

import re
from datetime import date

DUE_DATE_ERROR = "Due date must be blank or use YYYY-MM-DD."

_DUE_DATE_PATTERN = re.compile(r"\d{4}-\d{2}-\d{2}")

def parse_due_date(value:str | None) -> date | None:
    """
    Parse a stored due-date string.

    Returns None when the value is blank, incorrectly formatted,
    or not a real calendar date.
    """
    clean = (value or "").strip()

    if not clean:
        return None

    if _DUE_DATE_PATTERN.fullmatch(clean) is None:
        return None

    try:
        return date.fromisoformat(clean)
    except ValueError:
        return None

def normalize_due_date(
        value: str | None,
) -> tuple[str |None, str | None]:
    """
    Validate and normalize a user-supplied due date.

    Returns:
        (normalized_date, error_message)

    Examples:
        "2026-07-22" -> ("2026-07-22", None)
        ""           -> (None, None)
        "7/22/2026"  -> (None, DUE_DATE_ERROR)
    """
    clean = (value or "").strip()

    if not clean:
        return None, None

    parsed = parse_due_date(clean)

    if parsed is None:
        return None, DUE_DATE_ERROR

    return parsed.isoformat(), None

def today_iso() -> str:
    """Return today's local date in ISO format."""
    return date.today().isoformat()

def is_due_today(value: str | None) -> bool:
    """Return True if the given due date is today."""
    return parse_due_date(value) == date.today()

def is_overdue(value: str | None) -> bool:
    """Return True if the given due date is in the past."""
    parsed = parse_due_date(value)
    return parsed is not None and parsed < date.today()

def due_date_sort_key(value: str | None) -> date:
    """
    Return a safe sort key

    Missing or invalid dates are placed after valid dates.
    """
    return parse_due_date(value) or date.max