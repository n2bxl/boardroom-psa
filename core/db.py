# core/db.py
from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

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
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
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
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            );
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS ticket_notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER NOT NULL,
                body TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE
            );
            """
        )
    ensure_columns()

def ensure_columns() -> None:
    """Add new columns safely if the DB already exists."""
    with get_conn() as conn:
        cols = conn.execute("PRAGMA table_info(tasks);").fetchall()
        existing = {c["name"] for c in cols}

        # SQLite supports ADD COLUMN (no IF NOT EXISTS), so we check first.
        if "queue" not in existing:
            conn.execute(
                "ALTER TABLE tasks ADD COLUMN queue TEXT NOT NULL DEFAULT 'Personal';"
            )

        if "updated_at" not in existing:
            conn.execute(
                "ALTER TABLE tasks ADD COLUMN updated_at TEXT;"
            )

        if "waiting_reason" not in existing:
            conn.execute(
                "ALTER TABLE tasks ADD COLUMN waiting_reason TEXT;"
            )

        # TODO: do you want PSA-like statuses? (instead of Open/Done)
        # we can keep current data and just start using new statuses going forward

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

@dataclass
class TicketNote:
    id: int
    task_id: int
    body: str
    created_at: str

def add_task(
        title: str,
        priority: str,
        due_date: Optional[str],
        queue: str = "Personal"
    ) -> int:
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO tasks (title, priority, due_date, queue, status) VALUES (?, ?, ?, ?, 'New')",
            (title.strip(), priority, due_date, queue)
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

def set_task_status(task_id: int, status:str) -> None:
    with get_conn() as conn:
        conn.execute("UPDATE tasks SET status = ? WHERE id = ?", (status, task_id))

def add_note(title: str, body: str, tags: Optional[str]) -> None:
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO notes (title, body, tags) VALUES (?, ?, ?)",
            (title.strip(), body.strip(), tags.strip() if tags else None)
        )

def list_notes(limit: int = 50) -> list[Note]:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM notes ORDER BY created_at DESC LIMIT ?", (limit,)
        ).fetchall()
    return [Note(**dict(r)) for r in rows]

def update_task(
        task_id: int, 
        *, 
        status: Optional[str] = None, 
        priority: Optional[str] = None, 
        due_date: Optional[str] = None, 
        queue: Optional[str] = None,
        waiting_reason: Optional[str] = None,
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
    if waiting_reason is not None:
        fields.append("waiting_reason = ?")
        params.append(waiting_reason)

    fields.append("updated_at = datetime('now')")
    q = f"UPDATE tasks SET {', '.join(fields)} WHERE id = ?"
    params.append(task_id)

    with get_conn() as conn:
        conn.execute(q, params)

def add_ticket_note(task_id: int, body: str) -> None:
    body = body.strip()
    if not body:
        return
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO ticket_notes (task_id, body) VALUES (?, ?)",
            (task_id, body),
        )
        # Touch updated_at so the ticket shows recent activity
        conn.execute(
            "UPDATE tasks SET updated_at = datetime('now') WHERE id = ?",
            (task_id,),
        )


def list_ticket_notes(task_id: int, limit: int = 50) -> list[TicketNote]:
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT id, task_id, body, created_at
            FROM ticket_notes
            WHERE task_id = ?
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (task_id, limit),
        ).fetchall()
    return [TicketNote(**dict(r)) for r in rows]