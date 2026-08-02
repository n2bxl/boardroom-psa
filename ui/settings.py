# ui/settings.py

from __future__ import annotations

from copy import deepcopy
from typing import Any, Callable

import streamlit as st

from core.config import DEFAULTS
from core.settings_store import (
    save_settings as write_settings_file,
)
from core.version import __version__


SETTINGS_FORM_KEY = "settings_form"
SETTINGS_FEEDBACK_KEY = "settings_feedback"
DRAFT_PREFIX = "draft_setting_"

EDITABLE_SETTING_KEYS = (
    # AI
    "ollama_model",
    "llm_temperature",
    "llm_max_tokens",
    "ai_context_task_limit",

    # Board defaults
    "default_statuses",
    "default_queues",
    "stale_days_threshold",

    # UI
    "task_note_height",
    "note_body_height",
    "show_age_stale_columns",

    # Timezone
    "use_system_timezone",
    "timezone_override",

    # Home
    "recent_activity_limit",
    "note_preview_length",
    "today_focus_limit",
    "recent_notes_limit",

    # Worklog
    "time_log_step_minutes",
    "task_notes_limit",
)


def draft_key(setting_key: str) -> str:
    """Return the session-state key used by a settings form widget."""
    return f"{DRAFT_PREFIX}{setting_key}"


def setting_to_draft_value(
    setting_key: str,
    value: Any,
) -> Any:
    """
    Convert an active setting into the value displayed by its form widget.
    """
    if setting_key == "default_queues":
        return (
            "ALL"
            if value == "ALL"
            else "Personal only"
        )

    return deepcopy(value)


def draft_to_setting_value(
    setting_key: str,
    value: Any,
) -> Any:
    """
    Convert a form widget value into the application's active setting format.
    """
    if setting_key == "default_queues":
        return (
            "ALL"
            if value == "ALL"
            else ["Personal"]
        )

    return deepcopy(value)


def build_settings_from_drafts(
        session_state,
) -> dict[str, Any]:
    """
    Build a complete settings dictionary from active values and form drafts.
    
    Noneditable settings, such as the tab list, retain their active values.
    Editable settings are repalced by their submitted draft values.
    """

    settings ={ 
        key: deepcopy(
            session_state.get(key, default_value)
        )
        for key, default_value in DEFAULTS.items()
    }

    for setting_key in EDITABLE_SETTING_KEYS:
        settings[setting_key] = draft_to_setting_value(
            setting_key,
            session_state[draft_key(setting_key)],
        )

    return settings


def persist_settings_drafts(
        session_state,
        writer=write_settings_file,
) -> dict[str, Any]:
    """
    Save alll drafts and apply the validated saved values to the session.
    """
    candidate_settings = build_settings_from_drafts(
        session_state,
    )

    saved_settings = writer(candidate_settings)

    for key, value in saved_settings.items():
        session_state[key] = deepcopy(value)

    return saved_settings


def persist_default_settings(
        session_state,
        writer=write_settings_file,
) -> dict[str, Any]:
    """
    Save the application defaults and reset active values and form drafts.
    """
    saved_settings = writer(DEFAULTS)

    for key, value in saved_settings.items():
        session_state[key] = deepcopy(value)

    for setting_key in EDITABLE_SETTING_KEYS:
        session_state[draft_key(setting_key)] = (
            setting_to_draft_value(
                setting_key,
                saved_settings[setting_key],
            )
        )

    return saved_settings


def initialize_settings_drafts(
    session_state,
    get_setting: Callable[[str], Any],
) -> None:
    """
    Initialize form drafts from active settings.

    setdefault preserves any draft values already present in the current
    session instead of overwriting them during a normal rerun.
    """
    for setting_key in EDITABLE_SETTING_KEYS:
        session_state.setdefault(
            draft_key(setting_key),
            setting_to_draft_value(
                setting_key,
                get_setting(setting_key),
            ),
        )


def apply_settings_drafts(session_state) -> None:
    """Copy every form draft into the active application settings."""
    settings = build_settings_from_drafts(session_state)

    for key, value in settings.items():
        session_state[key] = deepcopy(value)


def reset_settings_state(session_state) -> None:
    """
    Restore all active settings and editable form drafts to defaults.
    """
    for setting_key, default_value in DEFAULTS.items():
        session_state[setting_key] = deepcopy(default_value)

    for setting_key in EDITABLE_SETTING_KEYS:
        session_state[draft_key(setting_key)] = (
            setting_to_draft_value(
                setting_key,
                DEFAULTS[setting_key],
            )
        )


def save_settings() -> None:
    """Persist and apply all submitted settings form values."""
    try:
        persist_settings_drafts(
            st.session_state,
        )
    except OSError as exc:
        st.session_state[SETTINGS_FEEDBACK_KEY] = (
            "error",
            f"Settings could not be saved: {exc}",
        )
        return

    st.session_state[SETTINGS_FEEDBACK_KEY] = (
        "success",
        "Settings saved and applied.",
    )


def reset_settings() -> None:
    """Persist defaults and reset active settings and form controls."""
    try:
        persist_default_settings(
            st.session_state,
        )
    except OSError as exc:
        st.session_state[SETTINGS_FEEDBACK_KEY] = (
            "error",
            f"Settings could not be reset: {exc}",
        )
        return

    st.session_state[SETTINGS_FEEDBACK_KEY] = (
        "success",
        "Settings reset to defaults.",
    )


def render_ai_settings() -> None:
    """Render AI-related settings."""
    st.markdown("### AI")

    st.text_input(
        "Ollama model",
        key=draft_key("ollama_model"),
        help="Run `ollama list` to see available models.",
    )

    st.slider(
        "Temperature",
        min_value=0.0,
        max_value=1.5,
        step=0.05,
        key=draft_key("llm_temperature"),
        help="Lower = more consistent. Higher = more creative.",
    )

    st.slider(
        "Max response tokens",
        min_value=128,
        max_value=2048,
        step=16,
        key=draft_key("llm_max_tokens"),
        help=(
            "Limits the maximum number of tokens generated "
            "by Ollama."
        ),
    )

    st.slider(
        "AI context task count",
        min_value=5,
        max_value=50,
        step=1,
        key=draft_key("ai_context_task_limit"),
    )


def render_board_settings() -> None:
    """Render Board defaults and stale-task settings."""
    st.divider()
    st.markdown("### Board Defaults")

    st.selectbox(
        "Default status filter",
        options=["OPEN", "ALL"],
        key=draft_key("default_statuses"),
    )

    st.selectbox(
        "Default queue filter",
        options=["ALL", "Personal only"],
        key=draft_key("default_queues"),
    )

    st.slider(
        "Stale task threshold (days)",
        min_value=1,
        max_value=30,
        step=1,
        key=draft_key("stale_days_threshold"),
        help=(
            "Open tasks with no activity for this many days "
            "are treated as stale."
        ),
    )


def render_ui_settings() -> None:
    """Render interface size and visibility settings."""
    st.divider()
    st.markdown("### UI")

    st.slider(
        "Task note entry height",
        min_value=80,
        max_value=300,
        step=10,
        key=draft_key("task_note_height"),
    )

    st.slider(
        "Notes body height",
        min_value=120,
        max_value=600,
        step=10,
        key=draft_key("note_body_height"),
    )

    st.checkbox(
        "Show Age/Stale columns on board",
        key=draft_key("show_age_stale_columns"),
    )


def render_timezone_settings() -> None:
    """Render timezone settings."""
    st.divider()
    st.markdown("### Timezone")

    st.checkbox(
        "Use system timezone",
        key=draft_key("use_system_timezone"),
    )

    st.text_input(
        "Manual timezone override",
        key=draft_key("timezone_override"),
        placeholder="America/Chicago",
        help=(
            "Leave blank to use the system timezone. "
            "Examples: America/Chicago, America/New_York"
        ),
    )


def render_home_settings() -> None:
    """Render Home dashboard settings."""
    st.divider()
    st.markdown("### Home")

    st.slider(
        "Recent task activity items",
        min_value=3,
        max_value=20,
        step=1,
        key=draft_key("recent_activity_limit"),
    )

    st.slider(
        "Recent Activity preview length",
        min_value=20,
        max_value=250,
        step=5,
        key=draft_key("note_preview_length"),
    )

    st.slider(
        "Today's Focus items",
        min_value=3,
        max_value=12,
        step=1,
        key=draft_key("today_focus_limit"),
    )

    st.slider(
        "Recent Notes items",
        min_value=5,
        max_value=50,
        step=5,
        key=draft_key("recent_notes_limit"),
    )


def render_worklog_settings() -> None:
    """Render worklog and task-history settings."""
    st.divider()
    st.markdown("### Worklog")

    st.slider(
        "Time log step (minutes)",
        min_value=1,
        max_value=30,
        step=1,
        key=draft_key("time_log_step_minutes"),
    )

    st.slider(
        "Task Notes history count",
        min_value=5,
        max_value=100,
        step=5,
        key=draft_key("task_notes_limit"),
    )


def render_settings_tab(
    get_setting: Callable[[str], Any],
) -> None:
    """Render the Settings tab using one explicit save workflow."""
    st.subheader("Settings")

    initialize_settings_drafts(
        st.session_state,
        get_setting,
    )

    feedback = st.session_state.pop(
        SETTINGS_FEEDBACK_KEY,
        None,
    )

    if feedback:
        # Support any feedback string left in an existing session
        # from the pre-persistence implementation.
        if isinstance(feedback, str):
            feedback_level = "success"
            feedback_message = feedback
        else:
            feedback_level, feedback_message = feedback

        if feedback_level == "error":
            st.error(feedback_message)
        else:
            st.success(feedback_message)

    with st.form(
        SETTINGS_FORM_KEY,
        clear_on_submit=False,
    ):
        save_column, reset_column, _ = st.columns([1, 1, 2])

        save_column.form_submit_button(
            "Save Settings",
            type="primary",
            width="stretch",
            on_click=save_settings,
        )

        reset_column.form_submit_button(
            "Reset to Defaults",
            width="stretch",
            on_click=reset_settings,
        )

        st.caption(
            "Changes below are not applied until you select "
            "Save Settings."
        )

        render_ai_settings()
        render_board_settings()
        render_ui_settings()
        render_timezone_settings()
        render_home_settings()
        render_worklog_settings()

    st.divider()
    st.caption(f"Boardroom Personal PSA v{__version__}")