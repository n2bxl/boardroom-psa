# tests/test_db_tasks_and_activity.py
from __future__ import annotations

import core.db as db


def test_add_task_defaults(temp_db):
    task_id = db.add_task(
        title="My task",
        priority="Medium",
        due_date=None,
    )

    task = db.get_task(task_id)
    assert task is not None
    assert task.title == "My task"
    assert task.status == "New"
    assert task.queue == "Personal"


def test_add_task_note_updates_recent_activity(temp_db):
    task_id = db.add_task(
        title="Server check",
        priority="High",
        due_date=None,
    )

    db.add_task_note(
        task_id=task_id,
        body="Investigated issue and logged findings",
        time_spent_minutes=25,
    )

    activity = db.list_recent_task_activity(limit=5)
    assert len(activity) == 1
    assert activity[0].task_id == task_id
    assert activity[0].task_title == "Server check"
    assert activity[0].time_spent_minutes == 25


def test_get_task_time_total_sums_minutes(temp_db):
    task_id = db.add_task(
        title="Work item",
        priority="Low",
        due_date=None,
    )

    db.add_task_note(task_id, "First chunk", 15)
    db.add_task_note(task_id, "Second chunk", 30)
    db.add_task_note(task_id, "No time logged", None)

    total = db.get_task_time_total(task_id)
    assert total == 45


def test_update_task_changes_status_priority_queue_and_waiting_reason(temp_db):
    task_id = db.add_task(
        title="Follow-up",
        priority="Low",
        due_date=None,
    )

    db.update_task(
        task_id,
        status="Waiting",
        priority="High",
        due_date="2026-03-20",
        queue="Personal",
        waiting_reason="External",
    )

    task = db.get_task(task_id)
    assert task is not None
    assert task.status == "Waiting"
    assert task.priority == "High"
    assert task.due_date == "2026-03-20"
    assert task.waiting_reason == "External"


def test_update_task_title_changes_title(temp_db):
    task_id = db.add_task(
        title="Old title",
        priority="Medium",
        due_date=None,
    )

    db.update_task_title(task_id, "New title")

    task = db.get_task(task_id)
    assert task is not None
    assert task.title == "New title"