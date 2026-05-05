# Research Artifact: New Personas & System Improvements
**Date:** 2026-05-05  
**Cycles:** 5  
**Scope:** Non-standard roles beyond fullstack dev, marketing/sales, system improvements

---

## Executive Summary

The current system (engineer / devops / data-scientist / pm / designer) covers the obvious developer-adjacent roles well. The highest-value additions are **5 new personas** and **6 system improvements** — all validated against the existing `persona + stack` architecture. Priority order is based on: (1) role frequency in enterprise teams, (2) clear AI-augmentable workflow, (3) distinct deliverable that maps to an Architecture Shape.

**Top 5 new personas to add (in priority order):**
1. `sdet` — Test automation engineers (Playwright/Pytest); huge job market growth (+17%), clear stack pattern
2. `appsec` — Application security engineers; Semgrep + Cursor hooks pattern is mature and proven
3. `tech-writer` — Technical writers; Mintlify/Docusaurus stack maps cleanly; 55% already use AI
4. `gtm-engineer` — Growth/marketing/RevOps engineers; builds CRM integrations and analytics pipelines
5. `solutions-architect` — Produces ADRs, diagrams, Well-Architected assessments; no stack needed (like PM)

**Top 6 system improvements:**
1. PostToolUse hooks for auto-lint/test after file edits
2. Company overlays (client-config per company on top of persona)
3. CLAUDE.md compaction instruction
4. Adversarial review agent (two agents critique each other's output)
5. Self-reflection pattern (REFLECTION.md after each session)
6. Hybrid Cursor+Claude Code routing guidance

---

## Key Findings

### What was confirmed
- **SDET/QA is the fastest-growing adjacent role** — QA positions grew 17% vs 9% for general devs (2023-2025). 62% of QA professionals expanded in scope due to AI tools. Playwright is now the dominant framework (78,600 stars, 45% adoption, tripled job postings 2024-2026).
- **AppSec has a mature AI workflow** — Semgrep MCP Server + Cursor hooks pattern is production-validated. `afterFileEdit` hook triggers scan, agent remediates, loop continues until clean. This is a real workflow used in production at enterprise companies.
- **Technical writers are underserved** — 55% use AI regularly but no AI coding assistant has a TW persona. Mintlify is the dominant modern docs stack. The deliverable (MDX files in git) maps perfectly to the existing Architecture Shape pattern.
- **GTM Engineer is the 2025 term for marketing engineer** — builds CRM/MAP/analytics integrations in Python/Node, owns pipeline automation, uses Cursor for POC scripts. Deliverable is automation scripts + data pipelines.
- **Solutions Architect** — Produces ADRs, C4 diagrams, Well-Architected assessments. No stack needed. Claude used for "45% faster solution design cycles" at Salesforce.

### What was wrong in initial hypothesis
- SRE is NOT a separate persona — overlaps too heavily with devops. Better handled as a devops stack variant (`observability-stack`) or a devops sub-command.
- Sales Engineer is too contextual — demo environments are company-specific. Risk of low reuse. Would only work as a "solutions-engineer" persona with very lightweight stacks.
- "AI/Prompt Engineer" persona is hype — no stable toolchain, no consensus on deliverable. Skip.
- Marketing Engineer stack varies too much (HubSpot vs Marketo vs custom) to have 6 standard stacks like engineer. Should be 2 stacks max: `hubspot-python` and `segment-analytics`.

### Competitor landscape (SuperClaude Framework)
- SuperClaude (5,700+ GitHub stars) has 9 personas: architect, frontend, backend, security, analyzer, qa, performance, refactorer, mentor — all purely technical.
- GitHub Copilot Agents (`.github/agents/`): enterprise teams use 3-8 agents, typically code review + infra + testing + docs.
- None of the competitors have non-developer personas (PM, designer, tech writer, GTM engineer). **This is a differentiation opportunity.**

### System improvement findings
- **PostToolUse hooks** are more reliable than CLAUDE.md instructions for enforcing behavior. Semgrep uses this pattern in production.
- **Company overlays** (client-config/) already partially exist in the set-persona command but are not documented or standardized.
- **Self-reflection pattern** (REFLECTION.md after session): compound learning — the AI notes what surprised it, lead reviews and merges improvements. Gets better over time.
- **Adversarial review**: two-model critique (Claude + another model, or two Claude instances with different system prompts) catches issues single-agent review misses. 1.7x more issues found in AI-written code per research.
- **Hybrid routing**: Cursor for daily editing, Claude Code for large-context agentic tasks. 59% of devs run 3+ AI tools. Having a `/which-tool` command that recommends Cursor vs Claude Code based on task type would be uniquely useful.

---

## Trade-offs

| Addition | Value | Effort | Risk |
|----------|-------|--------|------|
| `sdet` persona + playwright-typescript stack | Very High | Medium | Low — clear deliverable |
| `appsec` persona + semgrep stack | Very High | Medium | Low — proven workflow |
| `tech-writer` persona + mintlify/docusaurus stacks | High | Low | Low — docs = MDX files in git |
| `gtm-engineer` persona + hubspot/segment stacks | Medium | Medium | Medium — stack varies by company |
| `solutions-architect` persona (no stack) | Medium | Low | Low — like PM, no stack needed |
| PostToolUse hooks | High | Low | Low |
| Company overlays (standardize client-config) | High | Medium | Low |
| CLAUDE.md compaction instruction | Medium | Very Low | None |
| Adversarial review agent | Medium | Low | Low |
| Self-reflection pattern | High | Low | Low |
| Hybrid Cursor/Claude Code routing command | Medium | Low | Low |
| SRE persona | Low | Medium | High — overlaps devops |
| Sales Engineer persona | Low | High | High — too contextual |

---

## Proposed Plan

### Phase 1 — New Personas (high ROI, low overlap)

#### `sdet` persona
- `personas/sdet/persona.md` — test-first mindset, AAA pattern, no implementation code
- `stacks/playwright-typescript/` — full stack: context.md, 4 rules, starter template, vibe
- `stacks/pytest-api/` — API testing with pytest + httpx + respx
- Architecture Shape: "Test Suite (Page Objects → Fixtures → Specs → Reports)"
- Key commands: `@architect` generates Page Object scaffolds; `@code-review` checks for selector fragility, missing assertions, flaky patterns
- Agent: `test-coverage-auditor.md` — finds untested flows in the codebase

#### `appsec` persona
- `personas/appsec/persona.md` — find vulns, not ship features; triage/prioritize/remediate
- `stacks/semgrep-sast/` — Semgrep rules, custom rule templates, CI integration patterns
- Hooks: `afterFileEdit` → run semgrep scan; `stop` → remediation summary
- Architecture Shape: "Security Scan Pipeline (Code → SAST → SCA → DAST → Report)"
- Agent: `vuln-triager.md` — prioritizes findings by exploitability + business impact

#### `tech-writer` persona
- `personas/tech-writer/persona.md` — docs-as-code, every PR needs a docs update, llms.txt matters
- `stacks/mintlify/` — MDX structure, mint.json config, component library, llms.txt generation
- `stacks/docusaurus/` — React-based, sidebars.js, custom components
- Architecture Shape: "Documentation Site (MDX → Static Site → AI-Indexed)"
- Agent: `docs-coverage-auditor.md` — finds public APIs with no docs

#### `solutions-architect` persona (no stack, like PM)
- `personas/solutions-architect/persona.md` — ADRs, C4 diagrams, Well-Architected assessments
- No setup-stack needed
- Commands: `@architect` repurposed for system design (not code scaffold); `@research` for technology decisions
- Deliverables: `docs/adr/`, `docs/diagrams/`, `docs/well-architected/`

#### `gtm-engineer` persona
- `personas/gtm-engineer/persona.md` — pipeline automation, CRM integrations, analytics
- `stacks/hubspot-python/` — HubSpot API + Python, webhook handlers, workflow automation
- `stacks/segment-analytics/` — Segment Sources API, event tracking, warehouse sync
- Architecture Shape: "GTM Pipeline (CRM → Enrichment → Routing → Analytics)"

---

### Phase 2 — System Improvements

#### 1. PostToolUse hooks (standardize)
- Add `scripts/run-linter.sh` and `scripts/run-tests.sh` to each persona
- Wire into `hooks.json` for all personas: `afterFileEdit` → lint, `stop` → test
- Document in QUICKSTART.md

#### 2. Standardize company overlays
- Create `client-config/README.md` explaining the overlay system
- Define standard overlay structure: `personas/{role}/`, `stacks/{stack}/`, `CLAUDE.md` patches
- Add to CHOOSE_YOUR_ADVENTURE.md as "Bring Your Own Client"

#### 3. CLAUDE.md compaction instruction
- Add to every stack's context.md and to the base CLAUDE.md:
  > "When compacting, always preserve: Active Persona, Active Stack, Architecture Shape, Active Phase, and the full list of modified files in the current session."

#### 4. Adversarial review agent
- `.claude/agents/adversarial-reviewer.md` — spawns two review passes with different system prompts, merges findings
- Useful for: security-sensitive code, complex domain logic, migration scripts

#### 5. Self-reflection pattern
- Add to `next-session.md`: after writing the transition doc, write a `REFLECTION.md` noting what surprised the AI, what instructions were unclear, what context was missing
- Lead reviews REFLECTION.md weekly and updates CLAUDE.md/context.md accordingly

#### 6. `/which-tool` command
- New command in both `.claude/` and `.cursor/`
- Input: describe the task
- Output: recommendation — Cursor (fast iteration, UI work, single-file edits) vs Claude Code (large context, multi-file agentic, codebase-wide refactor)
- Teaches students the hybrid workflow

---

## Sources (Key)

- SuperClaude Framework (5,700+ stars): https://github.com/SuperClaude-Org/SuperClaude_Framework
- Semgrep × Cursor Hooks pattern: https://semgrep.dev/blog/2025/cursor-hooks-mcp-server/
- SDET job market growth: https://prepare.sh/articles/qa-and-sdet-is-the-safest-job-during-ai-boom-analysis-of-qa-2025-job-market-trends
- Playwright 2026 adoption stats: https://tech-insider.org/playwright-vs-cypress-vs-selenium-2026/
- GTM Engineer career path: https://www.tabula.io/blog/becoming-a-gtm-engineer-in-saas-career-path-guide
- Technical writing AI tools: https://instrktiv.com/en/ai-in-technical-writing/
- Mintlify AI-first docs: https://www.mintlify.com/library/best-technical-documentation-software-in-2026
- Solutions Architect AI (Salesforce 45% faster): https://intuitionlabs.ai/articles/claude-enterprise-deployment-training-guide-2026
- Claude Code best practices: https://code.claude.com/docs/en/best-practices
- AllStacks 2030 team structure: https://www.allstacks.com/blog/the-2030-software-engineering-team-structure-for-an-ai-native-world
- Cursor Enterprise (64% Fortune 500): https://cursor.com/enterprise
- AI code quality issues (1.7x more bugs): https://www.qodo.ai/reports/state-of-ai-code-quality/
- Self-reflection pattern: https://addyosmani.com/blog/code-agent-orchestra/
