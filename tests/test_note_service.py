# tests/test_note_service.py
from __future__ import annotations

import core.db as db
from core.note_service import (
    create_note,
    save_note_edits,
    remove_note,
    find_notes,
    get_recent_notes,
)


def test_create_note_rejects_blank_title(temp_db):
    ok, message = create_note(
        title="   ",
        body="Body exists",
        tags=None,
        task_id=None,
    )

    assert ok is False
    assert message == "Title and body are required."
    assert db.list_notes() == []


def test_create_note_rejects_blank_body(temp_db):
    ok, message = create_note(
        title="Title exists",
        body="   ",
        tags=None,
        task_id=None,
    )

    assert ok is False
    assert message == "Title and body are required."
    assert db.list_notes() == []


def test_create_note_accepts_task_id(temp_db):
    task_id = db.add_task(
        title="Attach target",
        priority="Medium",
        due_date=None,
    )

    ok, message = create_note(
        title="Attached note",
        body="Hello",
        tags="tag1",
        task_id=task_id,
    )

    assert ok is True
    assert message == "Note saved."

    note = db.list_notes()[0]
    assert note.task_id == task_id


def test_save_note_edits_updates_existing_note(temp_db):
    db.add_note(
        title="Original",
        body="Original body",
        tags="old",
        task_id=None,
    )
    note = db.list_notes()[0]

    ok, message = save_note_edits(
        note_id=note.id,
        title="Updated",
        body="Updated body",
        tags="new",
        task_id=None,
    )

    assert ok is True
    assert message == "Note updated."

    updated = db.get_note(note.id)
    assert updated is not None
    assert updated.title == "Updated"
    assert updated.body == "Updated body"
    assert updated.tags == "new"


def test_remove_note_deletes_note(temp_db):
    db.add_note(
        title="Temporary",
        body="Remove me",
        tags=None,
        task_id=None,
    )
    note = db.list_notes()[0]

    remove_note(note.id)

    assert db.get_note(note.id) is None


def test_find_notes_returns_filtered_results(temp_db):
    db.add_note("One", "alpha body", "x", None)
    db.add_note("Two", "beta body", "y", None)

    results = find_notes("beta", limit=10)

    assert len(results) == 1
    assert results[0].title == "Two"


def test_get_recent_notes_returns_recent_items(temp_db):
    db.add_note("Older", "1", None, None)
    db.add_note("Newer", "2", None, None)

    results = get_recent_notes(limit=1)

    assert len(results) == 1
    assert results[0].title == "Newer"