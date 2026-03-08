# Boardroom Development Roadmap
## Current Bugs
### Notes
- Ability to delete notes
- Ability to edit existing notes

### Settings
- Settings changes sometimes require a rerun before applying
- Consider explicit "Save Settings" behavior

---
## Feature Queue
### Time Intelligence
Now that worklogs support time tracking, add basic reporting.

Ideas:
- total time per queue
- total time per task
- weekly time summary
- most active tasks this week

---
## Activity Heatmap
Render a Github-style activity grid based on worklogs.

Possible implementation:
- count task_notes per day
- render colored grid
- highlight productive streaks

---
## Task Extraction from Notes (AI)
Allow the AI to create tasks automatically

Example workflow:
1. Add button inside note expander
    > "Extract tasks from this note"
2. Send note body to AI
3. AI returns structured tasks
    - Example response:
        [
            {"title": "File taxes", "priority": "High"},
            {"title": "Schedule dentist appointment", "priority": "Medium"}
        ]
4. Insert tasks into SQLite

---
## AI Boardroom
Introduce specialized AI advisors with defined roles.
### The Strategist
Focus:
- long-term priorities
- alignment with goals
- identifying important work
### The Operator
Focus:
- what should be done today
- identifying blockers
- keeping the board moving
### The Analyst
Focus:
- patterns in notes
- repeated themes
- inefficiencies
### The CFO
Focus:
- time allocation
- ROI of tasks
- effort vs impact
### The Wellness Officer
Focus:
- burnout signals
- overload detection
- recommending breaks or deferrals

---
## Dashboard Expansion
Future Home dashboard could include:
- 🟥 Overdue tasks
- 🟨 Due today
- 🟩 Recently completed
- Recent notes
- AI focus recommendation
- Activity heatmap

---
## Long-Term Ideas
- semantic search across ntoes
- local vector embeddings
- natural language queries
    - Example:
    > "What patterns show up in my last two weeks of notes?"

---
## Guiding Philosophy
Boardroom should remain:
- lightweight
- local-first
- fast
- understandable

The goal is not to build a massive productivity platform.

The goal is to build a **personal operations system**.