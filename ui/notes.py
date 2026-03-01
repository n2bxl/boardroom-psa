from __future__ import annotations
import streamlit as st

from core.db import add_note, list_notes


def render_notes():
    st.subheader("Notes")

    with st.form("add_note_form", clear_on_submit=True):
        title = st.text_input("Title", placeholder="Quick note title")
        body = st.text_area("Body", placeholder="Add notes here...")
        tags = st.text_input("Tags (comma-separated)", placeholder="health, money, school, etc.")
        submitted = st.form_submit_button("Save note")

        if submitted:
            if not title.strip() or not body.strip():
                st.warning("Title and body are required.")
            else:
                add_note(title=title, body=body, tags=tags)
                st.success("Note saved")

    st.markdown("### Recent notes")
    for n in list_notes(limit=20):
        with st.expander(f"{n.title} | {n.created_at}"):
            if n.tags:
                st.caption(f"Tags: {n.tags}")
            st.write(n.body)