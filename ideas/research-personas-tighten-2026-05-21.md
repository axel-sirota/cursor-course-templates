# Research — Tighten Non-Engineer Personas (Designer, PM, Data Scientist)

**Date:** 2026-05-21
**Branch:** `feat/improve_personnas`
**Protocol:** `/research` — 5 cycles, web search ON, foreground
**Scope:** Designer, PM, Data Scientist (existing packs). L&D / HR descoped.
**Status:** Findings only — no files modified during research.

---

## 1. Executive Summary

**Tighten the three non-engineer personas by restructuring `persona.md` to lead with a "Smallest Valuable Loop" — one entry command, one expected output, one platform gotcha — before any abstract workflow phases.** Do not add new commands. The dominant failure mode is documentation that explains the *shape* of work (phases, rules, vocab) before the user has felt the loop close once.

**Top 3 recommendations per persona:**

### Designer
1. Open `persona.md` with: "Paste a Figma frame URL into Claude Code → run `/designer-extract` → expect `docs/figma-context-{frame}.md` with tokens + components."
2. Move the Figma desktop app requirement *into* `persona.md` (not just `SETUP.md`) — it's a fail-fast precondition, not an install step.
3. State the platform gotcha explicitly: "Roundtrip to Figma loses business logic — visual layers only."

### PM
1. Open `persona.md` with a three-fork entry: *I have raw notes / I have a PRD / I have a validated PRD* → which command goes with which.
2. State the file-first mental model: "PRDs live in `prds/*.md`. Jira sync is a push step, not your editor."
3. Position relative to Anthropic's official PM plugin: ours is the *teaching* subset focused on validate → decompose. Students who graduate can adopt the full plugin.

### Data Scientist
1. Open `persona.md` with the side-by-side pattern: "Open Claude Code in one pane, JupyterLab in the other. Claude edits `.ipynb` and `.py`; you re-run cells."
2. State the platform gotcha explicitly: "Claude Code is file-level. It does NOT see your live kernel state or in-memory DataFrames. Always re-run notebooks top-to-bottom before handoff."
3. Smallest valuable loop: "Drop a CSV in `data/`, run `/ds-explore`, expect a profile report in `docs/eda/`."

---

## 2. Key Findings per Persona

### Designer
Real workflows are **bidirectional**: Figma → code AND code → Figma (Figma blog, Feb 2026). Our pack covers only the first direction. Day-1 entry is "select frame, paste URL." The pack's `token-validator` agent is the actual value prop (prevents hardcoded values) but isn't surfaced in `persona.md`.

Notable specifics from the field:
- Figma's MCP `get_design_context` returns base component tokens instead of variant-specific tokens — known limitation.
- Without Code Connect, AI generates new components from scratch instead of reusing existing ones.
- Designers consistently misuse primitive tokens (e.g. `blue.500`) where semantic tokens are needed (`color.interactive.primary`).

### PM
Real PM workflows have **three forks**:
1. notes-to-PRD,
2. PRD-to-validation,
3. PRD-to-tickets,

each a different entry point. Our pack covers forks 2 and 3 but **assumes the PRD already exists**. Successful PMs operate in tight markdown + terminal loops (Chime example: 20 minutes from PRD to clickable prototype).

**Critical context:** Anthropic's official PM plugin (`knowledge-work-plugins/product-management`) ships **14 commands and 11 skills** — `/write-spec`, `/roadmap-update`, `/stakeholder-update`, `/synthesize-research`, `/competitive-brief`, `/metrics-review`, etc. Ours has 3. Positioning matters or students will feel they're getting the lesser version.

### Data Scientist
Real workflow is **side-by-side Claude Code + Jupyter**, not Claude Code replacing Jupyter. Community consensus (ReviewNB article, Mineault) is to use **Jupyter MCP** (not the built-in `NotebookEdit`) for `.ipynb` reliability — we ship `filesystem` and `context7` but NOT Jupyter MCP. Gap.

The foundational gotcha for DS folks: **Claude Code is file-level, sees no kernel state or in-memory DataFrames.** Our `persona.md` doesn't warn about this. Coming from notebook-native AI (Colab DS Agent, Cursor), this surprises people.

---

## 3. Concrete persona.md improvements (section names + purpose)

**Add to ALL three personas, in this order, BEFORE existing Mental Model section:**

| Section | Purpose | Length cap |
|---|---|---|
| **First 5 minutes** | Literal commands, expected outputs, one excerpt of success. Zero context required. | ~10 lines |
| **Platform gotchas** | What Claude Code can't see / can't do that this role specifically cares about. | 3-4 bullets |
| **What this pack does NOT do** | Explicit non-goals. Designer: no logic changes. PM: no code generation. DS: no kernel visibility. | 3-4 bullets |

**Add AFTER existing Mental Model / Vocabulary / Phases / Rules sections:**

| Section | Purpose | Length cap |
|---|---|---|
| **How this relates to official Anthropic plugins** *(PM specifically)* | One paragraph positioning ours as the teaching subset. Link to the full plugin as "graduation." | ~5 lines |
| **Smallest valuable loop** | Restate the entry in a single command + expected output. For students who skipped "First 5 minutes." | 1-2 lines |

**Do NOT** add new commands. **Do NOT** extend existing commands. The fix is documentation restructuring.

---

## 4. Cross-cutting findings (apply to all 3 non-engineer personas)

1. **Lead with the loop, not the schema.** Phases/vocab are reference; entry experience is the hook.
2. **Name the platform gotcha early.** Each role has one foundational misunderstanding:
   - Designer: roundtrip loses logic.
   - PM: file-first, Jira is a push target.
   - DS: no kernel state visibility.
   Surface it in `persona.md`, not buried in `agents/`.
3. **Three-fork entry.** Each role has 2-3 different starting situations; the entry doc must branch on which one the student has.
4. **Project-based, not reference-based.** Tie `persona.md` to a concrete exercise file (e.g. `examples/designer-figma-frame.md` with a sample Figma URL and expected output). RMIT research: "just add AI" curricula fail; project-based persists.
5. **Tool-count discipline.** Don't add commands. Vercel finding: >20 tools degrades agent performance ~consistently. Claude Code Desktop has poor command discoverability. Argues for fewer, clearer commands — not more.

---

## 5. Antithesis / risks (strongest case against this work)

- **Over-engineering the docs**: If we add 50 lines to each `persona.md`, we've made the problem worse. Cap each new section at ~10 lines.
- **Re-inventing Anthropic's PM plugin**: Real risk for PM specifically. Mitigation = explicit positioning as the teaching subset; link out to Anthropic's plugin as "graduation path."
- **Day-1 walkthroughs go stale**: Tool versions change. Mitigation = keep walkthrough abstract enough (paste URL, run command, get markdown file) that minor version drift doesn't break it.
- **Persona ≠ skill confusion**: Community evidence shows users don't understand the difference. Our personas conflate them. May need a one-line "this pack is a bundle of commands + subagents + rules + MCPs — think of it as the role's whole desk, not a single skill" in each `README.md`.
- **Tool-count failure mode**: Designer persona alone installs 4 commands + 3 subagents + 2 hooks + 3 MCPs = 12 surface items. We're already in the safe zone but adding more would cross the Vercel threshold. Documentation tightening is safer than tool expansion.

---

## 6. Concrete next steps (not yet executed)

If user approves, the implementation order would be:

1. **Designer** `persona.md` — add 3 new sections (First 5 minutes / Platform gotchas / Non-goals + Smallest valuable loop). ~30 new lines total.
2. **PM** `persona.md` — same 3 new sections + the "How this relates to Anthropic's official PM plugin" paragraph. ~35 new lines total.
3. **Data Scientist** `persona.md` — same 3 new sections, with extra emphasis on the kernel-state gotcha. ~30 new lines total.
4. **Optional follow-up** (separate decision): add Jupyter MCP to `personas/data-scientist/mcp.json` and document the side-by-side IDE pattern. Larger change; needs its own gate.
5. **Optional follow-up**: create `examples/designer-figma-frame.md`, `examples/pm-raw-notes.md`, `examples/ds-sample-csv-walkthrough.md` to back the "First 5 minutes" sections.

Total estimated change: ~100 lines across 3 `persona.md` files, no command/MCP changes in the first pass.

---

## 7. Sources (grouped by cycle)

### Cycle 1 — Designer
- [Figma Blog: Introducing Claude Code to Figma](https://www.figma.com/blog/introducing-claude-code-to-figma/)
- [Figma: Claude Code MCP setup guide](https://help.figma.com/hc/en-us/articles/39888612464151-Claude-Code-and-Figma-Set-up-the-MCP-server)
- [Builder.io: Claude Code + Figma MCP Server](https://www.builder.io/blog/claude-code-figma-mcp-server)
- [UX Collective: How to make Claude Code follow your design system](https://uxdesign.cc/how-to-make-claude-code-follow-your-design-system-in-figma-559618cffaa9)
- [Designer's Guide to Claude Code (Katherine Yeh)](https://medium.com/design-bootcamp/a-designers-guide-to-organizing-ai-skills-and-tools-in-claude-code-f87477c35b82)
- [Romina Kavcic: Design tokens that AI can actually read](https://learn.thedesignsystem.guide/p/design-tokens-that-ai-can-actually)

### Cycle 2 — PM
- [Claude Code for PMs: Complete Setup Guide (Aggarwal)](https://medium.com/product-powerhouse/claude-code-for-product-managers-complete-setup-guide-real-pm-workflows-2026-c94ec7087b6f)
- [Anthropic Product Management Plugin](https://claude.com/plugins/product-management)
- [Anthropic knowledge-work-plugins (GitHub)](https://github.com/anthropics/knowledge-work-plugins/tree/main/product-management)
- [Sachin Rekhi: Claude Code for PMs](https://www.sachinrekhi.com/p/claude-code-for-product-managers)
- [MindStudio: Jira MCP sprint planning](https://www.mindstudio.ai/blog/claude-code-jira-mcp-sprint-planning-automation)

### Cycle 3 — Data Scientist
- [Patrick Mineault: Claude Code for Scientists](https://www.neuroai.science/p/claude-code-for-scientists)
- [ReviewNB: Claude Code + Jupyter](https://www.reviewnb.com/claude-code-with-jupyter-notebooks)
- [Dataquest: Getting Started with Claude Code for Data Scientists](https://www.dataquest.io/blog/getting-started-with-claude-code-for-data-scientists/)
- [Kanaries: Can Claude Code Analyze Jupyter Notebooks](https://docs.kanaries.net/articles/claude-code-jupyter-data-science)
- [Towards Data Science: Beyond Code Generation](https://towardsdatascience.com/beyond-code-generation-ai-for-the-full-data-science-workflow/)

### Cycle 4 — Cross-cutting
- [Product Talk: Claude Code for Non-Technical](https://www.producttalk.org/claude-code-what-it-is-and-how-its-different/)
- [Agentic Coding: Project Onboarding](https://agenticoding.ai/docs/practical-techniques/lesson-6-project-onboarding)
- [Blake Niemyjski: AGENTS.md + Skills full workflow](https://blakeniemyjski.com/blog/agentic-driven-development/)
- [ccforpms.com: CLAUDE.md for Product Managers](https://ccforpms.com/fundamentals/project-memory)

### Cycle 5 — Antithesis
- [Atlan: 13 Agent Harness Anti-Patterns](https://atlan.com/know/agent-harness-failures-anti-patterns/) — tool-count degradation
- [GitHub Issue: Claude Code Desktop slash command autocomplete](https://github.com/anthropics/claude-code/issues/40413)
- [RMIT: Why "just add AI" fails educators](https://www.rmit.edu.au/about/educational-ai/blog/agentic-thinking-why-just-add-ai-keeps-failing-educators)
- [MindStudio: Claude Code Skills vs Slash Commands](https://www.mindstudio.ai/blog/claude-code-skills-vs-slash-commands)
- [Ballpoint: Claude Code for Non-Engineers courses](https://courses.weareballpoint.com/)
