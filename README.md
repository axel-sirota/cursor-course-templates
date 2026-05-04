# AI-Assisted Development Template: The Adaptive SDLC

**One workflow to rule them all.**

This repository is a **Context-Aware Development Environment** for AI Assistants. It defines a rigorous, professional software development lifecycle (SDLC) that adapts to *your* technology stack.

**Works with both Cursor IDE and Claude Code CLI.**

## 🚀 Getting Started

### Using Cursor IDE

1.  **Clone this repo** (or copy the `.cursor` folder to your project).
2.  Open **Cursor**.
3.  Run `@set-persona` and pick your role:
     - `engineer` — if you write code
     - `designer` — if you build prototypes
     - `pm` — if you write product specs
     - `data-scientist` — if you run experiments
4.  (engineer + data-scientist only) Type in the chat:

    > **`@setup-stack`**

5.  Follow the instructions to configure your project.

### Using Claude Code

1.  **Clone this repo** (or copy the `.claude` folder and `CLAUDE.md` to your project).
2.  Navigate to the directory: `cd cursor-course-templates`
3.  Run: `claude`
4.  Run `/set-persona` and pick your role:
     - `engineer` — if you write code
     - `designer` — if you build prototypes
     - `pm` — if you write product specs
     - `data-scientist` — if you run experiments
5.  (engineer + data-scientist only) Type in the chat:

    > **/setup-stack**

6.  Follow the instructions to configure your project.

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

## 🎭 Personas

This repo supports four roles. Run `@set-persona` or `/set-persona` to activate yours.

| Persona | Who it's for | What it installs |
|---|---|---|
| **engineer** | Software developers | TDD commands, code-reviewer + security-auditor agents, lint/type-check hooks, GitHub/Postgres/Playwright MCPs |
| **designer** | UI/UX designers | Figma extract/compose/iterate/handoff commands, token-validator agent, design-token hooks, Figma/Playwright MCPs |
| **pm** | Product managers | PRD validate/decompose/report commands, Three Amigos agents, INVEST/AC-format hooks, Atlassian/Jira MCPs |
| **data-scientist** | Data scientists & ML engineers | EDA/experiment/validate/handoff commands, data-profiler agent, seed/reproducibility hooks, filesystem/context7 MCPs |

Client-specific tool configurations (internal GitHub Enterprise, Jira URLs, data platforms) are injected automatically from `client-config/` if your instructor provided one.

## 🛠️ Commands

| Cursor IDE | Claude Code | Description |
| :--- | :--- | :--- |
| **`@set-persona`** | **`/set-persona`** | **START HERE.** Choose your role. Installs all role-specific tools. |
| **`@setup-stack`** | **`/setup-stack`** | Configures the project context and rules. (engineer + data-scientist only) |
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
