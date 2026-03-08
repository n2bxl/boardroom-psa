# ui/notes.py

from __future__ import annotations

import streamlit as st

from core.config import DEFAULTS
from core.db import add_note, list_notes
from core.time_utils import resolve_timezone, format_timestamp_for_display

from ui.text_utils import preview_text

def render_notes(get_setting):
    st.subheader("Notes")
    display_tz = resolve_timezone(st.session_state, DEFAULTS)
    preview_limit = int(get_setting("note_preview_length"))
    recent_notes_limit = int(get_setting("recent_notes_limit"))

    with st.form("add_note_form", clear_on_submit=True):
        title = st.text_input("Title", placeholder="Quick note title")
        body = st.text_area(
            "Body", 
            placeholder="Add notes here...",
            height=int(get_setting("note_body_height")),
        )
        tags = st.text_input("Tags (comma-separated)", placeholder="health, money, school, etc.")
        submitted = st.form_submit_button("Save note")

        if submitted:
            if not title.strip() or not body.strip():
                st.warning("Title and body are required.")
            else:
                add_note(title=title, body=body, tags=tags)
                st.success("Note saved")

    st.markdown("### Recent notes")
    for n in list_notes(limit=recent_notes_limit):
        preview = preview_text(n.body, preview_limit
        )
        with st.expander(
                f"{n.title} — {format_timestamp_for_display(n.created_at, display_tz)} — {preview}"
            ):
            if n.tags:
                st.caption(f"Tags: {n.tags}")
            st.write(n.body)