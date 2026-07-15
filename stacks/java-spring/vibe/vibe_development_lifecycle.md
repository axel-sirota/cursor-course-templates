# Development Lifecycle Guide

## Purpose

This guide provides instructions for the Cursor LLM on how to manage the Git workflow and
development lifecycle for Java/Spring Boot projects. Use this as a reference when the user
requests Git operations.

## Git Workflow Commands

### Start New Feature
**User says:** "Start new feature: [feature-name]"
**You do:**
```bash
cd your_project
make start-feature FEATURE_NAME=[feature-name]
```

**What this does:**
- Switches to develop branch
- Pulls latest develop
- Creates feature branch: `feature/[feature-name]`
- Pushes feature branch to remote
- Validates feature name (alphanumeric, hyphens, underscores only)

### Push Feature
**User says:** "Push feature" or "Merge [feature-name]"
**You do:**
```bash
cd your_project
make push-feature
```

**What this does:**
- Checks you're on a feature branch
- Pulls latest develop and rebases
- Runs quality checks (`make quality`)
- Pushes feature branch to remote
- Creates PR from feature → develop
- Uses GitHub CLI if available, otherwise provides manual instructions

### Complete Feature
**User says:** "Complete feature" or "Finish feature" (after PR is merged)
**You do:**
```bash
cd your_project
make complete-feature
```

**What this does:**
- Checks you're on a feature branch
- Verifies PR has been merged
- Switches to develop branch
- Pulls latest develop
- Deletes local feature branch
- Deletes remote feature branch
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
cd your_project
make deploy-production
```

**What this does:**
- Ensures you're on develop branch
- Pulls latest develop
- Runs quality checks
- Generates changelog from commit messages
- Bumps the `<version>` in `pom.xml` (via `./mvnw versions:set`)
- Pushes develop with release updates
- Creates PR from develop → main
- Provides release checklist and next steps

**PR Description Format:**
- **Title**: "🚀 Production Release v[version]"
- **Summary**: Brief description of the release
- **Key Changes**: Bullet list of main changes from recent commits

## Project Structure

### Overview
This guide assumes a standard Maven/Spring Boot project structure with proper Git workflow
management.

### Repository Structure
- **Main Repository**: Your project repository
- **Development Branch**: `develop` (main development branch)
- **Production Branch**: `main` (production releases)
- **Feature Branches**: `feature/[feature-name]` (feature development)

## Branch Strategy

- **develop**: Main development branch (always deploy from here)
- **feature/[name]**: Feature branches (created from develop)
- **main**: Production branch (only updated via PR from develop)

## Quality Gates

All commands automatically run:
- `make quality` (`./mvnw checkstyle:check`, `./mvnw spotless:check`, `./mvnw test`)
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
your_project/
├── scripts/
│   ├── start-feature.sh      # Feature branch creation
│   ├── push-feature.sh       # Feature push and PR creation
│   ├── deploy-production.sh  # Production release
│   └── generate-changelog.sh # Changelog generation
├── .github/
│   ├── pull_request_template.md
│   └── workflows/
│       └── ci.yml            # Build + test + checkstyle pipeline
├── Makefile                  # Enhanced with Git workflow commands
├── pom.xml                   # Version management and build configuration
├── mvnw / mvnw.cmd            # Maven wrapper
├── .sdkmanrc                 # Pinned JDK version
└── CHANGELOG.md              # Generated changelog
```

## Common User Requests

### "Start new feature: user authentication"
```bash
cd your_project
make start-feature FEATURE_NAME=user-authentication
```

### "Push feature"
```bash
cd your_project
make push-feature
```

### "Complete feature"
```bash
cd your_project
make complete-feature
```

### "Release to production"
```bash
cd your_project
make deploy-production
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
- GitHub CLI (`gh`) is optional but recommended for automatic PR creation
- JDK pinned via sdkman/asdf and Maven wrapper working (see `rules/000-environment-setup.mdc`)

## Notes for Future Self

- Always run commands from the project root directory
- The scripts are already executable and ready to use
- Quality gates ensure code quality before any Git operations
- Changelog generation is automatic and follows conventional commit format
- **PR descriptions are automatically generated** - no need for user to edit templates
- **Create concise PR descriptions** with Summary + Key Changes format
- Version management is handled automatically in `pom.xml`

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
chmod +x scripts/*.sh mvnw
```

**"Not in git repository" errors:**
```bash
cd your_project
```

**"GitHub CLI not found" warnings:**
- Install GitHub CLI or create PRs manually using provided URLs

**"Quality checks failed" errors:**
- Run `make quality` manually to see specific issues
- Fix issues and try again (`./mvnw spotless:apply` auto-fixes formatting)

## Build-Then-Deploy Flow

Local build and container image, using the artifacts from `templates/Dockerfile` and
`templates/docker-compose-template.yaml`:

```bash
# 1. Run tests and build a runnable jar
./mvnw clean verify

# 2. Build the Docker image (multi-stage, see rules/500-docker-java.mdc)
docker build -t my-app:latest .

# 3. Bring up the full stack locally
docker compose --profile app up --build

# 4. Verify
curl http://localhost:8080/actuator/health
```

## CI Pipeline Sketch (GitHub Actions)

```yaml
name: CI

on:
  pull_request:
    branches: [develop, main]
  push:
    branches: [develop, main]

jobs:
  build-test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15-alpine
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: appdb
        ports:
          - 5432:5432
        options: >-
          --health-cmd "pg_isready -U postgres"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    steps:
      - uses: actions/checkout@v4

      - name: Set up JDK 21
        uses: actions/setup-java@v4
        with:
          distribution: temurin
          java-version: '21'
          cache: maven

      - name: Checkstyle
        run: ./mvnw -B checkstyle:check

      - name: Spotless (format check)
        run: ./mvnw -B spotless:check

      - name: Test
        run: ./mvnw -B verify
        env:
          SPRING_DATASOURCE_URL: jdbc:postgresql://localhost:5432/appdb
          SPRING_DATASOURCE_USERNAME: postgres
          SPRING_DATASOURCE_PASSWORD: postgres

      - name: Build jar
        run: ./mvnw -B clean package -DskipTests
```

Note that Testcontainers-based integration tests spin up their own ephemeral Postgres per test
class and do **not** need the `services.postgres` block above — that service container is only
needed if some tests connect to a fixed, externally-provisioned database instead of Testcontainers.

## Development Workflow

### Important Notes
- **Single repository** workflow for Spring Boot projects
- **PRs are created** for each feature
- **PRs must be merged** for complete feature completion
- **Production releases** require proper testing and validation

### Workflow Summary
1. **Start Feature** → Branch created from develop
2. **Push Feature** → PR created from feature → develop
3. **Merge PR** → Repository updated
4. **Complete Feature** → Branch cleaned up
5. **Deploy Production** → Production PR from develop → main

### Troubleshooting Common Issues
**"Working tree not clean" errors:**
- Ensure all changes are committed or stashed before running commands
- Check git status for uncommitted changes

**"Branch not found" errors:**
- Verify you're on the correct branch
- Check that the feature branch exists locally and remotely
