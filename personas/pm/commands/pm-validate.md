# /pm-validate

**Purpose:** Run a Three Amigos critique on a PRD — dev feasibility, QA edge cases, and structural gap analysis — before any decomposition begins.

## Steps

1. **Locate the PRD**
   - Ask the user for the PRD file path.
   - Default: the most recently modified `.md` file under `prds/` or `docs/`.
   - If no PRD is found, stop and ask the user to provide one.

2. **Dev feasibility review** — Invoke the `dev-perspective` subagent on the full PRD text.
   - Receives: the PRD content.
   - Returns: feasibility verdict per story, hidden complexity findings, cost estimates (S/M/L), and a list of blocking dependencies not named in the PRD.

3. **QA edge case analysis** — Invoke the `qa-perspective` subagent on the full PRD text.
   - Receives: the PRD content.
   - Returns: unnamed edge cases per story, untestable acceptance criteria, and suggested Given/When/Then rewrites.

4. **Structural gap check** — Invoke the `gap-detector` subagent on the full PRD text.
   - Receives: the PRD content.
   - Returns: a section-by-section completeness report (Present / Missing / Weak) covering goals, personas, stories, AC, NFRs, edge cases, dependencies, rollout plan, success metrics, and open questions.

5. **Synthesize findings** — Combine all three subagent outputs into a validation report saved at:
   ```
   docs/validation-{prd-name}.md
   ```
   The report has three sections (one per subagent) plus a final **"Ready to decompose?"** verdict:
   - **Yes** — no Critical findings.
   - **No** — one or more Critical findings require PM action first.

6. **Handle Critical findings** — For each finding tagged Critical, ask the PM:
   > "This finding is Critical: [finding]. Do you want to fix the PRD before decomposing, or proceed anyway?"
   - If the PM chooses to fix: open the PRD and wait for the edit, then re-run only the relevant subagent.
   - If the PM proceeds anyway: note the override in the validation report.

## Output

A file at `docs/validation-{prd-name}.md` containing:
- Dev Perspective section (feasibility per story + cost estimates)
- QA Perspective section (edge cases + testability issues)
- Gap Detector section (completeness table)
- Ready-to-decompose verdict with any Critical overrides logged
