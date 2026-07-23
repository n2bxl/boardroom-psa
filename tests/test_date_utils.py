# tests/test_date_utils.py

from __future__ import annotations

from datetime import date, timedelta

from core.date_utils import (
    DUE_DATE_ERROR,
    due_date_sort_key,
    is_due_today,
    is_overdue,
    normalize_due_date,
    parse_due_date,
)

def test_parse_due_date_accepts_iso_date():
    parsed = parse_due_date("2026-07-22")
    assert parsed == date(2026, 7, 22)

def test_parse_due_date_rejects_wrong_format():
    assert parse_due_date("7/22/2026") is None
    assert parse_due_date("20260722") is None

def test_parse_due_date_rejects_impossible_date():
    assert parse_due_date("2026-02-30") is None

def test_normalize_due_date_accepts_blank_value():
    normalized, error = normalize_due_date("")
    assert normalized is None
    assert error is None

def test_normalize_due_date_returns_validation_error():
    normalized, error = normalize_due_date("tomorrow")
    assert normalized is None
    assert error == DUE_DATE_ERROR

def test_today_and_overdue_helpers():
    today = date.today()
    yesterday = today - timedelta(days=1)
    tomorrow = today + timedelta(days=1)

    assert is_due_today(today.isoformat()) is True
    assert is_overdue(yesterday.isoformat()) is True
    assert is_overdue(tomorrow.isoformat()) is False

def test_due_date_sort_key_places_invalid_dates_last():
    valid = due_date_sort_key("2026-07-22")
    missing = due_date_sort_key(None)
    invalid = due_date_sort_key("not-a-date")

    assert valid == date(2026, 7, 22)
    assert missing == date.max
    assert invalid == date.max