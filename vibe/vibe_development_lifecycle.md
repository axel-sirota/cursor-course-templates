# Development Lifecycle Guide

## Purpose

This guide provides instructions for the Cursor LLM on how to manage the Git workflow and development lifecycle for this project. Use this as a reference when the user requests Git operations.

## Git Workflow Commands

### Start New Feature
**User says:** "Start new feature: [feature-name]"
**You do:** 
```bash
cd geniegets_api
make start-feature FEATURE_NAME=[feature-name]
```

**What this does:**
- Switches to develop branch
- Pulls latest develop
- Creates feature branch: `feature/[feature-name]`
- **Pushes monorepo branch to remote**
- **Syncs latest UI changes from UI repository**
- **Creates corresponding branch in UI repository**
- Validates feature name (alphanumeric, hyphens, underscores only)

### Push Feature
**User says:** "Push feature" or "Merge [feature-name]"
**You do:**
```bash
cd geniegets_api
make push-feature
```

**What this does:**
- Checks you're on a feature branch
- Pulls latest develop and rebases
- Runs quality checks (`make quality`)
- Pushes feature branch to monorepo
- **Pushes UI changes to UI repository**
- **Creates PR in monorepo** from feature → develop
- **Creates PR in UI repository** from feature → develop
- Uses GitHub CLI if available, otherwise provides manual instructions

### Complete Feature
**User says:** "Complete feature" or "Finish feature" (after PR is merged)
**You do:**
```bash
cd geniegets_api
make complete-feature
```

**What this does:**
- Checks you're on a feature branch
- Verifies PR has been merged
- Switches to develop branch
- Pulls latest develop
- Deletes local feature branch
- Deletes remote feature branch
- **Merges UI changes back to develop in UI repository**
- Runs final quality check on develop
- Provides next steps guidance

**PR Description Format:**
- **Title**: "Feature: [Feature Name]"
- **Summary**: Brief description of what the feature does
- **Key Changes**: Bullet list of main changes from recent commits

### Release to Production
**User says:** "Release to production" or "Deploy to production"
**You do:**
```bash
cd geniegets_api
make deploy-production
```

**What this does:**
- Ensures you're on develop branch
- Pulls latest develop
- Runs quality checks
- Generates changelog from commit messages
- Updates version in pyproject.toml
- Pushes develop with release updates
- **Syncs UI changes to UI repository**
- **Creates PR in monorepo** from develop → main
- **Creates PR in UI repository** from develop → main
- Provides release checklist and next steps

**PR Description Format:**
- **Title**: "🚀 Production Release v[version]"
- **Summary**: Brief description of the release
- **Key Changes**: Bullet list of main changes from recent commits

## UI Subtree Workflow

### Overview
This project uses a **git subtree** to integrate the UI repository (`geniegets-web`) into the monorepo. This enables coordinated development between the API and UI while maintaining separate repositories.

### Repository Structure
- **Monorepo**: `genie-gets` (contains API + UI subtree)
- **UI Repository**: `geniegets-web` (Lovable-controlled)
- **Subtree Directory**: `geniegets_web/` (UI code in monorepo)

### Dual-Repository Coordination
All workflow commands now handle **both repositories**:

**Start Feature:**
- Creates branch in monorepo
- Creates corresponding branch in UI repository
- Syncs latest UI changes

**Push Feature:**
- Pushes changes to monorepo
- Pushes UI changes to UI repository
- Creates PRs in both repositories

**Complete Feature:**
- Cleans up monorepo branch
- Merges UI changes back to UI repository develop

**Deploy Production:**
- Creates production PRs in both repositories
- Ensures coordinated releases

### UI Repository Access
- **URL**: `https://github.com/garage-vibe/geniegets-web.git`
- **Branch**: `develop` (main development branch)
- **Subtree Commands**: Automatically handled by scripts

## Branch Strategy

- **develop**: Main development branch (always deploy from here)
- **feature/[name]**: Feature branches (created from develop)
- **main**: Production branch (only updated via PR from develop)

## Quality Gates

All commands automatically run:
- `make quality` (format, lint, type-check, test)
- Rebase on latest develop
- Commit message validation
- Feature branch naming validation

## Commit Message Conventions

The changelog generator looks for these prefixes:
- `feat:` or `feature:` - New features
- `fix:` or `bugfix:` - Bug fixes
- `change:` or `update:` - Changes/updates
- `refactor:` - Code refactoring
- `security:` or `sec:` - Security updates
- `docs:` or `doc:` - Documentation updates

## File Structure

```
geniegets_api/
├── scripts/
│   ├── start-feature.sh      # Feature branch creation
│   ├── push-feature.sh       # Feature push and PR creation
│   ├── deploy-production.sh  # Production release
│   └── generate-changelog.sh # Changelog generation
├── .github/
│   ├── pull_request_template.md
│   └── PULL_REQUEST_TEMPLATE.md
├── Makefile                  # Enhanced with Git workflow commands
├── pyproject.toml           # Version management
└── CHANGELOG.md             # Generated changelog
```

## Common User Requests

### "Start new feature: user authentication"
```bash
cd geniegets_api
make start-feature FEATURE_NAME=user-authentication
```

### "Push feature"
```bash
cd geniegets_api
make push-feature
```

### "Complete feature"
```bash
cd geniegets_api
make complete-feature
```

### "Release to production"
```bash
cd geniegets_api
make deploy-production
```

### "Merge user authentication"
```bash
cd geniegets_api
make push-feature
```

### "Complete user authentication"
```bash
cd geniegets_api
make complete-feature
```

## Error Handling

If any command fails:
1. **Quality checks fail**: Tell user to fix issues and try again
2. **Rebase conflicts**: Tell user to resolve conflicts and continue
3. **Not on correct branch**: Tell user to switch to appropriate branch
4. **Uncommitted changes**: Tell user to commit or stash changes first

## Prerequisites

- User must be in the project root directory
- Git repository must be initialized
- Remote origin must be configured
- GitHub CLI (gh) is optional but recommended for automatic PR creation

## Notes for Future Self

- Always run commands from the `geniegets_api` directory
- The scripts are already executable and ready to use
- Quality gates ensure code quality before any Git operations
- Changelog generation is automatic and follows conventional commit format
- **PR descriptions are automatically generated** - no need for user to edit templates
- **Create concise PR descriptions** with Summary + Key Changes format
- Version management is handled automatically in pyproject.toml

## PR Description Guidelines

When creating PRs, always generate concise descriptions:

**For Feature PRs:**
```
## Summary
Implements [feature name] - [brief description].

## Key Changes
- [Change 1 from commit message]
- [Change 2 from commit message]
- [Change 3 from commit message]
```

**For Production Releases:**
```
## Summary
Production release v[version] - merges latest changes from develop to main.

## Key Changes
- [Recent change 1]
- [Recent change 2]
- [Recent change 3]

**Version:** v[version]
**Release Date:** [date]
```

## Troubleshooting

**"Permission denied" errors:**
```bash
chmod +x scripts/*.sh
```

**"Not in git repository" errors:**
```bash
cd geniegets_api
```

**"GitHub CLI not found" warnings:**
- Install GitHub CLI or create PRs manually using provided URLs

**"Quality checks failed" errors:**
- Run `make quality` manually to see specific issues
- Fix issues and try again

## Dual-Repository Workflow

### Important Notes
- **Both repositories** must be coordinated for proper development
- **PRs are created in both repositories** for each feature
- **Both PRs must be merged** for complete feature completion
- **Production releases** require coordination between both repositories

### Workflow Summary
1. **Start Feature** → Branches created in both repos
2. **Push Feature** → PRs created in both repos
3. **Merge PRs** → Both repositories updated
4. **Complete Feature** → Both repositories cleaned up
5. **Deploy Production** → Production PRs in both repos

### Troubleshooting Subtree Issues
**"Subtree push failed" errors:**
- Ensure working tree is clean before running commands
- Check that UI repository is accessible
- Verify GitHub CLI is installed for PR creation

**"UI repository not in sync" warnings:**
- Run `git subtree pull` to sync latest UI changes
- Check that both repositories have the same branch names
- Ensure PRs are merged in both repositories
