from __future__ import annotations
import datetime as dt
import pandas as pd
import streamlit as st

from core.ai import daily_triage
from core.constants import STATUS_ORDER, PRIORITIES, QUEUES, WAITING_REASONS
from core.config import APP, DEFAULTS
from core.db import list_tasks, update_task, list_ticket_notes, add_ticket_note
from core.time_utils import resolve_timezone, format_timestamp_for_display

def today_iso() -> str:
    return str(dt.date.today())

def days_since(iso_dt: str | None) -> int | None:
    """
    Returns integer days since a timestamp string.
    Supports both naive SQLite timestamps and aware ISO timestamps.
    """
    if not iso_dt:
        return None
    try:
        d = dt.datetime.fromisoformat(iso_dt.replace("Z", "+00:00"))

        # If timestamp is timezone-aware, compare against aware "now"
        if d.tzinfo is not None:
            now = dt.datetime.now(dt.timezone.utc)
            return (now - d.astimezone(dt.timezone.utc)).days
        
        # Otherwise, compare against naive "now"
        return (dt.datetime.now() - d).days

    except ValueError:
        return None

def is_overdue(due_date: str | None) -> bool:
    if not due_date:
        return False
    try:
        return dt.date.fromisoformat(due_date) < dt.date.today()
    except ValueError:
        return False


def compute_kpis(all_tasks):
    open_like = [t for t in all_tasks if t.status != "Done"]
    due_today = [t for t in open_like if (t.due_date == today_iso())]
    overdue = [t for t in open_like if is_overdue(t.due_date)]
    waiting = [t for t in open_like if t.status == "Waiting"]
    return open_like, due_today, overdue, waiting


def build_ai_context():
    all_open = [t for t in list_tasks() if t.status != "Done"]
    lines = []
    lines.append(f"DATE: {today_iso()}\n")
    lines.append("OPEN TASKS:")
    if all_open:
        for t in all_open[:12]:
            lines.append(
                f"- {t.title} (status={t.status}, priority={t.priority}, queue={getattr(t, 'queue', 'Personal')}, due={t.due_date or 'none'})"
            )
    else:
        lines.append("- none")
    return "\n".join(lines)


def render_board(
        model_name: str, 
        get_default_statuses, 
        get_default_queues,
        get_setting
    ):
    st.subheader("Task Board")

    all_tasks = list_tasks()
    open_like, due_today, overdue, waiting = compute_kpis(all_tasks)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Open Tasks", len(open_like))
    c2.metric("Due Today", len(due_today))
    c3.metric("Overdue", len(overdue))
    c4.metric("Waiting", len(waiting))

    st.divider()

    # Daily Triage
    with st.expander("Daily Triage (AI)", expanded=False):
        st.caption("Generates a dispatcher-style triage report from your current queue.")
        if st.button("Run Daily Triage", use_container_width=True, key="run_daily_triage"):
            try:
                with st.spinner("Running triage..."):
                    report = daily_triage(model=model_name, context=build_ai_context())
                st.markdown("### Triage Report")
                st.write(report)
            except Exception as e:
                st.error(f"AI error: {e}")

    # Filters
    f1, f2, f3 = st.columns([1, 1, 1])
    status_filter = f1.multiselect("Status", options=STATUS_ORDER, default=get_default_statuses())
    queue_filter = f2.multiselect("Queue", options=QUEUES, default=get_default_queues())
    prio_filter = f3.multiselect("Priority", options=PRIORITIES, default=PRIORITIES)

    filtered = [
        t for t in all_tasks
        if t.status in status_filter
        and getattr(t, "queue", "Personal") in queue_filter
        and t.priority in prio_filter
    ]

    # Queue grid
    display_tz = resolve_timezone(st.session_state, DEFAULTS)
    rows = []
    show_age_stale = bool(get_setting("show_age_stale_columns"))

    for t in filtered:
        age_days = days_since(getattr(t, "created_at", None))    
        stale_days = days_since(
            getattr(t, "updated_at", None) or getattr(t, "created_at", None)
        )

        row = {
            "ID": t.id,
            "Title": t.title,
            "Status": t.status,
            "Priority": t.priority,
            "Queue": getattr(t, "queue", "Personal"),
            "Waiting Reason": (
                getattr(t, "waiting_reason", "") if t.status == "Waiting" else ""
            ),
            "Due": t.due_date or "",
            "Created": format_timestamp_for_display(getattr(t, "created_at", None), display_tz),
            "Updated": format_timestamp_for_display(getattr(t, "updated_at", None), display_tz),
            "Overdue": "YES" if is_overdue(t.due_date) else "",
        }

        if show_age_stale:
            row["Age"] = age_days if age_days is not None else ""
            row["Stale"] = stale_days if stale_days is not None else ""

        rows.append(row)

    df = pd.DataFrame(rows)

    st.markdown("### Queue")

    stale_threshold = DEFAULTS["stale_days_threshold"]

    def highlight_stale(row):
        try:
            stale_val = int(row.get("Stale", 0) or 0)
        except ValueError:
            stale_val = 0

        if stale_val >= stale_threshold and row.get("Status") != "Done":
            return ["font-weight: 700"] * len(row)
        return [""] * len(row)

    df = df.loc[:, ~(df.fillna("").eq("").all())]
    styled = df.style.apply(highlight_stale, axis=1)
    st.dataframe(styled, use_container_width=True, hide_index=True)

    # st.dataframe(df, use_container_width=True, hide_index=True)

    st.divider()
    st.markdown("### Task Details")

    if not filtered:
        st.info("No tasks match your filters.")
        return

    id_to_label = {t.id: f"{t.id} | {t.title}" for t in filtered}
    selected_id = st.selectbox(
        "Select task",
        options=list(id_to_label.keys()),
        format_func=lambda i: id_to_label[i],
    )

    ticket = next(t for t in all_tasks if t.id == selected_id)

    top = st.columns([2, 1, 1, 1])
    top[0].text_input("Title (read-only for now)", value=ticket.title, disabled=True)
    
    new_status = top[1].selectbox(
        "Status",
        STATUS_ORDER,
        index=STATUS_ORDER.index(ticket.status),
    )
    new_priority = top[2].selectbox(
        "Priority",
        PRIORITIES,
        index=PRIORITIES.index(ticket.priority),
    )
    new_queue = top[3].selectbox(
        "Queue",
        QUEUES,
        index=QUEUES.index(getattr(ticket, "queue", "Personal"))
    )

    current_waiting_reason = getattr(ticket, "waiting_reason", None)

    if new_status == "Waiting":
        default_idx = 0
        if current_waiting_reason in WAITING_REASONS:
            default_idx = WAITING_REASONS.index(current_waiting_reason)

        new_waiting_reason = st.selectbox(
            "Waiting reason",
            WAITING_REASONS,
            index=default_idx,
        )
    else:
        new_waiting_reason = None

    d1, _ = st.columns([1, 2])
    new_due = d1.text_input("Due (YYYY-MM-DD or blank).", value=ticket.due_date or "")

    st.markdown("### Task Notes")

    existing_notes = list_ticket_notes(ticket.id, limit=25)
    if existing_notes:
        for note in existing_notes:
            with st.expander(
                format_timestamp_for_display(
                    note.created_at,
                    display_tz
                ),
                expanded=False
            ):
                st.write(note.body)
    else:
        st.info("No notes yet. Add the first worklog entry below.")

    with st.form(f"add_note_{ticket.id}", clear_on_submit=True):
        note_body = st.text_area("Add a note / worklog", placeholder="What did you do? What did you learn? What's next?")
        submitted = st.form_submit_button("Add Note")
        if submitted:
            if not note_body.strip():
                st.warning("Note cannot be empty.")
            else:
                add_ticket_note(ticket.id, note_body)
                st.success("Note added.")
                st.rerun()

    a1, a2, _ = st.columns([1, 1, 2])
    if a1.button("Save Changes", use_container_width=True):
        update_task(
            ticket.id,
            status=new_status,
            priority=new_priority,
            due_date=new_due.strip() or None,
            queue=new_queue,
            waiting_reason=new_waiting_reason if new_status == "Waiting" else None,
        )
        st.success("Updated.")
        st.rerun()

    if a2.button("Mark Done", use_container_width=True):
        update_task(ticket.id, status="Done")
        st.success("Closed.")
        st.rerun()