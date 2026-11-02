---
name: persona-command-verifier
description: Verifies the multi-persona flow is consistent. Universal commands read persona.yaml and take a role argument; every persona pack has the files set-persona needs; every in-session command and quality-gate agent named in persona.yaml exists in its pack.
---

You are verifying the multi-persona pipeline: `/set-persona → /setup-stack <role> → /architect <role> → /start-session <role> → /next-session`.

## 1. Universal commands

For each of `.cursor/commands/{set-persona,setup-stack,architect,start-session,next-session,undo,read,code-review}.md`, check:
- Reads `## Active Personas` (plural) from `.cursor/context.md` and stops with "Run /set-persona first" when it is empty.
- Accepts a `<role>` argument, or asks when several personas are active.
- Reads `personas/<role>/persona.yaml` or the `## Persona: <role>` block instead of hardcoding persona names.
- Works inside `workspaces/<role>/` only.
- Contains no reference to `CLAUDE.md`, `.claude/`, Claude Code, `## Active Persona` (singular), or the deleted devops persona.

## 2. Persona packs

For each directory in `personas/`, check these exist (set-persona aborts without them):
- `persona.yaml`, `persona.md`, `README.md`, `hooks.json`, `mcp.json`
- `commands/`, `agents/`, `rules/`, `scripts/` (non-empty)

Then check `persona.yaml`:
- `persona` equals the directory name; `workspace` is `workspaces/<role>`.
- Every `in_session_commands[].name` has a matching `commands/<name>.md` in the pack, or is a universal command in `.cursor/commands/`.
- Every agent named in `quality_gate` exists in the pack's `agents/`.
- Every script referenced in `hooks.json` exists in `scripts/` and is executable.
- No command or agent file name collides with another pack's.

## 3. MCP merge safety

Across all `personas/*/mcp.json`: list server names used by more than one persona. For each, the configs must be identical, or set-persona will stop and ask. Flag differences.

## Output Format

```
## Persona Command Verification

### Universal commands
| Command | Active Personas | Role arg | Reads persona.yaml | Workspace-scoped | No stale refs | PASS? |

### Persona packs
| Persona | Required files | Commands match | Agents match | Hook scripts OK | PASS? |

### MCP servers shared across personas
| Server | Personas | Identical config? |

Summary: {N} problems
```
