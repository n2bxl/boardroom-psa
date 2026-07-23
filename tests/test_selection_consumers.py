# tests/test_selection_consumers.py
from __future__ import annotations

import streamlit as st

from ui.board import _consume_selected_task_id
from ui.notes import _consume_selected_note_id


def test_consume_selected_task_id_returns_value_once():
    st.session_state.clear()
    st.session_state["selected_task_id"] = 55

    first = _consume_selected_task_id()
    second = _consume_selected_task_id()

    assert first == 55
    assert second is None
    assert "selected_task_id" not in st.session_state


def test_consume_selected_note_id_returns_value_once():
    st.session_state.clear()
    st.session_state["selected_note_id"] = 77

    first = _consume_selected_note_id()
    second = _consume_selected_note_id()

    assert first == 77
    assert second is None
    assert "selected_note_id" not in st.session_state