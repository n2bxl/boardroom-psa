# tests/test_settings.py

from __future__ import annotations

from copy import deepcopy

from core.config import DEFAULTS
from ui.settings import (
    EDITABLE_SETTING_KEYS,
    apply_settings_drafts,
    build_settings_from_drafts,
    draft_key,
    draft_to_setting_value,
    initialize_settings_drafts,
    persist_default_settings,
    persist_settings_drafts,
    reset_settings_state,
    setting_to_draft_value,
)


def get_setting_from(values):
    """Return a test-friendly get_setting function."""
    return lambda key: values[key]


def test_draft_key_uses_consistent_prefix():
    assert (
        draft_key("stale_days_threshold")
        == "draft_setting_stale_days_threshold"
    )


def test_queue_setting_converts_to_display_value():
    assert (
        setting_to_draft_value(
            "default_queues",
            "ALL",
        )
        == "ALL"
    )

    assert (
        setting_to_draft_value(
            "default_queues",
            ["Personal"],
        )
        == "Personal only"
    )


def test_queue_draft_converts_to_active_value():
    assert (
        draft_to_setting_value(
            "default_queues",
            "ALL",
        )
        == "ALL"
    )

    assert (
        draft_to_setting_value(
            "default_queues",
            "Personal only",
        )
        == ["Personal"]
    )


def test_initialize_settings_drafts_uses_active_settings():
    active_settings = deepcopy(DEFAULTS)
    active_settings["stale_days_threshold"] = 7
    active_settings["default_queues"] = ["Personal"]

    session_state = {}

    initialize_settings_drafts(
        session_state,
        get_setting_from(active_settings),
    )

    assert (
        session_state[draft_key("stale_days_threshold")]
        == 7
    )

    assert (
        session_state[draft_key("default_queues")]
        == "Personal only"
    )


def test_initialize_settings_drafts_preserves_unsaved_values():
    session_state = {
        draft_key("stale_days_threshold"): 12,
    }

    initialize_settings_drafts(
        session_state,
        get_setting_from(DEFAULTS),
    )

    assert (
        session_state[draft_key("stale_days_threshold")]
        == 12
    )


def test_apply_settings_drafts_updates_all_active_settings():
    session_state = {
        "tabs": deepcopy(DEFAULTS["tabs"]),
    }

    initialize_settings_drafts(
        session_state,
        get_setting_from(DEFAULTS),
    )

    session_state[draft_key("ollama_model")] = "test-model"
    session_state[draft_key("llm_temperature")] = 0.7
    session_state[draft_key("default_queues")] = "Personal only"
    session_state[draft_key("stale_days_threshold")] = 9
    session_state[draft_key("task_note_height")] = 200

    apply_settings_drafts(session_state)

    assert session_state["ollama_model"] == "test-model"
    assert session_state["llm_temperature"] == 0.7
    assert session_state["default_queues"] == ["Personal"]
    assert session_state["stale_days_threshold"] == 9
    assert session_state["task_note_height"] == 200
    assert session_state["tabs"] == DEFAULTS["tabs"]


def test_apply_settings_drafts_covers_every_editable_setting():
    session_state = {}

    initialize_settings_drafts(
        session_state,
        get_setting_from(DEFAULTS),
    )

    apply_settings_drafts(session_state)

    for setting_key in EDITABLE_SETTING_KEYS:
        assert setting_key in session_state


def test_reset_settings_state_restores_active_defaults():
    session_state = {
        setting_key: "changed"
        for setting_key in DEFAULTS
    }

    for setting_key in EDITABLE_SETTING_KEYS:
        session_state[draft_key(setting_key)] = "changed"

    reset_settings_state(session_state)

    for setting_key, expected_value in DEFAULTS.items():
        assert session_state[setting_key] == expected_value


def test_reset_settings_state_restores_form_drafts():
    session_state = {}

    reset_settings_state(session_state)

    for setting_key in EDITABLE_SETTING_KEYS:
        expected_value = setting_to_draft_value(
            setting_key,
            DEFAULTS[setting_key],
        )

        assert (
            session_state[draft_key(setting_key)]
            == expected_value
        )


def test_build_settings_from_drafts_preserves_noneditable_settings():
    session_state = {
        "tabs": [
            "Home",
            "Board",
            "Notes",
            "Settings",
        ],
    }

    initialize_settings_drafts(
        session_state,
        get_setting_from(DEFAULTS),
    )

    session_state[draft_key("stale_days_threshold")] = 8
    session_state[draft_key("default_queues")] = "Personal only"

    settings = build_settings_from_drafts(
        session_state,
    )

    assert settings["stale_days_threshold"] == 8
    assert settings["default_queues"] == ["Personal"]
    assert settings["tabs"] == DEFAULTS["tabs"]


def test_persist_settings_drafts_writes_and_applies_values():
    session_state = {
        "tabs": deepcopy(DEFAULTS["tabs"]),
    }

    initialize_settings_drafts(
        session_state,
        get_setting_from(DEFAULTS),
    )

    session_state[draft_key("ollama_model")] = "saved-model"
    session_state[draft_key("stale_days_threshold")] = 11
    session_state[draft_key("default_queues")] = "Personal only"

    written_settings = {}

    def fake_writer(settings):
        written_settings.update(
            deepcopy(settings)
        )
        return deepcopy(settings)

    saved = persist_settings_drafts(
        session_state,
        writer=fake_writer,
    )

    assert written_settings["ollama_model"] == "saved-model"
    assert written_settings["stale_days_threshold"] == 11
    assert written_settings["default_queues"] == ["Personal"]

    assert saved == written_settings
    assert session_state["ollama_model"] == "saved-model"
    assert session_state["stale_days_threshold"] == 11
    assert session_state["default_queues"] == ["Personal"]


def test_persist_default_settings_resets_active_and_draft_values():
    session_state = {
        key: deepcopy(value)
        for key, value in DEFAULTS.items()
    }

    initialize_settings_drafts(
        session_state,
        get_setting_from(DEFAULTS),
    )

    session_state["stale_days_threshold"] = 12
    session_state[draft_key("stale_days_threshold")] = 12
    session_state["default_queues"] = ["Personal"]
    session_state[draft_key("default_queues")] = "Personal only"

    written_settings = {}

    def fake_writer(settings):
        written_settings.update(
            deepcopy(settings)
        )
        return deepcopy(settings)

    persist_default_settings(
        session_state,
        writer=fake_writer,
    )

    assert written_settings == DEFAULTS

    assert (
        session_state["stale_days_threshold"]
        == DEFAULTS["stale_days_threshold"]
    )

    assert (
        session_state[draft_key("stale_days_threshold")]
        == DEFAULTS["stale_days_threshold"]
    )

    assert (
        session_state["default_queues"]
        == DEFAULTS["default_queues"]
    )

    assert (
        session_state[draft_key("default_queues")]
        == "ALL"
    )