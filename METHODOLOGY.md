# Methodology

The principles behind the course. They apply to every persona and every stack. `/read` loads this file, so the AI works by it too.

## The five principles

| # | Principle | In one line |
|---|---|---|
| 1 | Phases | Build the shape first, then fill it in one piece at a time |
| 2 | Test first | Write the check before the work. The check decides when you are done |
| 3 | Sessions | Bounded units of work with a goal, a gate and a handoff |
| 4 | Context first | The AI knows only what the repo tells it. Write it down |
| 5 | Explicit over clever | Consistency beats cleverness. Files are cheap; confusion is expensive |

## 1. Phases

| Phase | What you build | Who decides it is right |
|---|---|---|
| Phase 0: skeleton | The whole surface as stubs: every route, PRD section, token, notebook step or workpaper, with no real content | You, at the `/architect` review gate, then the skeleton check |
| Phase 1+: features | One contract item at a time, until its check passes | The check for that item |

The skeleton proves the shape before anyone sinks hours into details. `/architect` writes the plan, stops at the review gate, and builds the skeleton only after you approve.

What "the surface" means depends on the Architecture Shape:

| Persona | Shape | Phase 0 stubs |
|---|---|---|
| engineer | REST API / gRPC Service | Routes or RPCs returning hardcoded responses |
| pm | PRD Workspace | Every PRD section headed, bodies marked TODO |
| designer | Design System | Token file and components rendering placeholders |
| data-scientist | Experiment Notebook / Data Pipeline / Analytics Model / Statistical Computing | Notebooks, stages or models that run on empty input |
| accountant | Close Workbook | Workpaper steps with empty outputs and tie-out stubs |

## 2. Test first, for every role

The rule is the same everywhere: you may not do the work until a check exists that fails without it. Red, then green, then clean up.

"Test" means the check that fits the role:

| Persona | The test | Red means | Green means |
|---|---|---|---|
| engineer | Acceptance tests (Hurl over HTTP) plus unit tests in the stack | The endpoint returns the wrong thing | The test passes for real values |
| pm | INVEST checks on every story, Given/When/Then on every acceptance criterion | `/pm-validate` lists a failing story | Every story passes and the gap-detector finds no missing NFR |
| designer | Token and accessibility checks | A hardcoded color, spacing or font size, or a contrast failure | Components use tokens only and pass at every breakpoint |
| data-scientist | Fixed seeds and a logged baseline | No seed, no baseline, or leakage between train and test | The model beats the baseline in `experiments/log.md` and reruns to the same numbers |
| accountant | Tie-outs | A reported number with no source row | Every number in `output/` traces to a source file and row |

The AI is good at writing these checks once the skeleton exists. Ask for the check first, read it, then ask for the work.

Never let the AI change a check to make it pass. If the check is wrong, fix it yourself and say why.

## 3. Sessions

```
/start-session <role>  →  in-session commands  →  /next-session
```

| Part | What happens |
|---|---|
| Start | Load the role's rules, plan and last handoff. Agree one goal from the current session file |
| Work | Use the role's in-session commands. Stay inside `workspaces/<role>/` |
| End | Run the role's quality gate. Write `workspaces/<role>/plans/transitions/latest.md`. Advance the phase only if every acceptance criterion is met |

Sessions stop context drift. The plan lives in files, not in the chat history, so a new chat picks up exactly where the last one stopped.

Each role's in-session commands and quality gate are in `personas/<role>/persona.yaml`.

## 4. Context first

| What the AI needs | Where it lives |
|---|---|
| Which roles are active, their stacks and phases | `.cursor/context.md` |
| What the role is and how it works | `personas/<role>/persona.yaml` |
| How work must look | Rules in `.cursor/rules/<role>/`, scoped to `workspaces/<role>/**` |
| What to build and in what order | `workspaces/<role>/plans/interface-contract.md` and `plans/sessions/` |
| Where the last session stopped | `workspaces/<role>/plans/transitions/latest.md` |

Rules are scoped per role, so several personas share one repo without their rules colliding. A PM's rules never fire on engineering code.

## 5. Explicit over clever

| Do | Instead of |
|---|---|
| Write the decision in the plan | Hoping the AI remembers it |
| One small file per concern | One large file that does everything |
| Name the source of every number | "Approximately" |
| Follow the stack's conventions | A clever pattern only you understand |

## Working across roles

Each persona writes only to its own workspace and may read the others. Handoffs between roles go through files: a PRD in `workspaces/pm/`, a component spec in `workspaces/designer/`, flags in `workspaces/data-scientist/`. The capstone (`exercises/capstone/README.md`) runs one feature through several roles this way.

To switch roles, close the current session with `/next-session`, then `/start-session <other-role>`.

## Anti-patterns

| Anti-pattern | Why it hurts | Do this |
|---|---|---|
| Skipping the review gate | You build the wrong thing fast | Read the plan, then approve |
| Work before the check | You cannot tell when you are done | Write the check first |
| One giant session | The AI loses the plan | Keep sessions to 1 to 4 hours |
| Editing another role's workspace | Their rules and gates never see the change | Hand off through a file in your own workspace |
| Skipping `/next-session` | The next session starts blind | Always close with the handoff |
