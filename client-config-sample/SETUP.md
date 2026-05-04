# Pre-Class Setup — [REPLACE THIS: Your Organization Name]

> **For instructors:** Replace every `[REPLACE THIS: ...]` marker with your org-specific value before distributing this file to students.

---

## Standard items (keep these for every org)

1. Clone the course repo:
   ```
   git clone [REPLACE THIS: repo-url]
   ```
2. Drop `client-config.zip` into the repo root and unzip it:
   ```
   unzip client-config.zip
   ```
3. Copy `client-config/env.example` content into a new `.env` file in the repo root:
   ```
   cp client-config/env.example .env
   ```
4. Fill in the credential values in `.env` — see your instructor if you need help
5. Open the repo in Cursor or Claude Code
6. Run `/set-persona` and pick your role

---

## Organization-specific items

[REPLACE THIS: Add or remove items from this section based on your org's environment]

- **VPN required:** [REPLACE THIS: yes/no — if yes, name the VPN and link to enrollment instructions]
- **Internal GitHub org:** [REPLACE THIS: github.your-org.com/your-org-name]
- **Jira project for exercises:** [REPLACE THIS: project key, e.g., COURSE-123]
- **Figma file URL for exercises:** [REPLACE THIS: https://www.figma.com/file/...]
- **SSO/MFA steps:** [REPLACE THIS: any SSO login flows students need to complete before class]
- **Tool access provisioning:** [REPLACE THIS: who to contact / how to request access to internal tools]

---

## Credentials checklist

Before the first session, confirm you have working credentials for every tool your persona uses:

- [ ] GitHub Personal Access Token created (at [REPLACE THIS: github.your-org.com/settings/tokens])
- [ ] Jira API token created (at https://id.atlassian.com/manage-profile/security/api-tokens)
- [ ] Confluence access confirmed
- [ ] Figma access token created (at https://www.figma.com/settings)
- [ ] [REPLACE THIS: any org-specific tool access items]

---

## Questions?

Contact: [REPLACE THIS: instructor-email@yourorg.com]

[REPLACE THIS: Add any org-specific support channels, Slack handles, or office hour links here]
