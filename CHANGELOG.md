# Changelog

All notable changes to this project will be documented in this file.

We follow Semantic Versioning (MAJOR.MINOR.PATCH).

---
## [0.6.2] - Task Notes and Worklog Maintenance

### Added

* Edit actions for task notes and worklog entries
* Delete actions for task notes and worklog entries
* Confirmation flow before deleting a task note
* Streamlit AppTest regression coverage for rendered task-note interactions
* Regression coverage for task-note deletion and logged-time recalculation

### Improved

* Task notes remain read-only until explicitly placed into Edit mode
* Delete actions are only available while editing a task note
* Canceling a delete confirmation returns the note to Edit mode
* Editing or deleting worklog entries updates the parent task activity timestamp
* Logged-time totals immediately reflect edited or deleted worklog entries
* Board task selection remains stable through task-note edit and delete reruns
* Task-note Save, Cancel, and Delete actions now use evenly stretched button layouts
* Save actions use consistent primary-button styling across Task Notes and standalone Notes

### Fixed

* Task-note edit state now clears correctly after saving changes
* Task-note interaction paths that were not previously exercised by automated tests now have UI regression coverage

---
## [0.6.1] - Board Reliability and Persistent Settings

### Added

- Local JSON persistence for application settings
- Validation and default fallback for saved setting values
- Atomic settings-file replacement to avoid partial writes
- Regression tests for persistent Board task selection
- Tests for settings drafts, validation, saving, loading, and reset behavior

### Improved

- Reworked Settings into one unified form with a single **Save Settings** action
- Added a clear **Reset to Defaults** action
- Settings changes remain drafts until explicitly saved
- Saved settings now survive Streamlit restarts
- Moved **Save Changes** and **Mark Done** above the Task Notes section
- Kept local settings data outside version control

### Fixed

- Adding a task note after navigating from Home could switch the Board to a different task
- Worklog text and time could be submitted against the wrong selected task
- Board task selection could reset during Streamlit reruns
- Settings could require an additional rerun before appearing to take effect

---
## [0.6.0] - Database Safety Foundation

### Added
- Read-only SQLite database health-check command
- SQLite schema version tracking
- Ordered database migration runner
- Automatic validated backups before pending migrations
- Migration fixtures and regression tests
- Migration-path reporting for outdated databases

### Improved
- Application startup now validates database compatibility
- Unversioned databases are safely adopted as schema version 1
- Database integrity and foreign keys are checked after migrations

### Safety
- Databases created by newer unsupported Boardroom versions are rejected
- Failed migrations roll back without advancing the schema version
- Missing migration paths abort before creating changes
---
## [0.5.3] - Compatibility and Stability
### Added
- Centralized due-date parsing, validation, and sorting
- Automated GitHub Actions test workflow
- Tests for due-date behavior, AI configuration, and schema types
- Configurable Ollama response-token limit

### Improved
- Default Ollama model updated to `gpt-oss:20b`
- AI temperature and response-token settings now affect Daily Triage
- Recent Notes limit now controls the Home dashboard
- Virtual-environment launch instructions
- README architecture documentation

### Fixed
- Invalid due dates could break Home and AI task sorting
- Existing due dates could not be cleared
- Queue column was declared as `TEST` instead of `TEXT`
- Unused tab-navigation state
- Inactive AI context-height setting
- Generated coverage data was tracked by Git

## [0.5.2] - Polishing and Architecture Cleanup
### Added
- Home dashboard activity feed
- Note preview system
- Time logging in task notes

### Improved
- AI triage prompt
- Config-driven UI limits
- Priority icon display

### Fixed
- Navigation jump-to-task
- `session_state` bugs

## [0.5.0] - Core Task Workflow
### Added
- Editable task titles
- Task waiting reasons
- Task notes/worklog entries
- Standalone Notes tab
- AI Daily Triage report

## Improved
- Timezone-aware timestamp display
- Dispatcher-style AI triage prompt
- Configurable UI heights via Settings
- Stale task highlighting

## Refined
- Unified terminology from "ticket" to "task"
- Improved board filtering and KPI metrics
- Cleaner prompt structure for AI outputs

## [0.4.0] – Modular PSA Foundation
### Added
- Modular UI structure (`ui/` directory)
- Centralized constants (`core/constants.py`)
- Centralized configuration (`core/config.py`)
- Versioning system (`core/version.py`)
- Sidebar version footer
- Settings tab version display
- Task notes / worklog support
- Age (days since created) column
- Stale (days since last update) column
- Waiting reason support (Blocked, External, Scheduled, Other)

### Changed
- Refactored large `app.py` into modular architecture
- Dynamic tab rendering instead of hardcoded tab tuple
- Unified terminology: "Tickets" → "Tasks"
- Improved board filtering defaults
- Reduced hardcoded values across the application

### Fixed
- Streamlit width parameter misuse
- Missing Optional import
- Schema typo (`udpated_at` → `updated_at`)
- Column visibility logic for empty fields

---

## [0.3.x] – Feature Expansion Phase

### Added
- Task creation via sidebar
- Task status updates
- Priority and queue selection
- AI Daily Triage
- Initial note support on task creation

---

## [0.2.x] – Early Task Board Prototype

### Added
- Basic task model (SQLite)
- Task list rendering
- Status transitions (New → In Progress → Waiting → Done)

---

## [0.1.x] – Initial Prototype

### Added
- Single-file Streamlit dashboard
- SQLite database integration
- Basic AI integration (Ollama)