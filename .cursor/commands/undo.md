---
description: Reverse a persona or stack install. Reads manifests written by /set-persona and /setup-stack to cleanly remove every file they wrote.
---

# Undo Command

**When to use:** You want to try a different persona or stack and need to roll back the previous install cleanly — not just overwrite. Common scenarios: experimenting with different stacks during the course, switching from engineer to data-scientist mid-exercise, or starting over after a misconfiguration.

**What it does:** Reads `.claude/.persona-manifest.json` and/or `.claude/.stack-manifest.json` to find every file the previous install wrote, deletes those files, removes the manifests, and resets the corresponding sections in `CLAUDE.md`. Your application code is never touched — only template/config files the install created.

---

## Execution Flow

### Step 1: Determine What to Undo

Parse the argument:

- `/undo` (no argument) → prompt: `"What would you like to undo? (persona, stack, all, cancel)"` and wait.
- `/undo persona` → undo persona only (see Step 2).
- `/undo stack` → undo stack only (see Step 3).
- `/undo all` → undo stack first, then persona (Step 3, then Step 2).
- `/undo cancel` → stop with no changes.
- Any other value → print `"Unknown argument '{value}'. Valid: persona, stack, all, cancel."` and stop.

### Step 2: Undo Persona

**2a. Find the manifest:**
Read `.claude/.persona-manifest.json`. If it does not exist, respond: `"No persona manifest found — nothing to undo. Is a persona currently set?"` and stop.

**2b. Show what will be removed:**
Parse the manifest. Show the user:
```
About to undo persona: {persona}
  Client overlay: {client or "none"}
  Installed at:  {installed_at}
  Files to remove: {len(base_files) + len(client_files)} total
    {first 5 paths, then "... and N more"}
  CLAUDE.md sections to reset: Active Persona → (none), Active Client → (none)

Proceed? (y/n)
```
Wait for confirmation. If `n` or anything other than `y`/`yes`, stop with no changes.

**2c. Delete files:**
For each path in `base_files` and `client_files`:
- If the file exists, delete it. Print `"removed {path}"`.
- If the file does not exist, print `"warning: {path} already removed — skipping"` but continue.

**2d. Delete the manifests:**
Delete `.claude/.persona-manifest.json` and `.cursor/.persona-manifest.json` (if either exists).

**2e. Reset CLAUDE.md:**
- Find the `## Active Persona` section and set its value to `(none)`.
- Find the `## Active Client` section and set its value to `(none)`.
- Do the same in `.cursor/context.md` if it exists.

**Do NOT** touch `## Active Stack`, `## Architecture Shape`, or `## Active Phase` here — those belong to the stack, not the persona. If `/undo all` is in progress, Step 3 will handle them.

**2f. Print summary:**
```
✅ Persona undone.
   Removed {N} files
   CLAUDE.md: Active Persona reset to (none)

Next: run /set-persona to install a different persona.
```

### Step 3: Undo Stack

**3a. Find the manifest:**
Read `.claude/.stack-manifest.json`. If it does not exist, respond: `"No stack manifest found — nothing to undo. Did setup-stack run successfully?"` and stop.

**3b. Show what will be removed:**
```
About to undo stack: {stack}
  Architecture Shape: {architecture_shape}
  Installed at:       {installed_at}
  Reconcile mode:     {reconcile_mode}
  Files to remove:    {len(files)} total
    {first 5 paths, then "... and N more"}
  CLAUDE.md sections to reset: Active Stack, Architecture Shape, Active Phase

Proceed? (y/n)
```

**WARNING for `reconcile_mode == "merge"`:** in merge mode some files may have been *added alongside* existing user code (e.g. `routes.py.from-stack`). Removing them is safe. But if the user manually edited any of the listed files after install, those edits will be lost. Add this line to the prompt:

```
⚠️  Files installed in 'merge' mode may have been edited by you since install.
    Review the list above carefully before confirming.
```

If `n`, stop.

**3c. Delete files:**
For each path in `files`:
- If the file exists, delete it. Print `"removed {path}"`.
- If the file does not exist, print `"warning: {path} already removed — skipping"`.

**3d. Delete the manifest:**
Delete `.claude/.stack-manifest.json`.

**3e. Reset CLAUDE.md:**
Find each section listed in `claude_md_sections` (typically `Active Stack`, `Architecture Shape`, `Active Phase`) and set values to:
- `## Active Stack` → `(unset)`
- `## Architecture Shape` → `(unset — run /setup-stack)`
- `## Active Phase` → `(unset)`

Do the same in `.cursor/context.md` if it exists.

**Do NOT** touch `## Active Persona` or `## Active Client` here — those belong to the persona.

**3f. Print summary:**
```
✅ Stack undone.
   Removed {N} files
   CLAUDE.md: stack fields reset

Next: run /setup-stack to install a different stack
      (or /undo persona if you also want to clear the persona).
```

### Step 4: After `/undo all`

Once both Step 3 and Step 2 have completed, print:

```
✅ Full undo complete.
   Persona reset to (none)
   Stack reset to (unset)

Next: start fresh with /set-persona.
```

---

## Error Handling

| Situation | Action |
|---|---|
| Manifest file missing | Stop with clear message — there is nothing to undo |
| Manifest file is malformed JSON | Stop. Tell the user to manually remove `.claude/.{persona,stack}-manifest.json` and re-run the install fresh |
| Listed file already deleted | Warn, continue with the rest |
| User answers `n` to confirmation | Stop. Make NO changes |
| CLAUDE.md section not found | Skip silently (the section may have been manually removed) |

---

## What `/undo` does NOT do

- It does NOT delete your application code (anything under `src/`, `app/`, `tests/`, etc.).
- It does NOT delete files you created manually that aren't in the manifest.
- It does NOT touch `plans/`, `docs/`, or other working artifacts.
- It does NOT remove `.git/`, `.env`, or `.env.example`.

The manifests are the source of truth — only files installed by `/set-persona` or `/setup-stack` get removed.

---

## Usage Examples

```
/undo                    # interactive — asks which to undo
/undo persona            # remove the active persona install
/undo stack              # remove the active stack install
/undo all                # both, stack first, then persona
/undo cancel             # no-op (useful in scripts)
```
