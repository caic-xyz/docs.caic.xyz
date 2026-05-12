# caic

**Coding Agents in Containers.** Manage multiple AI coding agents running in parallel in isolated Docker containers. Access them from your phone with Tailscale. All private.

## What is caic?

caic lets you run AI coding agents (Claude Code, Codex, Gemini CLI, Kilo, OpenCode) in isolated [md](../md/) containers, orchestrated through a unified web UI and Android app. Each task runs in its own container so agents never interfere with each other or your local checkout.

## Platform support

caic is supported on **Linux**, **macOS**, and **Windows via WSL2**.

## Key features

- **Parallel agents** — run many agents simultaneously on different branches
- **Resilient sessions** — server restarts don't kill running agents; a relay process inside each container keeps agents alive across SSH disconnects
- **Forge integration** — automatic PR/MR creation and CI monitoring for [GitHub](./github) and [GitLab](./gitlab)
- **Lightweight** — single Go binary, low memory and CPU footprint
- **Web UI** — SolidJS frontend embedded in the binary
- **Android app** — voice-first companion app to manage agents from your phone

## Screenshots

### Interacting with an agent

![Interacting with an agent](/screenshots/task-detail.webp)

### Plan mode

![Plan mode](/screenshots/task-plan.webp)

### Ask mode — agent asks for user input

![Ask mode](/screenshots/task-ask.webp)

### Widget — generative UI

![Widget](/screenshots/task-widget.avif)

### Android app

<img src="/screenshots/android-task-list.avif" alt="Android task list" style="max-width: 300px">

## Quick start

```bash
curl -fsSL https://caic.xyz/install.sh | bash
```

See [Installation](./installation) for full setup, and [Configuration](./configuration) for config file reference and service setup.

## Documentation

- [Installation](./installation) — prerequisites, platform notes, from-source builds
- [Configuration](./configuration) — config file reference, auth modes, HTTPS exposure
- [GitHub Integration](./github) — automatic PR creation and CI monitoring
- [GitLab Integration](./gitlab) — automatic MR creation and CI monitoring
- [Android App](./android) — voice-first companion app
- [Architecture](./architecture) — system components, task lifecycle, relay, startup
- [Design](./design) — design rationale, trade-offs, core principles
- [Security](./security) — authentication, credential handling, isolation model

## Getting help

- GitHub issues: [caic-xyz/caic](https://github.com/caic-xyz/caic/issues)
- Discord: [caic-xyz community](https://discord.gg/caic){.discord-cta}
- Include `caic -version` output and the error message when reporting issues
