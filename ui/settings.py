# ui/settings.py

from __future__ import annotations

import streamlit as st

from core.config import DEFAULTS
from core.version import __version__


def render_settings_tab(get_setting):
    st.subheader("Settings")

    st.markdown("### AI")
    st.session_state["ollama_model"] = st.text_input(
        "Ollama model",
        value=get_setting("ollama_model"),
        help="Run `ollama list` to see available models.",
    )

    st.session_state["llm_temperature"] = st.slider(
        "Temperature",
        min_value=0.0,
        max_value=1.5,
        value=float(get_setting("llm_temperature")),
        step=0.05,
        help="Lower = more consistent. Higher = more creative.",
    )

    st.session_state["ai_context_task_limit"] = st.slider(
        "AI context task count",
        min_value=5,
        max_value=50,
        value=int(get_setting("ai_context_task_limit")),
        step=1,
    )

    st.divider()
    st.markdown("### Board Defaults")

    st.session_state["default_statuses"] = st.selectbox(
        "Default status filter",
        options=["OPEN", "ALL"],
        index=0 if get_setting("default_statuses") == "OPEN" else 1,
    )

    queue_mode = "ALL" if get_setting("default_queues") == "ALL" else "Personal only"
    selected = st.selectbox("Default queue filter", options=["ALL", "Personal only"], index=0 if queue_mode == "ALL" else 1)
    st.session_state["default_queues"] = "ALL" if selected == "ALL" else ["Personal"]

    st.divider()
    st.markdown("### UI")

    st.session_state["ai_context_height"] = st.slider(
        "AI Context box height",
        min_value=100,
        max_value=600,
        value=int(get_setting("ai_context_height")),
        step=10,
    )

    st.session_state["task_note_height"] = st.slider(
        "Task note entry height",
        min_value=80,
        max_value=300,
        value=int(get_setting("task_note_height")),
        step=10,
    )

    st.session_state["note_body_height"] = st.slider(
        "Notes body height",
        min_value=120,
        max_value=600,
        value=int(get_setting("note_body_height")),
        step=10,
    )

    st.session_state["show_age_stale_columns"] = st.checkbox(
        "Show Age/Stale columns on board",
        value=bool(get_setting("show_age_stale_columns")),
    )

    st.divider()
    st.markdown("### Timezone")

    st.session_state["use_system_timezone"] = st.checkbox(
        "Use system timezone",
        value=bool(get_setting("use_system_timezone")),
    )

    st.session_state["timezone_override"] = st.text_input(
        "Manual timezone override",
        value=str(get_setting("timezone_override")),
        placeholder="America/Chicago",
        help="Leave blank to use the system timezone. Examples: America/Chicago, America/New_York",
    )

    st.divider()
    st.markdown("### Home")

    st.session_state["recent_activity_limit"] = st.slider(
        "Recent Activity items",
        min_value=3,
        max_value=20,
        value=int(get_setting("recent_activity_limit")),
        step=1
    )

    st.session_state["note_preview_length"] = st.slider(
        "Recent Activity preview length",
        min_value=20,
        max_value=250,
        value=int(get_setting("note_preview_length")),
        step=5,
    )

    st.session_state["today_focus_limit"] = st.slider(
        "Today's Focus items",
        min_value=3,
        max_value=12,
        value=int(get_setting("today_focus_limit")),
        step=1
    )
    st.session_state["recent_notes_limit"] = st.slider(
        "Recent Notes items",
        min_value=5,
        max_value=50,
        value=int(get_setting("recent_notes_limit")),
        step=5,
    )

    st.divider()
    st.markdown("### Worklog")

    st.session_state["time_log_step_minutes"] = st.slider(
        "Time log step (minutes)",
        min_value=1,
        max_value=30,
        value=int(get_setting("time_log_step_minutes")),
        step=1,
    )

    st.session_state["task_notes_limit"] = st.slider(
        "Task Notes history count",
        min_value=5,
        max_value=100,
        value=int(get_setting("task_notes_limit")),
        step=5,
    )

    st.divider()
    if st.button("Reset to defaults", use_container_width=True):
        for k, v in DEFAULTS.items():
            st.session_state[k] = v
        st.success("Reset.")
        st.rerun()

    st.divider()
    st.caption(f"Boardroom Personal PSA v{__version__}")