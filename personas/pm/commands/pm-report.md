# /pm-report

**Purpose:** Read current ticket status from the markdown ticket file and generate a stakeholder-ready status update.

Paths are relative to `workspaces/pm/`.

## Steps

1. **Identify the epic**
   - Ask the user for the epic name or ID.
   - Default: the most recently created ticket document in `docs/tickets-*.md`.

2. **Read ticket status**

   **Default (markdown, no MCP needed):**
   - Read `docs/tickets-{epic}.md`.
   - Take each ticket's status from its `Status` field. If a ticket has no status, treat it as Not Started and list it so the user can update the file.
   - For any ticket marked Blocked, read the blocker note in the ticket.

   **Optional, if you configured an Atlassian MCP:**
   - Ask the user whether to pull status from Jira instead of the markdown file.
   - If yes, query the tickets belonging to the named epic and retrieve status and assignee for each.
   - If the MCP call fails, fall back to the markdown file and say so.

3. **Build the status summary**
   Categorize every ticket into one of four states:
   - **Completed**: Done, closed, or accepted.
   - **In Progress**: Actively being worked on.
   - **Blocked**: Cannot proceed; include the blocker reason.
   - **Not Started**: Not yet picked up.

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
