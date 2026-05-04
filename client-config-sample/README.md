# Instructor Guide — Client Config

## What this is

The `client-config/` directory is how you customize this course for your organization without modifying the base repo. Students never see other clients' configs because each client gets their own private copy of this directory.

This `client-config-sample/` directory is the committed reference showing you the full structure and every file you need to fill in. Copy it to `client-config/` and fill in the values.

---

## How to use it

1. Copy this `client-config-sample/` directory to `client-config/` in the repo root
2. Fill in the values as described in each file
3. Distribute to students as a zip file or private git repo
4. Students unzip/clone into the repo root before running `/set-persona`

The `/set-persona` command detects `client-config/` automatically and merges your org-specific settings on top of the base persona.

---

## What you customize

| File | Purpose |
|------|---------|
| `client.md` | Your org identity and any course policies |
| `env.example` | Your org-specific env var names and instructions |
| `SETUP.md` | Your org-specific pre-class checklist |
| `personas/{role}/mcp.json` | Your org's internal tool endpoints per role |
| `mcp-overrides.json` | Top-level MCP overrides applied to all personas (rarely needed) |

---

## What you NEVER need to share with the instructor (Axel)

You own `client-config/` completely. The following stay private to your organization:

- Your internal GitHub Enterprise URL
- Your Jira/Confluence URLs (e.g., `https://your-org.atlassian.net`)
- Your Snowflake connection strings or warehouse identifiers
- Your Slack bot tokens
- Any internal service credentials or API keys
- Your org's VPN or SSO configuration details
- Any internal hostnames, IP ranges, or service discovery endpoints

The `mcp.json` files in each persona directory are entirely yours to fill in. They never need to be sent to Axel for the course to work.

---

## How persona MCP overrides work

Each `personas/{role}/mcp.json` file **fully replaces** the base persona's `mcp.json` — it is not merged on top. This means:

- If you only need to change one server, you still must include all the servers you want active
- If you omit a server that exists in the base config, it will not be available for that persona
- Copy the base persona's `mcp.json` as a starting point, then add your org's servers

---

## Distribution checklist

Before distributing `client-config/` to students:

- [ ] `client.md` has your org name and policies
- [ ] `env.example` lists every env var students need to set
- [ ] `SETUP.md` has your org-specific setup steps and contacts
- [ ] Each persona `mcp.json` uses `${ENV_VAR}` syntax for credentials (never hardcoded values)
- [ ] You have confirmed all internal URLs are reachable from the course environment
- [ ] Students have been granted the necessary access to internal tools in advance
