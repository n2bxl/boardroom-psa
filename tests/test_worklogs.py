# tests/test_worklogs.py

from __future__ import annotations

from ui import worklogs
from streamlit.testing.v1 import AppTest


def _render_task_notes_app():
    import streamlit as st

    from core.db import TaskNote
    from ui import worklogs

    note = TaskNote(
        id=7,
        task_id=1,
        body="Regression test worklog",
        created_at="2026-08-15T06:43:00+00:00",
        time_spent_minutes=30,
    )

    deleted_note_id = st.session_state.get(
        "test_deleted_task_note_id"
    )

    existing_notes = (
        []
        if deleted_note_id == note.id
        else [note]
    )

    settings = {
        "task_note_height": 160,
        "time_log_step_minutes": 15,
        "note_preview_length": 80,
    }

    def get_setting(key):
        return settings[key]

    def add_task_note(*args, **kwargs):
        return None

    def update_task_note(note_id, body):
        st.session_state[
            "test_updated_task_note_id"
        ] = note_id

    def delete_task_note(note_id):
        st.session_state[
            "test_deleted_task_note_id"
        ] = note.id

    worklogs.render_task_notes(
        task_id=1,
        existing_notes=existing_notes,
        display_tz="America/Chicago",
        add_task_note=add_task_note,
        update_task_note=update_task_note,
        delete_task_note=delete_task_note,
        get_setting=get_setting,
    )


def _button_by_label(app, label):
    return next(
        button
        for button in app.button
        if button.label == label
    )


def test_render_task_notes_places_entry_before_history(monkeypatch):
    render_order = []

    monkeypatch.setattr(
        worklogs,
        "render_task_note_entry",
        lambda *args, **kwargs: render_order.append("entry")
    )

    monkeypatch.setattr(
        worklogs,
        "render_task_note_history",
        lambda *args, **kwargs: render_order.append("history")
    )

    worklogs.render_task_notes(
        task_id=1,
        existing_notes=[],
        display_tz="America/Chicago",
        add_task_note=lambda *args, **kwargs: None,
        update_task_note=lambda *args, **kwargs: None,
        delete_task_note=lambda *args, **kwargs: None,
        get_setting=lambda key: None,
    )

    assert render_order == ["entry", "history"]


def test_render_task_notes_with_existing_note():
    app = AppTest.from_function(
        _render_task_notes_app
    ).run()

    assert len(app.exception) == 0

    labels = [
        button.label
        for button in app.button
    ]

    assert "Edit" in labels
    assert "Delete" not in labels


def test_task_note_delete_cancel_returns_to_edit():
    app = AppTest.from_function(
        _render_task_notes_app
    ).run()

    _button_by_label(
        app,
        "Edit",
    ).click().run()

    assert len(app.exception) == 0

    labels = [
        button.label
        for button in app.button
    ]

    assert "Save note" in labels
    assert "Cancel" in labels
    assert "Delete" in labels

    _button_by_label(
        app,
        "Delete",
    ).click().run()

    assert len(app.exception) == 0

    labels = [
        button.label
        for button in app.button
    ]

    assert "Confirm delete" in labels
    assert "Cancel" in labels

    _button_by_label(
        app,
        "Cancel",
    ).click().run()

    assert len(app.exception) == 0

    assert (
        app.session_state[
            "editing_task_note_id"
        ]
        == 7
    )

    assert (
        app.session_state[
            "confirm_delete_task_note_id"
        ]
        is None
    )

    labels = [
        button.label
        for button in app.button
    ]

    assert "Save note" in labels
    assert "Delete" in labels


def test_task_note_confirm_delete():
    app = AppTest.from_function(
        _render_task_notes_app
    ).run()

    _button_by_label(
        app,
        "Edit",
    ).click().run()

    _button_by_label(
        app,
        "Delete",
    ).click().run()

    _button_by_label(
        app,
        "Confirm delete",
    ).click().run()

    assert len(app.exception) == 0

    assert (
        app.session_state[
            "test_deleted_task_note_id"
        ]
        == 7
    )

    assert (
        app.session_state[
            "editing_task_note_id"
        ]
        is None
    )

    assert (
        app.session_state[
            "confirm_delete_task_note_id"
        ]
        is None
    )

    assert any(
        "No notes yet" in info.value
        for info in app.info
    )