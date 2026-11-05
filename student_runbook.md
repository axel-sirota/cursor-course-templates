# Student Runbook: AI-Assisted Development

**Welcome!** This runbook is your practical guide to using the AI-Assisted Development Template in **Cursor IDE**. Type every command below in Cursor chat.

**Personas first.** Everything starts with `/set-persona add <role>`. There are five personas: `engineer`, `pm`, `designer`, `data-scientist` and `accountant`. You can add several at once. Each persona gets its own exercises in `exercises/<role>/` and its own workspace in `workspaces/<role>/`.

**Note:** Engineers build the Blog API (`exercises/engineer/`) in any of the six engineer stacks (Python, Go, Java or TypeScript). The workflow is the same for every stack, and grading is done over HTTP by `exercises/engineer/run-acceptance.sh`. The other personas work on the fictional company Northwind Co. (data in `exercises/_data/northwind/`). Setup and prerequisites are in `QUICKSTART.md`.

---

## Quick Reference: Which Workflow Do I Use?

| Your Situation | Use This Workflow |
|----------------|------------------|
| In class, any persona, using a stack from `stacks/` | **Workflow 1: Known Stack** |
| Starting fresh with Ruby/Elixir/Kotlin | **Workflow 2: Custom Stack** |
| Adding AI to existing legacy code | **Workflow 3: Brownfield** |
| Playing several roles, or the capstone | **Multi-Persona and the Capstone** (below) |

---

## Workflow 1: Fresh Project with Known Stack

**Best for:** Class work. Every persona uses a pre-built stack from `stacks/`. Engineers pick one of python-fastapi, go-gin, go-grpc, java-spring, node-express or node-nestjs.

### Step 1: Get the Template

```bash
git clone https://github.com/your-org/cursor-course-templates my-project
cd my-project
```

### Step 2: Open in Cursor

```bash
cursor .
```
Open Chat: `Cmd+L` (Mac) or `Ctrl+L` (Windows/Linux)

### Step 3: Add Your Persona and Configure Its Stack

```
/set-persona add engineer
/setup-stack engineer
```

Engineers select `python-fastapi`, `go-gin`, `go-grpc` (graded with `--grpc`), `java-spring`, `node-express` or `node-nestjs`. The full table is under **Stack Selection** below.

**Other roles:** every persona runs `/setup-stack <role>`. pm uses `pm-prd-markdown`, designer uses `designer-react-tokens`, data-scientist picks from python-datascience, python-mlops, python-spark, python-dbt-snowflake or r-tidyverse, and accountant defaults to `sheets-accounting` (no code; `python-accounting` if you want scripts).

**What happens:**
- Persona rules and stack rules copied to `.cursor/rules/<role>/` (stack rules are prefixed `stack-`)
- A `## Persona: <role>` block in `.cursor/context.md` records your Stack, Architecture Shape and Active Phase
- Templates, examples and vibe guides copied to `workspaces/<role>/`

### Step 4: Design Your Feature

**Two options:**

**Option A: Plan from the exercise brief (what you do in class)**
```
/architect engineer @exercises/engineer/00-skeleton/README.md
```

→ AI extracts the requirements from the brief → Breaks them into phases → Stops at the review gate

Pass the README with `@` so Cursor attaches the file. Read the plan in `workspaces/<role>/plans/`, then reply "approved". Nothing is built before you approve.

**Option B: Provide Your Own Plan or a Description**

If you have a plan document (`plan.md`, `requirements.md`, etc.), or only a sentence:
```
/architect engineer @plan.md
/architect engineer "Build a blog API with posts and comments"
```

→ AI extracts requirements from your plan (or designs from your description) → Breaks into phases → Creates skeleton based on YOUR specifications

**What the AI creates (engineer):**
- `workspaces/engineer/plans/sessions/session-1-phase-0.md` (Skeleton)
- `workspaces/engineer/plans/sessions/session-2-phase-1.md` (First feature)
- `workspaces/engineer/plans/sessions/session-3-phase-1.md` (Second feature)
- Mock endpoints for all features, in the shape of `exercises/engineer/contract/openapi.yaml`
- Directory structure for your stack, under `workspaces/engineer/`

**Other roles:** run `/architect <role> @exercises/<role>/01-.../README.md` on your first exercise folder (the list is in `exercises/<role>/README.md`). No exceptions: every exercise needs an approved plan before `/start-session` will run, including pm exercise 02 (fix a flawed PRD).

### Step 5: Start Implementing

```
/start-session engineer
```

The AI will:
1. Load your persona block and stack rules
2. Read the session plan in `workspaces/engineer/plans/sessions/`
3. Ask which session to work on
4. Implement using TDD (Test-Driven Development) through `/engineer-tasks` and `/engineer-implement`

**Other roles:** `/start-session <role>`, then your persona's in-session commands (see **Per-Persona Workflows** below).

### Step 6: Run Your App and Grade It

Your app lives in `workspaces/engineer/`; run these from there. Ports, file locations and test commands for all six stacks are in `exercises/engineer/STACK_NOTES.md`.

**Python FastAPI:**
```bash
# Setup virtual environment
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Start services
docker-compose up -d
pip install -r requirements.txt
python main.py

# Visit: http://localhost:8000/docs
```

**Node Express:**
```bash
npm install
npm run dev
# Visit: http://localhost:3000
```

**Java Spring:**
```bash
./mvnw spring-boot:run
# Visit: http://localhost:8080/swagger-ui.html
```

With the server running, grade the phase from the repo root:

```bash
exercises/engineer/run-acceptance.sh 00
BASE_URL=http://localhost:8080 exercises/engineer/run-acceptance.sh 00   # not on port 8000
GRPC_ADDR=localhost:50051 exercises/engineer/run-acceptance.sh 00 --grpc  # go-grpc
```

The graders are Hurl files, so they work for every stack. Each failure names a rule id (for example `P-12`) that you look up in the phase README.

**Other roles:** there is no server. The "done when" list in your exercise README, plus the checks your persona's commands and hooks run, is the grade.

### Step 7: Commit Your Work

```bash
git add .
git commit -m "Session 1: Phase 0 - Skeleton complete"
```

### Step 8: Wrap Up Session

```
/next-session
```

→ Runs your persona's quality gate → Updates the `## Persona: <role>` block → Writes `workspaces/<role>/plans/transitions/latest.md`

Repeat Steps 5 to 8 for each phase (engineers: 01-auth, 02-posts, and so on). Engineers run `/architect` once, on 00-skeleton. Other roles run it once per exercise.

---

## Workflow 2: Fresh Project with Custom Stack

**Best for:** Building with a stack not in the library (Ruby on Rails, Elixir Phoenix, Kotlin Spring, Rust Axum).

### Step 1: Get the Template

```bash
git clone https://github.com/your-org/cursor-course-templates my-project
cd my-project
```

### Step 2: Create Your Stack

```bash
mkdir -p stacks/my-stack/rules
mkdir -p stacks/my-stack/templates  # Optional
mkdir -p stacks/my-stack/examples   # Optional
```

### Step 3: Define Stack Context

Create `stacks/my-stack/context.md`:

```markdown
# Project Context: My Stack

## Architecture Shape
REST API (Rails MVC + Service Objects + PostgreSQL)

## Tech Stack
- Language: Ruby 3.2+
- Framework: Rails 7.1
- Database: PostgreSQL
- Testing: RSpec

## Vibe & Style
- Coding Style: snake_case
- Architecture: MVC with Service Objects

## Key Rules
- Use strong parameters in controllers
- Business logic in Service Objects
- TDD with RSpec

## Active Phase
- Current: Phase 0 (Skeleton)
```

`/setup-stack` and `/architect` read the `## Architecture Shape` line. They never assume REST.

### Step 4: Create Rules

Create `stacks/my-stack/rules/style.mdc`:

```markdown
---
description: Ruby on Rails coding standards
alwaysApply: true
---

# Style Guide

- Use snake_case for variables and methods
- Use PascalCase for classes
- Controllers handle HTTP only
- Service Objects contain business logic
```

See `stacks/python-fastapi/rules/` for comprehensive examples.

### Step 5: Use Your Stack

`/setup-stack` only offers the stacks listed in `personas/<role>/persona.yaml` → `stacks`. Add `my-stack` to that list for your persona, then open Cursor and run:
```
/setup-stack engineer
```

Select `my-stack` from the list. Shortcut: type `new` at the stack menu and `/setup-stack` copies `stacks/blank/` to `stacks/<name>/` and walks you through `context.md`.

### Step 6-8: Follow Workflow 1 Steps 4-8

Use `/architect <role>`, `/start-session <role>`, and `/next-session` as normal. For the Blog API, the graders still apply: `exercises/engineer/run-acceptance.sh <phase>` does not care which language you used.

---

## Workflow 3: Adapt Existing Codebase (Brownfield)

**Best for:** Legacy projects, existing codebases.

### Step 1: Copy Configuration

```bash
cd /path/to/your-existing-project
cp -r /path/to/cursor-course-templates/.cursor .
cp -r /path/to/cursor-course-templates/personas .
cp -r /path/to/cursor-course-templates/stacks .
```

`/set-persona` installs from `personas/<role>/`, and stack detection compares against `stacks/`, so copy all three.

### Step 2: Open in Cursor and Add Your Persona

```bash
cursor .
```

```
/set-persona add engineer
```

Persona and stack rules apply to `workspaces/<role>/**` only. Put the code you want the rules to cover (or a clone of it) under `workspaces/engineer/`.

### Step 3: Detect Your Stack

Run the detection command instead of `/setup-stack`:
```
/detect-stack engineer
/detect-stack engineer path/to/code   # scan another folder
```

**What the AI does:**
1. Scans for `package.json`, `requirements.txt`, `go.mod`, etc.
2. Analyzes 2-3 source files for coding style
3. Checks if stack already exists in `stacks/` directory

**If stack already exists (e.g., `python-fastapi`):**
- Uses existing stack configuration
- Sets `Strictness: Low` for brownfield
- Done!

**If stack is new (e.g., "React + AppFabric"):**
- AI asks: "Save as reusable stack in `stacks/react-appfabric/`?"

**If you say YES:**
- Creates `stacks/react-appfabric/context.md`
- Creates `stacks/react-appfabric/rules/` with detected patterns
- **Extracts templates/** from your actual config files (`.env.example`, `docker-compose.yml`, `package.json`, etc.)
- **Extracts examples/** from your actual code (controllers, models, services with REAL patterns from your repo)
- Installs the rules into `.cursor/rules/<role>/stack-*.mdc` AND saves the stack in `stacks/` for future reuse

**If you say NO:**
- Only creates rules for this persona in `.cursor/rules/<role>/`
- Not reusable for future projects

### Step 4: Review Generated Context

Open:
- `.cursor/context.md`, the `## Persona: engineer` block (Stack, Architecture Shape, Active Phase)
- `.cursor/rules/engineer/stack-*.mdc` (each rule starts with a brownfield note)
- `stacks/<name>/context.md`, if you saved the stack

**Critical:** Verify `Strictness: Low` is set:

```markdown
## Strictness: Low
- Refactoring: Only touch what is necessary
- New Code: Apply full standards to new features only
- Legacy Code: Document issues but don't force refactoring
```

This tells the AI:
- Don't refactor existing code
- Apply standards only to NEW code
- Respect existing patterns

### Step 5: Start Working on New Features

```
/architect engineer "the new feature"
# read workspaces/engineer/plans/, reply "approved"
/start-session engineer
```

The AI respects your existing codebase while writing clean new code. `/detect-stack` takes a `<role>` for every persona, but in class only engineers use brownfield; the other roles start from their exercise folders.

---

## Command Reference

Once configured, use these commands:

| Command | What It Does | When to Use |
|---------|--------------|-------------|
| `/set-persona add <role>` | Install a persona (several can be active) | Very first step |
| `/set-persona list` / `remove <role>` | Show or remove active personas | Any time |
| `/setup-stack <role>` | Configure that persona's stack | After adding the persona |
| `/detect-stack <role>` | Analyze existing code | Brownfield projects |
| `/architect <role> @<brief>` | Design docs + review gate + skeleton | After stack setup |
| `/start-session <role>` | Load context + begin work | Start of each session |
| `/research "<question>"` | Deep 3-cycle investigation | When stuck or uncertain |
| `/code-review [<role>]` | Audit work against persona and stack rules | Before committing |
| `/next-session [<role>]` | Quality gate + transition doc | End of each session |
| `/read [<role>]` | Quick context load | Rejoining a project |
| `/undo persona <role>` / `stack <role>` / `all` | Reverse an install | Switching stack or starting over |

Each persona also has in-session commands (for example `/engineer-tasks`, `/pm-validate`, `/acct-reconcile`). They are listed under **Per-Persona Workflows** below and in `personas/<role>/persona.yaml`.

---

## Key Concepts

### Phase-Based Development

Software is built in layers, not vertical slices:

- **Phase 0 (Skeleton)**: Build structure, mock all endpoints, verify API shape
- **Phase 1+ (Implementation)**: Implement one feature at a time

**Why?** Prevents getting stuck in implementation before architecture is proven.

### Test-Driven Development (TDD)

Tests are design tools, not just quality checks:

1. **Red**: Write failing test
2. **Green**: Make it pass
3. **Refactor**: Clean up

**Rule:** Can't write implementation until test fails.

For engineers the outer test is the Hurl acceptance suite (`run-acceptance.sh`), with your own unit tests inside it. The other roles write the check first too: pm writes INVEST and Given/When/Then criteria before stories, designer checks tokens and accessibility, data-scientist fixes seeds and a baseline before modelling, accountant defines the tie-outs before the numbers.

### Session-Based Workflow

Development happens in bounded units:

1. **Start**: Load context → Define goal
2. **Execute**: Work on ONE thing
3. **End**: Document changes → Update context

**Why?** Prevents "context drift" where AI forgets the plan.

### Strictness Levels

Controls how aggressively rules are enforced:

- **High**: Greenfield projects, enforce all rules strictly
- **Medium**: Some tech debt, enforce on critical paths
- **Low**: Brownfield projects, enforce only on new code

---

## Special Features

### Architect with Plan vs Without Plan

**Without Plan (Design Mode):**
```
/architect engineer "Build a task manager"
```
→ AI designs everything (API, data model, architecture)

**With Plan (Plan Extraction Mode):**
```
/architect engineer @plan.md
/architect pm @exercises/pm/01-notes-to-prd/README.md
```
→ AI extracts from YOUR plan (or the exercise brief), doesn't redesign. Every class exercise uses this mode.

**Plan Extraction Mode benefits:**
- Faster (no design phase)
- Trusts your decisions
- Asks clarification if unclear
- Checks compatibility with active stack

### Detect-Stack Creates Reusable Stacks

When you run `/detect-stack <role>` on a codebase:
- First student: Detects "Flask" → saves to `stacks/python-flask/` with REAL templates and examples
- Second student: Detects "Flask" → finds existing `stacks/python-flask/` → uses it immediately

**Templates extracted:**
- Your actual `.env.example`
- Your actual `docker-compose.yml`
- Your actual `requirements.txt`
- Your actual framework configs

**Examples extracted:**
- Your actual controller code
- Your actual model code
- Your actual service patterns
- Your actual test files

**Result:** Future projects get the SAME patterns found in your original codebase!

---

## Typical Session Flow

> **Which flow is mine?** Run `/set-persona add <role>` first. Your persona determines which flow below applies.
> Every persona then runs `/setup-stack <role>` and `/architect <role>` before its first session.

### Engineer Session Flow

```bash
# 1. First time setup
/set-persona add engineer
/setup-stack engineer            # pick your stack (any of the six)

# 2. Plan (once, then review gate)
/architect engineer @exercises/engineer/00-skeleton/README.md
# read workspaces/engineer/plans/, reply "approved"

# 3. Start session
/start-session engineer          # state which phase you are on

# 4. Task decomposition
/engineer-tasks                  # task list for this session

# 5. Implement (TDD loop, per task)
/engineer-implement              # red→green→refactor, subagents auto-fire

# 6. Grade + review
exercises/engineer/run-acceptance.sh 00
/code-review                     # security-auditor + code-reviewer

# 7. Wrap up
/next-session                    # quality gate + transition doc
git commit -m "feat: ..."
```

### Designer Session Flow

```bash
# 1. First time setup
/set-persona add designer
/setup-stack designer          # designer-react-tokens

# 2. Plan (review gate)
/architect designer @exercises/designer/01-brand-to-tokens/README.md

# 3. Start session
/start-session designer        # state which screen/component you're building

# 4. Extract tokens (brand file, token JSON or a Figma frame)
/designer-extract

# 5. Assemble components from tokens only
/designer-compose

# 6. Refine
/designer-iterate              # apply review feedback

# 7. Verify responsiveness
# (auto-fires in designer-handoff)

# 8. Ship
/designer-handoff              # dev-ready spec for finished components
/next-session
```

### PM Session Flow

```bash
# 1. First time setup
/set-persona add pm
/setup-stack pm                 # pm-prd-markdown

# 2. Draft PRD plan (review gate)
/architect pm @exercises/pm/01-notes-to-prd/README.md

# 3. Start session
/start-session pm               # state the feature or problem

# 4. Decompose into stories and tickets
/pm-decompose   # INVEST stories with Given/When/Then criteria

# 5. Validate (Three Amigos critique)
/pm-validate    # dev-perspective + qa-perspective + gap-detector fire

# 6. Report
/pm-report

# 7. Wrap up
/next-session
```

Exercise 02 (fix a flawed PRD) still runs `/architect pm @exercises/pm/02-fix-the-flawed-prd/README.md` and needs "approved". The PRD already exists, so answer "skip" if the skeleton step asks about files in `prds/` or `stories/`.

### Data Scientist Session Flow

```bash
# 1. First time setup
/set-persona add data-scientist
/setup-stack data-scientist   # python-datascience, python-mlops, python-spark,
                              # python-dbt-snowflake or r-tidyverse

# 2. Plan (review gate)
/architect data-scientist @exercises/data-scientist/01-eda-data-quality/README.md

# 3. Start session
/start-session data-scientist # state your experiment goal

# 4. Explore + experiment
/ds-explore                   # profile data, form hypotheses
/ds-experiment                # seeded run against a logged baseline

# 5. Validate
/ds-validate                  # held-out test, leakage and reproducibility checks
/code-review

# 6. Wrap up
/next-session
```

### Accountant Session Flow

```bash
# 1. First time setup
/set-persona add accountant
/setup-stack accountant       # sheets-accounting (default, no code) or python-accounting

# 2. Plan (review gate)
/architect accountant @exercises/accountant/01-october-bank-rec/README.md

# 3. Start session
/start-session accountant     # state the period and the task

# 4. Do the work (one per exercise)
/acct-reconcile               # 01: bank vs GL, every unmatched item listed
/acct-variance                # 02: flux with explanations over threshold
/acct-je-test                 # 03: duplicates, weekend postings, round amounts

# 5. Close
/acct-close-handoff           # close memo with tie-outs and open items
/next-session
```

On sheets-accounting, review the workbooks Cursor writes in Excel or Google Sheets.

---

### For Greenfield Engineer (Blog API, detailed)

```bash
# 1. Setup
git clone https://github.com/your-org/cursor-course-templates my-project
cd my-project
cursor .

# 2. Configure
/set-persona add engineer
/setup-stack engineer
→ Select your stack (python-fastapi, go-gin, go-grpc, java-spring, node-express, node-nestjs)

# 3. Design
/architect engineer @exercises/engineer/00-skeleton/README.md
→ Read workspaces/engineer/plans/, reply "approved"

# 4. Implement Phase 0 (Skeleton)
/start-session engineer
→ Select "Session 1: Phase 0"
→ AI creates mocked endpoints in the contract shape

# 5. Verify
# start your server (see exercises/engineer/STACK_NOTES.md)
exercises/engineer/run-acceptance.sh 00

# 6. Implement Phase 1 (Authentication)
/start-session engineer
→ Select "Session 2: Phase 1 - Auth"
→ AI writes test → implements endpoint

# 7. Grade + review
exercises/engineer/run-acceptance.sh 01 --cumulative
/code-review
→ Security: ✓ No secrets
→ Style: ✓ Stack rules
→ Tests: ✓ All passing

# 8. Wrap Up
/next-session
→ Writes workspaces/engineer/plans/transitions/latest.md

# 9. Commit
git add .
git commit -m "Session 2: Phase 1 auth"
```

### For Brownfield (Existing Project)

```bash
# 1. Add configuration
cd /path/to/existing-project
cp -r /path/to/cursor-course-templates/.cursor .
cp -r /path/to/cursor-course-templates/personas /path/to/cursor-course-templates/stacks .
cursor .

# 2. Detect
/set-persona add engineer
/detect-stack engineer
→ Detected: "Python 3.9 + Flask"
→ "Save as reusable stack in stacks/python-flask/?" → Yes
→ Extracts templates and examples from your code

# 3. Review
# Check the "## Persona: engineer" block in .cursor/context.md
# and .cursor/rules/engineer/stack-*.mdc
# Ensure: Strictness: Low

# 4. Start on NEW feature
/architect engineer "Build /api/v2/users endpoint"
→ Read workspaces/engineer/plans/, reply "approved"
/start-session engineer
→ AI respects existing code, applies standards to new code only

# 5. Verify
pytest tests/api/v2/  # Only tests for new code

# 6. Commit
git add .
git commit -m "Add /api/v2/users endpoint"
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| **"No persona configured"** | Run `/set-persona add <role>` first |
| **"Run /setup-stack <role> first"** | Every persona needs a stack, pm and designer included |
| **"No plan for `<role>` yet"** | Run `/architect <role> @exercises/<role>/<exercise>/README.md` |
| **"The `<role>` plan is not approved yet"** | Reply "approved" to the `/architect` review gate, or run `/architect <role>` and pick `review` |
| **"No open session for `<role>`"** | Run `/start-session <role>` before `/next-session <role>` |
| **AI ignores my rules** | Rules live in `.cursor/rules/<role>/` and apply to `workspaces/<role>/**` only. Check your files are inside your workspace |
| **Wrong persona picked up** | Pass the role explicitly: `/start-session <role>`. `/set-persona list` shows what is active |
| **Too many linter errors** | Set `Strictness: Low` in your stack's `context.md` |
| **detect-stack misidentifies** | Manually create `context.md` with correct framework |
| **AI redesigns my plan** | Use `/architect <role> @plan.md` instead of `/architect <role> "description"` |
| **Acceptance test fails** | Read the rule id in the Hurl output, look it up in the phase README. Do not ask the AI to change the grader |
| **Docker fails** | Only needed for databases - run `docker-compose down -v` to reset |
| **Stack doesn't appear in setup** | Check `stacks/{name}/context.md` exists and the stack is listed in `personas/<role>/persona.yaml` → `stacks` |

---

## Tips for Success

1. **Always start with `/set-persona add <role>` then `/setup-stack <role>`** - Don't skip this step, whatever your role
2. **Use `/architect <role> @<exercise README>`** - The brief is your plan; faster than letting AI design
3. **Trust Phase 0** - Mock endpoints (or a PRD outline, a token set, a baseline) feel slow but catch design issues early
4. **One session = One thing** - Don't try to implement multiple features in one session
5. **Use `/research` when uncertain** - Safer than trial and error
6. **Run `/code-review` before committing** - Catches issues early
7. **Set Strictness: Low for legacy code** - Prevents "linter hell"
8. **Save detected stacks as reusable** - Helps future projects

---

## Stack-Specific Quick Reference

Engineer stacks below. Full per-stack notes (ports, where the contract copy goes, framework defaults that break the contract, go-grpc and node-nestjs) are in `exercises/engineer/STACK_NOTES.md`. Whatever the stack, the grade is `exercises/engineer/run-acceptance.sh <phase>`.

### Python FastAPI
- **Docs**: http://localhost:8000/docs
- **Tests**: `pytest`
- **Lint**: `ruff check .`
- **Format**: `black .`
- **Type Check**: `mypy .`

### Node Express
- **Tests**: `npm test`
- **Lint**: `npm run lint`
- **Dev Server**: `npm run dev`

### Java Spring Boot
- **Docs**: http://localhost:8080/swagger-ui.html
- **Tests**: `./mvnw test`
- **Run**: `./mvnw spring-boot:run`

### Go Gin
- **Tests**: `go test ./...`
- **Lint**: `golangci-lint run`
- **Run**: `go run main.go`

---

## Docker Quick Reference

### The `/dockerize` Command

Containerize your application with one command (engineer phase 05 asks for Docker):

```
/dockerize engineer
```

It builds from `workspaces/engineer/` using the stack in your persona block.

This generates:
- `Dockerfile` - Multi-stage build (smaller images)
- `docker-compose.yml` - App + database with health checks
- `.dockerignore` - Excludes unnecessary files
- `.env.example` - Environment variable template

### Common Docker Commands

| Command | What It Does |
|---------|--------------|
| `docker compose up --build` | Build and start all services |
| `docker compose up -d` | Start in background |
| `docker compose logs -f app` | Follow app logs |
| `docker compose down` | Stop and remove containers |
| `docker compose down -v` | Stop and reset database |
| `docker compose exec app /bin/sh` | Shell into container |

### Typical Docker Flow

```bash
# 1. Generate Docker config
/dockerize

# 2. Build and start
docker compose up --build

# 3. Verify health
curl http://localhost:8000/health

# 4. View logs if issues
docker compose logs -f app

# 5. Stop when done
docker compose down
```

### Docker Troubleshooting

| Issue | Solution |
|-------|----------|
| "Port already in use" | Change `APP_PORT` in `.env` or run `docker compose down` |
| "Database connection refused" | Wait for health check or run `docker compose down -v` |
| "Module not found" | Rebuild: `docker compose build --no-cache app` |
| "Permission denied" | Check Dockerfile has non-root user |

---

## Further Reading

- **[METHODOLOGY.md](METHODOLOGY.md)**: Deep dive into Phase-Based Development, TDD, command workflows
- **[QUICKSTART.md](QUICKSTART.md)**: Step-by-step guides for all three workflows
- **[ADAPTATION_GUIDE.md](ADAPTATION_GUIDE.md)**: How to create custom stacks for any language/framework
- **[CHOOSE_YOUR_ADVENTURE.md](CHOOSE_YOUR_ADVENTURE.md)**: Which persona, stack and exercise to pick
- **[exercises/README.md](exercises/README.md)**: The exercise folders for every persona, and the capstone

---

## Quick Wins

**"I am in class"**
```
/set-persona add <role> → /setup-stack <role> → /architect <role> @exercises/<role>/<first folder>/README.md → "approved" → /start-session <role> → work → /next-session <role>
```

**"I want to build the Blog API in Go (or Java, or TypeScript)"**
```
/set-persona add engineer → /setup-stack engineer → go-gin → /architect engineer @exercises/engineer/00-skeleton/README.md → "approved" → /start-session engineer
```

**"I want to start a Ruby project"**
```
Create stacks/ruby-rails/ → add it to personas/engineer/persona.yaml → /setup-stack engineer → select ruby-rails → /architect engineer @plan.md → "approved" → /start-session engineer
```

**"I have an existing Flask project"**
```
Copy .cursor/, personas/, stacks/ → /set-persona add engineer → /detect-stack engineer → Yes to save stack → /architect engineer @plan.md → "approved" → /start-session engineer
```

**That's it! You're ready to build with AI assistance.**

---

## Multi-Persona and the Capstone

Several personas can be active in one repo. Each one has its own block in `.cursor/context.md`, its own rules in `.cursor/rules/<role>/` and its own workspace in `workspaces/<role>/`.

| Command | What it does |
|---|---|
| `/set-persona add <role>` | Add a persona. Nothing already installed is removed |
| `/set-persona list` | Show active personas, their stacks and phases |
| `/set-persona remove <role>` | Remove one persona (same as `/undo persona <role>`). Your workspace stays |

Pass `<role>` to `/setup-stack`, `/architect` and `/start-session` when more than one persona is active. Work one role at a time: `/next-session` first, then `/start-session <other-role>`. Reading another persona's workspace is fine. Writing to it is not.

**Capstone.** The brief is `exercises/capstone/README.md`. One Northwind expense feature moves through pm, designer, data-scientist and accountant, and each persona reads the previous persona's output. Engineers: see the Engineers section of the capstone README. In a team, each person adds only their own role. If you play several roles yourself, add each one, run `/setup-stack <role>` for each, then `/architect <role> @exercises/capstone/README.md` once per role, in the order the README gives.

---

## Per-Persona Workflows

Run `/set-persona add <role>` first, then follow the workflow for your role. Each persona's exercises and their order are in `exercises/<role>/README.md`; each workflow below lists its exercise folders. Answer keys (every `SOLUTION.md`, `checks/expected*` file and `exercises/_data/northwind/answer_key.json`) are hidden from the AI by `.cursorignore`. Check your work against the README's "done when" list.

---

## Stack Selection

After setting your persona, every persona runs `/setup-stack <role>` to choose a stack. The command shows only the stacks valid for your persona (from `personas/<role>/persona.yaml`).

### Engineer Stacks

| Stack | Description | Best For |
|-------|-------------|----------|
| `python-fastapi` | Python REST API (FastAPI + SQLAlchemy + Alembic) | General backend, ML-adjacent services |
| `go-gin` | Go REST API (Gin + sqlx + testify) | High-performance microservices |
| `go-grpc` | Go gRPC Service (Protocol Buffers + buf) | **Intuit internal services**, high-throughput RPC |
| `java-spring` | Java REST API (Spring Boot 3 + JPA + Testcontainers) | **Salesforce / Travelers Java** enterprise backend |
| `node-express` | Node.js REST API (Express + TypeScript + Zod) | Lightweight Node APIs |
| `node-nestjs` | Node.js Enterprise API (NestJS + TypeORM + Swagger) | **Salesforce / Travelers enterprise Node** |

Every engineer stack builds the same Blog API from `exercises/engineer/contract/openapi.yaml` (go-grpc uses `contract/grpc/blog.proto`), and every one is graded by `exercises/engineer/run-acceptance.sh`.

### Data Scientist Stacks

| Stack | Description | Best For |
|-------|-------------|----------|
| `python-datascience` | Notebooks + ML (Jupyter + scikit-learn + MLflow) | Exploratory analysis, model prototyping |
| `python-mlops` | ML lifecycle (training, evaluation, model registry, serving) | Production ML, automated retraining |
| `python-spark` | Distributed Pipelines (PySpark + Delta Lake) | **Databricks / large-scale ML** |
| `python-dbt-snowflake` | Analytics Modeling (dbt Core + Snowflake/BigQuery) | **Analytics engineering / Snowflake teams** |
| `r-tidyverse` | Reproducible R analysis and statistical modeling | Actuarial and statistical work in R |

### PM, Designer and Accountant Stacks

| Persona | Stack | Description |
|---------|-------|-------------|
| pm | `pm-prd-markdown` | PRDs in Markdown: problem, goals, epics, INVEST stories, Given/When/Then criteria. `check_prd.py` is optional; `/pm-validate` is the check |
| designer | `designer-react-tokens` | Design tokens and React components built from tokens only |
| accountant | `sheets-accounting` | Default. No code: Cursor writes workbooks you review in Excel or Google Sheets |
| accountant | `python-accounting` | Same work as Python scripts, for accountants who want them |

---

### Engineer Workflow

```
Plan:  /architect engineer @exercises/engineer/00-skeleton/README.md  (once, review gate)
Start: /start-session engineer
Tasks: /engineer-tasks
Build: /engineer-implement  (loops per task: red→green→refactor)
Grade: exercises/engineer/run-acceptance.sh <phase>
Check: /code-review
End:   /next-session
```

**Subagents fired automatically by `/engineer-implement`:**
- `test-runner`: after each red and green step
- `security-auditor`: on tasks touching auth/DB/I-O
- `verifier`: before marking task done
- `code-reviewer`: before `/code-review`

**Hooks:**
- Every file edit → `lint.sh` + `type-check.sh` (advisory)
- Every shell command → `block-destructive.sh` (blocking for dangerous patterns)
- Session end → `test-runner.sh`

**Hook scope:** scripts are installed to `.cursor/scripts/engineer/` and merged into `.cursor/hooks.json`. File-edit hooks fire only for files under `workspaces/engineer/`, session-end hooks only when the active session is engineer. The same scoping applies to every persona below.

**Capstone output:** the Blog API phases, graded by `run-acceptance.sh`. Engineers who finish phase 05 early add a second persona and take a capstone step (see `exercises/capstone/README.md`).

---

### Designer Workflow

```
Plan:    /architect designer @exercises/designer/<exercise>/README.md  (review gate)
Start:   /start-session designer
Extract: /designer-extract  (brand file, token JSON, screen spec or Figma frame)
Build:   /designer-compose  (tokens only)
Refine:  /designer-iterate  (apply review feedback)
Ship:    /designer-handoff
End:     /next-session
```

Exercises: 01-brand-to-tokens, 02-claim-components, 03-my-claims-screen (`exercises/designer/README.md`).

**Subagents:**
- `figma-extractor`: invoked by `/designer-extract`
- `token-validator`: invoked by `/code-review`
- `responsive-checker`: invoked by `/designer-handoff`

**Hooks:**
- Every CSS/SCSS/TSX/JSX edit → `token-validator.sh` + `no-inline-styles.sh` (advisory)
- Session end → `screenshot-compare.sh` (advisory prompt)

**Capstone output:** a "Fast-track" StatusBadge variant and banner on the my-claims screen, tokens only, passing token and contrast checks (step 2 of `exercises/capstone/README.md`)

---

### PM Workflow

```
Draft:     /architect pm @exercises/pm/<exercise>/README.md  (review gate, every exercise)
Start:     /start-session pm
Decompose: /pm-decompose
Validate:  /pm-validate  (Three Amigos critique)
Report:    /pm-report
End:       /next-session
```

Exercises: 01-notes-to-prd, 02-fix-the-flawed-prd, 03-rice-and-mvp-cut (`exercises/pm/README.md`).

**Subagents fired by `/pm-validate`:**
- `dev-perspective`: technical feasibility
- `qa-perspective`: edge cases + testability
- `gap-detector`: structural PRD completeness

**Hooks:**
- Every PRD/spec markdown edit → `invest-validator.sh` + `ac-format-check.sh` (advisory)
- Session end → `gap-detector.sh` (advisory prompt)

**Capstone output:** `workspaces/pm/prds/receipt-fast-track.md` with the eligibility rule, goals with metrics, and 3 to 5 INVEST stories with Given/When/Then ACs

---

### Data Scientist Workflow

```
Plan:       /architect data-scientist @exercises/data-scientist/<exercise>/README.md  (review gate)
Start:      /start-session data-scientist
Explore:    /ds-explore  (profile data, form hypotheses)
Experiment: /ds-experiment  (run model, log results)
Validate:   /ds-validate  (held-out test, bias check)
Ship:       /ds-handoff  (model card)
End:        /next-session
```

Exercises: 01-eda-data-quality, 02-category-model (watch for leakage), 03-duplicate-and-policy-detection (`exercises/data-scientist/README.md`).

**Subagents:**
- `data-profiler`: invoked by `/ds-explore`
- `experiment-tracker`: invoked by `/ds-experiment` and `/next-session`
- `reproducibility-checker`: invoked by `/ds-validate`

**Hooks:**
- Every `.py`/`.ipynb` edit → `seed-check.sh` + `notebook-lint.sh` (advisory)
- Session end → `log-experiment.sh` (advisory prompt)

**Capstone output:** `workspaces/data-scientist/docs/fast-track-impact.md` with the qualifying-claim counts, reproducible with a fixed seed

---

### Accountant Workflow

```
Plan:      /architect accountant @exercises/accountant/<exercise>/README.md  (review gate)
Start:     /start-session accountant
Reconcile: /acct-reconcile  (bank vs GL, every unmatched item listed)
Flux:      /acct-variance  (budget vs actual, month over month, explanations)
JE test:   /acct-je-test  (duplicates, weekend postings, round amounts, self-approval)
Close:     /acct-close-handoff  (close memo with tie-outs and open items)
End:       /next-session
```

Exercises: 01-october-bank-rec, 02-flux-analysis, 03-je-testing-close-memo (`exercises/accountant/README.md`). Default stack is `sheets-accounting`.

**Subagents:**
- `tie-out-checker`: invoked by `/acct-reconcile`, `/acct-je-test` and `/acct-close-handoff`; every number traces to a source file and row
- `controls-checker`: invoked by `/acct-je-test` and `/acct-close-handoff`
- `pii-redactor`: invoked by `/acct-je-test` and `/acct-close-handoff`; no names, emails or full account numbers in outputs

**Hooks:**
- Every file edit → `protect-raw.sh` (warns if anything under `data/raw/` was edited, advisory)
- Session end → `tie-out-check.sh`

**Capstone output:** a working paper showing the effect on the 2150 Accrued Reimbursements balance, tying to 0.00, and a memo naming the compensating control
