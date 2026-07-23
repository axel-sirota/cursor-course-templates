---
description: Rebuild context after /clear or /compact — reread in-flight changes and re-trigger service memory
---

# Catchup Command

## Usage
`/catchup`

Run this immediately after `/clear` (or after a `/compact` you did not plan).
Compaction summarizes away detail, and the nested per-service `CLAUDE.md`
files are LOST from context until something re-triggers their lazy load. This
command rebuilds a fresh, accurate picture from the repo itself instead of
trusting a summary.

## Execution Flow

**1. Find what changed**
- Run `git diff main...HEAD --name-only`.
- **Fallback**: if the current branch IS `main` (or the diff is empty), run
  `git status --short` instead and use those paths.

**2. Read the changed files**
- Read every file from step 1 IN FULL. Do not skim from the diff alone — the
  surrounding code is part of the context you are rebuilding.

**3. Re-trigger service memory**
- For each service whose files appear in step 1 (`services/gateway/`,
  `services/payments/`, `services/notifications/`), read that service's
  `CLAUDE.md` if it exists.
- This is the important part: reading the file is what re-loads the nested
  memory that `/compact` dropped.

**4. Summarize the state**
- Produce **at most 10 bullets** covering:
  - What has changed relative to `main`.
  - What appears to be in flight (partial implementations, failing pieces,
    TODOs found while reading).

**5. Declare loaded memory**
- End by listing exactly which memory files are now loaded (root `CLAUDE.md`
  plus each service `CLAUDE.md` read in step 3).
- Tell the user: "Verify with `/context` that these files appear."
