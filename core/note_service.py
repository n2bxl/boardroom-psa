from __future__ import annotations

from core.db import (
    add_note,
    get_note,
    list_notes,
    update_note,
    delete_note,
    search_notes,
)

def create_note(
    title: str,
    body: str,
    tags: str | None,
    task_id: int | None = None,
) -> tuple[bool, str]:
    if not title.strip() or not body.strip():
        return False, "Title and body are required."
        
    add_note(
        title=title,
        body=body,
        tags=tags,
        task_id=task_id,
    )
    return True, "Note saved."

def save_note_edits(
    note_id: int,
    title: str,
    body: str,
    tags: str | None,
    task_id: int | None = None,
) -> tuple[bool, str]:
    if not title.strip() or not body.strip():
        return False, "Title and body are required."
    update_note(
        note_id=note_id,
        title=title,
        body=body,
        tags=tags,
        task_id=task_id,
    )
    return True, "Note updated."

def remove_note(note_id: int) -> None:
    delete_note(note_id)

def get_recent_notes(limit: int = 50):
    return list_notes(limit=limit)

def find_notes(query: str, limit: int = 50):
    query = query.strip()
    if not query:
        return list_notes(limit=limit)
    return search_notes(query=query, limit=limit)

def fetch_note(note_id: int):
    return get_note(note_id)