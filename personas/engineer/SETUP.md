# Engineer Persona: Pre-Class Setup

Complete every item below before class. The instructor cannot wait for tool installation during the session.

## 1. Cursor

Install **Cursor IDE**: https://cursor.sh

Verify it launches and can open the course repo directory.

## 2. Programming language

Install the language for the stack you plan to use:

| Language | Version | Verify with | Stacks |
|---|---|---|---|
| Python | 3.11+ | `python3 --version` | python-fastapi |
| Node.js | 20+ | `node --version` | node-express, node-nestjs |
| Go | 1.22+ | `go version` | go-gin, go-grpc |
| Java | 21 | `java --version` | java-spring |

Also install the package manager for your language (`pip`/`venv`, `npm`, standard for Go/Java).

## 3. Git

Install Git and configure your identity:

```bash
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
```

Verify: `git --version`

## 4. Docker (optional but recommended)

Required if your stack runs a containerized PostgreSQL database (python-fastapi, node-express).

Install Docker Desktop: https://www.docker.com/products/docker-desktop/

Verify: `docker --version` and `docker compose version`

## 5. MCP credentials

Create a `.env` file in the repo root (if `personas/engineer/.env.example` exists, copy it: `cp personas/engineer/.env.example .env`) and fill in:

- **Required:** `GITHUB_PAT`, a GitHub personal access token with `repo` scope
  - Generate at: https://github.com/settings/tokens
- **Optional:** `SENTRY_AUTH_TOKEN` and `SENTRY_ORG_SLUG`, only if your project uses Sentry
- **Optional:** `DATABASE_URL`, only if you connect to an external Postgres instance

The course uses synthetic data only. Never point these at production systems.

## 6. Repository access

Clone the course repo:

```bash
git clone https://github.com/axel-sirota/cursor-course-templates
cd cursor-course-templates
```

## 7. Smoke test

Open the repo in Cursor and run in the chat:

```
/set-persona add engineer
/setup-stack engineer
```

After the first command you should see a confirmation listing the engineer commands, subagents, hooks, MCP servers and the new `workspaces/engineer/` folder. Pick `python-fastapi` (or your stack) at the second; you should see the stack configured in the `## Persona: engineer` block of `.cursor/context.md`.

If either step fails, contact the instructor before class.
