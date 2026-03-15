# caic

**Coding Agents in Containers.** Manage multiple AI coding agents running in parallel in isolated Docker containers. Access them from your phone with Tailscale. All private.

[![codecov](https://codecov.io/gh/caic-xyz/caic/graph/badge.svg?token=VB9D2PKPCC)](https://codecov.io/gh/caic-xyz/caic)

## What is caic?

caic lets you run AI coding agents (Claude Code, Codex, Gemini CLI, Kilo) in isolated [md](https://github.com/caic-xyz/md) containers, orchestrated through a unified web UI and Android app. Each task runs in its own container so agents never interfere with each other or your local checkout.

## Key features

- **Parallel agents** — run many agents simultaneously on different branches
- **Resilient sessions** — server restarts don't kill running agents; a relay process inside each container keeps agents alive across SSH disconnects
- **Forge integration** — automatic PR/MR creation and CI monitoring for GitHub and GitLab
- **Web UI** — SolidJS frontend embedded in the binary
- **Android app** — voice-first companion app to manage agents from your phone

## Quick start

```bash
go install github.com/caic-xyz/caic/backend/cmd/caic@latest
```

See [Installation](./installation) for full setup, and [Configuration](./configuration) for environment variables and systemd service setup.
