# core/settings_store.py

from __future__ import annotations

from copy import deepcopy
import json
import os
from pathlib import Path
import tempfile
from typing import Any, Mapping

from core.config import DEFAULTS
from core.constants import QUEUES, STATUS_ORDER


SETTINGS_PATH = Path("data/settings.json")


_INT_RANGES = {
    "llm_max_tokens": (128, 2048),
    "ai_context_task_limit": (5, 50),
    "task_note_height": (80, 300),
    "note_body_height": (120, 600),
    "stale_days_threshold": (1, 30),
    "recent_activity_limit": (3, 20),
    "note_preview_length": (20, 250),
    "today_focus_limit": (3, 12),
    "recent_notes_limit": (5, 50),
    "time_log_step_minutes": (1, 30),
    "task_notes_limit": (5, 100),
}

_FLOAT_RANGES = {
    "llm_temperature": (0.0, 1.5),
}

_ALLOWED_TABS = {
    "Home",
    "Board",
    "Notes",
    "Settings",
}


def _is_string_list(
    value: Any,
    allowed: set[str],
) -> bool:
    """Return True when value is a nonempty list of allowed strings."""
    return (
        isinstance(value, list)
        and bool(value)
        and all(
            isinstance(item, str) and item in allowed
            for item in value
        )
    )


def _normalize_setting_value(
    key: str,
    value: Any,
    default: Any,
) -> tuple[bool, Any]:
    """
    Validate one setting and return its normalized value.

    The boolean indicates whether the supplied value is valid.
    """
    if key in _INT_RANGES:
        lower, upper = _INT_RANGES[key]

        valid = (
            type(value) is int
            and lower <= value <= upper
        )

        return valid, value

    if key in _FLOAT_RANGES:
        lower, upper = _FLOAT_RANGES[key]

        valid = (
            not isinstance(value, bool)
            and isinstance(value, (int, float))
            and lower <= float(value) <= upper
        )

        return (
            valid,
            float(value) if valid else value,
        )

    if key == "default_queues":
        valid = (
            value == "ALL"
            or _is_string_list(
                value,
                set(QUEUES),
            )
        )

        return valid, value

    if key == "default_statuses":
        valid = (
            isinstance(value, str)
            and value in {"ALL", "OPEN"}
        ) or _is_string_list(
            value,
            set(STATUS_ORDER),
        )

        return valid, value

    if key == "tabs":
        valid = (
            _is_string_list(
                value,
                _ALLOWED_TABS,
            )
            and len(value) == len(set(value))
        )

        return valid, value

    if isinstance(default, bool):
        return isinstance(value, bool), value

    if isinstance(default, str):
        return isinstance(value, str), value

    return type(value) is type(default), value


def sanitize_settings(
    raw_settings: Any,
    defaults: Mapping[str, Any] = DEFAULTS,
) -> dict[str, Any]:
    """
    Merge valid saved values over a deep copy of current defaults.

    Unknown keys and invalid values are ignored.
    """
    sanitized = deepcopy(dict(defaults))

    if not isinstance(raw_settings, dict):
        return sanitized

    for key, default in defaults.items():
        if key not in raw_settings:
            continue

        valid, normalized = _normalize_setting_value(
            key,
            raw_settings[key],
            default,
        )

        if valid:
            sanitized[key] = deepcopy(normalized)

    return sanitized


def load_settings(
    path: Path | str = SETTINGS_PATH,
    defaults: Mapping[str, Any] = DEFAULTS,
) -> dict[str, Any]:
    """
    Load and validate settings from disk.

    Missing, unreadable, or malformed files fall back to defaults.
    """
    settings_path = Path(path)

    try:
        with settings_path.open(
            "r",
            encoding="utf-8",
        ) as handle:
            raw_settings = json.load(handle)

    except (
        FileNotFoundError,
        OSError,
        json.JSONDecodeError,
    ):
        return deepcopy(dict(defaults))

    return sanitize_settings(
        raw_settings,
        defaults,
    )


def save_settings(
    settings: Mapping[str, Any],
    path: Path | str = SETTINGS_PATH,
    defaults: Mapping[str, Any] = DEFAULTS,
) -> dict[str, Any]:
    """
    Validate and atomically save settings.

    The temporary file is created in the same directory so os.replace()
    can replace the final file without leaving a partially written JSON file.
    """
    settings_path = Path(path)

    settings_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    sanitized = sanitize_settings(
        dict(settings),
        defaults,
    )

    file_descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{settings_path.name}.",
        suffix=".tmp",
        dir=settings_path.parent,
        text=True,
    )

    temporary_path = Path(temporary_name)

    try:
        with os.fdopen(
            file_descriptor,
            "w",
            encoding="utf-8",
        ) as handle:
            json.dump(
                sanitized,
                handle,
                indent=2,
                sort_keys=True,
            )

            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())

        os.replace(
            temporary_path,
            settings_path,
        )

    except Exception:
        temporary_path.unlink(
            missing_ok=True,
        )
        raise

    return deepcopy(sanitized)