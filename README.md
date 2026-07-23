# AI-Assisted Development Template: The Adaptive SDLC

**One workflow to rule them all.**

This repository is a **Context-Aware Development Environment** for AI Assistants. It defines a rigorous, professional software development lifecycle (SDLC) that adapts to *your* technology stack.

**Works with both Cursor IDE and Claude Code CLI.**

## Course 102 — Parallel Development

Course 102 builds on the 101 workflow and teaches parallel AI-assisted development with Claude Code: delegating work to subagents, isolating them in git worktrees, coordinating several implementation agents against frozen contracts, and running experimental Agent Teams — closing with a capstone where you apply the pattern to your own monorepo. Attendees who took 101 can jump straight in; everyone else starts from the workflow reference listed below.

### Materials map

| Material | What it is |
| :--- | :--- |
| [`materials/claude-code-102-guide.html`](materials/claude-code-102-guide.html) | The student guide — all modules, demos, and labs |
| `materials/instructor/` | Instructor-only materials: lab solutions, demo captures, timing notes |
| [`sample-monorepo/python-fastapi/`](sample-monorepo/python-fastapi/), [`sample-monorepo/node-express/`](sample-monorepo/node-express/) | The practice monorepo in two variants — copy one out of this repo, then run `./init.sh` inside the copy |
| [`student_runbook.md`](student_runbook.md) | The workflow reference for attendees who did not take 101 |

### Session structure (180 minutes)

| Block | Duration |
| :--- | :--- |
| Intro & workflow recap | 15 min |
| Module 1 — Subagents & Worktree Isolation (4 topics, Labs 1–4) | 40 min |
| Module 2 — Parallel Orchestration & Agent Teams (4 topics, Labs 5–8) | 80 min |
| Module 3 — Capstone: Your Monorepo (Lab 9) | 35 min |
| Wrap-up & references | 10 min |

## 🚀 Getting Started

### Using Cursor IDE

1.  **Clone this repo** (or copy the `.cursor` folder to your project).
2.  Open **Cursor**.
3.  Type this in the chat:

    > **`@setup-stack`**

4.  Follow the instructions to configure your project.

### Using Claude Code

1.  **Clone this repo** (or copy the `.claude` folder and `CLAUDE.md` to your project).
2.  Navigate to the directory: `cd cursor-course-templates`
3.  Run: `claude`
4.  Type this in the chat:

    > **/setup-stack**

5.  Follow the instructions to configure your project.

## 🌟 Features

-   **Stack Agnostic**: Comes with Python FastAPI, but supports any language via "Stack Packs".
-   **Context-Aware**: The AI knows your stack, style, and rules. It won't suggest Python code in a Node project.
-   **Phase-Based Development**: A structured workflow from "Architect" to "Implementation".
-   **TDD First**: Baked-in rules for Test-Driven Development.
-   **Brownfield Ready**: Can analyze existing codebases and adapt ("Strictness Levels").

## 📚 Documentation

-   **[Methodology](METHODOLOGY.md)**: The core philosophy (Phase-based, TDD, Agentic).
-   **[Adaptation Guide](ADAPTATION_GUIDE.md)**: How to add new languages or frameworks.
-   **[Python Stack](stacks/python-fastapi/)**: The reference implementation.

## 🛠️ Commands

| Cursor IDE | Claude Code | Description |
| :--- | :--- | :--- |
| **`@setup-stack`** | **`/setup-stack`** | **START HERE.** Configures the project context and rules. |
| **`@start-session`** | **`/start-session`** | Loads the active context for a coding session. |
| **`@research`** | **`/research`** | Performs TDD-style research and planning. |
| **`@architect`** | **`/architect`** | Starts the Phase 0 (Design/Skeleton) workflow. |

## 🏗️ Architecture

```
# For Cursor IDE
.cursor/
  context.md          # The Brain (Defines your stack)
  rules/              # The Guardrails (Active rules)
  commands/           # The Skills (AI Scripts)

# For Claude Code
CLAUDE.md             # The Brain (Project context)
.claude/
  rules/              # The Guardrails (Active rules)
  commands/           # The Skills (AI Scripts)

# Shared (used by both)
stacks/               # The Library
  python-fastapi/     # Reference Stack
  node-express/       # (Add your own!)
```

Both tools use the same workflow and methodology - just different directory names and command prefixes.
