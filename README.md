# Cursor SDD course: multi-persona edition

A Cursor workspace that teaches spec-driven development to five roles: engineer, product manager, designer, data scientist and accountant. Each role gets its own commands, agents, rules, hooks and stack. Several roles can be active in the same repo at once.

All exercises use synthetic data. No company systems, tools or documents are needed.

## The flow (per persona)

```
/set-persona add <role>   install the persona pack (repeat to add more roles)
/setup-stack <role>       pick the stack for that role
/architect <role>         plan: interface contract + session files, then a skeleton after you approve
/start-session <role>     load rules and plan, agree the goal
  ...in-session commands for that role...
/next-session             quality gate + handoff doc
```

`/read` shows every active persona and its next step. `/undo` reverses any install.

## Personas and stacks

| Persona | Stacks | Architecture Shape |
|---|---|---|
| engineer | python-fastapi, go-gin, go-grpc, java-spring, node-express, node-nestjs | REST API / gRPC Service |
| pm | pm-prd-markdown | PRD Workspace |
| designer | designer-react-tokens | Design System |
| data-scientist | python-datascience, python-mlops, python-spark, python-dbt-snowflake, r-tidyverse | Experiment Notebook / Data Pipeline / Analytics Model / Statistical Computing |
| accountant | python-accounting | Close Workbook |

## How several personas share one repo

| Piece | Location | Why |
|---|---|---|
| Persona contract | `personas/<role>/persona.yaml` | Workspace, stacks, in-session commands, quality gate. Every command reads it |
| Work | `workspaces/<role>/` | Plans, code, data and docs for that role only |
| Rules | `.cursor/rules/<role>/` | Scoped by glob to `workspaces/<role>/**`, so a PM's rules never fire on engineering code |
| Hooks | `.cursor/hooks.json` through `.cursor/scripts/_scope.sh` | Edit hooks run only for that role's files. Stop hooks run only for the role whose session is open |
| Install record | `.cursor/personas/<role>.manifest.json`, `.cursor/stacks/<role>.manifest.json` | Lets `/undo` remove one role cleanly |
| Project state | `.cursor/context.md` | Active personas, and per persona: stack, shape, phase |

## Repo layout

```
.cursor/        commands, agents, scope wrapper, context (Cursor reads this)
personas/       persona packs (source)
stacks/         stack packs (source)
exercises/      per-persona exercises on synthetic data
workspaces/     created by /set-persona; where students work
materials/      course slides and diagrams
METHODOLOGY.md  phase + TDD principles
```

Start with `QUICKSTART.md`.
