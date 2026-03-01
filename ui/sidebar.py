from __future__ import annotations
import streamlit as st

from core.constants import QUEUES, PRIORITIES
from core.db import add_task, add_ticket_note
from core.version import __version__


def render_sidebar(get_setting) -> None:
    """Sidebar: New Ticket intake."""
    with st.sidebar:
        st.subheader("New Ticket")

        with st.form("new_ticket_form", clear_on_submit=True):
            t_title = st.text_input("Summary")
            t_queue = st.selectbox("Queue", QUEUES)
            t_priority = st.selectbox("Priority", PRIORITIES, index=1)
            t_due = st.date_input("Due date", value=None)

            t_note = st.text_area(
                "Initial note (optional)",
                placeholder="Context, links, what you tried, next steps...",
                height=int(get_setting("ticket_note_height")),
            )

            submitted = st.form_submit_button("Create Ticket", use_container_width=True)

            if submitted:
                if not t_title.strip():
                    st.warning("Summary is required.")
                else:
                    ticket_id = add_task(
                        title=t_title,
                        priority=t_priority,
                        due_date=str(t_due) if t_due else None,
                        queue=t_queue,
                    )
                    if t_note.strip():
                        add_ticket_note(ticket_id, t_note)

                    st.success("Created.")
                    st.rerun()

        st.divider()

        st.sidebar.markdown("---")
        st.sidebar.caption(f"Boardroom Personal PSA v{__version__}")