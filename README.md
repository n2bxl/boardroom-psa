# Boardroom Personal PSA

Boardroom is a personal productivity system inspired by IT ticketing platforms and Professional Services Automation (PSA) tools.

It combines task management, worklogs, notes, and AI-assisted triage into a single lightweight dashboard built with Streamlit and SQLite.

The goal is to bring structured "operations thinking" to personal productivity.

---
## Project Roadmap

See [ROADMAP.md](ROADMAP.md) for current priorities, planned features, and future ideas.

---
## Core Concepts

Boardroom treats personal work the same way a help desk treats tickets.

Tasks move through a lifecycle:
> New → In Progress → Waiting → Done

Each task can include:
- priority
- queue/category
- due date
- waiting reason
- worklog entries
- time tracking

Notes and worklogs create a history of progress and decision-making over time.

---
## Key Features
### Task Board
A dispatcher-style task board with filtering and operational metrics.

Includes:
- task queues (Personal, School, Work, Health, Money)
- priority indicators
- waiting reason tracking
- due-date monitoring
- stale task detection
- time logged per task

---
## Worklogs / Time Tracking
Each task supports worklog entries with optional time tracking.

Worklogs function similarly to ticket notes in PSA systems and allow you to track:
- what was done
- what was learned
- next steps
- time spent

---
## Home Dashboard
The Home tab acts as a personal operations dashboard.

It provides:
- open task metrics
- today's focus list
- recent activity feed
- quick navigation into tasks

---
## AI Daily Triage

Boardroom includes an AI dispatcher that reviews your task board and produces a triage report.

The AI identifies:
- highest priority tasks
- approaching deadlines
- potential blockers
- recommended next actions

AI integration runs locally through Ollama.

---
# Architecture

This application follows a modular architecture:
- app.py
- core/
    - ai.py
    - config.py
    - constants.py
    - date_utils.py
    - db.py
    - note_service.py
    - time_utils.py
    - version.py
- ui/
    - board.py
    - home.py
    - notes.py
    - settings.py
    - sidebar.py
    - text_utils.py
    - worklogs.py

## core/
Contains business logic, database access, configuration, and AI integrations.

## ui/
Contains Streamlit rendering modules.

## app.py
Application entry point and tab routing.

---
## Local-First Design

Boardroom is intentionally simple and local-first.
- SQLite database
- local AI models
- no external services required

This keeps the system fast, private, and easy to maintain.

---
## Database Health and Migrations

Boardroom tracks its SQLite schema using
`PRAGMA user_version`.

Run the read-only database health check with:

```bash
python -m core.db_health
```
---
## Running the Application

Create a virtual environment and install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate

python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt

python3 -m streamlit run app.py
```

Ollama must be running before using AI Daily Triage. The Ollama
desktop application may already provide the local service. Otherwise,
start it separately with:

```bash
ollama serve
```