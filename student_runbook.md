# Session-Based Development Runbook

**Note:** This runbook uses **Python FastAPI** as the primary example. However, the workflow applies to any stack (Node, Java, Go) supported by the Master Template.

## Project Setup

### 1. Create Project and Virtual Environment
```bash
mkdir project-name
cd project-name

# If using Python:
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Initialize Master Template
Instead of copying files manually, use the Setup Command.

1.  **Open Cursor** in the project root.
2.  **Run Command**:
    ```
    @setup-stack
    ```
3.  **Select Your Stack**:
    - Choose `python-fastapi` to follow this runbook exactly.
    - Choose `node-express`, `java-spring`, etc., to adapt the workflow to those languages.

### 3. Initialize Git
```bash
git init
git add .
git commit -m "Initial setup with Cursor Master Template"
```

### 4. Verify Commands Available
In Cursor, you should see these commands available:
- `@setup-stack` - Configure project rules/context
- `@detect-stack` - Analyze existing code
- `@architect` - API design and session planning
- `@start-session` - Begin session execution
- `@next-session` - Generate session transitions
- `@read` - Read project context
- `@research` - Deep dive problem solving

## Architect Phase

### Design OpenAPI Specification

**Use Command:**
```
@architect [feature name] with these endpoints:
- [List endpoints]
```

**What the Command Does:**
- Reads your specific stack configuration (`.cursor/context.md`)
- Creates comprehensive plan/ folder structure
- Generates API design (OpenAPI for Web, Interface for CLI)
- Creates session plans for each phase

## Session 1: Phase 0 (Skeleton)

### Start Session 1

**Use Command:**
```
@start-session
```
(The Agent will ask which session to start if multiple are planned).

**What the Command Does:**
- Reads `plan/sessions/session-1-phase-0.md`
- Creates complete project structure based on **Your Stack**
- Implements all mock endpoints
- Sets up Docker/Container configuration

### Start Services (Stack Dependent)

**Python**:
```bash
docker-compose up -d
pip install -r requirements.txt
python main.py
```

**Node**:
```bash
npm install
npm run dev
```

**Java**:
```bash
./mvnw spring-boot:run
```

### Verify Skeleton
Visit `http://localhost:8000/docs` (Python) or your stack's equivalent health check.

## Session 2+: Endpoint Implementation

### Starting a Session

**Use Command:**
```
@start-session
```

**What the Command Does:**
- Reads the current session plan
- Implements one endpoint/feature per session
- Uses **TDD (Test-Driven Development)** by default (or Plan-Driven for DevOps)
- Generates session summary

### Session Execution Process

**The @start-session command handles all steps automatically:**

1.  **Verification First**
    - Writes a failing test (Python/Node/Java/Go) OR a Plan (Terraform).
2.  **Domain Models**
    - Creates Entities/Schemas using your stack's ORM (SQLAlchemy, Prisma, JPA, GORM).
3.  **Repository Layer**
    - Implements data access patterns.
4.  **Service Layer**
    - Implements business logic.
5.  **API Endpoint**
    - Connects the Controller/Router to the Service.
6.  **Verification**
    - Runs tests to ensure green state.

### Session Completion

**Commit Changes:**
```bash
git add .
git commit -m "Session N: Phase M - [Description]"
```

## Session Transition

### Generate Next Session Prompt

**Use Command:**
```
@next-session
```

**What the Command Does:**
- Summarizes what was built.
- Updates the Context.
- Generates a prompt to copy-paste for the next time you sit down.

## When Stuck: Deep Research

**Use Command:**
```
@research "How do I implement [X] in [Stack]?"
```

**What the Command Does:**
- Performs a rigorous 3-cycle research process (Hypothesis -> Evidence -> Refutation).
- Outputs a Research Artifact with code examples and trade-offs.
- **Does NOT** modify your code (safe to run anytime).

## Session-Based Workflow Summary

### Quick Start
1.  **@setup-stack** - Initialize the repo.
2.  **@architect** - Design API and create session plans.
3.  **@start-session** - Execute the plan, one session at a time.
4.  **@next-session** - Wrap up and prep for next time.
5.  **@research** - Solve hard problems safely.

## Stack-Specific References

### Python FastAPI
- **Docs**: `http://localhost:8000/docs`
- **Tests**: `pytest`
- **Lint**: `ruff`, `mypy`

### Node Express
- **Docs**: (Configured via Swagger UI if installed)
- **Tests**: `npm test` (Jest)
- **Lint**: `eslint`

### Java Spring Boot
- **Docs**: `http://localhost:8080/swagger-ui.html`
- **Tests**: `./mvnw test`
- **Lint**: `checkstyle`

### Go Gin
- **Docs**: (Swagger if configured)
- **Tests**: `go test ./...`
- **Lint**: `golangci-lint`

### DevOps Terraform
- **Docs**: `terraform-docs`
- **Tests**: `tflint`, `terraform validate`
