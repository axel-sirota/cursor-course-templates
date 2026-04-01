# Cursor Course Restructure Plan

**Date**: 2026-04-01
**Status**: Validated through 3-cycle TDD plan

---

## Problem Statement

The current `cursor-guide.html` has critical issues:

1. **46 instances of wrong command syntax**: Uses `@command` when Cursor uses `/command` for invocation (`@` is for context symbols only)
2. **Outdated terminology**: Uses "Schema-Driven Development" instead of the industry-standard "Spec-Driven Development" (ThoughtWorks 2025)
3. **No structured labs**: Content is reference-style, not lab-driven
4. **No prerequisites file**: Assumes Cursor knowledge without teaching basics
5. **Missing MCP section**: No coverage of Model Context Protocol
6. **Freeform structure**: No pedagogical progression

## Architecture Decisions

### Decision 1: Two-file course structure
- `cursor-basics.html` — Prereq: Cursor IDE mechanics (Tab, Cmd+K, Chat, Agent, @ context)
- `cursor-guide.html` — Main course: The Agentic SDLC methodology with 5 labs

**Rationale**: Separating "how to use Cursor" from "how to do AI-assisted development" lets instructors skip basics for experienced students.

### Decision 2: Rename SDD → Spec-Driven Development (Spec-First Pattern)
- Industry term from ThoughtWorks Technology Radar 2025
- Our approach is the "Spec-First" pattern (lightest form): API contract → skeleton → TDD
- NOT full SDD (we don't have executable specs that fail builds)
- Sources:
  - [ThoughtWorks SDD](https://www.thoughtworks.com/en-us/insights/blog/agile-engineering-practices/spec-driven-development-unpacking-2025-new-engineering-practices)
  - [Augment Code Guide](https://www.augmentcode.com/guides/what-is-spec-driven-development)

### Decision 3: Fix all `@command` → `/command`
- Per [Cursor Docs](https://cursor.com/docs/context/commands):
  - `/command-name` = **invokes** the command (executes it)
  - `@symbol` = **attaches context** (files, folders, codebase, web)
- The `@` prefix for commands is WRONG for invocation

### Decision 4: Lab-driven pedagogy
- 5 sequential labs, each building on the previous
- Each lab: ~15-20 min, clear objective, concrete deliverable
- Progressive build: Setup → Architect → TDD → Review → MCP

---

## Course Structure

### File 1: cursor-basics.html (NEW — ~30 min prereq)

```
Section 1: What is Cursor?
  - VS Code fork with native AI
  - Comparison table: Traditional IDE vs Cursor
  - Mermaid: Cursor architecture overview

Section 2: The 4 AI Interfaces
  - Tab Completion (inline predictions)
  - Inline Edit (Cmd+K)
  - Chat Panel (Cmd+L — Q&A)
  - Agent/Composer (Cmd+I — multi-file orchestration)
  - Mermaid: Decision tree — which interface for which task
  - Table: Shortcuts reference

Section 3: The Context System
  - @ symbols: @file, @folder, @codebase, @web, @docs, @git
  - How context flows to the LLM
  - Mermaid: Context assembly pipeline

Section 4: Quick Exercise
  - Open a project in Cursor
  - Use Tab completion to write a function
  - Use Cmd+K to refactor it
  - Use Chat to ask about it
  - Use Agent to add tests
```

### File 2: cursor-guide.html (REWRITE — ~2.5 hour main course)

```
Section 1: Introduction & Philosophy (10 min)
  - The Agentic Engineering Philosophy
  - "AI is context-hungry" — why structure matters
  - Course roadmap diagram
  - Mermaid: Traditional ad-hoc vs Structured agentic workflow

Section 2: The Workflow — Spec-Driven Development (25 min + Lab 1)
  - What is Spec-Driven Development? (industry context)
  - The three SDD patterns: Spec-First, Spec-Anchored, Spec-as-Source
  - Our approach: Spec-First Pattern
    - Design API contract FIRST (/architect)
    - Build skeleton with mocks (Phase 0)
    - Implement with TDD (Phase 1+)
  - How SDD + TDD complement each other
    - SDD = architectural contracts (what to build)
    - TDD = implementation verification (how to build)
  - Phase-Based Development explained
  - Session-Based Workflow explained
  - Mermaid diagrams (4):
    1. SDD landscape: 3 patterns comparison
    2. Our Spec-First flow: architect → skeleton → TDD
    3. Phase lifecycle: Phase 0 → Phase 1+ → Done
    4. Session workflow: start → execute → transition

  LAB 1: "Setup & Architect" (15 min)
    Objective: Configure a stack and produce an API spec + skeleton
    Steps:
    1. Clone template, open in Cursor
    2. Run /setup-stack → select python-fastapi
    3. Run /architect "Build a task management API with users and tasks"
    4. Inspect: context.md, rules/, skeleton files, session plans
    Deliverable: Running skeleton with mock endpoints
    Checkpoint: curl localhost:8000/docs shows all endpoints

Section 3: Skills — Slash Commands (20 min + Lab 2)
  - What are commands? (markdown files → injected into context)
  - / invocation vs @ context attachment
  - Where commands live: .cursor/commands/*.md
  - Command anatomy: frontmatter + markdown body
  - The command chain: /setup-stack → /architect → /start-session → /code-review → /next-session
  - How commands save tokens (pre-written prompts vs typing every time)
  - Mermaid diagrams (3):
    1. Command execution: user types / → loads .md → injects into prompt
    2. Sequence diagram: /start-session lifecycle
    3. The full command chain pipeline

  LAB 2: "The Command Chain" (15 min)
    Objective: Execute the full development lifecycle using commands
    Steps:
    1. Run /start-session → observe context loading
    2. Set session goal: "Implement POST /tasks"
    3. Observe: AI reads rules, follows TDD, creates files
    4. Run /code-review → observe audit output
    5. Run /next-session → observe transition summary
    Deliverable: Implemented endpoint with review and transition doc

Section 4: Rules System (20 min + Lab 3)
  - What are rules? (.mdc files with YAML frontmatter)
  - The 4 rule types:
    1. Always Apply (alwaysApply: true)
    2. Auto-Attached (globs: ["*.py"])
    3. Agent-Requested (description-based)
    4. Manual (@rule-name in chat)
  - Rule precedence: Team > Project > User
  - How rules enforce Spec-Driven Development:
    - 000-core-workflow.mdc: Enforces phase-based development
    - 400-testing-first.mdc: Enforces TDD
    - 100-architect-phase.mdc: Enforces spec-first design
  - How rules save tokens (context injection vs repetitive prompts)
  - Composable rules: many small > one monolithic
  - Real example: walking through 000-core-workflow.mdc
  - Mermaid diagrams (3):
    1. Rule loading decision tree
    2. Rule composition: multiple rules → combined context
    3. How rules enforce SDD phases

  LAB 3: "Rules in Action" (15 min)
    Objective: See rules enforcement and create a custom rule
    Steps:
    1. Inspect .cursor/rules/ — read 000-core-workflow.mdc
    2. Try to skip TDD: ask AI to "just implement GET /tasks without tests"
    3. Observe: AI refuses or follows TDD anyway (rule enforcement)
    4. Create a new rule: .cursor/rules/custom-logging.mdc
       - alwaysApply: true
       - "All endpoints must include structured logging"
    5. Run /start-session → implement GET /tasks
    6. Observe: AI adds logging to the endpoint
    Deliverable: Custom rule + endpoint that follows both TDD and logging rules

Section 5: TDD in Practice (20 min + Lab 4)
  - Red → Green → Refactor cycle (detailed)
  - How rules enforce TDD (the golden rule: no code without failing test)
  - TDD at each phase:
    - Phase 0: E2E tests against mocks (verify API shape)
    - Phase 1+: E2E tests with real assertions (verify logic)
  - Concrete code walkthrough: POST /tasks implementation
  - Mermaid diagrams (3):
    1. TDD cycle: Red → Green → Refactor (detailed with actions)
    2. Phase 0 → Phase 1 transition: mock tests → real tests
    3. Complete SDD+TDD flow from architect to done

  LAB 4: "Full TDD Cycle" (20 min)
    Objective: Implement an endpoint using strict TDD
    Steps:
    1. Run /start-session → "Implement PUT /tasks/{id}"
    2. Step 1 RED: Write failing test first
       - Test: PUT /tasks/1 with new title → assert 200 + updated
    3. Step 2 GREEN: Implement endpoint to pass test
       - Service layer, repository, model updates
    4. Step 3 REFACTOR: Extract validation, clean up
    5. Run tests: verify all pass
    6. Run /code-review
    Deliverable: PUT endpoint with test, service, and passing review

Section 6: MCP Servers (15 min + Lab 5)
  - What is Model Context Protocol?
  - How MCP extends Cursor's capabilities
  - Configuration: .cursor/mcp.json (project) or ~/.cursor/mcp.json (global)
  - Server types: stdio, HTTP
  - Popular MCP servers: filesystem, GitHub, database, fetch
  - Mermaid diagrams (2):
    1. MCP architecture: Cursor ↔ MCP Server ↔ External Tool
    2. Configuration flow: mcp.json → server startup → tool availability

  LAB 5: "Connect an MCP Server" (15 min)
    Objective: Add an MCP server and use it in development
    Steps:
    1. Create .cursor/mcp.json with a fetch MCP server
    2. Restart Cursor
    3. In Agent: "Use the fetch tool to check if our API returns valid JSON"
    4. Observe: Agent uses MCP tool to make real HTTP requests
    Deliverable: Working MCP integration

Section 7: Hooks (15 min — if time permits)
  - Lifecycle events overview
  - hooks.json format
  - Hook types: command vs prompt
  - Exit codes: 0 (proceed), 2 (block)
  - Practical examples:
    - Auto-format on file edit
    - Block dangerous shell commands
  - Mermaid diagram: Hook execution sequence
```

---

## Mermaid Diagram Inventory

Total: ~20 diagrams across both files

### cursor-basics.html (4 diagrams)
1. Cursor architecture overview (flowchart)
2. AI interface decision tree (flowchart)
3. Context assembly pipeline (flowchart LR)
4. @ symbol types (flowchart)

### cursor-guide.html (16 diagrams)
1. Traditional vs Agentic workflow (flowchart)
2. Course roadmap (flowchart TB)
3. SDD landscape: 3 patterns (flowchart LR)
4. Spec-First flow: architect → skeleton → TDD (flowchart LR)
5. Phase lifecycle (flowchart TB)
6. Session workflow (flowchart LR)
7. Command execution flow (flowchart)
8. /start-session sequence (sequenceDiagram)
9. Full command chain (flowchart LR)
10. Rule loading decision tree (flowchart TD)
11. Rule composition (flowchart)
12. Rules enforcing SDD phases (flowchart TB)
13. TDD cycle detailed (flowchart TB with subgraphs)
14. Phase 0 → Phase 1 transition (flowchart)
15. MCP architecture (flowchart LR)
16. Hook execution sequence (sequenceDiagram)

---

## Files to Create/Modify

| File | Action | Description |
|------|--------|-------------|
| `materials/cursor-basics.html` | CREATE | New prereq file (~800 lines) |
| `materials/cursor-guide.html` | REWRITE | Complete rewrite (~2800 lines) |

## Mermaid Syntax Rules (validated)

- Wrap node text with special chars in `"double quotes"`
- Never use lowercase `end` as a node name (use `End` or `END`)
- Inside `<div class="mermaid">`: use plain text, NOT HTML entities
- Use `<br/>` for line breaks in node text (works with htmlLabels: true)
- Avoid `&` in mermaid blocks — use `and` or `+` instead
- Test: Every mermaid block must be valid standalone

## Success Criteria

1. All 46 `@command` references replaced with `/command`
2. "Schema-Driven Development" replaced with "Spec-Driven Development"
3. All 5 labs have clear objectives, steps, and deliverables
4. All ~20 mermaid diagrams render correctly
5. cursor-basics.html covers Cursor fundamentals
6. Pedagogical flow: Basics → Workflow/SDD → Skills → Rules → TDD → MCP → Hooks
7. Same visual style as existing (Pico.css + Mermaid + Prism)

## Risks & Mitigations

| Risk | Mitigation |
|------|-----------|
| Mermaid diagrams break in HTML | Use plain text inside mermaid blocks, test with htmlLabels: true |
| Labs too long for tight schedule | Each lab capped at 15-20 min with clear checkpoint |
| Students fail Lab 1, stuck for rest | Add "Checkpoint" notes with expected state |
| SDD terminology confusion | Clearly explain "Spec-First Pattern" as our lighter approach |
| Commands vs Skills confusion | Teach "commands" (what we use) and note Skills evolution |

## Next Steps

1. Create `cursor-basics.html` (new file)
2. Rewrite `cursor-guide.html` section by section
3. Validate all mermaid diagrams render
4. Final review pass for consistency
