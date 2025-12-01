# Core Methodology: Agentic SDLC

This document defines the **language-agnostic principles** behind the Cursor Master Template. These principles apply whether you are writing Python, Go, TypeScript, or Rust.

## 1. Phase-Based Development
Software is built in distinct layers, not vertical slices.

- **Phase 0 (Skeleton)**: Build the structure first. Mock every endpoint. Verify the "shape" of the API before writing logic.
- **Phase 1+ (Implementation)**: Implement one endpoint at a time.
- **Why?**: Prevents getting stuck in implementation details before the architecture is proven.

## 2. Test-Driven Development (TDD)
Tests are not "quality assurance"; they are **design tools**.

- **The Rule**: You cannot write implementation code until a test fails.
- **The Flow**: Red (Write Test) -> Green (Make it Pass) -> Refactor (Clean up).
- **AI Role**: The AI is excellent at writing tests if you give it the skeleton (Phase 0).

## 3. Session-Based Workflow
Development happens in bounded units called "Sessions".

- **Start**: Load Context -> Define Goal.
- **Execute**: Work on *one* thing.
- **End**: Document what changed -> Update Context.
- **Why?**: Prevents "context drift" where the AI forgets the plan.

## 4. Context-First Architecture
The AI is only as smart as its context.

- **Explicit Context**: We don't rely on the AI guessing the stack. We define it in `.cursor/context.md`.
- **Rule Enforcement**: Rules are injected based on the context.
- **Strictness**: We acknowledge that legacy code requires different rules than new code.

## 5. The "Vibe"
- **Explicit is better than implicit.**
- **Consistency is better than cleverness.**
- **Files are cheap; confusion is expensive.** (Split code into modules).

