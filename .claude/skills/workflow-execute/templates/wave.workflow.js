// POINTER — not the live script. The canonical, runnable wave workflow is:
//     .claude/workflows/wave-execute.js
// which is resolvable by NAME:
//     Workflow({ name: 'wave-execute', args: { plan, feat, base, epicDir, repo, planSlug } })
//
// where `plan` is the .plan object from:
//     python3 .claude/skills/workflow-execute/scripts/load_wave.py plans/<epic>/plan --wave N --json
//
// You do NOT author or edit a per-wave script. ONE workflow, args change per wave. See the skill's
// "Step 2 — Run the wave via the NAMED workflow" for the exact call. This file exists only as a
// signpost so references to templates/wave.workflow.js still lead you to the real one.
export const meta = {
  name: 'wave.workflow (pointer)',
  description: 'POINTER → .claude/workflows/wave-execute.js (run by name). Not a live script.',
  phases: [],
}
throw new Error('templates/wave.workflow.js is a POINTER — run the canonical workflow by name instead: Workflow({ name: "wave-execute", args: {...} }). See .claude/workflows/wave-execute.js')
