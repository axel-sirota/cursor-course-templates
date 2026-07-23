# Fragment Convention — Claude Code 102 Guide

This folder holds the section fragments that Wave-1 authors write and the Wave-2
assembler (`w2-i02`) stitches into `materials/claude-code-102-guide.html`. The
skeleton guide contains one empty `<section>` per section id with a
`FRAGMENT-SLOT` comment inside; the assembler replaces each slot with the
matching fragment's content **verbatim**.

## Fragments stay the source of truth

Fragments REMAIN the maintainable source after assembly. To change a section:
edit its fragment, then re-run the assembler. Never hand-edit the assembled
guide's section bodies — the next assembly run would overwrite your edits.

## File layout

One file per section, named after its section id:

```
materials/fragments/<section-id>.html
```

The 11 section ids, in guide order:

1. `intro`
2. `subagent-architecture`
3. `worktree-isolation`
4. `nested-claude-md`
5. `token-budget`
6. `parallel-implementation`
7. `contract-hooks`
8. `sparse-checkout`
9. `agent-teams`
10. `capstone`
11. `references`

## Fragment format rules

- The file contains ONLY the inner HTML of its `<section>` — no `<html>`,
  `<head>`, or `<body>` tags, and no `<section>` wrapper (the skeleton already
  provides it).
- The FIRST line of the file must be the comment:

  ```html
  <!-- fragment: <section-id> -->
  ```

- Heading levels: `h2` for the section title, `h3` for subsections and labs.
  Lab headings carry ids of the form `lab-*` (e.g. `<h3 id="lab-worktree-setup">`).
- Callouts use the 101 classes exactly: `callout callout-info`,
  `callout callout-tip`, `callout callout-warning`, each with an inner
  `<div class="callout-title">`.
- Mermaid diagrams use `<div class="mermaid">` exactly as in the 101 guide.

## Diagram rule: EXACTLY ONE div per diagram id

Each diagram id gets EXACTLY ONE `<div class="mermaid">`. A "two-panel"
diagram (D9, D10) is ONE div using mermaid `subgraph` blocks for its panels —
never two divs. The assembler counts 12 mermaid divs total across all
fragments: D1–D11 plus the capstone flow.

## Demos vs. labs

- Demos include FULL solutions (commands, code, expected output).
- Labs include NO solutions — only Easy/Hard tier callouts and a
  "You succeeded when…" checklist. Lab solutions live only in instructor
  materials.

## Capture markers

Demo outputs that need a real captured run are marked with a comment:

```html
<!-- CAPTURE: <name> -->
```

`<name>` MUST come from the frozen capture registry below. The Wave-2 verify
run produces exactly these files as `materials/captured/<name>.txt`:

- `demo1-transcript`
- `demo2-worktree-list`
- `demo3-instructions-log`
- `demo4-context-before`
- `demo4-context-after`
- `demo5-activity-tail`
- `demo5-git-graph`
- `demo6-gate-fail`
- `demo6-gate-pass`
- `demo7-du`
- `demo8-team-transcript`

Do not invent new capture names; if a demo needs a capture that is not in the
registry, flag it to the master instead of adding one.
