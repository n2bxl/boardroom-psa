# ui/home.py

from __future__ import annotations

import streamlit as st

from core.config import DEFAULTS
from core.constants import PRIORITY_ICONS, OPEN_STATUSES
from core.db import list_tasks, list_recent_task_activity, list_recent_notes, get_task
from core.date_utils import due_date_sort_key, is_due_today, is_overdue
from core.time_utils import resolve_timezone, format_timestamp_for_display
from ui.text_utils import preview_text
from ui.worklogs import format_minutes

# --- Helpers ---

def compute_kpis(tasks):
    open_tasks = [
        t for t in tasks
        if t.status in OPEN_STATUSES
    ]
    due_today = [
        t for t in open_tasks
        if is_due_today(t.due_date)
    ]
    overdue = [
        t for t in open_tasks
        if is_overdue(t.due_date)
    ]
    waiting = [
        t for t in open_tasks
        if t.status == "Waiting"
    ]

    return open_tasks, due_today, overdue, waiting

def jump_to_task(task_id: int):
    st.session_state["selected_task_id"] = task_id
    st.session_state.pop("selected_note_id", None)
    st.info("Task selected. Open the Board tab to view it.")

def jump_to_note(note_id: int):
    st.session_state["selected_note_id"] = note_id
    st.session_state.pop("selected_task_id", None)
    st.info("Note selected. Open the Notes tab to view it.")

def render_recent_tasks(items, display_tz: str, preview_limit: int):
    st.markdown("#### Recent Tasks")

    if not items:
        st.info("No recent task activity.")
        return

    for item in items:
        ts = format_timestamp_for_display(item.created_at, display_tz)
        preview = preview_text(item.body, preview_limit)
        icon = PRIORITY_ICONS.get(item.priority, "")

        meta = f"{ts}"
        if getattr(item, "time_spent_minutes", None):
            meta = f"{meta} | {format_minutes(item.time_spent_minutes)}"

        st.markdown(f"{icon} #{item.task_id} | **{item.task_title}**")
        st.caption(meta)
        st.write(preview)

        if st.button("Open Task", key=f"recent_task_open_{item.id}", width="stretch"):
            jump_to_task(item.task_id)
        
        st.divider()

def render_recent_notes(items, display_tz: str, preview_limit: int):
    st.markdown("#### Recent Notes")

    if not items:
        st.info("No recent notes.")
        return

    for note in items:
        ts_source = note.updated_at or note.created_at
        ts = format_timestamp_for_display(ts_source, display_tz)
        preview = preview_text(note.body, preview_limit)

        st.markdown(f"**{note.title}**")

        meta_parts = [ts]
        if note.tags:
            meta_parts.append(f"Tags: {note.tags}")

        if getattr(note, "task_id", None):
            linked_task = get_task(note.task_id)
            if linked_task:
                meta_parts.append(f"Linked to {linked_task.title}")
            else:
                meta_parts.append(f"Linked to #{note.task_id}")

        st.caption(" | ".join(meta_parts))
        st.write(preview)

        if st.button("Open Note", key=f"recent_note_open_{note.id}", width="stretch"):
            jump_to_note(note.id)

        st.divider()

# --- Home ---

def render_home(get_setting):
    st.subheader("Home")

    recent_activity_limit = int(get_setting("recent_activity_limit"))
    recent_notes_limit = int(get_setting("recent_notes_limit"))
    note_preview_length = int(get_setting("note_preview_length"))
    today_focus_limit = int(get_setting("today_focus_limit"))

    tasks = list_tasks()
    open_tasks, due_today, overdue, waiting = compute_kpis(tasks)

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Open Tasks", len(open_tasks))
    c2.metric("Due Today", len(due_today))
    c3.metric("Overdue", len(overdue))
    c4.metric("Waiting", len(waiting))

    st.divider()

    # --- Today's Focus ---

    st.markdown("### Today's Focus")

    focus = [t for t in tasks if t.status in OPEN_STATUSES]
    focus = sorted(
        focus,
        key=lambda t: (
            t.priority != "High",
            due_date_sort_key(t.due_date),
            t.title.lower(),
        ),
    )

    if not focus:
        st.info("Nothing urgent today.")
    else:
        for t in focus[:today_focus_limit]:
            icon = PRIORITY_ICONS.get(t.priority, "")
            c1, c2 = st.columns([5, 1])

            c1.write(
                f"""
                {icon} #{t.id} | **{t.title}** — Status: {t.status}, Due: {t.due_date or '-'}
                """
            )

            if c2.button("Open", key=f"focus_open_{t.id}"):
                jump_to_task(t.id)

    st.divider()

    # --- Recent Activity ---

    st.markdown("### Recent Activity")

    recent_task_items = list_recent_task_activity(limit=recent_activity_limit)
    recent_note_items = list_recent_notes(limit=recent_notes_limit)

    display_tz = resolve_timezone(st.session_state, DEFAULTS)

    left_col, right_col = st.columns(2)

    with left_col:
        render_recent_tasks(
            items=recent_task_items,
            display_tz=display_tz,
            preview_limit=note_preview_length,
        )

    with right_col:
        render_recent_notes(
            items=recent_note_items,
            display_tz=display_tz,
            preview_limit=note_preview_length,
        )