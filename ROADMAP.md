# Boardroom Development Roadmap
Boardroom should remain lightweight, local-first, fast, and understandable.

The goal is not to build a massive productivity platform. The goal is to build a **personal operations system**.

---
## Next Patch
### Task Details Reliability
Prevent task navigation and Streamlit reruns from changing the task being edited.

**Observed bug:**
1. Open a task from Home
2. Switch to Board when prompted
3. Enter a task note/worklog and time spent
4. Select **Add note**
5. The selected task changes and the entry is not added to the original task

- [ ] Preserve the selected Board task across Streamlit reruns
- [ ] Keep the transient Home-to-Board navigation request separate from the persistent Board selection
- [ ] Ensure task notes and worklogs are always submitted to the task whose form was displayed
- [ ] Allow a new Home navigation request to replace the persistent Board selection
- [ ] Fall back safely when the selected task is no longer included by the active filters
- [ ] Add regression tests for opening a task from Home and submitting a worklog after the page reruns
- [ ] Add a regression test confirming that time spent is saved to the intended task

### Task Detail Action Placement
Reduce scrolling when editing or completing tasks.

- [ ] Move **Save Changes** above the Task Notes section
- [ ] Move **Mark Done** above the Task Notes section
- [ ] Keep **Save Changes** visually prominent without making **Mark Done** easy to trigger accidentally
- [ ] Confirm saving and completing a task still operate on the selected task
- [ ] Add or update tests for task action placement and behavior

### Settings Reliability
Continue migrating settings to an explicit Save workflow one setting at a time.

- [x] Decide that settings should use an explicit **Save Settings** button
- [x] Begin the Save Settings migration with the stale-task threshold
- [ ] Investigate remaining settings that appear to require an extra Streamlit rerun before taking effect
- [ ] Provide consistent success feedback after saving each settings section
- [ ] Preserve unsaved draft values across normal reruns
- [ ] Migrate remaining settings section by section rather than all at once
- [ ] Consider whether selected settings should persist between app sessions instead of living only in `st.session_state`

---
## Next Major Feature
### Events and Calendar Awareness
Represent time-bound life context that does not naturally behave like a task, such as family visits, appointments, vacations, and scheduled commitments.

**Initial distinction:**
- A task represents an action that needs to be completed
- An event represents something happening at a particular date or during a period of time
- Tasks may eventually be associated with an event, but the event itself should not require task status, priority, or **Mark Done** behavior

**Initial event model:**
- Title
- Start date and optional start time
- Optional end date and time
- All-day flag
- Notes
- Created and updated timestamps

**Initial scope:**
- [ ] Add an `events` table through the first real database migration
- [ ] Advance the SQLite schema version only when the event migration is introduced
- [ ] Create, view, edit, and delete lightweight events
- [ ] Support date-only events and optional start/end times
- [ ] Include relevant current and upcoming events in Daily Triage
- [ ] Add upcoming events to Home
- [ ] Decide how ongoing multi-day events should be displayed
- [ ] Decide whether tasks can optionally link to an event
- [ ] Add migration, database, service, and UI tests
- [ ] Keep event support lightweight rather than building a full calendar replacement

**Out of scope for the first version:**
- Recurring events
- Attendees or invitations
- External calendar synchronization
- Reminder notifications
- A full month/week calendar interface

---
## Near-Term Feature Queue
### Task Notes and Worklog UX
- [x] Move the **Add Task Note / Worklog** form above the existing note history so users do not need to scroll past a long list of notes
- [ ] Add edit actions for task notes
- [ ] Add delete actions for task notes
- [ ] Add confirmation before deleting a task note
- [ ] Add tests for editing and deleting task notes

### Initial Context and Pinning
Preserve important task context without permanently treating the first note as special.

- [ ] Replace the “always show the first note” behavior with explicit note pinning
- [ ] Add an `is_pinned` field through a tested database migration
- [ ] Allow any task note to be pinned or unpinned
- [ ] Decide whether multiple notes can be pinned
- [ ] Display pinned context separately from chronological worklog history
- [ ] Decide whether pinned notes remain visible at the top of the task history
- [ ] Add tests for pinning, unpinning, ordering, and migration behavior

### Floating and Exploratory Tasks
- [ ] Treat tasks without due dates as backlog items rather than urgent work
- [ ] Prevent undated tasks from distorting urgency and triage scoring
- [ ] Consider a separate **Backlog** or **Exploratory** section on Home
- [ ] Preserve support for long-term troubleshooting, research, and “someday” work

### Time Intelligence
Use worklog data to provide basic reporting.

- [ ] Total time by queue
- [ ] Total time by task
- [ ] Weekly time summary
- [ ] Most active tasks this week
- [ ] Optional comparison with the previous week

### Activity Heatmap
Render a GitHub-style activity grid based on worklogs.

**Possible implementation:**
- Count worklog entries or minutes by day
- Render a calendar-style grid
- Highlight productive streaks
- Show details for a selected day
- Decide whether intensity represents entry count, total minutes, or a configurable choice

### User-Configurable Queues and Statuses
- [ ] Replace hard-coded values such as `QUEUES` and `STATUS_ORDER` with configuration-backed values
- [ ] Allow custom queues such as Personal, Errands, Research, and Someday
- [ ] Allow custom statuses such as Blocked, Waiting, and Dropped
- [ ] Preserve sensible defaults for first-time users
- [ ] Validate custom values so sorting, filtering, and AI triage remain stable
- [ ] Plan a safe migration for existing tasks

---
## AI Features
### Task Extraction from Notes
Allow AI to suggest structured tasks from a note.

**Example workflow:**
1. Select **Extract Tasks** inside a note
2. Send the note body to the local model
3. Receive structured task suggestions
4. Review and edit the suggestions
5. Confirm which tasks should be inserted into SQLite

**Example structured response:**
```json
[
    {
        "title": "File taxes",
        "priority": "High"
    },
    {
        "title": "Schedule dentist appointment",
        "priority": "Medium"
    }
]
```

**Requirements:**
- [ ] Do not create tasks without user confirmation
- [ ] Validate titles, priorities, queues, and due dates before insertion
- [ ] Handle malformed model output safely
- [ ] Add tests around parsing and validation

### AI Boardroom
Treat the AI Boardroom as a **structured leadership meeting**, not an open-ended chat interface.

**Meeting Flow**
1. Create a meeting packet from tasks, notes, worklogs, events, and metrics
2. Give each advisor the same agenda
3. Collect structured advisor responses
4. Synthesize agreements, disagreements, risks, and recommendations
5. Present a concise Boardroom briefing
6. Optionally provide a collapsed discussion transcript for transparency or curiosity

#### Advisor Roles
- The Strategist
    - Long-term priorities
    - Goal alignment
    - High-impact work
- The Operator
    - What should move today
    - Blockers
    - Execution and follow-through
- The Analyst
    - Patterns in notes and activity
    - Repeated themes
    - Inefficiencies
- The CFO
    - Time allocation
    - Effort versus impact
    - Return on attention
- The Wellness Officer
    - Overload and burnout signals
    - Sustainable pacing
    - Breaks, deferrals, and workload reduction

#### Standard Agenda
- Opening remarks
- Priorities
- Concerns
- Recommendations
- Agreements
- Disagreements
- Final board recommendation

**Terminology Decision**
- [ ] Decide what to call the feature or tab:
    - Boardroom
    - Board Meeting
    - Executive Briefing
    - Daily Briefing
    - “The Room”
- [ ] Keep the final name consistent across the tab title, buttons, reports, and documentation

---
## Dashboard Expansion
Potential Home dashboard additions:

- [x] Overdue tasks
- [x] Tasks due today
- [x] Recent notes
- [x] AI focus or triage recommendation
- [ ] Recently completed tasks
- [ ] Backlog or exploratory tasks
- [ ] Weekly time summary
- [ ] Activity heatmap
- [ ] Upcoming events

---
## Task Lifecycle Improvements
### Staleness Detection
Current staleness detection already surfaces inactive tasks during triage.

- [x] Make the stale threshold user-configurable
- [ ] Add a visible stale indicator to task cards or tables
- [ ] Consider a flag icon or dedicated status treatment
- [ ] Add quick actions:
    - Defer
    - Archive
    - Schedule
    - Move to backlog

---
## Long-Term Ideas
### Semantic Search
- [ ] Semantic search across notes
- [ ] Local vector embeddings
- [ ] Natural-language questions over recent activity

Example:
> What patterns show up in my last two weeks of notes?

Consider a 30-60-90-day pattern view.

### Pattern and Trend Analysis
- [ ] Identify recurring blockers
- [ ] Compare planned priorities with actual time spent
- [ ] Detect tasks that repeatedly move between statuses
- [ ] Surface queues receiving too much or too little attention

---
## Completed Infrastructure and Features
### Database Compatibility and Migrations
- [x] Add a read-only SQLite database health check
- [x] Track the current SQLite schema version
- [x] Adopt healthy unversioned databases as version 1
- [x] Reject databases created by newer Boardroom versions
- [x] Add an ordered migration runner
- [x] Back up the database before pending migrations
- [x] Add migration fixtures and regression tests
- [x] Roll back failed migrations without advancing the version
- [x] Validate integrity and foreign keys after migrations
- [x] Report available and incomplete migration paths

### Other Completed Work
- [x] Edit standalone notes
- [x] Delete standalone notes
- [x] Show overdue and due-today metrics on Home
- [x] Show recent notes on Home
- [x] Add AI Daily Triage
- [x] Add basic task staleness scoring to AI context
- [x] Prevent missing due dates from breaking date sorting
- [x] Add due date validation and safe clearing of due dates
- [x] Connect Ollama temperature and response-token settings
- [x] Update the default model to `gpt-oss:20b`

---
## Planning Notes
When selecting work for a release:
1. Prefer one cohesive theme per patch
2. Fix issues that can lose or misdirect user-entered data before adding larger features
3. Add or update tests before considering the patch complete
4. Keep migrations safe for the existing local database
5. Create a validated backup before any pending schema migration
6. Avoid introducing a large framework when a small local solution is sufficient
7. Preserve the manual learning workflow: understand, plan, type, test, debug, and reflect
