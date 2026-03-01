from __future__ import annotations
import datetime as dt
import pandas as pd
import streamlit as st

from core.constants import STATUS_ORDER, PRIORITIES, QUEUES
from core.db import list_tasks, update_task, list_ticket_notes, add_ticket_note
from core.ai import daily_triage


def today_iso() -> str:
    return str(dt.date.today())


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
    lines.append("OPEN TICKETS:")
    if all_open:
        for t in all_open[:12]:
            lines.append(
                f"- {t.title} (status={t.status}, priority={t.priority}, queue={getattr(t, 'queue', 'Personal')}, due={t.due_date or 'none'})"
            )
    else:
        lines.append("- none")
    return "\n".join(lines)


def render_board(model_name: str, get_default_statuses, get_default_queues):
    st.subheader("Service Board")

    all_tasks = list_tasks()
    open_like, due_today, overdue, waiting = compute_kpis(all_tasks)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Open Tickets", len(open_like))
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
    df = pd.DataFrame(
        [
            {
                "ID": t.id,
                "Title": t.title,
                "Status": t.status,
                "Priority": t.priority,
                "Queue": getattr(t, "queue", "Personal"),
                "Due": t.due_date or "",
                "Created": getattr(t, "created_at", "") or "",
                "Updated": getattr(t, "updated_at", "") or "",
                "Overdue": "YES" if is_overdue(t.due_date) else "",
            }
            for t in filtered
        ]
    )

    st.markdown("### Ticket Queue")
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.divider()
    st.markdown("### Ticket Details")

    if not filtered:
        st.info("No tickets match your filters.")
        return

    id_to_label = {t.id: f"{t.id} | {t.title}" for t in filtered}
    selected_id = st.selectbox(
        "Select ticket",
        options=list(id_to_label.keys()),
        format_func=lambda i: id_to_label[i],
    )

    ticket = next(t for t in all_tasks if t.id == selected_id)

    top = st.columns([2, 1, 1, 1])
    top[0].text_input("Title (read-only for now)", value=ticket.title, disabled=True)
    new_status = top[1].selectbox("Status", STATUS_ORDER, index=STATUS_ORDER.index(ticket.status))
    new_priority = top[2].selectbox("Priority", PRIORITIES, index=PRIORITIES.index(ticket.priority))
    new_queue = top[3].selectbox("Queue", QUEUES, index=QUEUES.index(getattr(ticket, "queue", "Personal")))

    d1, _ = st.columns([1, 2])
    new_due = d1.text_input("Due (YYYY-MM-DD or blank).", value=ticket.due_date or "")

    st.markdown("### Ticket Notes")

    existing_notes = list_ticket_notes(ticket.id, limit=25)
    if existing_notes:
        for note in existing_notes:
            with st.expander(f"{note.created_at}", expanded=False):
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
        )
        st.success("Updated.")
        st.rerun()

    if a2.button("Mark Done", use_container_width=True):
        update_task(ticket.id, status="Done")
        st.success("Closed.")
        st.rerun()