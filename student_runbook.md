# Student Runbook: AI-Assisted Development

**Welcome!** This runbook is your practical guide to using the AI-Assisted Development Template. It works with both **Cursor IDE** and **Claude Code**.

**Note:** Examples use **Python FastAPI** as the reference stack, but the workflow applies to any stack (Node.js, Java, Go, Ruby, etc.).

---

## Quick Reference: Which Workflow Do I Use?

| Your Situation | Use This Workflow |
|----------------|------------------|
| Starting fresh with Python/Node/Java/Go | **Workflow 1: Known Stack** |
| Starting fresh with Ruby/Elixir/Kotlin | **Workflow 2: Custom Stack** |
| Adding AI to existing legacy code | **Workflow 3: Brownfield** |

---

## Workflow 1: Fresh Project with Known Stack

**Best for:** New projects using a pre-built stack (Python FastAPI, Node Express, Java Spring, Go Gin, DevOps Terraform).

### Step 1: Get the Template

```bash
git clone https://github.com/your-org/cursor-course-templates my-project
cd my-project
```

### Step 2: Open in Your AI Tool

**Cursor IDE:**
```bash
cursor .
```
Open Chat: `Cmd+L` (Mac) or `Ctrl+L` (Windows/Linux)

**Claude Code:**
```bash
claude
```

### Step 3: Configure Stack

Run the setup command and select your stack:

- **Cursor**: `@setup-stack`
- **Claude Code**: `/setup-stack`

Select from:
- `python-fastapi` (REST API with PostgreSQL)
- `node-express` (TypeScript API)
- `java-spring` (Enterprise Java)
- `go-gin` (High-performance Go)
- `devops-terraform` (Infrastructure as Code)

**What happens:**
- Rules copied to `.cursor/rules/` or `.claude/rules/`
- Context copied to `.cursor/context.md` or `CLAUDE.md`
- Templates and vibe guides copied to project root

### Step 4: Design Your Feature

**Two options:**

**Option A: Let AI Design Everything**
```
@architect "Build a blog API with posts and comments"
```
or
```
/architect "Build a blog API with posts and comments"
```

→ AI designs API surface → Creates skeleton → Generates session plans

**Option B: Provide Your Own Plan**

If you have a plan document (`plan.md`, `requirements.md`, etc.):
```
@architect plan.md
```
or
```
/architect plan.md
```

→ AI extracts requirements from plan → Breaks into phases → Creates skeleton based on YOUR specifications

**What the AI creates:**
- `plan/sessions/session-1-phase-0.md` (Skeleton)
- `plan/sessions/session-2-phase-1.md` (First feature)
- `plan/sessions/session-3-phase-1.md` (Second feature)
- Mock endpoints for all features
- Directory structure for your stack

### Step 5: Start Implementing

```
@start-session
```
or
```
/start-session
```

The AI will:
1. Load your stack context
2. Read the session plan
3. Ask which session to work on
4. Implement using TDD (Test-Driven Development)

### Step 6: Run Your App

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

### Step 7: Commit Your Work

```bash
git add .
git commit -m "Session 1: Phase 0 - Skeleton complete"
```

### Step 8: Wrap Up Session

```
@next-session
```
or
```
/next-session
```

→ Generates summary → Updates context → Creates transition document

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

Open your AI tool and run:
```
@setup-stack  or  /setup-stack
```

Select `my-stack` from the list.

### Step 6-8: Follow Workflow 1 Steps 4-8

Use `@architect`, `@start-session`, and `@next-session` as normal.

---

## Workflow 3: Adapt Existing Codebase (Brownfield)

**Best for:** Legacy projects, existing codebases.

### Step 1: Copy Configuration

**Cursor IDE:**
```bash
cd /path/to/your-existing-project
cp -r /path/to/cursor-course-templates/.cursor .
```

**Claude Code:**
```bash
cd /path/to/your-existing-project
cp -r /path/to/cursor-course-templates/.claude .
cp /path/to/cursor-course-templates/CLAUDE.md .
```

### Step 2: Open in Your AI Tool

**Cursor:** `cursor .`
**Claude Code:** `claude`

### Step 3: Detect Your Stack

Run the detection command:
```
@detect-stack  or  /detect-stack
```

**What the AI does:**
1. Scans for `package.json`, `requirements.txt`, `go.mod`, etc.
2. Analyzes 2-3 source files for coding style
3. Checks if stack already exists in `stacks/` directory

**If stack already exists (e.g., `python-fastapi`):**
- Uses existing stack configuration
- Sets `Strictness: Low` for brownfield
- Done! ✅

**If stack is new (e.g., "React + AppFabric"):**
- AI asks: "Save as reusable stack in `stacks/react-appfabric/`?"

**If you say YES:**
- Creates `stacks/react-appfabric/context.md`
- Creates `stacks/react-appfabric/rules/` with detected patterns
- **Extracts templates/** from your actual config files (`.env.example`, `docker-compose.yml`, `package.json`, etc.)
- **Extracts examples/** from your actual code (controllers, models, services with REAL patterns from your repo)
- Saves to both your project AND `stacks/` for future reuse

**If you say NO:**
- Only creates context for this project
- Not reusable for future projects

### Step 4: Review Generated Context

Open the context file:
- **Cursor**: `.cursor/context.md`
- **Claude Code**: `CLAUDE.md`

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
@start-session  or  /start-session
```

The AI respects your existing codebase while writing clean new code.

---

## Command Reference

Once configured, use these commands:

| Command | What It Does | When to Use |
|---------|--------------|-------------|
| `@setup-stack` / `/setup-stack` | Configure stack | First step in any project |
| `@detect-stack` / `/detect-stack` | Analyze existing code | Brownfield projects |
| `@architect` / `/architect` | Design API + create skeleton | After stack setup |
| `@start-session` / `/start-session` | Load context + begin coding | Start of each coding session |
| `@research` / `/research` | Deep 3-cycle investigation | When stuck or uncertain |
| `@code-review` / `/code-review` | Audit code against rules | Before committing |
| `@next-session` / `/next-session` | Wrap up + generate summary | End of coding session |
| `@read` / `/read` | Quick context load | Rejoining a project |

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
@architect "Build a task manager"
```
→ AI designs everything (API, data model, architecture)

**With Plan (Plan Extraction Mode):**
```
@architect plan.md
```
→ AI extracts from YOUR plan, doesn't redesign

**Plan Extraction Mode benefits:**
- Faster (no design phase)
- Trusts your decisions
- Asks clarification if unclear
- Checks compatibility with active stack

### Detect-Stack Creates Reusable Stacks

When you run `@detect-stack` on a codebase:
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

### For Greenfield (New Project)

```bash
# 1. Setup
git clone https://github.com/your-org/cursor-course-templates my-project
cd my-project
cursor .  # or claude

# 2. Configure (Cursor syntax shown, add / for Claude Code)
@setup-stack
→ Select "python-fastapi"

# 3. Design
@architect "Build a blog API"
→ Or: @architect plan.md (if you have a plan)

# 4. Implement Phase 0 (Skeleton)
@start-session
→ Select "Session 1: Phase 0"
→ AI creates mocked endpoints

# 5. Verify
python main.py
# Visit http://localhost:8000/docs

# 6. Implement Phase 1 (First Feature)
@start-session
→ Select "Session 2: Phase 1 - POST /posts"
→ AI writes test → implements endpoint

# 7. Review
@code-review
→ Security: ✓ No secrets
→ Style: ✓ Type hints
→ Tests: ✓ All passing

# 8. Wrap Up
@next-session
→ Generates summary for next session

# 9. Commit
git add .
git commit -m "Session 2: Implement POST /posts endpoint"
```

### For Brownfield (Existing Project)

```bash
# 1. Add configuration
cd /path/to/existing-project
cp -r /path/to/cursor-course-templates/.cursor .
cursor .

# 2. Detect
@detect-stack
→ Detected: "Python 3.9 + Flask"
→ "Save as reusable stack in stacks/python-flask/?" → Yes
→ Extracts templates and examples from your code

# 3. Review
# Check .cursor/context.md
# Ensure: Strictness: Low

# 4. Start on NEW feature
@start-session
→ "Build /api/v2/users endpoint"
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
| **"No Stack Configured"** | Run `@setup-stack` or `/setup-stack` first |
| **AI ignores my rules** | Check rules have `alwaysApply: true` and are in `.cursor/rules/` or `.claude/rules/` |
| **Too many linter errors** | Set `Strictness: Low` in context file |
| **detect-stack misidentifies** | Manually create `context.md` with correct framework |
| **AI redesigns my plan** | Use `@architect plan.md` instead of `@architect "description"` |
| **Docker fails** | Only needed for databases - run `docker-compose down -v` to reset |
| **Stack doesn't appear in setup** | Check `stacks/{name}/context.md` exists and is properly formatted |

---

## Tips for Success

1. **Always start with `@setup-stack` or `/setup-stack`** - Don't skip this step
2. **Use `@architect plan.md` if you have requirements** - Faster than letting AI design
3. **Trust Phase 0** - Mock endpoints feel slow but catch design issues early
4. **One session = One thing** - Don't try to implement multiple features in one session
5. **Use `@research` when uncertain** - Safer than trial and error
6. **Run `@code-review` before committing** - Catches issues early
7. **Set Strictness: Low for legacy code** - Prevents "linter hell"
8. **Save detected stacks as reusable** - Helps future projects

---

## Stack-Specific Quick Reference

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

## Further Reading

- **[METHODOLOGY.md](METHODOLOGY.md)**: Deep dive into Phase-Based Development, TDD, command workflows
- **[QUICKSTART.md](QUICKSTART.md)**: Step-by-step guides for all three workflows
- **[ADAPTATION_GUIDE.md](ADAPTATION_GUIDE.md)**: How to create custom stacks for any language/framework

---

## Quick Wins

**"I want to start a Python project"**
```
@setup-stack → python-fastapi → @architect "Build X" → @start-session
```

**"I want to start a Ruby project"**
```
Create stacks/ruby-rails/ → @setup-stack → select ruby-rails → @architect plan.md
```

**"I have an existing Flask project"**
```
Copy .cursor/ → @detect-stack → Yes to save stack → @start-session
```

**That's it! You're ready to build with AI assistance. 🚀**
