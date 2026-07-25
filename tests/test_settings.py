# test/test_settings.py

from __future__ import annotations

from core.config import DEFAULTS
from ui.settings import (
    STALE_THRESHOLD_DRAFT_KEY,
    apply_stale_threshold_draft,
    initialize_stale_threshold_draft,
    reset_settings_state,
)

def test_initialize_stale_threshold_draft_preserves_unsaved_value():
    session_state = {}

    initialize_stale_threshold_draft(
        session_state,
        lambda key: 3,
    )

    assert session_state[STALE_THRESHOLD_DRAFT_KEY] == 3

    session_state[STALE_THRESHOLD_DRAFT_KEY] = 7

    initialize_stale_threshold_draft(
        session_state,
        lambda key: 3,
    )

    assert session_state[STALE_THRESHOLD_DRAFT_KEY] == 7

def test_apply_stale_threshold_draft_updates_active_setting():
    session_state = {
        "stale_days_threshold": 3,
        STALE_THRESHOLD_DRAFT_KEY: 7,
    }

    apply_stale_threshold_draft(session_state)

    assert session_state["stale_days_threshold"] == 7
    assert session_state[STALE_THRESHOLD_DRAFT_KEY] == 7

def test_reset_settings_state_restores_defaults_and_draft():
    session_state = {
        key: "changed"
        for key in DEFAULTS
    }
    session_state[STALE_THRESHOLD_DRAFT_KEY] = 12

    reset_settings_state(session_state)

    for key, value in DEFAULTS.items():
        assert session_state[key] == value

    assert session_state[STALE_THRESHOLD_DRAFT_KEY] == 3