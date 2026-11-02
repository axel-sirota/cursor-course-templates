# PM Persona: Pre-Class Setup

Complete every item below before class. The instructor cannot wait for tool installation during the session.

## 1. Cursor

Install **Cursor IDE**: https://cursor.sh

Verify it launches and can open the course repo directory.

## 2. Python 3

The `pm-prd-markdown` stack ships a small PRD checker script. Verify: `python3 --version` (3.10+).

## 3. Optional MCP servers

The PM pack ships no MCP servers and needs no credentials. The course works fully in markdown with synthetic data: PRDs, stories and tickets are files in `workspaces/pm/`.

Jira, Confluence, GitHub Issues, Slack and Notion integrations are not needed for any exercise. If you want them for your own work after class, use the vendors' official servers and follow their setup docs:

- **Jira and Confluence:** the Atlassian remote MCP server (see Atlassian's support docs)
- **GitHub Issues:** the GitHub remote MCP server (`github/github-mcp-server` on GitHub)
- **Notion:** `@notionhq/notion-mcp-server` (`makenotion/notion-mcp-server` on GitHub)

Point them at a sandbox site, never at production data.

## 4. Repository access

Clone the course repo:

```bash
git clone https://github.com/axel-sirota/cursor-course-templates
cd cursor-course-templates
```

## 5. Smoke test

Open the repo in Cursor and run in the chat:

```
/set-persona add pm
/setup-stack pm
```

After the first command you should see a confirmation listing the PM commands, subagents, hooks and the new `workspaces/pm/` folder. After the second, the `## Persona: pm` block in `.cursor/context.md` should show `Stack: pm-prd-markdown`.

If any step fails, contact the instructor before class.
