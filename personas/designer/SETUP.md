# Designer Persona: Pre-Class Setup

Complete every item below before class. The instructor cannot wait for tool installation during the session. No Figma account is needed: the course works from `tokens/tokens.json` and markdown screen specs.

## 1. Cursor

Install **Cursor IDE**: https://cursor.sh

Verify it launches and can open the course repo directory.

## 2. Node.js 20+

Required for the `designer-react-tokens` stack (Vite, Storybook, the token build script) and Playwright.

| Tool | Version | Verify with |
|---|---|---|
| Node.js | 20+ | `node --version` |
| npm | 9+ | `npm --version` |

Install Node.js from https://nodejs.org/en/download if needed.

## 3. Browser (Chromium for Playwright)

The `responsive-checker` subagent uses Playwright to capture breakpoint screenshots.

```bash
npx playwright install chromium
```

Verify: `npx playwright --version`

## 4. Repository access

Clone the course repo if you have not already:

```bash
git clone https://github.com/axel-sirota/cursor-course-templates
cd cursor-course-templates
```

## 5. Smoke test

Open the repo in Cursor and run in the chat:

```
/set-persona add designer
/setup-stack designer
```

After the first command you should see a confirmation listing the designer commands, subagents, hooks, MCP servers (`playwright`, `context7`) and the new `workspaces/designer/` folder. After the second, the `## Persona: designer` block in `.cursor/context.md` should show `Stack: designer-react-tokens`.

If either step fails, contact the instructor before class.

## Optional: Figma

Only do this if you want to try `/designer-extract <figma-frame-url>`. The default path does not use it.

1. Create a personal access token at https://www.figma.com/developers/api#access-tokens with scope **File content** (read-only). It starts with `figd_`.
2. Add it to `.env` in the repo root (if `personas/designer/.env.example` exists, copy it first: `cp personas/designer/.env.example .env`):

   ```
   FIGMA_ACCESS_TOKEN=figd_...
   ```

3. Add this server to the `mcpServers` object in `.cursor/mcp.json`:

   ```json
   "figma": {
     "command": "npx",
     "args": ["-y", "figma-developer-mcp", "--figma-api-key=${FIGMA_ACCESS_TOKEN}", "--stdio"],
     "env": {}
   }
   ```

4. Restart Cursor and check the `figma` server shows as connected in Cursor's MCP settings.

`figma-developer-mcp` calls the Figma REST API with your token, so the Figma desktop app is not required. (Figma's own Dev Mode MCP server is a different server that runs inside the desktop app; this pack does not use it.)

`/undo persona designer` does not remove a server you added by hand. Delete the `figma` entry yourself if you no longer want it.
