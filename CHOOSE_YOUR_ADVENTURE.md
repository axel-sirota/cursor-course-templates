# Choose Your Adventure

Find your row. It gives the persona, the stack and the first command to type. Each exercise uses your role's own tools and language: a Java developer builds in Java, an accountant works in spreadsheets, a PM needs nothing beyond Cursor.

## Pick your row

| I am a ... and I want to ... | Persona | Stack | First exercise |
|---|---|---|---|
| Java developer building services | engineer | java-spring | `exercises/engineer/`: Blog API |
| Go developer building REST APIs | engineer | go-gin | `exercises/engineer/`: Blog API |
| Go developer building gRPC services | engineer | go-grpc | `exercises/engineer/`: Blog API (grpcurl variant) |
| Node developer, plain Express | engineer | node-express | `exercises/engineer/`: Blog API |
| Node developer, structured TypeScript | engineer | node-nestjs | `exercises/engineer/`: Blog API |
| Python developer building APIs | engineer | python-fastapi | `exercises/engineer/`: Blog API |
| Product manager writing PRDs and stories | pm | pm-prd-markdown | `exercises/pm/` 01: notes to PRD |
| Designer building a design system | designer | designer-react-tokens | `exercises/designer/` 01: brand to tokens |
| Data scientist in Python notebooks | data-scientist | python-datascience | `exercises/data-scientist/` 01: EDA |
| Data scientist shipping models (MLOps) | data-scientist | python-mlops | `exercises/data-scientist/` 01 |
| Data scientist or engineer on Spark | data-scientist | python-spark | `exercises/data-scientist/` 01 |
| Analytics engineer on dbt and SQL | data-scientist | python-dbt-snowflake | `exercises/data-scientist/` 01 |
| Statistician or analyst in R | data-scientist | r-tidyverse | `exercises/data-scientist/` 01 |
| Accountant who does not code | accountant | sheets-accounting (default) | `exercises/accountant/` 01: October bank rec |
| Accountant who wants scripted, repeatable workpapers | accountant | python-accounting | `exercises/accountant/` 01 |
| Someone who wants to try two roles | two personas | one stack each | exercise 01 for each role, then the capstone |

All engineer stacks are graded by the same Hurl acceptance tests over HTTP, so the stack choice changes the language, not the exercise.

## Commands for your row

```
/set-persona add <persona>
/setup-stack <persona>              # pick the stack from your row
/architect <persona> @exercises/<persona>/<first exercise folder>/README.md   # engineer: 00-skeleton, others: 01-...
   ...review the plan, reply "approved"...
/start-session <persona>
```

The folder names are in `exercises/<persona>/README.md`. Prerequisites per stack are in `QUICKSTART.md`.

## Trying two roles

Several personas can be active in one repo. Each has its own workspace, rules and hooks, so they do not interfere.

| Step | Command |
|---|---|
| Add the first role | `/set-persona add engineer` |
| Add the second role | `/set-persona add pm` |
| See both | `/set-persona list` |
| Stack for each | `/setup-stack engineer`, `/setup-stack pm` |
| Plan each | `/architect engineer ...`, `/architect pm ...` |
| Work one at a time | `/start-session pm` → `/next-session` → `/start-session engineer` |
| Drop one | `/set-persona remove pm` |

Good pairs to try:

| Pair | Why |
|---|---|
| pm + designer | The PRD's stories become the screen's components |
| data-scientist + accountant | Flags from the model, tie-outs from the books |
| engineer + pm | See the same loop with code tests and with INVEST checks |

When you are ready for every role at once, do `exercises/capstone/README.md`.

## Not sure?

| If you ... | Start with |
|---|---|
| write code most days | engineer, in the language you use at work |
| write specs, not code | pm |
| work in Figma or CSS | designer |
| live in notebooks or SQL | data-scientist |
| close the books | accountant on sheets-accounting |

You can switch at any time: `/undo stack <role>` changes the stack, `/undo persona <role>` drops the role. Your workspace is kept.
