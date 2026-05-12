---
# branch-locked Docker containers for AI coding agents
---

# md

**Branch-locked development containers for AI coding agents.** Each container is locked to a repository-branch pair. Safe parallel work, no conflicts.

## The problem

AI coding agents work best in YOLO mode (full command execution). But running them locally creates:

- **Branch conflicts**: agent changes interfere with your local checkout
- **Test conflicts**: simultaneous test runs cause failures and race conditions, leak processes
- **Environment pollution**: accumulated dependencies cause hidden bugs
- **Context switching**: switching branches while an agent works loses progress

## Platform support

md is supported on **Linux**, **macOS**, and **Windows via WSL2**.

## The solution

`md` gives each agent a **complete, isolated container** with a full git clone:

- Run agents on multiple branches simultaneously
- Switch local branches without affecting running agents
- Run tests in parallel without conflicts
- Keep your local checkout clean
- Delete containers cleanly when done

## Quick start

<AsciinemaPlayer src="/md-quickstart.cast" />

```bash
# Start container for your current branch (auto-SSH in)
git checkout -b wip origin/main
md start

# Inside the container: run your agent
cd ~/src/<repo-name>
claude

# Back on host: check changes and sync
md diff
md pull
```

## Install

```bash
curl -fsSL https://caic.xyz/install.sh | bash
```

## Documentation

- [Commands](./commands): full command reference, workflows (fork, multi-repo, CI)
- [Installation](./installation): prerequisites, platform notes, from-source builds
- [Configuration](./configuration): caches, environment variables, agent configs
- [Harnesses](./harnesses): agent-specific setup (Claude Code, Codex, Gemini, Pi, etc.)
- [Preinstalled Tools](./preinstalled-tools): what's available inside every container
- [Tailscale](./tailscale): remote access over your tailnet
- [Architecture](./architecture): image hierarchy, build pipeline, container lifecycle
- [Design](./design): design rationale, trade-offs, cache injection
- [Security](./security): SSH isolation, capabilities, network restrictions

## Getting help

- GitHub issues: [caic-xyz/md](https://github.com/caic-xyz/md/issues)
- Discord: [caic-xyz community](https://discord.gg/caic){.discord-cta}
- Include `md version` output and the error message when reporting issues
