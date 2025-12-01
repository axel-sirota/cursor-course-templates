# Cursor Master Template: The Adaptive SDLC

**One workflow to rule them all.**

This repository is a **Context-Aware Development Environment** for AI Assistants (Cursor). It defines a rigorous, professional software development lifecycle (SDLC) that adapts to *your* technology stack.

## 🚀 Getting Started

1.  **Clone this repo** (or copy the `.cursor` folder to your project).
2.  Open **Cursor**.
3.  Type this in the chat:

    > **`@setup-stack`**

4.  Follow the instructions to configure your project.

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

| Command | Description |
| :--- | :--- |
| **`@setup-stack`** | **START HERE.** Configures the project context and rules. |
| **`@start-session`** | Loads the active context for a coding session. |
| **`@research`** | Performs TDD-style research and planning. |
| **`@architect`** | Starts the Phase 0 (Design/Skeleton) workflow. |

## 🏗️ Architecture

```
.cursor/
  context.md          # The Brain (Defines your stack)
  rules/              # The Guardrails (Active rules)
  commands/           # The Skills (AI Scripts)

stacks/               # The Library
  python-fastapi/     # Reference Stack
  node-express/       # (Add your own!)
```
