# /pm-decompose

**Purpose:** Break a validated PRD into dependency-ordered tickets ready for the issue tracker.

## Steps

1. **Read inputs**
   - Read the PRD (path provided by user or defaulting to latest in `prds/` or `docs/`).
   - Read the corresponding validation report at `docs/validation-{prd-name}.md`.
   - If no validation report exists, warn the user: "No validation report found. Run `/pm-validate` first."
   - If the user explicitly skips validation, note the override and continue.

2. **Extract user stories**
   - Identify every user story in the PRD (lines or sections starting with "As a…").
   - For each story: extract the title, acceptance criteria (Given/When/Then blocks), and any NFRs or edge cases that belong to it.

3. **Create tickets**
   For each user story, produce a ticket with:
   - **Title:** The full "As a [role], I want [goal] so that [benefit]" statement.
   - **Description:** The story's context paragraph from the PRD.
   - **Acceptance Criteria:** All Given/When/Then blocks for this story, formatted as a checklist.
   - **Edge Cases:** Any edge cases explicitly listed for this story.
   - **Size Estimate:** S / M / L / unknown (use the dev-perspective output if available).
   - **Dependencies:** Which other tickets must be complete before this one can start.

4. **Build the dependency graph**
   - Identify which tickets block which.
   - Verify the graph is acyclic — if a cycle is found, stop and ask the PM to resolve it.
   - Order the ticket list by dependency: tickets with no blockers first.

5. **Write the ticket document**
   Save the ordered ticket list to:
   ```
   docs/tickets-{epic}.md
   ```
   The document includes:
   - An ordered ticket list (each ticket in the format above).
   - A dependency graph section showing which ticket IDs block which.

6. **Optional: create tickets in Jira**
   - If the Atlassian MCP is configured: ask the user "Shall I create these tickets in Jira under epic [epic-name]?"
   - If confirmed: use the Atlassian MCP to create each ticket in the correct order, setting blockers as Jira issue links.
   - If not confirmed or MCP is not available: skip this step silently.

## Constraints

- Ticket titles must always be written from the user perspective ("As a…"). Never "Implement X" or "Add Y to the DB."
- No implementation details in ticket descriptions — describe the user-visible outcome only.
- The dependency graph must be acyclic before outputting.
- Tickets must map 1-to-1 to stories in the PRD — do not merge or split stories without asking the PM first.
