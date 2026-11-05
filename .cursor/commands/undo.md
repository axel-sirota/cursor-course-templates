---
description: Reverse a persona or stack install for one persona, using the manifests written by /set-persona and /setup-stack
---

# Undo Command

```
/undo                         # ask what to undo
/undo stack <role>            # remove that persona's stack
/undo persona <role>          # remove that persona (its stack first, if any)
/undo all                     # every stack, then every persona
/undo cancel                  # no-op
```

If `<role>` is omitted and several personas are active, ask which one.

Manifests are the only source of truth. Student work in `workspaces/<role>/` is never deleted.

## Undo stack `<role>`

1. Read `.cursor/stacks/<role>.manifest.json`. Missing → "No stack installed for `<role>`." Stop.
2. Show: stack, Architecture Shape, install date, reconcile mode, file count, first 5 paths. If `reconcile_mode` is `merge` or `overwrite`, warn: "Files under workspaces/<role>/templates and examples may have been edited since install. Review the list." Ask y/n.
3. Delete each path in `files`. Missing → warn, continue.
4. Delete the manifest.
5. In the `## Persona: <role>` block of `.cursor/context.md` set `Stack: (unset, run /setup-stack <role>)`, `Architecture Shape: (unset)`, `Active Phase: (unset)`.
6. Print: "✅ Stack removed for <role>. Next: /setup-stack <role>".

## Undo persona `<role>`

1. If `.cursor/stacks/<role>.manifest.json` exists, run "Undo stack `<role>`" first.
2. Run the remove flow from `/set-persona remove <role>` (files, hook entries, MCP servers with shared-ownership handling, context block, manifest).
3. If `.cursor/.active-session` contains `<role>`, delete it.
4. Print: "✅ Persona <role> removed. workspaces/<role>/ was kept."

## Undo all

For each active persona: undo stack, then undo persona. Then print:

```
✅ Full undo complete. Active Personas: (none)
Next: /set-persona add <role>
```

## Error Handling

| Situation | Action |
|---|---|
| Manifest missing | Stop with a clear message |
| Manifest is invalid JSON | Stop. Tell the user to delete it and remove the files by hand |
| Listed file already gone | Warn, continue |
| User answers anything but y/yes | Stop, change nothing |

## What `/undo` never touches

`workspaces/`, `exercises/`, `personas/`, `stacks/`, `.git/`, `.env`, and any file not listed in a manifest.
