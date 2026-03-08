# ui/home.py

from __future__ import annotations

import datetime as dt
import streamlit as st

from core.config import DEFAULTS
from core.constants import PRIORITY_ICONS
from core.db import list_tasks, list_recent_task_activity
from core.time_utils import resolve_timezone, format_timestamp_for_display
from ui.text_utils import preview_text
from ui.worklogs import format_minutes

# --- Helpers ---

def today_iso():
    return str(dt.date.today())

def is_overdue(due_date):
    if not due_date:
        return False
    try:
        return dt.date.fromisoformat(due_date) < dt.date.today()
    except ValueError:
        return False

def compute_kpis(tasks):
    open_tasks = [
        t for t in tasks
        if t.status != "Done"
    ]
    due_today = [
        t for t in open_tasks
        if t.due_date == today_iso()
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
    st.info("Task selected. Open the Board tab to view it.")

# --- Home ---

def render_home(get_setting):
    st.subheader("Home")

    recent_activity_limit = int(get_setting("recent_activity_limit"))
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

    focus = [t for t in tasks]
    focus = sorted(
        focus,
        key=lambda t: (
            t.priority != "High",
            t.due_date or "9999-12-31",
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
                {icon} — **{t.title}** — Status: {t.status}, Due: {t.due_date or '-'}
                """
            )

            if c2.button("Open", key=f"focus_open_{t.id}"):
                jump_to_task(t.id)

    st.divider()

    # --- Recent Activity ---

    st.markdown("### Recent Activity")

    activity = list_recent_task_activity(limit=recent_activity_limit)

    display_tz = resolve_timezone(st.session_state, DEFAULTS)

    if not activity:
        st.info("No recent activity.")
    else:
        for item in activity:
            ts = format_timestamp_for_display(item.created_at, display_tz)
            preview = preview_text(item.body, note_preview_length)
            icon = PRIORITY_ICONS.get(item.priority, "")

            label = f"{icon} — {ts} — {item.task_title}"
            
            if getattr(item, "time_spent_minutes", None):
                label = f"{icon} — {ts} — {format_minutes(item.time_spent_minutes)} — {item.task_title}"

            label = f"{label} — {preview}"

            c1, c2 = st.columns([6, 1])

            with c1:
                with st.expander(label):
                    st.write(item.body)

            if c2.button("Open", key=f"activity_open_{item.id}"):
                jump_to_task(item.task_id)