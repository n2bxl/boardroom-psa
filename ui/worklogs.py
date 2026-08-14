# ui/worklogs.py

from __future__ import annotations

import streamlit as st

from core.time_utils import format_timestamp_for_display

from ui.text_utils import preview_text

def format_minutes(minutes: int) -> str:
    if not minutes:
        return "0m"

    hours = minutes // 60
    mins = minutes % 60

    if hours and mins:
        return f"{hours}h {mins}m"
    if hours:
        return f"{hours}h"
    return f"{mins}m"

def render_task_note_entry(
    task_id: int,
    add_task_note,
    get_setting
):
    with st.form(f"add_note_{task_id}", clear_on_submit=True):
        note_body = st.text_area(
            "Add a note/worklog",
            placeholder = "What did you do? What did you learn? What's next?",
            height=int(get_setting("task_note_height")),
        )

        time_spent_minutes = st.number_input(
            "Time spent (minutes)",
            min_value=0,
            step=int(get_setting("time_log_step_minutes")),
            value=0,
        )

        submitted = st.form_submit_button("Add note")
        if submitted:
            if not note_body.strip():
                st.warning("Note cannot be empty.")
            else:
                add_task_note(
                    task_id,
                    note_body,
                    time_spent_minutes = (
                        time_spent_minutes
                        if time_spent_minutes > 0
                        else None
                    )
                )
                st.success("Note added.")
                st.rerun()


def render_task_note_history(
    existing_notes,
    display_tz: str,
    get_setting,
    update_task_note,
):
    preview_limit = int(get_setting("note_preview_length"))
    edit_state_key = "editing_task_note_id"

    if edit_state_key not in st.session_state:
        st.session_state[edit_state_key] = None

    # If the user switched tasks while editing a note,
    # clear the stale edit state.
    visible_note_ids = {note.id for note in existing_notes}
    if (
        st.session_state[edit_state_key] is not None
        and st.session_state[edit_state_key] not in visible_note_ids
    ):
        st.session_state[edit_state_key] = None

    if existing_notes:
        for note in existing_notes:
            timestamp = format_timestamp_for_display(
                note.created_at,
                display_tz,
            )

            time_spent = getattr(
                note,
                "time_spent_minutes",
                None,
            )

            preview = preview_text(
                note.body,
                preview_limit,
            )

            label = timestamp

            if time_spent:
                label = (
                    f"{timestamp} — "
                    f"{format_minutes(time_spent)}"
                )

            label = f"{label} — {preview}"

            is_editing = (
                st.session_state[edit_state_key]
                == note.id
            )

            with st.expander(
                label,
                expanded=is_editing,
            ):
                if is_editing:
                    with st.form(
                        f"edit_task_note_{note.id}"
                    ):
                        edited_body = st.text_area(
                            "Edit note",
                            value=note.body,
                            height=int(
                                get_setting(
                                    "task_note_height"
                                )
                            ),
                        )

                        save_col, cancel_col = st.columns(2)

                        with save_col:
                            save_edit = (
                                st.form_submit_button(
                                    "Save note",
                                    type="primary",
                                )
                            )

                        with cancel_col:
                            cancel_edit = (
                                st.form_submit_button(
                                    "Cancel"
                                )
                            )

                    if cancel_edit:
                        st.session_state[
                            edit_state_key
                        ] = None
                        st.rerun()

                    if save_edit:
                        if not edited_body.strip():
                            st.warning(
                                "Note cannot be empty."
                            )
                        else:
                            update_task_note(
                                note.id,
                                edited_body,
                            )

                            st.session_state[
                                edit_state_key
                            ] = None

                            st.rerun()

                else:
                    st.markdown(note.body)

                    if st.button(
                        "Edit",
                        key=f"edit_task_note_button_{note.id}",
                    ):
                        st.session_state[
                            edit_state_key
                        ] = note.id

                        st.rerun()

    else:
        st.info(
            "No notes yet. Use the form above "
            "to add the first workflow entry."
        )


def render_task_notes(
        task_id: int,
        existing_notes,
        display_tz: str,
        add_task_note,
        update_task_note,
        get_setting,
):
    render_task_note_entry(
        task_id,
        add_task_note,
        get_setting,
    )

    render_task_note_history(
        existing_notes,
        display_tz,
        get_setting,
        update_task_note,
    )