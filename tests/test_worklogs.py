# tests/test_worklogs.py

from __future__ import annotations

from ui import worklogs

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
        get_setting=lambda key: None,
    )

    assert render_order == ["entry", "history"]