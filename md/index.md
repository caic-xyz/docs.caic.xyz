# md

**Branch-locked development containers for AI coding agents.** Each container is locked to a repository-branch pair. Safe parallel work, no conflicts.

[![codecov](https://codecov.io/gh/caic-xyz/md/graph/badge.svg?token=Q2ZK312LNF)](https://codecov.io/gh/caic-xyz/md)

## The problem

AI coding agents work best in YOLO mode (full command execution). But running them locally creates:

- **Branch conflicts** — agent changes interfere with your local checkout
- **Test conflicts** — simultaneous test runs cause failures and race conditions
- **Environment pollution** — accumulated dependencies cause hidden bugs
- **Context switching** — switching branches while an agent works loses progress

## The solution

`md` gives each agent a **complete, isolated container** with a full git clone:

- Run agents on multiple branches simultaneously
- Switch local branches without affecting running agents
- Run tests in parallel without conflicts
- Keep your local checkout clean
- Delete containers cleanly when done

## Quick start

```bash
# Start container for your current branch (auto-SSH in)
git checkout -b wip origin/main
md start

# Inside the container — run your agent
cd ~/src/<repo-name>
claude

# Back on host — check changes and sync
md diff
md pull
```

## Install

```bash
go install github.com/caic-xyz/md/cmd/md@latest
```

See [Commands](./commands) for the full command reference, [Configuration](./configuration) for caches and environment variables, and [Harnesses](./harnesses) for agent-specific setup.
