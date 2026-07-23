# tests/test_db_notes.py
from __future__ import annotations

import core.db as db


def test_init_db_adds_note_columns(temp_db):
    with db.get_conn() as conn:
        rows = conn.execute("PRAGMA table_info(notes);").fetchall()
        columns = {row["name"] for row in rows}

    assert "id" in columns
    assert "title" in columns
    assert "body" in columns
    assert "tags" in columns
    assert "created_at" in columns
    assert "updated_at" in columns
    assert "task_id" in columns


def test_add_note_without_task(temp_db):
    db.add_note(
        title="Test note",
        body="This is a body",
        tags="alpha,beta",
        task_id=None,
    )

    notes = db.list_notes()
    assert len(notes) == 1

    note = notes[0]
    assert note.title == "Test note"
    assert note.body == "This is a body"
    assert note.tags == "alpha,beta"
    assert note.task_id is None
    assert note.created_at is not None
    assert note.updated_at is not None


def test_add_note_with_task_link(temp_db):
    task_id = db.add_task(
        title="Linked task",
        priority="High",
        due_date=None,
    )

    db.add_note(
        title="Linked note",
        body="Attached to task",
        tags="linked",
        task_id=task_id,
    )

    note = db.list_notes()[0]
    assert note.task_id == task_id


def test_get_note_returns_expected_note(temp_db):
    db.add_note(
        title="Fetch me",
        body="Find this note",
        tags=None,
        task_id=None,
    )

    note = db.list_notes()[0]
    fetched = db.get_note(note.id)

    assert fetched is not None
    assert fetched.id == note.id
    assert fetched.title == "Fetch me"


def test_update_note_changes_fields(temp_db):
    task_id = db.add_task(
        title="Task A",
        priority="Medium",
        due_date=None,
    )
    new_task_id = db.add_task(
        title="Task B",
        priority="Low",
        due_date=None,
    )

    db.add_note(
        title="Old title",
        body="Old body",
        tags="old",
        task_id=task_id,
    )

    note = db.list_notes()[0]

    db.update_note(
        note_id=note.id,
        title="New title",
        body="New body",
        tags="new",
        task_id=new_task_id,
    )

    updated = db.get_note(note.id)
    assert updated is not None
    assert updated.title == "New title"
    assert updated.body == "New body"
    assert updated.tags == "new"
    assert updated.task_id == new_task_id
    assert updated.updated_at is not None


def test_delete_note_removes_note(temp_db):
    db.add_note(
        title="Delete me",
        body="Temporary note",
        tags=None,
        task_id=None,
    )

    note = db.list_notes()[0]
    db.delete_note(note.id)

    assert db.get_note(note.id) is None
    assert db.list_notes() == []


def test_search_notes_matches_title_body_and_tags(temp_db):
    db.add_note(
        title="Printer issue",
        body="HP printer in office 2 is offline",
        tags="work,troubleshooting",
        task_id=None,
    )
    db.add_note(
        title="School plan",
        body="Study for networking quiz",
        tags="school",
        task_id=None,
    )

    by_title = db.search_notes("Printer")
    by_body = db.search_notes("offline")
    by_tags = db.search_notes("school")

    assert len(by_title) == 1
    assert by_title[0].title == "Printer issue"

    assert len(by_body) == 1
    assert by_body[0].title == "Printer issue"

    assert len(by_tags) == 1
    assert by_tags[0].title == "School plan"


def test_list_recent_notes_returns_most_recent_first(temp_db):
    db.add_note("First", "Body 1", None, None)
    db.add_note("Second", "Body 2", None, None)
    db.add_note("Third", "Body 3", None, None)

    notes = db.list_recent_notes(limit=2)

    assert len(notes) == 2
    assert notes[0].title == "Third"
    assert notes[1].title == "Second"