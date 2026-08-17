# Boardroom Development Roadmap

Boardroom should remain lightweight, local-first, fast, and understandable.

The goal is not to build a massive productivity platform. The goal is to build a **personal operations system** that can be trusted with day-to-day tasks, work history, time, life context, and AI-assisted planning.

---

## Vision for 1.0

Boardroom 1.0 should be the point where the application feels dependable enough to function as a real personal operations system rather than an evolving prototype.

At 1.0, Boardroom should answer five core questions:

1. **What do I need to do?**
   * Tasks, priorities, queues, due dates, waiting states, backlog items, and completion.

2. **What is happening around me?**
   * Lightweight events such as appointments, trips, visits, vacations, and scheduled commitments.

3. **What have I done?**
   * Task notes, worklogs, historical context, and completed work.

4. **Where is my attention going?**
   * Time logged by task and queue, weekly summaries, and basic activity reporting.

5. **Given all of that, what deserves my attention next?**
   * Daily Triage and the structured AI Boardroom.

### 1.0 Scope Principle

A feature belongs before 1.0 if it directly completes one of those five responsibilities or materially protects the user's data.

A feature that mainly makes those capabilities richer, smarter, more automated, or more visually interesting can wait for 1.x.

---

# Road to 1.0

## 0.7.x - Data Ownership and Worklog Completion

Finish the task and worklog lifecycle before introducing another major data type.

### Task Notes and Worklog UX

Historical task notes should primarily behave as records to read. Editing or deleting them should require deliberate user action.

* [x] Move the **Add Task Note / Worklog** form above existing note history
* [x] Add editing for existing task-note text
* [x] Render existing task notes as formatted Markdown by default
* [x] Require an explicit **Edit** action before displaying editable Markdown source
* [x] Add **Save** and **Cancel** behavior for task-note editing
* [x] Preserve existing logged time and timestamps when only note text is edited
* [x] Update task activity timestamps after note edits
* [x] Add regression coverage for task-note editing
* [x] Preserve the selected task after worklog edits and deletions
* [ ] Allow logged time on an existing worklog entry to be corrected
* [ ] Reuse the existing Task Note / Worklog time-entry UI when editing logged time rather than introducing a separate editing control
* [ ] Pre-populate the edit-time control with the entry's currently logged time
* [ ] Preserve user-configured time-entry increments and related Settings behavior when editing existing worklogs
* [ ] Allow note text and logged time to be changed independently or together through the existing **Save note** action
* [ ] Allow logged time to be reduced to zero where appropriate
* [ ] Ensure edited time entries immediately update task time totals
* [ ] Update parent task activity timestamps after logged-time corrections
* [ ] Add database regression coverage for increasing, decreasing, clearing, and preserving logged time
* [ ] Add Streamlit AppTest coverage for editing existing logged time
* [ ] Consider extracting the shared time-entry UI into a reusable `worklogs.py` helper if doing so reduces duplication without complicating the current design

**Next sprint focus:** complete logged-time editing while preserving the existing Add Task Note / Worklog experience and user-configured time-entry behavior.

### Soft Delete and Recycle Bin

Adopt a reusable deletion model rather than permanently deleting records immediately.

**General lifecycle:**

`Active -> Soft Deleted -> Restored or Purged`

Initial goals:

* [ ] Define a reusable soft-delete strategy for Boardroom records
* [ ] Prefer a `deleted_at` style lifecycle over immediate row deletion
* [ ] Exclude soft-deleted records from normal application queries
* [ ] Create a **Recycle Bin** interface
* [ ] Allow deleted records to be restored during the grace period
* [ ] Allow deliberate permanent deletion where appropriate
* [ ] Add a configurable deletion grace period in Settings
* [ ] Consider **Never automatically purge** as an available retention option
* [ ] Place Recycle Bin access near deletion-retention Settings
* [ ] Add database and regression tests for delete, restore, and purge behavior
* [ ] Ensure parent task timestamps and time totals remain correct after worklog deletion or restoration

### Task Note Deletion

Task Notes are the first record type being prepared for the generalized soft-delete system.

The current deletion workflow intentionally establishes the user-facing interaction and database contract first. Until the generalized soft-delete infrastructure is implemented, deletion removes the task-note row immediately after explicit confirmation.

* [x] Show **Delete** only after entering task-note Edit mode
* [x] Require a deliberate confirmation step before deletion
* [x] Return to Edit mode when deletion is canceled
* [x] Preserve the selected task after deleting a task note
* [x] Recalculate logged-time totals when deleting a worklog entry
* [x] Update parent task activity after deleting a task note
* [x] Add database regression coverage for task-note deletion
* [x] Add UI regression coverage for rendering, entering Edit mode, canceling deletion, and confirming deletion
* [x] Keep task-note action buttons visually consistent across Save, Cancel, and Delete actions
* [ ] Replace immediate row deletion with the generalized soft-delete lifecycle
* [ ] Restore deleted notes through the Recycle Bin
* [ ] Preserve logged-time correctness when restoring a deleted worklog
* [ ] Add regression tests for restoring and permanently purging task notes

### Initial Context and Pinning

Preserve important task context without permanently treating the first note as special.

* [ ] Replace any implicit "first note is special" behavior with explicit note pinning
* [ ] Add an `is_pinned` field through a tested migration
* [ ] Allow task notes to be pinned and unpinned
* [ ] Decide whether multiple notes may be pinned
* [ ] Display pinned context separately from chronological worklog history
* [ ] Keep normal worklog history chronological
* [ ] Add regression tests for pinning, ordering, and migration behavior

### Floating and Exploratory Tasks

Tasks without due dates should represent backlog or exploratory work rather than artificial urgency.

* [ ] Treat tasks without due dates as backlog items
* [ ] Prevent undated tasks from distorting urgency and AI triage scoring
* [ ] Add a **Backlog** or **Exploratory** area where useful
* [ ] Preserve support for long-term troubleshooting, research, learning, and "someday" work
* [ ] Decide how backlog tasks should appear on Home
* [ ] Allow stale tasks to be intentionally moved into backlog

### Task Lifecycle Refinement

* [x] Make the stale-task threshold configurable

* [ ] Add a visible stale indicator to task displays where useful

* [ ] Consider quick actions for:
  * Defer
  * Archive
  * Schedule
  * Move to backlog

* [ ] Ensure lifecycle actions remain compatible with Daily Triage

### User-Controlled Backup

Existing migration backups protect database upgrades. Before 1.0, the user should also have an obvious way to protect their data independently of a migration.

* [ ] Add a user-initiated **Create Backup** action
* [ ] Show the most recent backup date or status
* [ ] Provide easy access to the backup location where practical
* [ ] Document the recovery process
* [ ] Validate manually created backups before reporting success
* [ ] Keep restoration conservative and safe
* [ ] Do not require a full automated Restore UI if a documented manual restore procedure is safer for 1.0

---

## 0.8.x - Events, Time, and Life Context

Introduce information that affects planning but does not naturally behave like a task.

### Events and Calendar Awareness

An event represents something happening at a particular time or during a period of time.

A task represents an action that needs to be completed.

An event should not require task status, priority, or **Mark Done** behavior.

**Initial event model:**

* Title
* Start date
* Optional start time
* Optional end date
* Optional end time
* All-day flag
* Notes
* Created timestamp
* Updated timestamp
* Soft-delete metadata

### Initial Event Scope

* [ ] Add the `events` table through a tested database migration
* [ ] Advance the SQLite schema version only when the migration is introduced
* [ ] Create lightweight events
* [ ] View and edit events
* [ ] Soft-delete and restore events through the shared Recycle Bin
* [ ] Support date-only events
* [ ] Support optional start and end times
* [ ] Support multi-day events
* [ ] Decide how ongoing multi-day events should display
* [ ] Add relevant current and upcoming events to Home
* [ ] Include relevant events in Daily Triage
* [ ] Decide whether tasks may optionally link to an event
* [ ] Add migration, database, service, and UI regression tests
* [ ] Keep Events lightweight rather than building a full calendar replacement

### Out of Scope for Initial Events

These are not required for 1.0:

* Recurring events
* Attendees or invitations
* External calendar synchronization
* Reminder notifications
* Full month/week calendar views

### Time Intelligence

Use existing worklog data to answer basic questions about where effort is going.

* [ ] Total time by task
* [ ] Total time by queue
* [ ] Weekly time summary
* [ ] Most active tasks this week
* [ ] Optional comparison with the previous week
* [ ] Make time information useful to both Home and the AI Boardroom

### Home Dashboard Expansion

By this stage, Home should provide a useful operational picture without becoming an analytics dashboard.

* [x] Overdue tasks
* [x] Tasks due today
* [x] Recent notes
* [x] AI focus or triage recommendation
* [ ] Recently completed tasks
* [ ] Backlog or exploratory tasks
* [ ] Weekly time summary
* [ ] Upcoming events

### User-Configurable Queues

Queues are a reasonable form of personalization before 1.0.

* [ ] Replace hard-coded queue values with validated configuration-backed values
* [ ] Allow queues such as Personal, Errands, Research, School, and Someday
* [ ] Preserve sensible defaults for first-time users
* [ ] Ensure custom queues remain compatible with filtering, sorting, reporting, and AI triage
* [ ] Plan a safe migration for existing tasks if required

Custom task statuses are intentionally deferred until after 1.0 because statuses affect task lifecycle rules more deeply than queues.

---

## 0.9.x - The AI Boardroom and Feature Completion

By 0.9.x, the core application should be feature-complete for 1.0.

The primary new capability in this phase is the feature that gives the project its name.

### AI Boardroom

Treat the AI Boardroom as a **structured leadership meeting**, not an open-ended chat interface.

The Boardroom should use the operational context already stored locally rather than requiring the user to manually explain their situation each time.

### Meeting Packet

Build a common meeting packet containing relevant information such as:

* Active tasks
* Priorities
* Due and overdue work
* Waiting or blocked work
* Backlog items
* Recent task notes and worklogs
* Pinned task context
* Current and upcoming events
* Recent time allocation
* Stale tasks
* Daily Triage context where useful

### Meeting Flow

1. Build one common meeting packet
2. Give each advisor the same agenda and source context
3. Collect structured advisor responses
4. Identify agreements
5. Identify disagreements
6. Identify risks and concerns
7. Synthesize recommendations
8. Present a concise final Boardroom briefing
9. Optionally expose advisor discussion or individual responses for transparency

### Advisor Roles

#### The Strategist

Focus:

* Long-term priorities
* Goal alignment
* High-impact work
* Whether current activity matches larger objectives

#### The Operator

Focus:

* What should move today
* Immediate blockers
* Execution
* Follow-through
* What should be deferred or scheduled

#### The Analyst

Focus:

* Patterns in recent work
* Repeated themes
* Workflow inefficiencies
* Stale or repeatedly revisited work

#### The CFO

Focus:

* Time allocation
* Effort versus impact
* Return on attention
* Whether too much time is being invested in low-value work

#### The Wellness Officer

Focus:

* Overload signals
* Sustainable pacing
* Excessive commitments
* Breaks and deferrals
* Whether the proposed workload is realistically achievable

The Wellness Officer should provide workload-management observations based on Boardroom data, not medical or diagnostic conclusions.

### Standard Agenda

* Opening remarks
* Priorities
* Concerns
* Recommendations
* Agreements
* Disagreements
* Final board recommendation

### Boardroom Requirements

* [ ] Build a deterministic meeting-packet structure
* [ ] Give advisors consistent source context
* [ ] Use structured outputs where practical
* [ ] Validate AI responses before presentation
* [ ] Handle malformed model output safely
* [ ] Avoid allowing AI output to directly modify tasks or data without user confirmation
* [ ] Generate a final synthesized recommendation
* [ ] Keep the primary briefing concise
* [ ] Allow deeper advisor detail to remain optional
* [ ] Add regression tests around meeting-packet construction and response parsing
* [ ] Keep the architecture understandable and local-first

### Daily Triage and Boardroom Roles

Daily Triage and the AI Boardroom should complement each other rather than duplicate each other.

**Daily Triage:**

* Fast operational recommendation
* What needs attention now
* Useful for frequent day-to-day review

**AI Boardroom:**

* Broader structured review
* Multiple perspectives
* Tradeoffs, risks, allocation, and strategic direction
* Useful when stepping back to reassess priorities

### Terminology

* [ ] Decide the final user-facing name:

  * Boardroom
  * Board Meeting
  * Executive Briefing
  * Daily Briefing
  * The Room

* [ ] Keep terminology consistent across UI, documentation, reports, and buttons

### Final Pre-1.0 UX Pass

* [ ] Review action placement across major screens
* [ ] Confirm destructive actions require deliberate intent
* [ ] Confirm forms preserve drafts where appropriate
* [ ] Confirm navigation does not unexpectedly change the active record
* [ ] Remove or resolve obsolete settings
* [ ] Review default values for a fresh installation
* [ ] Resolve duplicated or inconsistent terminology
* [ ] Ensure the application remains understandable without reading source code

---

## 1.0.0 - Hardening and Trust Release

Version 1.0.0 should not introduce another major feature.

The application should already be functionally complete during 0.9.x. The purpose of 1.0.0 is to prove that the complete system can be trusted.

### Release Validation

* [ ] Run the complete automated regression suite
* [ ] Perform manual smoke testing of all major workflows
* [ ] Test a completely fresh installation
* [ ] Test startup with an existing pre-1.0 database
* [ ] Test every required migration path
* [ ] Confirm migration backups are created and validated correctly
* [ ] Test soft-delete retention behavior
* [ ] Test Recycle Bin restoration
* [ ] Test permanent purge behavior
* [ ] Test user-initiated backup creation
* [ ] Validate documented database recovery procedures
* [ ] Confirm settings persistence and recovery from malformed settings
* [ ] Verify AI features fail safely when Ollama or the configured model is unavailable
* [ ] Resolve known bugs involving data loss, data misdirection, or unintended destructive actions before release

### Documentation

* [ ] Update README installation instructions
* [ ] Document first-run behavior
* [ ] Document database location
* [ ] Document settings storage
* [ ] Document backup creation
* [ ] Document database restoration
* [ ] Document the Recycle Bin and deletion grace period
* [ ] Document Events
* [ ] Document time logging and Time Intelligence
* [ ] Document Daily Triage
* [ ] Document the AI Boardroom
* [ ] Review screenshots and examples for accuracy
* [ ] Finalize CHANGELOG for 1.0.0

### 1.0 Release Rule

Do not release 1.0.0 simply because the planned features exist.

Release 1.0.0 when the existing feature set is stable enough that Boardroom can be trusted as the user's primary local personal operations system.

---

# Post-1.0 Opportunities

These ideas remain valuable, but they are not required to call Boardroom complete.

## Activity Heatmap

Render a GitHub-style activity view from worklog history.

Possible future implementation:

* Count worklog entries or minutes by day
* Render a calendar-style grid
* Highlight productive streaks
* Show detail for selected dates
* Decide whether intensity represents entry count, total minutes, or a configurable metric

## AI Task Extraction from Notes

Allow AI to suggest structured tasks from existing notes.

Possible workflow:

1. Select **Extract Tasks**
2. Send note content to the local model
3. Receive structured task suggestions
4. Review and edit suggestions
5. Explicitly confirm which tasks should be created

Requirements:

* Never create tasks without user confirmation
* Validate titles, priorities, queues, and due dates
* Handle malformed model output safely
* Add parsing and validation tests

## Custom Task Statuses

Consider allowing user-defined task statuses after the 1.0 task lifecycle is proven stable.

Possible examples:

* Blocked
* Waiting
* Dropped
* Deferred

Before implementation, determine how custom statuses affect:

* Sorting
* Filtering
* Completion semantics
* Waiting reasons
* Daily Triage
* AI Boardroom
* Reporting
* Backlog behavior
* Existing database records

## Semantic Search

* Semantic search across notes and worklogs
* Local vector embeddings
* Natural-language questions over recent activity

Example:

> What patterns show up in my last two weeks of notes?

Potential future views:

* 30-day
* 60-day
* 90-day

## Pattern and Trend Analysis

* Identify recurring blockers
* Compare planned priorities with actual time spent
* Detect tasks repeatedly moving between statuses
* Surface queues receiving too much or too little attention
* Identify frequently reopened or revisited work
* Compare Boardroom recommendations with subsequent activity

## Richer Event Features

Possible future additions:

* Recurring events
* Reminder notifications
* External calendar synchronization
* Attendees or invitations
* Month or week calendar views
* More advanced task/event relationships

---

# Completed Foundation

## Board and Settings Reliability

* [x] Preserve the selected Board task across Streamlit reruns
* [x] Separate transient Home navigation from persistent Board selection
* [x] Ensure task notes and time entries are submitted to the displayed task
* [x] Fall back safely when a selected task is excluded by active filters
* [x] Add regression coverage for Board selection behavior
* [x] Move **Save Changes** and **Mark Done** above Task Notes
* [x] Replace mixed live settings with one explicit Settings form
* [x] Preserve unsaved setting drafts across normal reruns
* [x] Apply all setting changes through one **Save Settings** action
* [x] Add a unified **Reset to Defaults** action
* [x] Persist validated settings between application sessions
* [x] Ignore malformed, unknown, and invalid saved setting values
* [x] Save settings atomically
* [x] Keep local settings data out of Git

## Database Compatibility and Migrations

* [x] Add a read-only SQLite database health check
* [x] Track the current SQLite schema version
* [x] Adopt healthy unversioned databases as version 1
* [x] Reject databases created by newer Boardroom versions
* [x] Add an ordered migration runner
* [x] Back up the database before pending migrations
* [x] Add migration fixtures and regression tests
* [x] Roll back failed migrations without advancing the schema version
* [x] Validate database integrity after migrations
* [x] Validate foreign keys after migrations
* [x] Report available and incomplete migration paths

## Existing Task and Note Capabilities

* [x] Create and manage tasks
* [x] Edit task titles and task details
* [x] Support task priority and queues
* [x] Support due dates
* [x] Safely clear due dates
* [x] Support Waiting state and waiting reasons
* [x] Complete tasks
* [x] Add Task Notes / Worklog entries
* [x] Log time through worklogs
* [x] Edit task-note text
* [x] Render task-note Markdown in read-only mode
* [x] Delete task notes through an explicit Edit and confirmation workflow
* [x] Recalculate task time totals after deleting worklog entries
* [x] Update parent task activity after task-note deletion
* [x] Edit standalone notes
* [x] Delete standalone notes

## Home and AI Foundation

* [x] Show overdue tasks on Home
* [x] Show tasks due today
* [x] Show recent notes
* [x] Add AI Daily Triage
* [x] Add basic task staleness context to AI
* [x] Connect Ollama temperature settings
* [x] Connect Ollama response-token settings
* [x] Use `gpt-oss:20b` as the current default model

## Reliability Improvements

* [x] Prevent missing due dates from breaking date sorting
* [x] Validate due dates before storage
* [x] Protect active task selection during Streamlit reruns
* [x] Add regression testing for previously observed navigation and worklog failures
* [x] Add Streamlit UI regression coverage for task-note rendering and deletion workflows
* [x] Establish automated GitHub Actions testing

---

# Planning Principles

When selecting work for a release:

1. Prefer one cohesive theme per patch.
2. Fix anything capable of losing, misdirecting, or unintentionally destroying user data before adding larger features.
3. Add or update tests before considering a feature complete.
4. Keep migrations safe for the existing local database.
5. Create and validate backups before applying pending schema migrations.
6. Prefer reusable infrastructure over one-off implementations when the same concern will affect multiple data types.
7. Avoid introducing a large framework when a small local solution is sufficient.
8. Require explicit confirmation before AI-generated content changes persisted application data.
9. Treat 1.0 scope as a finish line, not an invitation to continually add features.
10. Preserve the manual development workflow: understand, plan, type, test, debug, and reflect.

---

## Guiding Question

Before adding a pre-1.0 feature, ask:

> Does this make Boardroom meaningfully better at tracking what I need to do, understanding what is happening around me, preserving what I have done, showing where my attention is going, deciding what deserves attention next, or protecting the data that makes those answers possible?

If the answer is no, the feature can probably wait until after 1.0.
