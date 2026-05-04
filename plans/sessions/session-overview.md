# Session Overview — Multi-Persona AI Course Platform

**Source plan:** `plans/architecture.md`
**Total phases:** 10 (A–J)
**Total sessions:** 14

---

## Phase Map

| Phase | Goal | Sessions | Acceptance gate |
|---|---|---|---|
| A | Engineer persona pack | 1–2 | `set-persona engineer` installs all files, hooks parse, mcp parses |
| B | Designer persona pack | 3–4 | `set-persona designer` installs all files, persona switch clean |
| C | PM persona pack | 5–6 | `set-persona pm` installs all files, persona switch clean |
| D | Data Scientist persona pack | 7–8 | `set-persona data-scientist` installs all files, persona switch clean |
| E | `stacks/python-datascience/` | 9 | `setup-stack python-datascience` loads context + rules |
| F | `/set-persona` command | 10 | Full overlay logic: base + client merge, manifest, dual-tool |
| G | 6 universal commands — persona-aware | 11 | Each command branches correctly per Active Persona |
| H–I | `.gitignore` + client-config scaffold | 12 | `client-config/` gitignored; sample structure documented |
| J | Docs update | 13–14 | README, QUICKSTART, METHODOLOGY, student_runbook updated |

---

## Parallel Execution Graph

```
Session 1  (engineer scaffold)
    │
    ├── Session 2  (engineer commands/agents/hooks)  ──┐
    │                                                   │
    ├── Session 3  (designer scaffold)                  │
    │       └── Session 4  (designer commands) ─────────┤
    │                                                   │
    ├── Session 5  (pm scaffold)                        │
    │       └── Session 6  (pm commands) ───────────────┤
    │                                                   │
    ├── Session 7  (ds scaffold)                        │
    │       └── Session 8  (ds commands) ───────────────┤
    │                                                   │
    └── Session 9  (python-datascience stack) ──────────┘
                                                        │
                                              Session 10 (set-persona command)
                                                        │
                                              ┌─────────┴──────────┐
                                         Session 11           Session 12
                                    (universal cmds)      (gitignore+client)
                                              └─────────┬──────────┘
                                                        │
                                                  Session 13 (docs pt1)
                                                        │
                                                  Session 14 (docs pt2)
```

**Maximum parallelism:** Sessions 2, 3→4, 5→6, 7→8, 9 can all run simultaneously after Session 1.
Sessions 11 and 12 can run simultaneously after Session 10.

**Critical path (sequential minimum):** 1 → 2 → 10 → 11 → 13 → 14 (6 sessions)

---

## Session Index

- [Session 1](session-1-phase-A-engineer-scaffold.md) — Engineer persona: scaffold + persona.md + README + SETUP + env
- [Session 2](session-2-phase-A-engineer-commands-agents-hooks.md) — Engineer persona: commands + agents + scripts + hooks.json + mcp.json + rule
- [Session 3](session-3-phase-B-designer-scaffold.md) — Designer persona: scaffold + persona.md + README + SETUP + env
- [Session 4](session-4-phase-B-designer-commands-agents-hooks.md) — Designer persona: commands + agents + scripts + hooks.json + mcp.json + rule
- [Session 5](session-5-phase-C-pm-scaffold.md) — PM persona: scaffold + persona.md + README + SETUP + env
- [Session 6](session-6-phase-C-pm-commands-agents-hooks.md) — PM persona: commands + agents + scripts + hooks.json + mcp.json + rule
- [Session 7](session-7-phase-D-ds-scaffold.md) — Data Scientist persona: scaffold + persona.md + README + SETUP + env
- [Session 8](session-8-phase-D-ds-commands-agents-hooks.md) — Data Scientist persona: commands + agents + scripts + hooks.json + mcp.json + rule
- [Session 9](session-9-phase-E-ds-stack.md) — `stacks/python-datascience/` stack pack
- [Session 10](session-10-phase-F-set-persona-command.md) — `/set-persona` command with client-overlay logic
- [Session 11](session-11-phase-G-universal-commands.md) — 6 universal commands persona-aware branches
- [Session 12](session-12-phase-HI-gitignore-client-scaffold.md) — `.gitignore` + `client-config/` sample structure
- [Session 13](session-13-phase-J-docs-part1.md) — Docs: README + QUICKSTART + METHODOLOGY
- [Session 14](session-14-phase-J-docs-part2.md) — Docs: student_runbook + per-persona SETUP.md review
