# core/db.py

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from core.time_utils import utc_now_iso

DB_PATH = Path("data") / "life.db"

def get_conn() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)

    # Enable foreign key enforcement (SQLite disables it by default)
    conn.execute("PRAGMA foreign_keys = ON;")

    conn.row_factory = sqlite3.Row
    return conn

def init_db() -> None:
    with get_conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                priority TEXT NOT NULL DEFAULT 'Medium',
                due_date TEXT,
                status TEXT NOT NULL DEFAULT 'New',
                created_at TEXT NOT NULL,
                updated_at TEXT
            );
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                body TEXT NOT NULL,
                tags TEXT,
                created_at TEXT NOT NULL
            );
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS task_notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER NOT NULL,
                body TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE
            );
            """
        )
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_task_notes_created
            ON task_notes(created_at DESC);
            """
        )
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_task_notes_task_id
            ON task_notes(task_id);
            """
        )
    ensure_columns()

def ensure_columns() -> None:
    """Add new columns safely if the DB already exists."""
    with get_conn() as conn:
        # --- TASKS ---
        task_cols = conn.execute(
            "PRAGMA table_info(tasks);"
        ).fetchall()
        task_existing = {c["name"] for c in task_cols}

        if "queue" not in task_existing:
            conn.execute(
                "ALTER TABLE tasks ADD COLUMN queue TEST NOT NULL DEFAULT 'Personal';"
            )

        if "updated_at" not in task_existing:
            conn.execute(
                "ALTER TABLE tasks ADD COLUMN updated_at TEXT;"
            )

        if "waiting_reason" not in task_existing:
            conn.execute(
                "ALTER TABLE tasks ADD COLUMN waiting_reason TEXT;"
            )

        # --- TASK NOTES ---
        task_note_cols = conn.execute("PRAGMA table_info(task_notes);").fetchall()
        task_note_existing = {c["name"] for c in task_note_cols}

        if "time_spent_minutes" not in task_note_existing:
            conn.execute(
                "ALTER TABLE task_notes ADD COLUMN time_spent_minutes INTEGER;"
            )

        # --- NOTES ---
        note_cols = conn.execute("PRAGMA table_info(notes);").fetchall()
        note_existing = {c["name"] for c in note_cols}

        if "updated_at" not in note_existing:
            conn.execute(
                "ALTER TABLE notes ADD COLUMN updated_at TEXT;"
            )

        if "task_id" not in note_existing:
            conn.execute(
                "ALTER TABLE notes ADD COLUMN task_id INTEGER REFERENCES tasks(id) ON DELETE SET NULL;"
            )

def get_task(task_id: int) -> Optional[Task]:
    with get_conn() as conn:
        row = conn.execute(
            """
            SELECT *
            FROM tasks
            WHERE id = ?
            """,
            (task_id,),
        ).fetchone()

    if not row:
        return None

    return Task(**dict(row))
    
def get_task_time_total(task_id: int) -> int:
    with get_conn() as conn:
        row = conn.execute(
            """
            SELECT COALESCE(SUM(time_spent_minutes), 0) AS total
            FROM task_notes
            WHERE task_id = ?
            """,
            (task_id,),
        ).fetchone()

    return int(
        row["total"]
        if row and row["total"] is not None
        else 0
    )

def list_recent_task_activity(limit: int = 8) -> list[RecentTaskActivity]:
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT
                tn.id,
                tn.task_id,
                t.title AS task_title,
                t.priority,
                tn.body,
                tn.created_at,
                tn.time_spent_minutes
            FROM task_notes tn
            JOIN tasks t ON tn.task_id = t.id
            ORDER BY tn.created_at DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

    return [RecentTaskActivity(**dict(r)) for r in rows]

@dataclass
class Task:
    id: int
    title: str
    priority: str
    due_date: Optional[str]
    status: str
    created_at: str
    updated_at: Optional[str]
    queue: str = "Personal"
    waiting_reason: Optional[str] = None

@dataclass
class Note:
    id: int
    title: str
    body: str
    tags: Optional[str]
    created_at: str
    updated_at: Optional[str] = None
    task_id: Optional[int] = None

@dataclass
class TaskNote:
    id: int
    task_id: int
    body: str
    created_at: str
    time_spent_minutes: Optional[int] = None

@dataclass
class RecentTaskActivity:
    id: int
    task_id: int
    task_title: str
    priority: str
    body: str
    created_at: str
    time_spent_minutes: Optional[int] = None

def add_task(
        title: str,
        priority: str,
        due_date: Optional[str],
        queue: str = "Personal",
        status: str = "New",
        waiting_reason: Optional[str] = None,
    ) -> int:
    now_utc = utc_now_iso()

    if status != "Waiting":
        waiting_reason = None

    with get_conn() as conn:
        cur = conn.execute(
            """
            INSERT INTO tasks (title, priority, due_date, queue, status, waiting_reason, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                title.strip(),
                priority,
                due_date,
                queue,
                status,
                waiting_reason,
                now_utc,
                now_utc,
            ),
        )
        return int(cur.lastrowid)

def list_tasks(status: Optional[str] = None) -> list[Task]:
    q = "SELECT * FROM tasks"
    params: tuple = ()
    if status:
        q += " WHERE status = ?"
        params = (status,)
    q += " ORDER BY (due_date IS NULL), due_date ASC, created_at DESC"

    with get_conn() as conn:
        rows = conn.execute(q, params).fetchall()
    return [Task(**dict(r)) for r in rows]

def add_note(
    title: str,
    body: str,
    tags: Optional[str],
    task_id: Optional[int]= None,
) -> None:
    now_utc = utc_now_iso()
    clean_tags = tags.strip() if tags and tags.strip() else None

    with get_conn() as conn:
        conn.execute(
            """
            INSERT INTO notes (title, body, tags, task_id, created_at, updated_at)
            VALUES (?, ?, ?, ?, ? ,?)
            """,
            (
                title.strip(),
                body.strip(),
                clean_tags,
                task_id,
                now_utc,
                now_utc,
            ),
        )

def list_notes(limit: int = 50) -> list[Note]:
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM notes
            ORDER BY COALESCE(updated_at, created_at) DESC, created_at DESC
            LIMIT ?
            """,
            (limit, ),
        ).fetchall()
    return [Note(**dict(r)) for r in rows]

def get_note(note_id: int) -> Optional[Note]:
    with get_conn() as conn:
        row = conn.execute(
            """
            SELECT *
            FROM notes
            WHERE id = ?
            """,
            (note_id, ),
        ).fetchone()

    if not row:
        return None

    return Note(**dict(row))

def update_note(
    note_id: int,
    title: str,
    body:str,
    tags: Optional[str],
    task_id: Optional[int] = None,
) -> None:
    now_utc = utc_now_iso()
    clean_tags = tags.strip() if tags and tags.strip() else None

    with get_conn() as conn:
        conn.execute(
            """
            UPDATE notes
            SET title = ?, body = ?, tags = ?, task_id = ?, updated_at = ?
            WHERE id = ?
            """,
            (
                title.strip(),
                body.strip(),
                clean_tags,
                task_id,
                now_utc,
                note_id
            ),
        )

def delete_note(note_id: int) -> None:
    with get_conn() as conn:
        conn.execute(
            """
            DELETE FROM notes
            WHERE id = ?
            """,
            (note_id,),
        )

def search_notes(query: str, limit: int = 50) -> list[Note]:
    search_term = f"%{query.strip()}%"

    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM notes
            WHERE title LIKE ?
                OR body LIKE ?
                OR COALESCE(tags, '') LIKE ?
            ORDER BY COALESCE(updated_at, created_at) DESC, created_at DESC
            LIMIT ?
            """,
            (
                search_term,
                search_term,
                search_term,
                limit
            )
        ).fetchall()

    return [Note(**dict(r)) for r in rows]

def update_task(
        task_id: int, 
        *, 
        status: Optional[str] = None, 
        priority: Optional[str] = None, 
        due_date: Optional[str] = None, 
        queue: Optional[str] = None,
        waiting_reason: Optional[str] = "__UNCHANGED__",
    ) -> None:
    
    fields = []
    params = []

    if status is not None:
        fields.append("status = ?")
        params.append(status)
    if priority is not None:
        fields.append("priority = ?")
        params.append(priority)
    if due_date is not None:
        fields.append("due_date = ?")
        params.append(due_date)
    if queue is not None:
        fields.append("queue = ?")
        params.append(queue)
    if waiting_reason != "__UNCHANGED__":
        fields.append("waiting_reason = ?")
        params.append(waiting_reason)

    fields.append("updated_at = ?")
    params.append(utc_now_iso())

    q = f"UPDATE tasks SET {', '.join(fields)} WHERE id = ?"
    params.append(task_id)

    with get_conn() as conn:
        conn.execute(q, params)

def add_task_note(
        task_id: int, 
        body: str, 
        time_spent_minutes: Optional[int] = None
    ) -> None:
    body = body.strip()
    if not body:
        return

    now_utc = utc_now_iso()

    with get_conn() as conn:
        conn.execute(
            """
            INSERT INTO task_notes (task_id, body, created_at, time_spent_minutes)
            VALUES (?, ?, ?, ?)
            """,
            (task_id, body, now_utc, time_spent_minutes),
        )
        # Touch updated_at so the task shows recent activity
        conn.execute(
            "UPDATE tasks SET updated_at = ? WHERE id = ?",
            (now_utc, task_id),
        )


def list_task_notes(task_id: int, limit: int = 50) -> list[TaskNote]:
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT id, task_id, body, created_at, time_spent_minutes
            FROM task_notes
            WHERE task_id = ?
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (task_id, limit),
        ).fetchall()
    return [TaskNote(**dict(r)) for r in rows]

def list_recent_notes(limit: int = 5) -> list[Note]:
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM notes
            ORDER BY COALESCE(updated_at, created_at) DESC, created_at DESC
            LIMIT ?
            """,
            (limit, ),
        ).fetchall()

    return [Note(**dict(r)) for r in rows]

def update_task_title(task_id: int, title: str) -> None:
    clean_title = title.strip()
    if not clean_title:
        return

    now_utc = utc_now_iso()

    with get_conn() as conn:
        conn.execute(
            """
            UPDATE tasks
            Set title = ?, updated_at = ?
            WHERE id = ?
            """,
            (clean_title, now_utc, task_id)
        )