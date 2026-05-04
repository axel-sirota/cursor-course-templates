---
description: Activate a persona pack (engineer, designer, pm, data-scientist). Detects client overlay automatically. Installs everything into .cursor/ and .claude/.
---

# Set Persona Command

**When to use:** Run this first — before `/setup-stack`. Re-run at any time to switch personas; the previous install is cleaned first.

---

## Execution Flow

### Step 1: Detect Existing Persona

Read `.cursor/.persona-manifest.json`.

- If the file exists: read `base_files` and `client_files` arrays. Show the user which persona is currently installed and list the files that will be removed. Ask for confirmation before continuing.
- If the file does not exist: proceed directly to Step 2 without prompting.

### Step 2: Detect Client Config

Check whether `client-config/client.md` exists.

- If it exists: read the file and extract the value after the `## Client:` heading. Store this as `active_client`. Print: `"Client config detected: {active_client}"`
- If it does not exist: set `active_client = null`. Continue silently — no error, no warning.

### Step 3: Show Persona Menu

List the subdirectories inside the `personas/` directory dynamically (do not hardcode names). For each subdirectory found, read the first paragraph of its `README.md` to use as the description.

Present the menu like this:

```
Available personas:

1. {name}  — {first paragraph from personas/{name}/README.md}
2. ...

Which persona? (enter number or name)
```

Wait for the user to enter a number or a persona name. Validate the input; if it does not match any discovered subdirectory, print an error and re-prompt.

### Step 4: Remove Previous Persona

If a previous manifest was found in Step 1:

1. For each path listed in `base_files` and `client_files`, delete the file from disk. If a listed file no longer exists, warn: `"Warning: {path} was already removed — skipping."` but continue.
2. Delete `.cursor/.persona-manifest.json` and `.claude/.persona-manifest.json`.
3. Print: `"Previous persona ({name}) removed."`

If no previous manifest existed, skip this step silently.

### Step 5: Copy Base Persona Files

For the selected `{role}`, copy files from `personas/{role}/` to both `.cursor/` and `.claude/`. Before copying any file, check whether the destination already exists AND was NOT listed in the previous manifest. If so, ask the user: "Destination {path} already exists and was not installed by set-persona. Overwrite or abort?" — respect their choice.

If any source file listed below is missing, **abort immediately** and report the missing path. Do not perform a partial install.

| Source path | Destination (.cursor/) | Destination (.claude/) |
|---|---|---|
| `personas/{role}/commands/*.md` | `.cursor/commands/` | `.claude/commands/` |
| `personas/{role}/agents/*.md` | `.cursor/agents/` | `.claude/agents/` |
| `personas/{role}/scripts/*.sh` | `.cursor/scripts/` (chmod +x) | `.claude/scripts/` (chmod +x) |
| `personas/{role}/rules/*.mdc` | `.cursor/rules/` | `.claude/rules/` |
| `personas/{role}/hooks.json` | `.cursor/hooks.json` (verbatim) | `.claude/hooks.json` (paths rewritten — see below) |
| `personas/{role}/mcp.json` | `.cursor/mcp.json` | `.claude/mcp.json` |

**hooks.json path rewriting (Claude side only):**
When writing to `.claude/hooks.json`, replace every occurrence of the string `".cursor/scripts/"` with `".claude/scripts/"` in the JSON content before writing. The `.cursor/hooks.json` receives the file verbatim without any substitution.

Track every destination path written in this step in a list called `base_files`.

### Step 6: Apply Client Overlay (if present)

Check whether `client-config/personas/{role}/` exists. If it does not exist, skip this step silently.

If it exists, apply the following overlays in order:

**mcp.json overlay:**
- If `client-config/personas/{role}/mcp.json` exists, attempt to parse it as JSON.
  - If valid: REPLACE `.cursor/mcp.json` and `.claude/mcp.json` entirely with this file's content (apply the same `.cursor/scripts/` → `.claude/scripts/` path rewriting for the `.claude/` copy). Add both paths to `client_files`.
  - If invalid JSON: warn `"Warning: Client mcp.json failed to parse — using base persona MCP config instead."` and keep the base version.

**rules overlay:**
- If any `*.mdc` files exist in `client-config/personas/{role}/rules/`, copy each one to `.cursor/rules/` and `.claude/rules/`. Prefix each filename with `900-client-` so client rules sort after base rules (e.g., `client-config/personas/{role}/rules/security.mdc` → `.cursor/rules/900-client-security.mdc`). Add all destination paths to `client_files`.

**env.example overlay:**
- If `client-config/personas/{role}/env.example` exists, note its path in the summary output so the student knows to review it. Do NOT copy it to `.cursor/` — `.env.example` lives at the repo root.
- If `client-config/env.example` also exists (top-level), note it in the summary as an additional source for client-specific environment variables.

### Step 7: Update Context Files

Update **both** `.cursor/context.md` and `CLAUDE.md`.

For each file:
- If the file exists, find the `## Active Persona` section and update its value to `{role}`. Find the `## Active Client` section and update its value to `{active_client}`. If either section is missing, add it.
- If `active_client` is null, remove the `## Active Client` section (or set it to `"(none)"`).
- If the file does not exist or contains only a placeholder, create it with:

```markdown
# Project Context

## Active Persona
{role}

## Active Client
{active_client or "(none)"}

## Active Stack
(set by /setup-stack — engineer and data-scientist personas only)
```

### Step 8: Write Manifests

Write the following JSON to **both** `.cursor/.persona-manifest.json` and `.claude/.persona-manifest.json`:

```json
{
  "persona": "{role}",
  "client": "{active_client or null}",
  "installed_at": "{ISO 8601 timestamp}",
  "base_files": [
    ".cursor/commands/...",
    ".claude/commands/...",
    "... all base destination paths from Step 5 ..."
  ],
  "client_files": [
    "... all client overlay destination paths from Step 6, if any ..."
  ]
}
```

`base_files` must list every path written in Step 5. `client_files` must list every path written in Step 6. Both arrays should be flat lists of strings (relative paths from repo root).

### Step 9: Print Confirmation Summary

Print a summary in this format (adapt content to the actual persona and install):

```
✅ Persona active: {role}
   Client overlay: {active_client / "none"}

📋 Commands installed:
   {list of persona-specific commands copied in Step 5}
   + universal commands: /architect /start-session /start-project /code-review /next-session /read

🤖 Agents loaded:
   {list of agent files copied}

🪝 Hooks active:
   afterFileEdit: {script names from hooks.json}
   beforeShellExecution: {script names or "none"}
   stop: {script names or "none"}

🔌 MCP servers configured:
   {list each MCP server name from mcp.json}
   {for each: "no credentials needed" or "requires {VAR_NAME} in .env"}
   {if client overlay was applied: "(client overlay applied)"}

⚠️  Credentials needed before MCPs will work:
   {list env vars not currently set in the shell, with instruction:
    "Copy personas/{role}/.env.example to .env and fill in the values"}
   {if client env.example exists, also note: "Review client-config/personas/{role}/env.example for additional vars"}

➡️  Next step:
   engineer:       Run /setup-stack to choose your tech stack
   designer:       Copy personas/designer/.env.example to .env, set FIGMA_ACCESS_TOKEN
   pm:             Copy personas/pm/.env.example to .env, set Atlassian credentials
   data-scientist: Run /setup-stack python-datascience
```

---

## Error Handling Reference

| Situation | Action |
|---|---|
| Source file missing (e.g. `personas/engineer/mcp.json` not found) | Abort. Report the missing path. Do not write any files. |
| Destination exists and NOT in previous manifest | Ask user: overwrite or abort? Respect their choice. |
| Manifest lists files that no longer exist on disk | Warn per file, continue cleaning the rest. |
| `client-config/` present but `mcp.json` is malformed JSON | Warn, keep base persona MCP config, continue. |
| User enters invalid persona name/number | Print error, re-show the menu. |

---

## Notes for Implementors

- The persona list is always built by reading the `personas/` directory at runtime. Never hardcode persona names.
- The hooks.json path rewriting is the only content transformation applied during install. All other files are copied verbatim.
- Both manifest files (`.cursor/.persona-manifest.json` and `.claude/.persona-manifest.json`) must be written with identical content.
- This command is idempotent: running it twice with the same persona should produce a clean install without duplicate files (Step 4 removes the previous install before Step 5 copies fresh files).
- `setup-stack` must continue to work if no persona has been set (backwards compatibility — do not make persona a hard prerequisite in setup-stack).
