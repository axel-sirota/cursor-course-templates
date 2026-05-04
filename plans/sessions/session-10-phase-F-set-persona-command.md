# Session 10 — Phase F: `/set-persona` Command

**Phase:** F
**Goal:** The single student-facing setup command. Replaces the spec's `setup-persona`. Client-overlay-aware. Writes to both `.cursor/` and `.claude/`.
**Depends on:** Sessions 1–9 (all 4 persona packs must exist to test against)
**Next session:** Session 11 (universal commands persona-aware)

---

## Files to Create

```
.cursor/commands/set-persona.md     ← NEW (replaces setup-persona.md if it exists)
.claude/commands/set-persona.md     ← identical content
```

Note: also add `client-config/` to `.gitignore` in this session (one line).

---

## File Specification

### `.cursor/commands/set-persona.md` (and `.claude/commands/set-persona.md`)

**Purpose:** Activate a persona pack. Detects client overlay automatically. Installs everything into `.cursor/` and `.claude/`.

**When to use:** First command every student runs. Before `setup-stack`. Re-run to switch personas — cleans previous install first.

---

#### Step 1: Detect existing persona

Read `.cursor/.persona-manifest.json`.
- If exists: list every file from `base_files` + `client_files`, ask user to confirm removal.
- If not exists: proceed directly to Step 2.

#### Step 2: Detect client config

Check if `client-config/client.md` exists.
- If yes: read it, extract `## Client:` value, store as `active_client`. Show one-line message: "Client config detected: {active_client}"
- If no: `active_client = null`. Continue silently — no error, no warning.

#### Step 3: Show persona menu

Read `personas/` directory dynamically. For each subdirectory, read its `README.md` first paragraph.

Present menu:
```
Available personas:

1. engineer    — {first paragraph from personas/engineer/README.md}
2. designer    — {first paragraph from personas/designer/README.md}
3. pm          — {first paragraph from personas/pm/README.md}
4. data-scientist — {first paragraph from personas/data-scientist/README.md}

Which persona? (enter number or name)
```

#### Step 4: Remove previous persona

For each path in previous manifest's `base_files` + `client_files`: delete the file.
Delete `.cursor/.persona-manifest.json` and `.claude/.persona-manifest.json`.
Confirm: "Previous persona ({name}) removed."
If no previous manifest: skip silently.

#### Step 5: Copy base persona files

For selected `{role}`, copy from `personas/{role}/`:

| Source | Destination (Cursor) | Destination (Claude) |
|---|---|---|
| `commands/*.md` | `.cursor/commands/` | `.claude/commands/` |
| `agents/*.md` | `.cursor/agents/` | `.claude/agents/` |
| `scripts/*.sh` | `.cursor/scripts/` (chmod +x) | `.claude/scripts/` (chmod +x) |
| `rules/*.mdc` | `.cursor/rules/` | `.claude/rules/` |
| `hooks.json` | `.cursor/hooks.json` (verbatim) | `.claude/hooks.json` (paths rewritten) |
| `mcp.json` | `.cursor/mcp.json` | `.claude/mcp.json` |

**hooks.json path rewriting for Claude side:**
Replace every occurrence of `".cursor/scripts/"` with `".claude/scripts/"` in the JSON content before writing to `.claude/hooks.json`.

Track all destination paths in `base_files` list.

#### Step 6: Apply client overlay (if present)

If `client-config/personas/{role}/` exists:

- **`mcp.json`**: if `client-config/personas/{role}/mcp.json` exists → REPLACE `.cursor/mcp.json` and `.claude/mcp.json` entirely with client version (same path-rewriting for Claude side). Add to `client_files`.
- **`rules/*.mdc`**: if any rule files in `client-config/personas/{role}/rules/` → APPEND (copy alongside, do not replace) to `.cursor/rules/` and `.claude/rules/`. Prefix with `900-client-` to ensure they load after base rules. Add to `client_files`.
- **`.env.example`**: if `client-config/personas/{role}/env.example` exists → replace persona's `.env.example` display reference. (Do not copy to `.cursor/` — `.env.example` stays at repo root for the student. Just note the path in the summary.)

If `client-config/env.example` exists (top-level): note in summary that student should also check this for client-specific vars.

#### Step 7: Update context files

Update `.cursor/context.md` and `CLAUDE.md`:

Find or create `## Active Persona` section → set to `{role}`.
Find or create `## Active Client` section → set to `{active_client}` (or remove section if null).

If context file doesn't exist or is the placeholder, create with:
```markdown
# Project Context

## Active Persona
{role}

## Active Client
{active_client or "(none)"}

## Active Stack
(set by /setup-stack — engineer and data-scientist personas only)
```

#### Step 8: Write manifests

Write to `.cursor/.persona-manifest.json` AND `.claude/.persona-manifest.json`:

```json
{
  "persona": "{role}",
  "client": "{active_client or null}",
  "installed_at": "{ISO timestamp}",
  "base_files": [
    ".cursor/commands/...",
    ".claude/commands/...",
    "... all base files on both sides ..."
  ],
  "client_files": [
    "... client overlay files if any ..."
  ]
}
```

#### Step 9: Print confirmation summary

```
✅ Persona active: {role}
   Client overlay: {active_client / "none"}

📋 Commands installed:
   {list of persona-specific commands}
   + universal commands: /architect /start-session /start-project /code-review /next-session /read

🤖 Agents loaded:
   {list}

🪝 Hooks active:
   afterFileEdit: {scripts}
   beforeShellExecution: {scripts or "none"}
   stop: {scripts}

🔌 MCP servers configured:
   {list — mark each as "no credentials needed" or "requires {VAR_NAME} in .env"}
   {if client overlay applied: "(client overlay applied)"}

⚠️  Credentials needed before MCPs will work:
   {list of env vars that are not set, with instruction to copy .env.example}

➡️  Next step: {persona-specific instruction}
   engineer:        Run /setup-stack to choose your tech stack
   designer:        Copy personas/designer/.env.example to .env, set FIGMA_ACCESS_TOKEN
   pm:              Copy personas/pm/.env.example to .env, set Atlassian credentials
   data-scientist:  Run /setup-stack python-datascience
```

---

#### Error handling

- **Source file missing** (e.g., `personas/engineer/mcp.json` not found): abort, report which file, do not partial-install.
- **Destination file exists and NOT in previous manifest**: ask user — overwrite or abort? (Protects manually customized files.)
- **Manifest lists files that no longer exist on disk**: warn "X files from previous persona already removed", continue cleaning.
- **`client-config/` present but malformed `mcp.json`**: warn "Client mcp.json failed to parse — using base persona MCP config instead", continue with base.

---

## Acceptance Criteria

- [ ] File exists at BOTH `.cursor/commands/set-persona.md` and `.claude/commands/set-persona.md` with identical content
- [ ] Running `/set-persona engineer` (simulated): manifest written, engineer files in `.cursor/` and `.claude/`, hooks paths correct per side
- [ ] Running `/set-persona designer` after engineer: manifest confirms engineer files removed, designer files installed
- [ ] Idempotent: running `/set-persona engineer` twice installs cleanly without duplicates
- [ ] With `client-config/personas/engineer/mcp.json` present: client mcp.json replaces base in both `.cursor/` and `.claude/`
- [ ] Without `client-config/`: runs cleanly with no error or warning about missing client config
- [ ] `client-config/` added to `.gitignore`
- [ ] `.claude/hooks.json` references `.claude/scripts/` not `.cursor/scripts/` after install
