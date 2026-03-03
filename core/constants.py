"""
Centralized constants for the Personal PSA app.

Anything that represents a fixed domain concept
(statuses, queues, priorities) should live here.
"""


# --- Ticket Statuses ---
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


# --- Ticket Priorities ---
PRIORITIES = [
    "Low",
    "Medium",
    "High",
]


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
    "Blocked",
    "External",
    "Scheduled",
    "Other",
]