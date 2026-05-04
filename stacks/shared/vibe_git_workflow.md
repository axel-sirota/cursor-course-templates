# Git Workflow

This document covers the git branching strategy, commit conventions, PR discipline,
and quality gates used across all stacks. Stack-specific docs may extend or override
specific commands (e.g., the quality gate command differs per stack).

---

## Branch Strategy

| Branch | Purpose |
|--------|---------|
| `main` | Production. Only updated via PR from `develop` on release. |
| `develop` | Integration branch. All feature PRs target this branch. |
| `feature/{name}` | One branch per feature or task. Created from `develop`. |
| `hotfix/{name}` | Emergency fixes. Branched from `main`. |

Rules:
- Never commit directly to `main` or `develop`.
- Feature branches are short-lived — one branch per discrete task.
- Branch names: lowercase, hyphens only, no spaces. Example: `feature/add-email-verification`.

---

## Starting a Feature

```bash
git checkout develop
git pull origin develop
git checkout -b feature/{name}
```

Before starting, confirm:
- You are on `develop` before branching.
- Your local `develop` is current (`git pull`).
- The feature name is agreed upon and scoped.

---

## Committing

Use **Conventional Commits** format for all commit messages.

**Format:**
```
{type}: {subject}

[optional body]
```

**Types:**
| Type | When to use |
|------|-------------|
| `feat` | New feature or capability |
| `fix` | Bug fix |
| `refactor` | Code change that is not a fix or feature |
| `test` | Adding or updating tests |
| `docs` | Documentation only |
| `chore` | Build system, dependencies, tooling |
| `perf` | Performance improvement |

**Subject line rules:**
- Imperative mood: "add email field" not "added email field"
- ≤72 characters
- No period at the end
- Lowercase after the type prefix

**Good examples:**
```
feat: add email verification on signup
fix: prevent duplicate order creation on retry
refactor: extract payment processing into service layer
test: add integration tests for auth middleware
```

---

## Pushing for Review

When the feature is ready for review:

```bash
# Run quality gate first — all green before pushing
{stack quality command}

# Push the feature branch
git push origin feature/{name}
```

Then open a PR from `feature/{name}` → `develop`.

---

## PR Description Template

Every PR should include:

```markdown
## Summary
{What this PR does and why. 2–4 sentences.}

## Key Changes
- {Change 1}
- {Change 2}
- {Change 3}

## Testing
{How the changes were tested. Unit tests? Integration tests? Manual steps?}

## Screenshots
{If the change affects UI, include before/after screenshots.}
```

Keep it concise. Reviewers should understand the PR without reading all the code.

---

## Merge Discipline

- **Squash merge** feature → develop to keep history clean.
- PR title becomes the squash commit message — make it a valid Conventional Commit.
- Delete the feature branch immediately after merge (remote + local).
- Never leave merged feature branches open.

After squash merge and branch deletion:

```bash
git checkout develop
git pull origin develop
git branch -d feature/{name}
```

---

## Quality Gate Before Push

Before pushing any branch, the stack's quality command must pass with zero errors.

Examples by stack (use your stack's command):
- Python/pytest: `make quality` or `pytest && ruff check . && mypy .`
- Go: `go test ./... && go vet ./...`
- Java/Maven: `mvn verify`
- Node/npm: `npm test && npm run lint`
- Terraform: `terraform validate && tflint`

**Do not push a branch with failing quality gates.** Fix the issue locally first.

---

## Hotfix Flow

For urgent production fixes:

```bash
# Branch from main, not develop
git checkout main
git pull origin main
git checkout -b hotfix/{name}

# Make the fix, commit, push
git push origin hotfix/{name}
```

Open **two PRs**:
1. `hotfix/{name}` → `main` (the production fix)
2. `hotfix/{name}` → `develop` (so develop doesn't regress)

Merge `main` PR first. Then merge the `develop` PR.

---

## Release Flow

When `develop` is ready for production:

1. Run the full quality gate on `develop`.
2. Update version if your stack uses versioning (`pyproject.toml`, `package.json`, etc.).
3. Open PR from `develop` → `main`.
4. PR title: `chore: release v{version}`.
5. After merge, tag the commit: `git tag v{version} && git push origin v{version}`.

---

## Common Mistakes to Avoid

- Committing directly to `develop` or `main`.
- Pushing without running the quality gate.
- Leaving merged branches un-deleted.
- Using non-Conventional-Commit messages (breaks changelog generation).
- Long-running feature branches (more than a few days of work) — split the feature instead.
