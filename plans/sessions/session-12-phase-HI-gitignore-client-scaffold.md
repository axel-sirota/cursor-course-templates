# Session 12 — Phase H–I: `.gitignore` + Client Config Scaffold

**Phase:** H–I
**Goal:** Ensure `client-config/` is gitignored. Create a sample `client-config/` with documentation so instructors know exactly what to fill in.
**Depends on:** Session 10 (set-persona references client-config/)
**Next session:** Session 13 (docs)

---

## Files to Create/Update

```
.gitignore                          ← ADD client-config/ entry
client-config/                      ← NOT committed — this is the sample/docs only
client-config-sample/               ← COMMITTED sample showing instructors the structure
    README.md
    client.md
    mcp-overrides.json
    env.example
    SETUP.md
    personas/
        engineer/
            mcp.json
        designer/
            mcp.json
        pm/
            mcp.json
        data-scientist/
            mcp.json
```

Note: `client-config/` itself is gitignored. `client-config-sample/` is committed as documentation for instructors.

---

## File Specifications

### `.gitignore` addition

Add these lines (after existing entries):

```
# Client-specific configuration — never commit
client-config/
.env
```

### `client-config-sample/README.md`

**Title:** Instructor Guide — Client Config

Sections:

**What this is:** The `client-config/` directory is how you customize this course for your organization without modifying the base repo. Students never see other clients' configs because each client gets their own private copy of this directory.

**How to use it:**
1. Copy this `client-config-sample/` directory to `client-config/` in the repo root
2. Fill in the values as described in each file
3. Distribute to students as a zip file or private git repo
4. Students unzip/clone into the repo root before running `/set-persona`

**What you customize:**
- `client.md` — your org identity and any course policies
- `env.example` — your org-specific env var names and instructions
- `SETUP.md` — your org-specific pre-class checklist
- `personas/{role}/mcp.json` — your org's internal tool endpoints

**What you NEVER need to share with the instructor (Axel):**
- Your internal GitHub Enterprise URL
- Your Jira/Confluence URLs
- Your Snowflake connection strings
- Your Slack bot tokens
- Any internal service credentials

The `mcp.json` files in each persona directory are entirely yours to fill in.

### `client-config-sample/client.md`

```markdown
# Client Configuration

## Client
YourOrganizationName

## Course
Cursor for Software Engineers — Enterprise Edition

## Policies
- All work stays in the organization's GitHub org
- No personal GitHub accounts for course exercises
- (Add any other org-specific AI usage policies here)

## Instructor Contact
your-name@yourorg.com
```

### `client-config-sample/env.example`

```
# Organization-specific environment variables
# Distribute this to students alongside the client-config/ directory.
# Students copy this content into their .env file in the repo root.

# ── Engineer persona ──────────────────────────────────────────────
# GitHub Enterprise (replace github.com with your org's GitHub Enterprise host)
GITHUB_PAT=
# Internal PostgreSQL (if used in exercises)
DATABASE_URL=

# ── Designer persona ──────────────────────────────────────────────
# Figma (org-level access token — ask your Figma admin)
FIGMA_ACCESS_TOKEN=

# ── PM persona ────────────────────────────────────────────────────
# Internal Jira
JIRA_URL=https://your-org.atlassian.net
JIRA_USERNAME=
JIRA_API_TOKEN=
CONFLUENCE_URL=https://your-org.atlassian.net/wiki
CONFLUENCE_USERNAME=
CONFLUENCE_API_TOKEN=
# Slack (optional)
SLACK_BOT_TOKEN=

# ── Data Scientist persona ────────────────────────────────────────
# Add your internal data platform credentials here
# e.g., Snowflake, BigQuery, internal MLflow
# YOUR_PLATFORM_KEY=
```

### `client-config-sample/SETUP.md`

```markdown
# Pre-Class Setup — [Your Organization Name]

Replace this file with your organization's specific setup instructions.

## Standard items (keep these)

1. Clone the course repo: `git clone {repo-url}`
2. Drop `client-config.zip` into the repo root and unzip it
3. Copy `client-config/env.example` content into a new `.env` file in the repo root
4. Fill in the credential values — see your instructor if you need help
5. Open the repo in Cursor or Claude Code
6. Run `/set-persona` and pick your role

## Organization-specific items (add yours here)

- VPN required: yes/no
- Internal GitHub org to use: {org-name}
- Jira project for exercises: {project-key}
- Figma file URL for exercises: {url}
- Any SSO or MFA steps for internal tools

## Questions?

Contact: {instructor-email}
```

### `client-config-sample/personas/engineer/mcp.json`

```json
{
  "_instructor_note": "Replace the values below with your org's internal endpoints. This file FULLY REPLACES the base engineer mcp.json — include all servers you want active, not just the ones you're changing.",
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_PAT}",
        "GITHUB_HOST": "github.your-org.com"
      }
    },
    "postgres": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres", "${DATABASE_URL}"],
      "env": {}
    },
    "playwright": {
      "command": "npx",
      "args": ["-y", "@playwright/mcp@latest"],
      "env": {}
    },
    "context7": {
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp@latest"],
      "env": {}
    }
  }
}
```

### `client-config-sample/personas/designer/mcp.json`

```json
{
  "_instructor_note": "Replace with your org's Figma configuration. If your org uses a shared Figma token, put it here so students don't need individual tokens.",
  "mcpServers": {
    "figma": {
      "command": "npx",
      "args": ["-y", "figma-developer-mcp", "--figma-api-key=${FIGMA_ACCESS_TOKEN}", "--stdio"],
      "env": {}
    },
    "playwright": {
      "command": "npx",
      "args": ["-y", "@playwright/mcp@latest"],
      "env": {}
    },
    "context7": {
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp@latest"],
      "env": {}
    }
  }
}
```

### `client-config-sample/personas/pm/mcp.json`

```json
{
  "_instructor_note": "Replace JIRA_URL and CONFLUENCE_URL with your org's internal URLs. Add or remove optional servers (Slack, Notion) based on what your org uses.",
  "mcpServers": {
    "atlassian": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-atlassian"],
      "env": {
        "JIRA_URL": "${JIRA_URL}",
        "JIRA_USERNAME": "${JIRA_USERNAME}",
        "JIRA_API_TOKEN": "${JIRA_API_TOKEN}",
        "CONFLUENCE_URL": "${CONFLUENCE_URL}",
        "CONFLUENCE_USERNAME": "${CONFLUENCE_USERNAME}",
        "CONFLUENCE_API_TOKEN": "${CONFLUENCE_API_TOKEN}"
      }
    },
    "github-issues": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": { "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_PAT}" }
    }
  }
}
```

### `client-config-sample/personas/data-scientist/mcp.json`

```json
{
  "_instructor_note": "Add your org's data platform MCPs here alongside the default filesystem and context7. Examples below are commented out — uncomment and configure as needed.",
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "./data"],
      "env": {}
    },
    "context7": {
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp@latest"],
      "env": {}
    }
  }
}
```

---

## Acceptance Criteria

- [ ] `cat .gitignore | grep client-config` → shows the entry
- [ ] `git status` after creating `client-config/` directory → `client-config/` does NOT appear as untracked
- [ ] `ls client-config-sample/` shows all expected files
- [ ] `ls client-config-sample/personas/` shows all 4 persona subdirs
- [ ] Every `mcp.json` in sample has `_instructor_note` explaining it replaces the base config entirely
- [ ] `client-config-sample/README.md` explicitly lists what instructors never need to share with Axel
