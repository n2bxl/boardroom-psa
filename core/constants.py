# core/constants.py

"""
Centralized constants for the Personal PSA app.

Anything that represents a fixed domain concept
(statuses, queues, priorities) should live here.
"""

# --- Task Statuses ---
STATUS_ORDER = [
    "New",
    "In Progress",
    "Waiting",
    "Done",
]

# Used for default "open" filtering logic
OPEN_STATUSES = [
    "New",
    "In Progress",
    "Waiting",
]

# --- Task Priorities ---
PRIORITIES = [
    "Low",
    "Medium",
    "High",
]

# --- Priority Icons ---
PRIORITY_ICONS = {
    "High": "🟥",
    "Medium": "🟨",
    "Low": "🟩",
}

# --- Queues ---
QUEUES = [
    "Personal",
    "School",
    "Work",
    "Health",
    "Money",
]

# --- Waiting Reasons ---
WAITING_REASONS = [
    "(Select reason)",
    "Blocked",
    "Awaiting response",
    "External",
    "Scheduled",
    "Other",
]