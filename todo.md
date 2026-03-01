# TODO LIST:
## Make AI Create Tasks Automatically
Add a button inside each note:
> "Extract tasks from this note"
Flow:
1. Send note body to Ollama
2. Ask it to return a structure list
3. Parse it
4. Insert into SQLite

## Add a Real "Home Dashboard" Layout
Instead of tabs, build a main dashboard with:
- 🔴 Overdue tasks
- 🟡 Due today
- 🟢 Recently completed
- Latest note
- AI "Focus for Today" card

## Add Memory + Semantic Search
Later level:
- Embed your notes locally
- Store vectors
- Ask:
> "What patterns show up in my last 2 weeks of notes?"

Next “ticketing system” upgrades that feel amazing
Once the board is in place, these 3 add the most ConnectWise flavor:
- SLA vibe
- add “age” (created days) and “stale” (updated days)
- highlight stale tickets
- Ticket notes / worklog
- add a worklogs table: ticket_id, note, time_spent, created_at
- Statuses with intent
- New → In Progress → Waiting → Done
- Waiting reason dropdown (Blocked, External, Scheduled)

## AI Boardroom
Create different "experts," each with a defined role and bias.

Potential lineup:
### The Strategist
- Long-term thinking
- Are we aligned with goals?
- Are we working on the right things?

### The Operator
- What should be done today?
- What's blocking execution?
- What's overdue?

### The CFO
- Are we spending time on the highest ROI tasks?
- Is this worth the effort?

### The Wellness Officer
- Are we overloaded?
- Should something be deferred?
- Burnout risk assessment

### The Analyst
- Patterns in notes
- Repeated themes
- Inefficiencies