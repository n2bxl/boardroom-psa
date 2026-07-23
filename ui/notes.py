# ui/notes.py

from __future__ import annotations

import streamlit as st

from core.config import DEFAULTS
from core.db import get_task, list_tasks
from core.note_service import (
    create_note,
    find_notes,
    get_recent_notes,
    remove_note,
    save_note_edits,
)
from core.time_utils import resolve_timezone, format_timestamp_for_display
from ui.text_utils import preview_text

def _set_notes_flash(message: str) -> None:
    st.session_state["notes_flash"] = message

def _note_task_options():
    tasks = list_tasks()
    options = [("", None)]
    options.extend((f"{t.id} – {t.title}", t.id) for t in tasks)
    return options

def _task_id_to_index(options, task_id):
    for i, (_, value) in enumerate(options):
        if value == task_id:
            return i
    return 0

def _consume_selected_note_id():
    return st.session_state.pop("selected_note_id", None)

def render_note_create_form(get_setting):
    st.markdown("### Add note")

    task_options = _note_task_options()

    with st.form("add_note_form", clear_on_submit=True):
        title = st.text_input("Title", placeholder="Quick note title")
        body = st.text_area(
            "Body",
            placeholder="Add notes here...",
            height=int(get_setting("note_body_height")),
        )
        tags = st.text_input(
            "Tags (comma-separated)",
            placeholder="health, money, school, troubleshooting",
        )

        selected_task_label = st.selectbox(
            "Attach to task (optional)",
            options=[label for label, _ in task_options],
            index=0,
        )

        submitted = st.form_submit_button("Save note")

        if submitted:
            selected_task_id = dict(task_options).get(selected_task_label)

            ok, message = create_note(
                title=title,
                body=body,
                tags=tags,
                task_id=selected_task_id,
            )
            if ok:
                _set_notes_flash(message)
            else:
                st.warning(message)

def render_note_search():
    return st.text_input(
        "Search notes",
        placeholder="Search title, body, or tags...",
        key="notes_search_query",
    )

def render_note_edit_form(note, get_setting):
    task_options = _note_task_options()

    with st.form(f"edit_note_form{note.id}", clear_on_submit=False):
        title = st.text_input(
            "Title",
            value=note.title,
            key=f"edit_title_{note.id}"
        )
        body = st.text_area(
            "Body",
            value=note.body,
            height=int(get_setting("note_body_height")),
            key=f"edit_body_{note.id}",
        )
        tags = st.text_input(
            "Tags (comma-separated)",
            value=note.tags or "",
            key=f"edit_tags_{note.id}",
        )

        selected_index = _task_id_to_index(task_options, getattr(note, "task_id", None))
        selected_task_label = st.selectbox(
            "Attach to task (optional)",
            options=[label for label, _ in task_options],
            index=selected_index,
            key=f"edit_task_{note.id}",
        )

        c1, c2 = st.columns(2)
        save_clicked = c1.form_submit_button("Save")
        cancel_clicked = c2.form_submit_button("Cancel")

        if save_clicked:
            selected_task_id = dict(task_options).get(selected_task_label)

            ok, message = save_note_edits(
                note_id=note.id,
                title=title,
                body=body,
                tags=tags,
                task_id=selected_task_id,
            )
            if ok:
                st.session_state["editing_note_id"] = None
                _set_notes_flash(message)
                st.rerun()
            else:
                st.warning(message)

        if cancel_clicked:
            st.session_state["editing_note_id"] = None
            st.rerun()

def render_note_card(
    note,
    display_tz: str,
    preview_limit: int,
    get_setting,
    selected_note_id: int | None = None,
):
    editing_note_id = st.session_state.get("editing_note_id")
    confirm_delete_note_id = st.session_state.get("confirm_delete_note_id")

    display_ts = note.updated_at or note.created_at
    timestamp = format_timestamp_for_display(display_ts, display_tz)
    preview = preview_text(note.body, preview_limit)

    expander_label = f"{note.title} — {timestamp} — {preview}"

    should_expand = (
        editing_note_id == note.id
        or confirm_delete_note_id == note.id
        or selected_note_id == note.id
    )

    with st.expander(expander_label, expanded=should_expand):
        if editing_note_id == note.id:
            render_note_edit_form(note, get_setting)
            return

        meta_parts = []
        if note.tags:
            meta_parts.append(f"Tags: {note.tags}")
        if getattr(note, "task_id", None):
            linked_task = get_task(note.task_id)
            if linked_task:
                meta_parts.append(f"Linked task: {linked_task.id} | {linked_task.title}")
            else:
                meta_parts.append(f"Linked task: #{note.task_id}")
        if note.updated_at and note.updated_at != note.created_at:
            meta_parts.append(
                f"Edited: {format_timestamp_for_display(note.updated_at, display_tz)}"
            )

        if meta_parts:
            st.caption(" — ".join(meta_parts))

        st.markdown(note.body)

        c1, c2 = st.columns(2)

        if c1.button("Edit", key=f"edit_note_btn_{note.id}", width="stretch"):
            st.session_state["editing_note_id"] = note.id
            st.session_state["confirm_delete_note_id"] = None
            st.rerun()

        if confirm_delete_note_id == note.id:
            if c2.button(
                "Confirm delete",
                key=f"confirm_delete_note_btn_{note.id}",
                width="stretch",
            ):
                remove_note(note.id)
                st.session_state["confirm_delete_note_id"] = None
                if st.session_state.get("editing_note_id") == note.id:
                    st.session_state["editing_note_id"] = None
                _set_notes_flash("Note deleted.")
                st.rerun()
        else:
            if c2.button(
                "Delete",
                key=f"delete_note_btn_{note.id}",
                width="stretch",
            ):
                st.session_state["editing_note_id"] = None
                st.session_state["confirm_delete_note_id"] = note.id
                st.rerun()

def render_notes_list(
    notes,
    display_tz: str,
    preview_limit: int,
    get_setting,
    selected_note_id: int | None = None,
):
    if not notes:
        st.info("No notes found.")
        return
    
    for note in notes:
        render_note_card(
            note,
            display_tz,
            preview_limit,
            get_setting,
            selected_note_id=selected_note_id,
        )

def render_notes(get_setting):
    st.subheader("Notes")

    st.session_state.setdefault("editing_note_id", None)
    st.session_state.setdefault("confirm_delete_note_id", None)

    selected_note_id = _consume_selected_note_id()

    flash_message = st.session_state.pop("notes_flash", None)
    if flash_message:
        st.success(flash_message)

    display_tz = resolve_timezone(st.session_state, DEFAULTS)
    preview_limit = int(get_setting("note_preview_length"))
    recent_notes_limit = int(get_setting("recent_notes_limit"))

    render_note_create_form(get_setting)

    st.divider()

    query = render_note_search()

    st.markdown("### Recent notes")
    if query.strip():
        notes = find_notes(query=query, limit=recent_notes_limit)
    else:
        notes = get_recent_notes(limit=recent_notes_limit)

    render_notes_list(
        notes,
        display_tz,
        preview_limit,
        get_setting,
        selected_note_id=selected_note_id,
    )