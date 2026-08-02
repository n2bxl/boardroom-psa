# tests/test_settings_store.py

from __future__ import annotations

from copy import deepcopy
import json

from core.config import DEFAULTS
from core.settings_store import (
    load_settings,
    sanitize_settings,
    save_settings,
)


def test_load_missing_file_returns_defaults(tmp_path):
    settings_path = tmp_path / "settings.json"

    loaded = load_settings(settings_path)

    assert loaded == DEFAULTS
    assert loaded is not DEFAULTS


def test_save_and_load_round_trip(tmp_path):
    settings_path = (
        tmp_path
        / "nested"
        / "settings.json"
    )

    settings = deepcopy(DEFAULTS)
    settings["default_queues"] = ["Personal"]
    settings["stale_days_threshold"] = 8
    settings["llm_temperature"] = 0.7

    saved = save_settings(
        settings,
        settings_path,
    )

    loaded = load_settings(settings_path)

    assert saved == loaded
    assert loaded["default_queues"] == ["Personal"]
    assert loaded["stale_days_threshold"] == 8
    assert loaded["llm_temperature"] == 0.7


def test_partial_file_merges_with_defaults(tmp_path):
    settings_path = tmp_path / "settings.json"

    settings_path.write_text(
        json.dumps(
            {
                "stale_days_threshold": 7,
            }
        ),
        encoding="utf-8",
    )

    loaded = load_settings(settings_path)

    assert loaded["stale_days_threshold"] == 7
    assert (
        loaded["ollama_model"]
        == DEFAULTS["ollama_model"]
    )
    assert (
        loaded["task_note_height"]
        == DEFAULTS["task_note_height"]
    )


def test_unknown_keys_are_ignored():
    loaded = sanitize_settings(
        {
            "unknown_setting": "ignored",
            "stale_days_threshold": 9,
        }
    )

    assert "unknown_setting" not in loaded
    assert loaded["stale_days_threshold"] == 9


def test_malformed_json_returns_defaults(tmp_path):
    settings_path = tmp_path / "settings.json"

    settings_path.write_text(
        "{this is not valid json",
        encoding="utf-8",
    )

    loaded = load_settings(settings_path)

    assert loaded == DEFAULTS


def test_invalid_values_fall_back_to_defaults(tmp_path):
    settings_path = tmp_path / "settings.json"

    settings_path.write_text(
        json.dumps(
            {
                "stale_days_threshold": 0,
                "default_queues": ["Invalid Queue"],
                "show_age_stale_columns": 1,
                "llm_temperature": 9.5,
            }
        ),
        encoding="utf-8",
    )

    loaded = load_settings(settings_path)

    assert (
        loaded["stale_days_threshold"]
        == DEFAULTS["stale_days_threshold"]
    )

    assert (
        loaded["default_queues"]
        == DEFAULTS["default_queues"]
    )

    assert (
        loaded["show_age_stale_columns"]
        == DEFAULTS["show_age_stale_columns"]
    )

    assert (
        loaded["llm_temperature"]
        == DEFAULTS["llm_temperature"]
    )


def test_status_list_is_valid():
    loaded = sanitize_settings(
        {
            "default_statuses": [
                "New",
                "Waiting",
            ],
        }
    )

    assert loaded["default_statuses"] == [
        "New",
        "Waiting",
    ]


def test_boolean_is_not_accepted_as_integer():
    loaded = sanitize_settings(
        {
            "stale_days_threshold": True,
        }
    )

    assert (
        loaded["stale_days_threshold"]
        == DEFAULTS["stale_days_threshold"]
    )


def test_temperature_integer_is_normalized_to_float():
    loaded = sanitize_settings(
        {
            "llm_temperature": 1,
        }
    )

    assert loaded["llm_temperature"] == 1.0
    assert isinstance(
        loaded["llm_temperature"],
        float,
    )


def test_save_creates_parent_directory(tmp_path):
    settings_path = (
        tmp_path
        / "data"
        / "settings.json"
    )

    save_settings(
        DEFAULTS,
        settings_path,
    )

    assert settings_path.exists()


def test_save_leaves_no_temporary_files(tmp_path):
    settings_path = tmp_path / "settings.json"

    save_settings(
        DEFAULTS,
        settings_path,
    )

    temporary_files = list(
        tmp_path.glob("*.tmp")
    )

    assert settings_path.exists()
    assert temporary_files == []