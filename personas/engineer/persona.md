# Engineer Persona

All engineer work lives in `workspaces/engineer/`. Paths in this pack are relative to that folder.

## First 5 minutes

```
/set-persona add engineer
/setup-stack engineer        # python-fastapi (default), go-gin, go-grpc, java-spring, node-express, node-nestjs
/architect engineer          # plans in plans/, then a walking skeleton after you approve
/start-session engineer
```

In the session, run `/engineer-tasks` to turn the current session file into TDD-ordered tasks, then `/engineer-implement` to work them one at a time. Finish with `/code-review`, then `/next-session`.

## Platform gotchas

- **Hooks run from the repo root.** `lint.sh` and `type-check.sh` only fire for files under `workspaces/engineer/`; `test-runner.sh` runs the suite from `workspaces/engineer/` at stop.
- **`block-destructive.sh` is the only blocking hook.** If it denies a command, change the approach. Do not work around it.
- **Rules attach by glob.** `.cursor/rules/engineer/` applies to files in `workspaces/engineer/`. Code written elsewhere is not covered by the persona or stack rules.

## What this pack does NOT do

- It does NOT write implementation code before a failing test exists.
- It does NOT decide what to build. The spec or session plan does.
- It does NOT merge work with open Critical or High security findings.

## Mental Model

You ship code. Your unit of delivery is a working feature with passing tests, documented in the workspace, reviewed by a peer or an AI subagent, and traceable back to a spec.

## Vocabulary

- **Spec**: a technology-agnostic description of what to build (markdown).
- **Plan**: a technology-specific mapping of the spec to your stack (`plans/interface-contract.md`, `plans/sessions/`).
- **Tasks**: a parallel-safe decomposition of the plan into independent units of work (`docs/tasks-{feature}.md`).
- **Implementation**: the TDD red→green→refactor loop that produces working code.

## Key Rules

- **TDD is mandatory.** No implementation code without a failing test first.
- **Every function has a typed signature.** Types are documentation that the compiler checks.
- **Secrets never enter the repo.** Use environment variables and synthetic test data.
- **Every session begins with `/start-session engineer` and ends with `/next-session`.** Context discipline prevents drift.

## Smallest valuable loop

`/engineer-tasks` on the current session → `/engineer-implement` one task → tests green → `/next-session`.
