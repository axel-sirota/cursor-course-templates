---
description: Render all DIAGRAM_PLACEHOLDER comments in materials/*.html into SVG files in materials/diagrams/ using mmdc
---

Build diagrams for: $ARGUMENTS

## What this command does

Scans all HTML files in `materials/` for `<!-- DIAGRAM_PLACEHOLDER: filename.svg` comments, extracts the Mermaid source from each, renders it to an SVG using `mmdc`, and writes the SVG to `materials/diagrams/`.

The HTML files already contain `<img src="diagrams/xxx.svg">` placeholder tags. After this command runs, those images will resolve.

---

## Step 1: Find all placeholders

```bash
grep -n "DIAGRAM_PLACEHOLDER" materials/*.html
```

Print the full list:
```
Diagrams to render:
1. materials/cursor-guide.html → cursor_guide_dN.svg — [description]
2. materials/cursor-basics.html → cursor_basics_dN.svg — [description]
...
```

If $ARGUMENTS is a specific filename (e.g. `cursor-guide`), only process that file.

---

## Step 2: For each placeholder

Read the HTML file. Extract each `<!-- DIAGRAM_PLACEHOLDER: <filename> ... -->` block. The format is:

```html
<!-- DIAGRAM_PLACEHOLDER: cursor_guide_dN.svg
flowchart TB
    A[Node A] --> B[Node B]
-->
```

### 2a. Write the Mermaid source to a temp file

```bash
cat > /tmp/diagram_tmp.mmd << 'MERMAID'
<mermaid source here>
MERMAID
```

### 2b. Render with mmdc

```bash
mmdc -i /tmp/diagram_tmp.mmd -o materials/diagrams/<filename> -b transparent --width 900
```

If mmdc fails, show the error and skip to the next diagram (do not abort).

### 2c. Verify the SVG was written

```bash
ls -la materials/diagrams/<filename>
```

### 2d. Report result

```
✅ Rendered: materials/diagrams/<filename> (from <html-file> line <N>)
```

---

## Step 3: Summary

After all diagrams are processed:

```
## Build Diagrams — Summary

Rendered: N diagrams
Skipped: M (list any that failed with reason)

Files written to materials/diagrams/:
- cursor_guide_dN.svg
- ...

Next: open the HTML files in a browser to verify diagrams display correctly.
```

---

## Diagram design rules (when GENERATING new mermaid source)

- Keep diagrams focused: one concept per diagram
- Use `flowchart TB` for top-down flows (onboarding, pipelines)
- Use `flowchart LR` for left-right decision trees and command flows
- Use `sequenceDiagram` for request/response or tool interaction sequences
- Max ~10 nodes — if more, split into two diagrams
- Node labels: short phrases, plain ASCII, no em dashes
- Color key: `style NodeName fill:#3f51b5,color:#fff` for primary; `fill:#2e7d32,color:#fff` for success; `fill:#6a1b9a,color:#fff` for output

---

## Running non-interactively

If $ARGUMENTS is `all` or empty, render every placeholder in every materials/*.html file in one pass without asking for approval between each.
