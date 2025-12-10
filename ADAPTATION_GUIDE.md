# Adaptation Guide: Creating and Porting Stacks

This repository is designed to be a **Universal Template**. While it comes with several pre-built stacks (Python FastAPI, Node Express, Java Spring, Go Gin, DevOps Terraform), it is built to support *any* language or framework through custom stack creation.

**This guide covers all three core workflows and how to create custom stacks for each.**

---

## Overview: Three Paths to Stack Creation

| Workflow | Scenario | Stack Creation Method | Where Stack Lives |
|----------|----------|----------------------|-------------------|
| **Workflow 1** | Fresh project with known stack | Use pre-built stack from `stacks/` library | `stacks/{name}/` (already exists) |
| **Workflow 2** | Fresh project with custom stack | Manually create new stack in `stacks/` | `stacks/{name}/` (you create it) |
| **Workflow 3** | Existing codebase (brownfield) | AI detects and generates stack | Context file only, or optionally `stacks/detected-{name}/` |

---

## Workflow 1: Using Pre-Built Stacks

**No adaptation needed** - these stacks are ready to use out of the box.

### Available Pre-Built Stacks

```bash
stacks/
├── python-fastapi/      # REST API with PostgreSQL, SQLAlchemy, Pytest
├── node-express/        # TypeScript API with Prisma
├── java-spring/         # Enterprise Java with JPA
├── go-gin/             # High-performance Go API
├── devops-terraform/   # Infrastructure as Code
└── blank/              # Minimal template for custom stacks
```

### Using a Pre-Built Stack

1. Clone the template
2. Run setup command:
   - **Cursor**: `@setup-stack`
   - **Claude Code**: `/setup-stack`
3. Select stack from the list
4. AI copies rules, context, templates, and vibe guides

**That's it!** You're ready to use `@architect` or `/architect`.

---

## Workflow 2: Creating a Custom Stack from Scratch

**Best for:** Building with a technology stack not in the template library (Ruby on Rails, Elixir Phoenix, Kotlin Spring, Rust Axum, etc.).

### Step-by-Step Guide

#### 1. Create the Stack Directory Structure

```bash
mkdir -p stacks/my-stack/rules
mkdir -p stacks/my-stack/templates  # Optional
mkdir -p stacks/my-stack/examples   # Optional
mkdir -p stacks/my-stack/vibe       # Optional
```

**Example for Ruby on Rails:**

```bash
mkdir -p stacks/ruby-rails/rules
mkdir -p stacks/ruby-rails/templates
mkdir -p stacks/ruby-rails/vibe
```

#### 2. Define the Stack Context

Create `stacks/my-stack/context.md`. This is the **brain** of your stack - it tells the AI how to behave.

**Minimal Template:**

```markdown
# Project Context: [Stack Name]

## Tech Stack
- Language: [Language + Version]
- Framework: [Framework]
- Database: [Database]
- Testing: [Test Framework]
- Linting: [Linter/Formatter]

## Vibe & Style
- Coding Style: [camelCase/snake_case/PascalCase]
- Architecture: [MVC/Layered/Hexagonal/Microservices/etc.]

## Key Rules
- [Core rule 1: e.g., "Use async/await, never callbacks"]
- [Core rule 2: e.g., "TDD required for all business logic"]
- [Core rule 3: e.g., "No business logic in controllers"]

## Active Phase
- Current: Phase 0 (Skeleton)
```

**Real Example (Ruby on Rails):**

```markdown
# Project Context: Ruby on Rails

## Tech Stack
- Language: Ruby 3.2+
- Framework: Rails 7.1
- Database: PostgreSQL (ActiveRecord)
- Testing: RSpec
- Linting: RuboCop

## Vibe & Style
- Coding Style: snake_case for methods/variables, PascalCase for classes
- Architecture: MVC with Service Objects

## Key Rules
- Use strong parameters for all controller inputs
- Business logic belongs in Service Objects, not models
- TDD: Write RSpec tests before implementation
- Follow Rails conventions ("Convention over Configuration")

## Active Phase
- Current: Phase 0 (Skeleton)
```

#### 3. Create Stack Rules

Create `.mdc` files in `stacks/my-stack/rules/`. These enforce coding standards and workflow.

**Common rule files:**

- `000-core-workflow.mdc`: Phase-based development rules
- `100-style.mdc`: Naming conventions, formatting
- `200-testing.mdc`: TDD rules, test structure
- `300-architecture.mdc`: Layering, separation of concerns
- `400-security.mdc`: Security best practices

**Example: `stacks/ruby-rails/rules/100-style.mdc`**

```markdown
---
description: Ruby on Rails coding standards
alwaysApply: true
---

# Ruby on Rails Style Guide

## Naming Conventions
- Use `snake_case` for methods, variables, and file names
- Use `PascalCase` for classes and modules
- Use `SCREAMING_SNAKE_CASE` for constants

## Code Organization
- Controllers handle HTTP only, delegate to Service Objects
- Models contain associations and scopes, not business logic
- Service Objects live in `app/services/`
- Use `rails generate` for consistency

## Rails Conventions
- Follow RESTful routing patterns
- Use strong parameters in all controllers
- Leverage ActiveRecord callbacks sparingly
- Prefer composition over inheritance
```

**Example: `stacks/ruby-rails/rules/200-testing.mdc`**

```markdown
---
description: RSpec testing standards
alwaysApply: true
---

# Testing with RSpec

## TDD Workflow
- Write RSpec tests BEFORE implementation
- Tests must fail initially (Red)
- Implement minimal code to pass (Green)
- Refactor while keeping tests green

## Test Structure
- Request specs in `spec/requests/`
- Model specs in `spec/models/`
- Service specs in `spec/services/`
- Use `FactoryBot` for test data
- Use `describe/context/it` blocks

## Test Quality
- Each spec should test ONE behavior
- Use meaningful descriptions
- Avoid testing Rails framework code
- Mock external dependencies
```

See `stacks/python-fastapi/rules/` for comprehensive examples you can adapt.

#### 4. Optional: Add Templates

Create scaffolding files in `stacks/my-stack/templates/` that will be copied to the project root during setup.

**Example: `stacks/ruby-rails/templates/`**

```
templates/
├── .env.example
├── docker-compose.yml
├── Gemfile
├── config/
│   └── database.yml
└── spec/
    └── rails_helper.rb
```

#### 5. Optional: Add Examples

Create reference implementations in `stacks/my-stack/examples/`.

**Example: `stacks/ruby-rails/examples/`**

```
examples/
├── auth-example/
│   ├── app/controllers/sessions_controller.rb
│   ├── app/services/authentication_service.rb
│   └── spec/requests/sessions_spec.rb
└── crud-example/
    ├── app/controllers/posts_controller.rb
    └── spec/requests/posts_spec.rb
```

#### 6. Optional: Add Vibe Guides

Create documentation in `stacks/my-stack/vibe/` to guide development.

**Example: `stacks/ruby-rails/vibe/`**

```
vibe/
├── phase_workflow.md       # Phase-based development for Rails
├── service_objects.md      # How to structure service objects
├── testing_patterns.md     # RSpec patterns and best practices
└── deployment.md          # Deploying Rails to production
```

#### 7. Use Your New Stack

1. Open your AI tool (Cursor or Claude Code)
2. Run setup command: `@setup-stack` or `/setup-stack`
3. Select your new stack from the list
4. AI copies your rules, context, and templates
5. Start building: `@architect` or `/architect`

---

## Workflow 3: Adapting Existing Codebases (Brownfield)

**Best for:** Legacy projects, existing codebases, or when you want the AI to learn your existing patterns.

### Approach 1: AI-Generated Context Only (Quick Start)

**Use when:** You just want to add AI assistance to an existing project without creating a reusable stack.

#### Steps:

1. **Copy Configuration Files**

   **For Cursor IDE:**
   ```bash
   cd /path/to/your-existing-project
   cp -r /path/to/cursor-course-templates/.cursor .
   ```

   **For Claude Code:**
   ```bash
   cd /path/to/your-existing-project
   cp -r /path/to/cursor-course-templates/.claude .
   cp /path/to/cursor-course-templates/CLAUDE.md .
   ```

2. **Run Stack Detection**

   - **Cursor**: `@detect-stack`
   - **Claude Code**: `/detect-stack`

   The AI will:
   - Scan for `package.json`, `requirements.txt`, `go.mod`, `pom.xml`, etc.
   - Analyze 2-3 representative source files
   - Extract coding style, architecture, and testing patterns
   - Generate a custom context file (`.cursor/context.md` or `CLAUDE.md`)

3. **Review Generated Context**

   Open the context file and verify:
   - Tech stack is correct
   - Coding style matches your codebase
   - Architecture pattern is accurate

4. **Set Strictness Level**

   **Critical for brownfield:** Set `Strictness: Low`

   ```markdown
   ## Strictness: Low
   - Refactoring: Only touch what is necessary
   - New Code: Apply full standards to new features only
   - Legacy Code: Document issues but don't force refactoring
   ```

   This tells the AI:
   - Don't refactor existing code
   - Apply standards only to NEW code
   - Respect existing patterns in legacy code

5. **Start Working**

   - **Cursor**: `@start-session`
   - **Claude Code**: `/start-session`

   The AI will now respect your existing codebase while writing clean new features.

**Pros:**
- Fast setup (5 minutes)
- No manual stack creation needed
- Context lives in your project only

**Cons:**
- Not reusable for future projects
- Context is project-specific

### Approach 2: Create Reusable Stack from Detection (Best Practice)

**Use when:** You want to reuse the detected configuration for future projects with the same stack.

#### Steps:

1. **Follow Approach 1** to generate initial context

2. **Create Stack Structure**

   After `detect-stack` generates your context, create a reusable stack:

   ```bash
   # Assuming AI detected "Python 3.9 + Flask"
   mkdir -p stacks/python-flask/rules
   ```

3. **Extract Context to Stack**

   Copy the generated context:

   **From Cursor:**
   ```bash
   cp .cursor/context.md stacks/python-flask/context.md
   ```

   **From Claude Code:**
   ```bash
   cp CLAUDE.md stacks/python-flask/context.md
   ```

4. **Create Rules Based on Detection**

   The AI's detection should have identified patterns. Codify them:

   ```bash
   # Create style rule matching detected patterns
   cat > stacks/python-flask/rules/100-style.mdc <<EOF
   ---
   description: Flask coding standards (detected from codebase)
   alwaysApply: true
   ---

   # Flask Style Guide

   ## Detected Patterns
   - Naming: snake_case (detected in 95% of codebase)
   - Architecture: Blueprint-based (detected in app/ structure)
   - Testing: Pytest with fixtures (detected in tests/)

   ## Rules
   - Continue using Blueprints for route organization
   - Use Flask-SQLAlchemy for database operations
   - Write pytest tests for new features
   EOF
   ```

5. **Optional: Refine and Add TDD Rules**

   Even if legacy code doesn't follow TDD, enforce it for NEW code:

   ```bash
   cat > stacks/python-flask/rules/200-testing.mdc <<EOF
   ---
   description: Testing standards for new code
   alwaysApply: true
   ---

   # Testing Rules (New Code Only)

   ## TDD for New Features
   - All NEW endpoints require pytest tests first
   - Legacy code: tests optional but encouraged
   - Use pytest fixtures for test data
   EOF
   ```

6. **Commit Stack to Template Repository**

   ```bash
   cd /path/to/cursor-course-templates
   # Copy your new stack
   cp -r /path/to/your-project/stacks/python-flask stacks/

   git add stacks/python-flask
   git commit -m "Add Python Flask stack (detected from legacy project)"
   git push
   ```

7. **Reuse for Future Projects**

   Now your "python-flask" stack is available in Workflow 1 for any future Flask projects!

**Pros:**
- Reusable for future projects
- Codifies your existing patterns
- Can be shared with team

**Cons:**
- Takes longer to set up (30 minutes)
- Requires manual rule creation

---

## Concept Mapping: Adapting Patterns Across Stacks

When porting the methodology to a new stack, map these core concepts:

| Concept | Python (Ref) | Node.js | Java Spring | Go Gin | Ruby Rails | DevOps |
|---------|-------------|---------|-------------|---------|------------|--------|
| **Skeleton** | Mock Routes | Mock Routes | Mock Controllers | Mock Handlers | Mock Actions | `terraform plan` |
| **Models** | Pydantic | Zod | JPA Entities | Go Structs | ActiveRecord | `variables.tf` |
| **Repository** | SQLAlchemy | Prisma | JpaRepository | GORM | ActiveRecord | Modules |
| **Tests** | Pytest | Jest | JUnit 5 | `testing` | RSpec | `tflint`/`checkov` |
| **Entry Point** | `main.py` | `server.ts` | `Application.java` | `main.go` | `config.ru` | `main.tf` |
| **DI/Services** | FastAPI `Depends` | InversifyJS | `@Autowired` | Interfaces | Service Objects | N/A |

### Example: Porting "Repository Pattern" to Rails

**Python FastAPI:**
```python
class UserRepository:
    async def get_by_id(self, user_id: int) -> User:
        return await db.query(User).filter(User.id == user_id).first()
```

**Ruby on Rails Equivalent:**
```ruby
class UserRepository
  def self.find_by_id(user_id)
    User.find(user_id)
  end
end
```

**Stack Rule:** Document this mapping in `stacks/ruby-rails/vibe/architecture.md`.

---

## Best Practices for Stack Creation

### 1. Start with Blank Template

Use `stacks/blank/` as your starting point - it has the minimal required structure.

```bash
cp -r stacks/blank stacks/my-new-stack
cd stacks/my-new-stack
# Edit context.md and rules/
```

### 2. Study Existing Stacks

Before creating rules, study `stacks/python-fastapi/rules/` - it's the reference implementation with comprehensive examples.

### 3. Incremental Rule Creation

Don't create all rules at once:

1. Start with minimal `context.md` and one `style.mdc` rule
2. Use the stack for a small project
3. Add rules as needed when you encounter gaps
4. Iterate based on real usage

### 4. Rule Naming Convention

Use numeric prefixes to control rule loading order:

```
000-core-workflow.mdc     # Load first (always)
100-style.mdc            # General style
200-testing.mdc          # Testing rules
300-architecture.mdc     # Structure rules
400-security.mdc         # Security rules
```

### 5. Vibe Guides Over Rigid Rules

For complex patterns, use vibe guides (`vibe/`) instead of strict rules:

- Rules (`.mdc`): Enforced standards (naming, TDD workflow)
- Vibe guides (`.md`): Patterns and examples (architecture decisions, design patterns)

### 6. Document Deviations from Framework Conventions

If your stack intentionally deviates from framework conventions, document WHY:

```markdown
## Deviations from Rails Conventions

- **Service Objects**: Rails doesn't have a standard location. We use `app/services/` to separate business logic from models.
- **Why**: Models were becoming too large. Service Objects improve testability.
```

### 7. Test Your Stack Before Committing

Create a small test project using your new stack:

1. Run `@setup-stack` and select your stack
2. Run `@architect "Build a simple CRUD API"`
3. Verify AI generates correct code
4. Check if rules are respected
5. Iterate on context.md and rules as needed

---

## Sharing Stacks with Your Team

Once you've created a custom stack, share it:

### Option 1: Commit to Template Repository

```bash
cd cursor-course-templates
git add stacks/my-stack
git commit -m "Add custom stack for [Technology]"
git push
```

Team members pull latest template and have access to the stack.

### Option 2: Stack as Separate Repository

For organization-wide stacks:

```bash
# Create a separate repo
git init cursor-stacks
cd cursor-stacks

# Structure
mkdir -p stacks/company-python-api
mkdir -p stacks/company-react-app

# Teammates clone and copy
git clone git@company.com/cursor-stacks.git
cp -r cursor-stacks/stacks/* cursor-course-templates/stacks/
```

### Option 3: Share Single Stack

Share just one stack via zip or gist:

```bash
cd stacks
tar -czf ruby-rails.tar.gz ruby-rails/
# Share ruby-rails.tar.gz

# Teammate extracts
cd cursor-course-templates/stacks
tar -xzf ruby-rails.tar.gz
```

---

## Troubleshooting Stack Creation

### AI Doesn't Respect My Rules

**Problem:** AI ignores rules in `.mdc` files.

**Solutions:**
1. Check rule has `alwaysApply: true` in frontmatter
2. Verify rules were copied to `.cursor/rules/` or `.claude/rules/`
3. Run `@start-session` or `/start-session` to reload context
4. Make rules more explicit (avoid vague language)

### AI Suggests Wrong Patterns

**Problem:** AI uses Python patterns in a Node.js project.

**Solutions:**
1. Check `context.md` clearly states the language/framework
2. Add explicit rule: "NEVER use Python syntax in this Node.js project"
3. Add counter-examples in rules showing what NOT to do

### Detect-Stack Misidentifies My Stack

**Problem:** `@detect-stack` thinks Flask project is Django.

**Solutions:**
1. Manually create `context.md` with correct framework
2. Run `@setup-stack` and select "From Plan" option
3. Create a proper stack in `stacks/` for future projects

### Rules Conflict with Each Other

**Problem:** Style rule says "camelCase" but testing rule shows "snake_case" examples.

**Solutions:**
1. Review all `.mdc` files for consistency
2. Use a single source of truth (context.md) for style decisions
3. Reference context.md in rules: "Follow naming from context.md"

---

## Summary: Which Approach to Use?

| Scenario | Recommended Workflow | Stack Creation Method |
|----------|---------------------|----------------------|
| New project, pre-built stack exists | **Workflow 1** | Use existing stack from `stacks/` |
| New project, stack doesn't exist | **Workflow 2** | Create custom stack manually |
| Legacy codebase, one-time use | **Workflow 3 Approach 1** | AI-generated context only |
| Legacy codebase, reuse for future | **Workflow 3 Approach 2** | Extract detected stack to `stacks/` |
| Team sharing custom stack | **Workflow 2** + commit to repo | Create reusable stack |

**Pro tip:** Start with Workflow 1 (known stack) to learn the methodology. Then try Workflow 2 (custom stack) for your specific needs. Save Workflow 3 (brownfield) for legacy codebases.

---

## Need Help?

- **Examples**: Check `stacks/python-fastapi/` for comprehensive reference implementation
- **Minimal Example**: Check `stacks/blank/` for minimal required structure
- **Methodology**: Read [METHODOLOGY.md](METHODOLOGY.md) to understand command workflows
- **Quick Start**: Read [QUICKSTART.md](QUICKSTART.md) for step-by-step guides
