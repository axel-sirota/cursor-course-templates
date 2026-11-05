---
description: Add, remove or list persona packs (engineer, pm, designer, data-scientist, accountant). Several personas can be active at once. Installs into .cursor/.
---

# Set Persona Command

**When to use:** First, before `/setup-stack`. Run it again to add a second persona; nothing already installed is removed.

```
/set-persona                 # show menu, add the chosen persona
/set-persona add <role>      # add a persona
/set-persona remove <role>   # remove one persona (same as /undo persona <role>)
/set-persona list            # show active personas, their stacks and phases
```

The pipeline per persona is: `/set-persona → /setup-stack → /architect → /start-session → /next-session`.

---

## Concepts

| Thing | Where | Purpose |
|---|---|---|
| Persona pack | `personas/<role>/` | Source files. Never edited by this command |
| Persona contract | `personas/<role>/persona.yaml` | Workspace, allowed stacks, in-session commands, quality gate. Every command reads it |
| Workspace | `workspaces/<role>/` | Where this persona's plans, code, data and docs live |
| Installed files | `.cursor/{commands,agents}/`, `.cursor/rules/<role>/`, `.cursor/scripts/<role>/` | What Cursor loads |
| Manifest | `.cursor/personas/<role>.manifest.json` | Every file and config entry this install wrote, used by remove |

---

## Execution Flow (add)

### Step 1: Read current state

- Read `.cursor/context.md` → `## Active Personas` (comma-separated list, or `(none)`).
- List `.cursor/personas/*.manifest.json`.
- If the requested role is already active, say so and stop: "`{role}` is already active. Use `/set-persona remove {role}` first to reinstall."

### Step 2: Show menu (when no role was given)

List the subdirectories of `personas/` at runtime (never hardcode names). For each, read `title` and `summary` from `personas/<role>/persona.yaml`. Mark active ones.

```
Available personas:

1. accountant      Corporate Accountant: Runs reconciliations, flux analysis ...
2. data-scientist  Data Scientist: ...
3. designer        Product Designer: ...   (active)
...

Which persona to add? (number or name)
```

Validate input; re-prompt on an unknown value.

### Step 3: Pre-flight (abort before writing anything)

For the selected `<role>`, verify these exist. If any is missing, abort and report the path:
- `personas/<role>/persona.yaml`, `persona.md`, `README.md`, `hooks.json`, `mcp.json`
- `personas/<role>/commands/`, `agents/`, `rules/`, `scripts/`

Check for collisions with OTHER active personas:
- A file in `personas/<role>/commands/` or `agents/` whose name already exists in `.cursor/commands/` or `.cursor/agents/` and is NOT a universal command. Universal commands are the ones committed to the repo in `.cursor/commands/` (git tracked). Report the clash and abort.
- An MCP server name in `personas/<role>/mcp.json` that already exists in `.cursor/mcp.json` with a DIFFERENT config. Show both and ask: keep existing / replace / abort.

### Step 4: Copy files

Track every path written in `files`.

| Source | Destination | Transformation |
|---|---|---|
| `personas/<role>/commands/*.md` | `.cursor/commands/` | none |
| `personas/<role>/agents/*.md` | `.cursor/agents/` | none |
| `personas/<role>/scripts/*.sh` | `.cursor/scripts/<role>/` | `chmod +x` |
| `personas/<role>/rules/*.mdc` | `.cursor/rules/<role>/` | scope frontmatter (below) |

**Rule scoping.** In each copied `.mdc`, replace the frontmatter keys so the rule attaches only to this persona's workspace:

```yaml
---
description: <keep original>
globs: workspaces/<role>/**
alwaysApply: false
---
```

### Step 5: Merge hooks into `.cursor/hooks.json`

1. Read `.cursor/hooks.json`. If missing, start from `{"version": 1, "hooks": {}}`.
2. For each event in `personas/<role>/hooks.json`, for each entry `{"command": ".cursor/scripts/<name>.sh"}`, append to that event's array:
   ```json
   { "command": ".cursor/scripts/_scope.sh <role> .cursor/scripts/<role>/<name>.sh" }
   ```
3. Record each appended command string in the manifest under `hooks` as `{"event": "...", "command": "..."}`.

`_scope.sh` (committed in the repo) runs an `afterFileEdit` hook only for files under `workspaces/<role>/`, and a `stop` hook only when `.cursor/.active-session` is `<role>`. `beforeShellExecution` hooks always run. Never edit entries that belong to other personas.

### Step 6: Merge MCP servers into `.cursor/mcp.json`

1. Read `.cursor/mcp.json`. If missing, start from `{"mcpServers": {}}`.
2. For each server in `personas/<role>/mcp.json`:
   - Name not present → add it. Record in manifest `mcp_added`.
   - Name present with identical config → leave it. Record in manifest `mcp_shared`.
   - Name present with different config → apply the answer from Step 3.

### Step 7: Create the workspace

Create `workspaces/<role>/` with `plans/sessions/`, `plans/transitions/` and a `README.md`:

```markdown
# <title> workspace

Everything the <role> persona produces lives here: plans, code, data, docs.
Rules in .cursor/rules/<role>/ apply only to files in this folder.
```

Do not overwrite an existing workspace (a student may be re-adding a persona). Record the workspace in the manifest but NOT its contents: remove never deletes student work.

### Step 8: Update `.cursor/context.md`

- Add `<role>` to `## Active Personas` (keep the list comma-separated, alphabetical).
- Append a block if missing:

```markdown
## Persona: <role>
Workspace: workspaces/<role>
Stack: (unset, run /setup-stack <role>)
Architecture Shape: (unset)
Active Phase: (unset)
```

### Step 9: Write the manifest

`.cursor/personas/<role>.manifest.json`:

```json
{
  "persona": "<role>",
  "installed_at": "<ISO 8601>",
  "files": [".cursor/commands/...", ".cursor/agents/...", ".cursor/rules/<role>/...", ".cursor/scripts/<role>/..."],
  "hooks": [{"event": "afterFileEdit", "command": ".cursor/scripts/_scope.sh <role> .cursor/scripts/<role>/lint.sh"}],
  "mcp_added": ["github"],
  "mcp_shared": ["context7"],
  "workspace": "workspaces/<role>"
}
```

### Step 10: Confirm

```
✅ Persona added: <role>   (active: <full list>)

Workspace:  workspaces/<role>/
Commands:   <persona commands installed>
Agents:     <agents installed>
Hooks:      <event: script> (scoped to workspaces/<role>/)
MCP:        <servers added>, shared: <servers shared>
Env vars:   <vars referenced in mcp.json that are not set; "cp personas/<role>/.env.example .env" if one exists>

Next: /setup-stack <role>
```

---

## Execution Flow (remove)

1. Read `.cursor/personas/<role>.manifest.json`. Missing → "`<role>` is not installed." Stop.
2. Show what will be removed (file count, hook entries, MCP servers) and ask for confirmation.
3. Delete every path in `files`. Missing file → warn and continue.
4. Remove from `.cursor/hooks.json` exactly the command strings listed in `hooks`. Drop empty event arrays.
5. Remove each server in `mcp_added` from `.cursor/mcp.json` UNLESS another active persona's manifest lists it in `mcp_added` or `mcp_shared`. In that case move ownership: add it to that persona's `mcp_added`.
6. Delete `.cursor/rules/<role>/` and `.cursor/scripts/<role>/` if empty.
7. Remove `<role>` from `## Active Personas` and delete the `## Persona: <role>` block in `.cursor/context.md`. If a stack manifest exists for this role (`.cursor/stacks/<role>.manifest.json`), run the stack removal from `/undo stack <role>` first.
8. Delete the manifest. Leave `workspaces/<role>/` untouched and say so.

---

## Execution Flow (list)

Read `.cursor/context.md` and print one table:

| Persona | Stack | Architecture Shape | Active Phase | Workspace |
|---|---|---|---|---|

---

## Error Handling

| Situation | Action |
|---|---|
| Source file missing in the pack | Abort before writing. Report the path |
| Command or agent name collides with another persona | Abort. Report both owners |
| MCP server name collides with a different config | Ask: keep existing / replace / abort |
| Manifest lists a file that is already gone | Warn, continue |
| `.cursor/hooks.json` or `.cursor/mcp.json` is invalid JSON | Stop. Ask the user to fix or delete it |

## Notes

- Persona is mandatory. Every other pipeline command stops with "Run `/set-persona add <role>` first" when `## Active Personas` is empty.
- Never hardcode persona names here. Read `personas/` and `persona.yaml`.
- Removing a persona never deletes `workspaces/<role>/`.
