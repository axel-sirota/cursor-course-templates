# Lab 2 solution — Base Branch Forensics (worktree isolation)

Source lab: `materials/fragments/worktree-isolation.html`.

- **Easy:** give the Lab 1 agent `isolation: worktree`, run it, locate its worktree directory and `worktree-*` branch with git commands, and verify the main checkout stayed clean.
- **Hard:** from a feature branch with a commit `main` lacks, run the agent under `baseRef: "fresh"` and under `"head"`, and prove from `git log` which commit each worktree branched from.

## Easy solution

Add the isolation line to the rebuilt notifications agent's frontmatter (or use the
shipped `changelog-scribe`, which already carries it):

```yaml
---
name: notifications-implementer
...
isolation: worktree
---
```

Restart `claude`, delegate a small task, and while it runs, from a second terminal at
the repo root:

```bash
git worktree list
git branch --list 'worktree-*'
git status
```

Real output shape (captured mid-run, `materials/captured/demo2-worktree-list.txt`):

```text
$ git worktree list
/private/tmp/refund-monorepo                                           cc106e8 [main]
/private/tmp/refund-monorepo/.claude/worktrees/agent-a3643a1fcff8ba6e5 cc106e8 [worktree-agent-a3643a1fcff8ba6e5] locked

$ git branch --list 'worktree-*'
+ worktree-agent-a3643a1fcff8ba6e5

$ git status
On branch main
nothing to commit, working tree clean
```

The three checks the student must call out:

1. The worktree lives under `.claude/worktrees/agent-<id>` on branch
   `worktree-agent-<id>` (the CLI names runs `agent-<hash>`, not after the agent).
2. Both checkouts point at the same commit — the worktree branched from the session's
   HEAD because the shipped settings say `"baseRef": "head"`.
3. `git status` in the main checkout is clean while the agent is mid-edit; every
   change is inside the worktree.

**Observed deviation to teach (2.1.218):** the fragment's claim that a no-change run
removes its worktree automatically did not hold in the captured run — the worktree
survived holding only the `.venv` symlink. Cleanup is manual:

```bash
git worktree remove --force .claude/worktrees/agent-<id>
git branch -D worktree-agent-<id>
```

Sometimes cleanup does happen (it did in the Lab 2 Hard reference run below), so
teach "check with `git worktree list`, clean what is left" rather than either
absolute.

## Hard solution

Reference run executed 2026-07-24 (claude 2.1.218) with the shipped
`changelog-scribe` agent. Two setups matter: see the first failure mode for why.

Create the evidence commit:

```bash
git checkout -b lab2-feature
echo "Lab 2 marker: this commit exists ONLY on lab2-feature" > LAB2_MARKER.md
git add LAB2_MARKER.md && git commit -m "lab2: marker commit that main does not have"
git log --oneline -2
```

```text
a8ef117 lab2: marker commit that main does not have
ce610db Merge notifications: require reason on NotificationEvent and log it   <- main's tip
```

Prediction to write down before running: `"fresh"` branches from the repository's
default branch, so its worktree must sit on `ce610db` and `LAB2_MARKER.md` must not
exist there; `"head"` branches from the current checkout, so its worktree sits on
`a8ef117` with the marker present.

The trick that makes the proof cheap: a worktree-isolated agent's `Bash` runs inside
its own worktree, so the agent itself is the forensic instrument. Set
`"baseRef": "fresh"` in `.claude/settings.json`, then:

```text
> Use the changelog-scribe agent for a forensic check: run exactly these commands
  with Bash and report their raw output verbatim, changing nothing:
  git log --oneline -2 ; ls LAB2_MARKER.md
```

Real result under `"fresh"` — the agent's worktree log came back as:

```text
ce610db Merge notifications: require reason on NotificationEvent and log it
9bfccf0 notifications: require reason on NotificationEvent and log it
```

and the agent itself flagged that `a8ef117` was missing from its checkout. The
feature-branch commit is invisible: an agent asked to build on the marker would
silently implement against code that does not contain it.

Switch to `"baseRef": "head"` and repeat the same delegation. Real result:

```text
a8ef117 lab2: marker commit that main does not have
ce610db Merge notifications: require reason on NotificationEvent and log it

$ ls LAB2_MARKER.md
LAB2_MARKER.md
```

Same repo, same agent, same prompt — the only variable is `baseRef`, and the worktree
base moved exactly as predicted. If the run leaves a `worktree-*` branch behind,
`git log --oneline -1 worktree-agent-<id>` and
`git merge-base main worktree-agent-<id>` give the same proof from outside.

## What students get wrong

1. **Running the Hard tier on an `init.sh` copy and seeing no difference.** The
   shipped `init.sh` creates a local-only repo with no `origin` remote, and observed
   on 2.1.218: with no `origin` to resolve, `"fresh"` falls back to the current HEAD
   — both settings behave identically and the student concludes the gotcha is a myth.
   The reference run above used a clone (`git clone ~/labs/refund-monorepo lab2-clone`)
   so `origin/main` exists. Have students do the same, or add a remote first.
2. **Editing `settings.json` mid-session and expecting the running session to honor
   it.** Worktree settings are read when the agent spawns from a session that loaded
   them at start. Restart `claude` after each `baseRef` change.
3. **Forensics on the wrong branch.** `git log` on `lab2-feature` instead of on the
   `worktree-*` branch (or inside the worktree) proves nothing about what the agent
   saw. The evidence is the worktree's own log — via the agent's Bash report or
   `git -C .claude/worktrees/agent-<id> log --oneline -2`.

Verified: 2026-07-24 against sample-monorepo/python-fastapi
