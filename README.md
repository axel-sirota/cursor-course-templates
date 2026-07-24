# AI-Assisted Development Template: The Adaptive SDLC

**One workflow to rule them all.**

This repository is a **Context-Aware Development Environment** for AI Assistants. It defines a rigorous, professional software development lifecycle (SDLC) that adapts to *your* technology stack.

**This branch is the Course 102 delivery and targets Claude Code CLI only.** The dual-tool (Cursor + Claude Code) template lives on `main`; the 101 delivery lives on the `salesforce-agentic-ai-coding-101` branch.

## Course 102 — Parallel Development

Course 102 builds on the 101 workflow and teaches parallel AI-assisted development with Claude Code: delegating work to subagents, isolating them in git worktrees, coordinating several implementation agents against frozen contracts, and running experimental Agent Teams — closing with a capstone where you apply the pattern to your own monorepo. Attendees who took 101 can jump straight in; everyone else starts from the workflow reference listed below.

### Repo map — what belongs to which course

| Material | Course | What it is |
| :--- | :--- | :--- |
| [`materials/claude-code-102-guide.html`](materials/claude-code-102-guide.html) | **102** | The student guide — all modules, demos, and labs |
| `materials/fragments/` | **102** | The guide's per-section source files (edit these, then re-assemble) |
| `materials/captured/` | **102** | Real terminal captures pasted into the guide's demos |
| `materials/instructor/` | **102** | Instructor-only: the instructor guide, lab solutions, review report |
| [`sample-monorepo/python-fastapi/`](sample-monorepo/python-fastapi/), [`sample-monorepo/node-express/`](sample-monorepo/node-express/) | **102** | The practice monorepo in two variants — copy one out of this repo, then run `./init.sh` inside the copy |
| [`CLAUDE_CODE_BUILD_PROMPT.md`](CLAUDE_CODE_BUILD_PROMPT.md) | **102** | How these materials are built (regenerability notes) |
| [`materials/claude-code-guide.html`](materials/claude-code-guide.html) | 101 (prerequisite) | The 101 guide — 102's references link to it |
| [`student_runbook.md`](student_runbook.md) | 101 (prerequisite) | The workflow reference for attendees who did not take 101 |
| `.claude/commands/`, [`stacks/`](stacks/) | 101 (used by 102) | The 101 workflow commands (`/setup-stack`, `/detect-stack`, …) — the 102 capstone runs them |
| [`METHODOLOGY.md`](METHODOLOGY.md), [`ADAPTATION_GUIDE.md`](ADAPTATION_GUIDE.md) | 101 | Core philosophy and stack-adaptation docs |

### Session structure (180 minutes)

| Block | Duration |
| :--- | :--- |
| Intro & workflow recap | 15 min |
| Module 1 — Subagents & Worktree Isolation (4 topics, Labs 1–4) | 40 min |
| Module 2 — Parallel Orchestration & Agent Teams (4 topics, Labs 5–8) | 80 min |
| Module 3 — Capstone: Your Monorepo (Lab 9) | 35 min |
| Wrap-up & references | 10 min |

## 🚀 Getting Started (Claude Code)

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

| Claude Code | Description |
| :--- | :--- |
| **`/setup-stack`** | **START HERE.** Configures the project context and rules. |
| **`/start-session`** | Loads the active context for a coding session. |
| **`/research`** | Performs TDD-style research and planning. |
| **`/architect`** | Starts the Phase 0 (Design/Skeleton) workflow. |

## 🏗️ Architecture

```
CLAUDE.md             # The Brain (Project context)
.claude/
  rules/              # The Guardrails (Active rules)
  commands/           # The Skills (AI Scripts)

stacks/               # The Library
  python-fastapi/     # Reference Stack
  node-express/       # (Add your own!)
```
