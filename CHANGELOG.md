# Changelog

All notable changes to this project will be documented in this file.

We follow Semantic Versioning (MAJOR.MINOR.PATCH).

---
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