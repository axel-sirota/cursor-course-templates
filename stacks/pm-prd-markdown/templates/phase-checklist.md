# Phase Checklist

Check every box before moving to the next phase. Paths are relative to the workspace root.

---

## Phase 0: Skeleton

- [ ] `prds/<feature-slug>.md` exists with all 12 required H2 headings
- [ ] All 6 NFR H3 headings exist under Non-functional Requirements
- [ ] `stories/`, `research/`, `decisions/`, `docs/` folders exist
- [ ] `glossary.md` exists
- [ ] `scripts/check_prd.py` and `.markdownlint-cli2.jsonc` are in place
- [ ] `npx markdownlint-cli2@0.18.1` reports 0 errors
- [ ] `python3 scripts/check_prd.py .` prints `OK`

---

## Phase 1: Discover

- [ ] Problem names one user, one number and cites a `research/` file
- [ ] Every goal has an ID, a baseline, a target and a time window
- [ ] At least 2 non-goals, each with a reason
- [ ] Users table names every role the stories will mention
- [ ] New domain terms are in `glossary.md`

---

## Phase 2: Specify

- [ ] Every epic points at one goal; every goal has at least one epic
- [ ] One story file per story, named `<feature-slug>-<NN>-<story-slug>.md`
- [ ] Every story line reads "As a ..., I want ... so that ..."
- [ ] Every story has at least one AC with **Given**, **When** and **Then**
- [ ] Every story has its INVEST table filled with evidence
- [ ] All 6 NFR subsections have a number or a named standard
- [ ] Edge cases are named and each points at a story
- [ ] Dependencies, Rollout Plan, Success Metrics, Open Questions are filled
- [ ] Every open question has an owner and a due date
- [ ] `python3 scripts/check_prd.py . --strict` prints `OK`

---

## Phase 3: Validate

- [ ] `/pm-validate prds/<feature-slug>.md` has run
- [ ] `docs/validation-<feature-slug>.md` exists
- [ ] Every Critical finding is fixed or logged as an override
- [ ] Verdict reads "Ready to decompose: Yes"
- [ ] Strict check still passes after the fixes

---

## Phase 4: Decompose

- [ ] `/pm-decompose prds/<feature-slug>.md` has run
- [ ] Tickets map 1 to 1 to story files
- [ ] Every ticket title starts with "As a"
- [ ] Dependency graph is acyclic
- [ ] Tickets pushed to the tracker only after review

---

## Phase 5: Track

- [ ] `/pm-report` produced `docs/status-<YYYY-MM-DD>-<epic>.md`
- [ ] Blocked tickets list a cause and an unblock action
- [ ] Story counts (validated / open) recorded in the transition doc
