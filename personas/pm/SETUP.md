# PM Persona: Pre-Class Setup

Complete every item below before class. The instructor cannot wait for tool installation during the session.

## 1. Cursor

Install **Cursor IDE**: https://cursor.sh

Verify it launches and can open the course repo directory.

## 2. Python 3

The `pm-prd-markdown` stack ships a small PRD checker script. Verify: `python3 --version` (3.10+).

## 3. Optional: Atlassian credentials (Jira + Confluence)

The course works fully in markdown with synthetic data. Configure Atlassian only if you want to practise pushing tickets to a sandbox Jira.

### Generate an API token

1. Go to: https://id.atlassian.com/manage-profile/security/api-tokens
2. Click **Create API token**, give it a name (e.g. `cursor-course`), and copy the token value.

### Set environment variables

Create a `.env` file in the repo root (if `personas/pm/.env.example` exists, copy it: `cp personas/pm/.env.example .env`) and fill in:

| Variable | Value |
|---|---|
| `JIRA_URL` | Your Atlassian base URL, e.g. `https://yourcompany.atlassian.net` |
| `JIRA_USERNAME` | Your Atlassian account email |
| `JIRA_API_TOKEN` | The token you generated above |
| `CONFLUENCE_URL` | Usually `JIRA_URL` + `/wiki`; your instructor confirms |
| `CONFLUENCE_USERNAME` | Same email as `JIRA_USERNAME` |
| `CONFLUENCE_API_TOKEN` | Same token as `JIRA_API_TOKEN` |

## 4. Optional: GitHub Personal Access Token

Only needed for the GitHub Issues MCP.

1. Go to: https://github.com/settings/tokens
2. Generate a classic token with `repo` scope.
3. Set `GITHUB_PAT` in your `.env` file.

## 5. Optional: Slack and Notion

- Set `SLACK_BOT_TOKEN` if you want status updates in Slack.
- Set `NOTION_API_KEY` if you want documentation sync to Notion.

Leave these blank if not needed. The MCP servers will simply not connect.

## 6. Repository access

Clone the course repo:

```bash
git clone https://github.com/axel-sirota/cursor-course-templates
cd cursor-course-templates
```

## 7. Smoke test

Open the repo in Cursor and run in the chat:

```
/set-persona add pm
/setup-stack pm
```

After the first command you should see a confirmation listing the PM commands, subagents, hooks, MCP servers and the new `workspaces/pm/` folder. After the second, the `## Persona: pm` block in `.cursor/context.md` should show `Stack: pm-prd-markdown`.

If you configured Atlassian, ask Cursor to list your Jira projects. Results mean your credentials work.

If any step fails, contact the instructor before class.
