# /pm-report

**Purpose:** Pull current status from the issue tracker and generate a stakeholder-ready status update.

## Steps

1. **Identify the epic**
   - Ask the user for the epic name or ID.
   - Default: the most recently created ticket document in `docs/tickets-*.md`.

2. **Query the issue tracker**

   **If Jira (Atlassian MCP) is configured:**
   - Query the active sprint for tickets belonging to the named epic.
   - Retrieve status (To Do / In Progress / In Review / Done / Blocked) and assignee for each ticket.
   - For any ticket with status Blocked, retrieve the blocker description.

   **If GitHub Issues is configured:**
   - Query open and closed issues with the epic label.
   - Map GitHub labels to statuses: `open` → In Progress or Not Started; `closed` → Done; `blocked` label → Blocked.

   **If neither is configured:**
   - Warn the user: "No issue tracker MCP is configured. Add Atlassian or GitHub Issues credentials to `.env` and restart."
   - Stop.

3. **Build the status summary**
   Categorize every ticket into one of four states:
   - **Completed** — Done, closed, or accepted.
   - **In Progress** — Actively being worked on.
   - **Blocked** — Cannot proceed; include the blocker reason.
   - **Not Started** — Not yet picked up.

4. **Generate the report**
   Save to:
   ```
   docs/status-{YYYY-MM-DD}-{epic}.md
   ```

   The report includes:
   - **Executive Summary** (3–5 sentences): overall progress, top risk, next milestone date.
   - **Story-by-Story Status** table: Ticket ID | Title | Status | Owner | Blocker (if any).
   - **Risks** section: any Blocked tickets with root cause and suggested unblock action.
   - **Next Milestone** section: what must complete in the next sprint and by when.

## Output

A stakeholder-ready status document at `docs/status-{YYYY-MM-DD}-{epic}.md` suitable for sharing with leadership without editing.
