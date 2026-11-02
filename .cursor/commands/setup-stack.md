---
description: Pick and install the tech stack for one active persona (every persona has at least one stack)
---

# Setup Stack Command

Installs a stack for ONE persona. Every persona has stacks; the list comes from `personas/<role>/persona.yaml` → `stacks`.

```
/setup-stack            # if one persona is active, use it; if several, ask which
/setup-stack <role>     # install a stack for that persona
```

## Execution Flow

### Step 1: Pick the persona

- Read `## Active Personas` from `.cursor/context.md`.
  - Empty or `(none)` → "⚠️ No persona configured. Run `/set-persona` first." Stop.
- If `<role>` was given, it must be in the active list. Otherwise: "`<role>` is not active. Run `/set-persona add <role>` first." Stop.
- If no role was given: one active persona → use it. Several → ask "Which persona is this stack for? {list}".
- If `## Persona: <role>` already has a Stack set → "`<role>` already uses `{stack}`. Run `/undo stack <role>` first to switch." Stop.

### Step 2: Show the stack menu

Read `personas/<role>/persona.yaml` → `stacks`. For each stack, read `stacks/<stack>/context.md` and show the `## Architecture Shape` summary line. The first stack is the default.

```
Stacks for <role>:

  1. <stack>   <Architecture Shape line>   (default)
  2. <stack>   <Architecture Shape line>

Which stack? (number, name, Enter for default, or "new")
```

`new` → ask for a name (lowercase-hyphenated), copy `stacks/blank/` to `stacks/<name>/`, create `rules/`, `templates/`, `vibe/`, `examples/`, and walk the student through filling `context.md` (Architecture Shape, Tech Stack, Key Rules). Then continue with that stack.

Reject a stack that is not in the persona's list: "That stack is not available for <role>. Pick from the list, type `new`, or `cancel`."

### Step 3: Read the Architecture Shape

From `stacks/<stack>/context.md` → `## Architecture Shape`, take the first non-empty line. If missing, ask the user for one sentence describing the shape. Never assume REST.

### Step 4: Reconcile with existing work in the workspace

Look only inside `workspaces/<role>/` (ignore `plans/` and `README.md`).

- Empty → "Clean install." Mode `clean-install`.
- Not empty → summarise what exists (file counts by type, top-level folders), show the stack's `## Key Rules`, and ask:

```
(a) Overwrite: copy templates/examples on top of existing files
(b) Skip templates/examples: install rules and context only
(c) Merge: ask per file (overwrite / skip / rename to <file>.from-stack)
```

### Step 5: Install

Track every path written in `files`.

| Source | Destination | Transformation |
|---|---|---|
| `stacks/<stack>/rules/*.mdc` | `.cursor/rules/<role>/stack-<file>.mdc` | Scope frontmatter to `globs: workspaces/<role>/**`, `alwaysApply: false` (same as /set-persona) |
| `stacks/<stack>/templates/` | `workspaces/<role>/templates/` | per Step 4 mode |
| `stacks/<stack>/examples/` | `workspaces/<role>/examples/` | per Step 4 mode |
| `stacks/<stack>/vibe/` + `stacks/shared/vibe_*.md` | `workspaces/<role>/docs/vibe/` | none |

The `stack-` prefix keeps stack rules apart from the persona's own rules in the same folder.

### Step 6: Update `.cursor/context.md`

In the `## Persona: <role>` block set:

```
Stack: <stack>
Architecture Shape: <shape line>
Active Phase: Phase 0 (Skeleton)
```

Do not touch other persona blocks.

### Step 7: Write the stack manifest

`.cursor/stacks/<role>.manifest.json`:

```json
{
  "persona": "<role>",
  "stack": "<stack>",
  "architecture_shape": "<shape>",
  "installed_at": "<ISO 8601>",
  "reconcile_mode": "clean-install | overwrite | skip-templates | merge",
  "files": ["..."]
}
```

### Step 8: Confirm

```
✅ Stack for <role>: <stack> (<shape>)
   Rules:     .cursor/rules/<role>/stack-*.mdc  (apply to workspaces/<role>/** only)
   Templates: workspaces/<role>/templates/
   Examples:  workspaces/<role>/examples/

Next: /architect <role>
```

Never recommend `/start-session` straight after `/setup-stack`. `/architect` must produce the plan first.

## Error Messages

| Situation | Message |
|---|---|
| No active persona | "⚠️ No persona configured. Run `/set-persona` first." |
| Role not active | "`<role>` is not active. Run `/set-persona add <role>` first." |
| Stack already set | "`<role>` already uses `<stack>`. Run `/undo stack <role>` first." |
| Stack not in persona.yaml | "That stack is not available for <role>. Pick from the list, type `new`, or `cancel`." |
