# Engineer Persona — Pre-Class Setup

Complete every item below before class. The instructor cannot wait for tool installation during the session.

## 1. AI code assistant

Install one of:
- **Cursor IDE:** https://cursor.sh
- **Claude Code:** https://docs.anthropic.com/en/docs/claude-code/overview

Verify it launches and can open the course repo directory.

## 2. Programming language

Install whichever you plan to use during class:

| Language | Version | Verify with |
|---|---|---|
| Python | 3.11+ | `python3 --version` |
| Node.js | 20+ | `node --version` |
| Go | 1.22+ | `go version` |
| Java | 21 | `java --version` |

Also install the package manager for your language (`pip`/`venv`, `npm`, standard for Go/Java).

## 3. Git

Install Git and configure your identity:

```bash
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
```

Verify: `git --version`

## 4. Docker (optional but recommended)

Required if you plan to use the Python FastAPI or Node Express stacks, which run a containerized PostgreSQL database.

Install Docker Desktop: https://www.docker.com/products/docker-desktop/

Verify: `docker --version` and `docker compose version`

## 5. MCP credentials

Copy the persona env file to the project root and fill in your values:

```bash
cp personas/engineer/.env.example .env
```

Then edit `.env`:
- **Required:** `GITHUB_PAT` — GitHub personal access token with `repo` scope
  - Generate at: https://github.com/settings/tokens
- **Optional:** `SENTRY_AUTH_TOKEN` and `SENTRY_ORG_SLUG` — only if your project uses Sentry
- **Optional:** `DATABASE_URL` — only if your project connects to an external Postgres instance

If your instructor provided a `client-config/` directory, also check `client-config/env.example` for org-specific variables.

## 6. Repository access

Clone the course repo:

```bash
git clone https://github.com/axel-sirota/cursor-course-templates
cd cursor-course-templates
```

If your instructor provided a `client-config.zip`, unzip it into the repo root:

```bash
unzip ~/client-config.zip
# should create client-config/ in the repo root
```

## 7. Smoke test

In the repo root, open your AI tool and run:

- **Cursor:** `@set-persona`
- **Claude Code:** `/set-persona`

Pick `engineer`. You should see a confirmation listing the engineer commands, subagents, hooks, and MCP servers.

Then run `/setup-stack` and pick `blank`. You should see a confirmation that the blank stack is configured alongside the engineer persona.

If either step fails, contact the instructor before class.
