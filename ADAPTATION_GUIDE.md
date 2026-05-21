# Adaptation Guide

This template can adapt to any existing repo or be extended with new stacks. Most students need the first section; the handbook below is for advanced customization.

---

## Quick Reference — Adapt your existing repo in 4 commands

You have a real codebase. You want AI-assisted development to know your stack and respect your patterns. Run these in order:

```bash
# 1. Copy the AI configuration into your repo
cd /path/to/your-existing-repo
cp -r /path/to/cursor-course-templates/.claude .       # for Claude Code
cp /path/to/cursor-course-templates/CLAUDE.md .        #   (and CLAUDE.md)
# OR:
cp -r /path/to/cursor-course-templates/.cursor .       # for Cursor IDE

# 2. Pick your persona
/set-persona            # then choose: engineer, designer, pm, data-scientist, devops

# 3. Detect and configure the stack from your existing code
/detect-stack           # scans your repo, generates context + rules from observed patterns

# 4. Start working
/architect "describe what you want to build"
/start-session
```

That's it. The whole pipeline is `/set-persona → /setup-stack OR /detect-stack → /architect → /start-session → /next-session`.

**When to use `/detect-stack` vs `/setup-stack`:**
- `/detect-stack` — your repo already has code. The AI reads your files and generates a stack config matching what's there.
- `/setup-stack` — empty repo or fresh start. Pick a pre-built stack from the library (`python-fastapi`, `go-gin`, etc.).

**If your stack isn't in the library:** `/setup-stack` will offer a `new` option that scaffolds a custom stack from `stacks/blank/`.

**If something goes wrong or you want to start over:** `/undo persona`, `/undo stack`, or `/undo all` removes installs cleanly.

---

## Handbook — Three Workflows in Depth

For deeper customization, here are the three workflows in detail.

| Workflow | Scenario | Stack Creation Method | Where Stack Lives |
|----------|----------|----------------------|-------------------|
| **Workflow 1** | Fresh project with known stack | Use pre-built stack from `stacks/` library | `stacks/{name}/` (already exists) |
| **Workflow 2** | Fresh project with custom stack | Manually create new stack in `stacks/` | `stacks/{name}/` (you create it) |
| **Workflow 3** | Existing codebase (brownfield) | AI detects and generates stack | Context file only, or optionally `stacks/detected-{name}/` |

### Per-stack folder shape

Every stack under `stacks/{name}/` has exactly this shape:

```
stacks/{name}/
├── context.md      # Tech stack, key rules, vibe & style (the brain)
├── rules/          # Numbered .mdc rules (000-, 100-, 200-, ...). Enforced standards.
├── templates/      # Files copied to project root on install (boilerplate, guides, scaffolding code)
└── examples/       # Reference code samples — NOT copied, just for reading
```

The `templates/` directory holds everything that the install copies into the project root: starter code, walkthroughs, phase checklists, anything the student should see in their working tree. The `examples/` directory holds reference snippets that stay in the stack library for browsing.

(Earlier versions had a separate `vibe/` directory. As of 2026-05-21 it's been merged into `templates/` — the `vibe_*.md` files are now alongside the other templates.)

### Rule numbering convention

Rules use numeric prefixes so they load in a predictable order:

| Prefix | Purpose |
|--------|---------|
| `000-` | Core workflow (phase-based development, TDD, session loop) |
| `100-` | Architecture (layering, modules, separation of concerns) |
| `200-` | Testing (TDD rules, test structure, fixtures) |
| `300-` | Style (naming, formatting, framework idioms) |
| `400-` | Standards (security, conventions, best practices) |
| `500-` | Implementation / infra (Docker, CI, deployment) |
| `600-` | Phase transition / lifecycle |

Within a tier, use `001-`, `002-`, etc. to avoid collisions (see `stacks/python-fastapi/rules/` for the reference layout).

---

## Workflow 1: Using a Pre-Built Stack

**No adaptation needed** — these stacks are ready to use out of the box.

### Available pre-built stacks (14)

```
stacks/
├── python-fastapi/           # REST API with PostgreSQL, SQLAlchemy, Pytest
├── go-gin/                   # High-performance Go REST API
├── go-grpc/                  # Go gRPC service
├── java-spring/              # Enterprise Java with JPA
├── node-express/             # TypeScript API with Prisma
├── node-nestjs/              # Enterprise Node with DI + Swagger
├── python-datascience/       # Notebooks + sklearn + MLflow
├── python-spark/             # PySpark + Delta Lake
├── python-dbt-snowflake/     # SQL-first transformations
├── python-mlops/             # MLflow training + FastAPI serving
├── r-tidyverse/              # R + tidymodels + Quarto + Plumber
├── devops-terraform/         # Cloud Infrastructure as Code
├── devops-ansible/           # Configuration management
├── devops-k8s-helm/          # Kubernetes GitOps with ArgoCD
└── blank/                    # Empty scaffold for custom stacks
```

### Use one

```
/set-persona            # pick engineer / data-scientist / devops as appropriate
/setup-stack            # pick a stack from the menu
/architect "Build X"    # design the phases and session plan
/start-session          # begin executing
```

---

## Workflow 2: Creating a Custom Stack from Scratch

**Best for:** Building with a technology stack not in the library (Ruby on Rails, Elixir Phoenix, Kotlin Spring, Rust Axum, etc.).

### Option A: via the `new` escape hatch (recommended)

When you run `/setup-stack` and pick a stack that isn't in the list, it offers:

```
That stack is not available for the {persona} persona. You have three options:
  1. Choose a different stack from the list above.
  2. Type `new` to create a custom stack — I'll walk you through scaffolding ...
  3. Type `cancel` to abort.
```

Pick `new` and the command will copy `stacks/blank/` to `stacks/{your-name}/`, scaffold the standard subdirs, and prompt you to fill in `context.md`. Then it continues with the normal install.

### Option B: manually create the stack directory

Do this if you want to author a stack offline first.

#### 1. Create the directory structure

```bash
mkdir -p stacks/my-stack/{rules,templates,examples}
cp stacks/blank/context.md stacks/my-stack/context.md   # start from blank scaffold
```

#### 2. Define the stack context

Edit `stacks/my-stack/context.md`. This is the **brain** of your stack:

```markdown
# Project Context: My Stack

## Tech Stack
- Language: [Language + Version]
- Framework: [Framework]
- Database: [Database]
- Testing: [Test Framework]
- Linting: [Linter/Formatter]

## Vibe & Style
- Coding Style: [camelCase/snake_case/PascalCase]
- Architecture: [MVC/Layered/Hexagonal/etc.]

## Architecture Shape
[One of: REST API / gRPC Service / Data Pipeline / Analytics Model /
 Statistical Computing / IaC Playbook / GitOps Platform / Cloud Infrastructure /
 Experiment Notebook / Custom]

## Key Rules
- [Core rule 1]
- [Core rule 2]
- [Core rule 3]

## Active Phase
- Current: Phase 0 (Skeleton)
```

The `## Architecture Shape` field is what `/architect` reads to know which interface contract to design.

#### 3. Create stack rules

Create `.mdc` files in `stacks/my-stack/rules/` using the numbering convention (`000-`, `100-`, etc.). Each rule has YAML frontmatter:

```markdown
---
description: My Stack coding standards
alwaysApply: true
---

# My Stack Style Guide
...
```

Reference: `stacks/python-fastapi/rules/` has the most complete example set.

#### 4. Optional: add templates

Anything in `stacks/my-stack/templates/` gets copied to the project root on `/setup-stack`. This is where boilerplate code, walkthroughs, phase checklists, and explanatory guides go. Use the `vibe_*.md` naming convention for walkthrough docs to keep them visually distinct from scaffolding code.

#### 5. Optional: add examples

`stacks/my-stack/examples/` holds reference code samples that stay in the library (not copied into projects). Use this for "look how someone built X in this stack" reference material.

#### 6. Use your new stack

```
/setup-stack            # your stack now appears in the menu
/architect "Build X"
```

---

## Workflow 3: Adapting an Existing Codebase (Brownfield)

**Best for:** Legacy projects, existing codebases, or when you want the AI to learn your existing patterns.

### Approach 1: AI-generated context only (quick start)

```bash
cd /path/to/your-existing-project
cp -r /path/to/cursor-course-templates/.claude .
cp /path/to/cursor-course-templates/CLAUDE.md .

/set-persona            # required
/detect-stack           # scans repo, generates context + rules
```

`/detect-stack` will:
- Scan for `package.json`, `requirements.txt`, `go.mod`, `pom.xml`, etc.
- Analyze 2-3 representative source files
- Extract coding style, architecture, and testing patterns
- Generate a custom context file (`CLAUDE.md`)

Then verify the generated context and set `Strictness: Low` if it's a legacy codebase (legacy code shouldn't be force-refactored).

### Approach 2: extract a reusable stack from detection

If you want to reuse the detected config across multiple projects with the same stack:

1. Run Approach 1 first.
2. Copy the generated context into a new stack:
   ```bash
   mkdir -p stacks/my-detected-stack/{rules,templates,examples}
   cp CLAUDE.md stacks/my-detected-stack/context.md
   ```
3. Codify the detected patterns as `.mdc` rules in `stacks/my-detected-stack/rules/` using the standard numbering.
4. Commit the stack to share with your team.

Now your detected stack is reusable via `/setup-stack` for future projects.

---

## Best Practices

### 1. Start from `stacks/blank/`

Don't write a stack from a blank file — `cp -r stacks/blank stacks/my-new-stack` first. It already has the standard 4-folder shape.

### 2. Study `stacks/python-fastapi/` as the reference

It's the most complete stack: 10 numbered rules, full `templates/` with both code scaffolding and `vibe_*.md` walkthroughs, plus `examples/`.

### 3. Incremental rule creation

Don't write all rules at once:
1. Start with minimal `context.md` and one `100-style.mdc` rule.
2. Use the stack for a small project.
3. Add rules as gaps appear in real usage.

### 4. Document deviations from framework conventions

If your stack intentionally deviates from a framework's defaults, document WHY in a `vibe_*.md` walkthrough inside `templates/`. The rule says what; the walkthrough says why.

### 5. Test your stack before committing

```
/setup-stack                # pick your new stack
/architect "Build a simple CRUD app"
```
Verify the AI generates code matching your rules. Iterate on `context.md` and `rules/` based on what you see.

---

## Sharing Stacks

### Option 1: Commit to this repo

```bash
git add stacks/my-stack && git commit -m "Add my-stack" && git push
```
Team members pull and have access.

### Option 2: As a separate repo

For org-wide stacks, keep them in a `org-stacks` repo and rsync into `stacks/` on demand.

### Option 3: Single-stack tarball

```bash
cd stacks && tar -czf my-stack.tar.gz my-stack/
# share my-stack.tar.gz; teammate: tar -xzf my-stack.tar.gz inside stacks/
```

---

## Troubleshooting

| Problem | Solution |
|---|---|
| AI ignores rules | Check `alwaysApply: true` in frontmatter; verify rules are in `.claude/rules/`; run `/start-session` to reload context. |
| AI suggests wrong-framework patterns | Check `context.md` clearly states the language/framework; add explicit "NEVER use X" rules. |
| `/detect-stack` misidentifies stack | Manually edit `CLAUDE.md` with correct framework; create the proper stack in `stacks/` for next time. |
| Rules conflict | Use `context.md` as single source of truth; reference it from rules ("Follow naming from context.md"). |
| Want to undo a `setup-stack` / `set-persona` | Run `/undo stack` or `/undo persona` or `/undo all` — uses manifests to clean up. |

---

## Concept Mapping: Adapting Patterns Across Stacks

When porting the methodology to a new stack, map the core concepts:

| Concept | Python | Node.js | Java Spring | Go Gin | Ruby Rails | DevOps |
|---------|--------|---------|-------------|--------|------------|--------|
| **Skeleton** | Mock routes | Mock routes | Mock controllers | Mock handlers | Mock actions | `terraform plan` |
| **Models** | Pydantic | Zod | JPA Entities | Go structs | ActiveRecord | `variables.tf` |
| **Repository** | SQLAlchemy | Prisma | JpaRepository | GORM | ActiveRecord | Modules |
| **Tests** | Pytest | Jest | JUnit 5 | `testing` | RSpec | `tflint`/`checkov` |
| **Entry point** | `main.py` | `server.ts` | `Application.java` | `main.go` | `config.ru` | `main.tf` |
| **DI / Services** | FastAPI `Depends` | InversifyJS | `@Autowired` | Interfaces | Service Objects | N/A |

---

## Need Help?

- **Reference stack**: `stacks/python-fastapi/` (most complete)
- **Minimal scaffold**: `stacks/blank/` (use as starting point)
- **Methodology**: [METHODOLOGY.md](METHODOLOGY.md) — the principles
- **Quick start**: [QUICKSTART.md](QUICKSTART.md) — first project walkthrough
- **Path picker**: [CHOOSE_YOUR_ADVENTURE.md](CHOOSE_YOUR_ADVENTURE.md) — by role and stack
