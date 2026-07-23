# tests/test_home_navigation.py
from __future__ import annotations

import streamlit as st

from ui.home import jump_to_note, jump_to_task


def test_jump_to_task_sets_expected_session_state():
    st.session_state.clear()

    jump_to_task(42)

    assert st.session_state["selected_task_id"] == 42
    assert st.session_state["active_tab"] == "Board"
    assert "selected_note_id" not in st.session_state


def test_jump_to_note_sets_expected_session_state():
    st.session_state.clear()

    jump_to_note(99)

    assert st.session_state["selected_note_id"] == 99
    assert st.session_state["active_tab"] == "Notes"
    assert "selected_task_id" not in st.session_state


def test_jump_to_task_clears_old_note_selection():
    st.session_state.clear()
    st.session_state["selected_note_id"] = 7

    jump_to_task(8)

    assert st.session_state["selected_task_id"] == 8
    assert "selected_note_id" not in st.session_state


def test_jump_to_note_clears_old_task_selection():
    st.session_state.clear()
    st.session_state["selected_task_id"] = 12

    jump_to_note(13)

    assert st.session_state["selected_note_id"] == 13
    assert "selected_task_id" not in st.session_state