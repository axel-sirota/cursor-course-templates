# Designer Persona — Pre-Class Setup

Complete every item below before class. The instructor cannot wait for tool installation during the session.

## 1. AI code assistant

Install one of:
- **Cursor IDE:** https://cursor.sh
- **Claude Code:** https://docs.anthropic.com/en/docs/claude-code/overview

Verify it launches and can open the course repo directory.

## 2. Figma desktop app

The designer persona uses Figma's Dev Mode MCP Server, which requires the desktop app — the browser version does not expose the MCP server.

1. Download and install Figma Desktop: https://www.figma.com/downloads/
2. Sign in to your Figma account.
3. Open **Figma → Preferences** (macOS: `Cmd+,` / Windows: `Ctrl+,`)
4. Navigate to the **Dev Mode** or **Integrations** section.
5. Enable **Dev Mode MCP Server** and note the local port it listens on (default: `3845`).

Verify: with the desktop app open, `curl http://localhost:3845/health` (or the port shown in Preferences) should return a JSON response.

## 3. Figma access token

The MCP server authenticates API calls using a personal access token.

1. Go to https://www.figma.com/developers/api#access-tokens
2. Click **Create new token** — scope: **File content** (read-only is sufficient).
3. Copy the token (starts with `figd_`).

You will add this token to `.env` in the next step.

## 4. Environment variables

Copy the persona env file to the project root and fill in your values:

```bash
cp personas/designer/.env.example .env
```

Then edit `.env` and set `FIGMA_ACCESS_TOKEN` to the token you just generated.

If your instructor provided a `client-config/` directory, also check `client-config/env.example` for an org-level token.

## 5. Node.js 20+

Required to run the Figma MCP server and Playwright.

| Tool | Version | Verify with |
|---|---|---|
| Node.js | 20+ | `node --version` |
| npm | 9+ | `npm --version` |

Install Node.js from https://nodejs.org/en/download if needed.

## 6. Browser (Chrome / Chromium for Playwright)

The `responsive-checker` subagent uses Playwright to capture breakpoint screenshots.

```bash
npx playwright install chromium
```

Verify: `npx playwright --version`

## 7. Repository access

Clone the course repo if you have not already:

```bash
git clone https://github.com/axel-sirota/cursor-course-templates
cd cursor-course-templates
```

If your instructor provided a `client-config.zip`, unzip it into the repo root:

```bash
unzip ~/client-config.zip
# should create client-config/ in the repo root
```

## 8. Smoke test

With the Figma desktop app open and your `.env` populated, open your AI tool and run:

- **Cursor:** `@set-persona`
- **Claude Code:** `/set-persona`

Pick `designer`. You should see a confirmation listing the designer commands, subagents, hooks, and MCP servers — including `figma` in the MCP list.

If the Figma MCP does not appear or shows an error, confirm the desktop app is running with Dev Mode MCP enabled and that `FIGMA_ACCESS_TOKEN` is set in `.env`.

If any step fails, contact the instructor before class.
