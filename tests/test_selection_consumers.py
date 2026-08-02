# tests/test_selection_consumers.py
from __future__ import annotations

import streamlit as st

from ui.board import (
    BOARD_SELECTED_TASK_KEY,
    _consume_selected_task_id,
    _sync_board_selection,
)
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

def test_sync_board_selection_uses_home_jump_target():
    st.session_state.clear()
    st.session_state[BOARD_SELECTED_TASK_KEY] = 33

    selected_id = _sync_board_selection(
        task_options=[32, 33],
        jump_task_id=32,
    )

    assert selected_id == 32
    assert st.session_state[BOARD_SELECTED_TASK_KEY] == 32


def test_sync_board_selection_survives_rerun():
    st.session_state.clear()
    st.session_state[BOARD_SELECTED_TASK_KEY] = 32

    selected_id = _sync_board_selection(
        task_options=[32, 33],
        jump_task_id=None,
    )

    assert selected_id == 32
    assert st.session_state[BOARD_SELECTED_TASK_KEY] == 32


def test_sync_board_selection_falls_back_when_task_is_filtered_out():
    st.session_state.clear()
    st.session_state[BOARD_SELECTED_TASK_KEY] = 99

    selected_id = _sync_board_selection(
        task_options=[32, 33],
        jump_task_id=None,
    )

    assert selected_id == 32
    assert st.session_state[BOARD_SELECTED_TASK_KEY] == 32