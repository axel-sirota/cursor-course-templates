# PM Persona — Pre-Class Setup

Complete every item below before class. The instructor cannot wait for tool installation during the session.

## 1. AI code assistant

Install one of:
- **Cursor IDE:** https://cursor.sh
- **Claude Code:** https://docs.anthropic.com/en/docs/claude-code/overview

Verify it launches and can open the course repo directory.

## 2. Atlassian credentials (Jira + Confluence)

The PM persona uses the Atlassian MCP to create and query Jira tickets and Confluence pages.

### Generate an API token

1. Go to: https://id.atlassian.com/manage-profile/security/api-tokens
2. Click **Create API token**, give it a name (e.g. `cursor-course`), and copy the token value.

### Set environment variables

Copy the env file to the project root and fill in your values:

```bash
cp personas/pm/.env.example .env
```

Then edit `.env`:

| Variable | Value |
|---|---|
| `JIRA_URL` | Your Atlassian base URL — e.g. `https://yourcompany.atlassian.net` |
| `JIRA_USERNAME` | Your Atlassian account email |
| `JIRA_API_TOKEN` | The token you generated above |
| `CONFLUENCE_URL` | Usually `JIRA_URL` + `/wiki` — your instructor confirms |
| `CONFLUENCE_USERNAME` | Same email as `JIRA_USERNAME` |
| `CONFLUENCE_API_TOKEN` | Same token as `JIRA_API_TOKEN` |

Your instructor provides the correct `JIRA_URL` and `CONFLUENCE_URL` for the class environment.

## 3. GitHub Personal Access Token

Required for the GitHub Issues MCP.

1. Go to: https://github.com/settings/tokens
2. Generate a classic token with `repo` scope.
3. Set `GITHUB_PAT` in your `.env` file.

## 4. Optional: Slack and Notion

If your instructor's org uses Slack or Notion:
- Set `SLACK_BOT_TOKEN` — your instructor provides this value.
- Set `NOTION_API_KEY` — your instructor provides this value.

Leave these blank if not needed. The MCP servers will simply not connect.

## 5. Repository access

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

## 6. Smoke test

In the repo root, open your AI tool and run `/set-persona`, then pick `pm`. You should see a confirmation listing the PM commands, subagents, hooks, and MCP servers.

Then test the Atlassian MCP by asking your AI tool to list your Jira projects. If this returns results, your credentials are working.

If any step fails, contact the instructor before class.
