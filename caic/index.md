# caic

**Coding Agents in Containers.** Manage multiple AI coding agents running in parallel in isolated containers powered by Docker or Podman. Access them from your phone with Tailscale. All private.

## What is caic?

caic lets you run AI coding agents (Claude Code, Codex, OpenCode, Pi) in [md](../md/) containers, orchestrated through a unified web UI and Android app. Each task gets a separate container and repository copy, so agents do not edit one another's workspace or your local checkout. Shared agent and harness state, caches, and custom mounts remain common where configured.

## Platform support

caic is supported on **Linux**, **macOS**, and **Windows via WSL2**.

## Key features

- **Parallel agents**: run many agents simultaneously on different branches
- **Flexible runtimes**: use Docker and Podman side by side, then choose the runtime for each new task
- **Resilient sessions**: server restarts don't kill running agents; a relay process inside each container keeps agents alive across SSH disconnects
- **Recoverable workspaces**: fork a running, stopped, or crashed task with an editable handoff, or continue quota-blocked work with another available agent
- **Task visibility**: inspect usage, cost, resource graphs, compact repository state, task commits, collapsible per-file diffs, and the native subagents a task's agent spawns
- **Fast task actions**: right-click a task card to push, stop, revive, purge, fork, or compact it without opening the task
- **Keyboard navigation**: open shortcuts with `?` or `F1`, move through tasks with the arrow keys, use `Tab` to jump from a card to its prompt, select repositories with `F2`, choose a harness with `F3`, toggle voice with `F4`, and purge with `Shift+Delete`
- **Forge integration**: automatic PR/MR creation and CI monitoring for [GitHub](./github) and [GitLab](./gitlab)
- **Lightweight**: single Go binary, low memory and CPU footprint
- **Web UI**: SolidJS frontend embedded in the binary
- **Task inspection**: view launch config, runtime image, platform, caches, mounts, and diagnostics for each task
- **Voice control**: supervise and steer agents hands-free with [voice mode](./voice)
- **MCP server**: connect Claude or ChatGPT to your tasks through the [MCP endpoint](./mcp)
- **Android app**: voice-first companion app to manage agents from your phone

## Screenshots

### Interacting with an agent

<figure class="docs-figure">
  <img class="docs-screenshot" src="/screenshots/frontend/desktop/task-detail.webp" alt="caic task view with streamed agent output, expanded tool calls, repository changes, CI status, and a message composer" width="1280" height="800" loading="lazy" decoding="async">
  <figcaption>Follow a task from setup through tool use and its final result.</figcaption>
</figure>

### Plan mode

<figure class="docs-figure">
  <img class="docs-screenshot" src="/screenshots/frontend/desktop/task-plan.webp" alt="caic task in plan mode showing a five-step implementation plan and an action to execute it" width="1280" height="800" loading="lazy" decoding="async">
  <figcaption>Review an agent's plan before allowing implementation to begin.</figcaption>
</figure>

### Ask mode

<figure class="docs-figure">
  <img class="docs-screenshot" src="/screenshots/frontend/desktop/task-ask.webp" alt="caic task asking the user to choose among three storage backends or provide another answer" width="1280" height="800" loading="lazy" decoding="async">
  <figcaption>Answer structured questions without leaving the task view.</figcaption>
</figure>

### Widget

<figure class="docs-figure">
  <img class="docs-screenshot" src="/screenshots/frontend/desktop/task-widget.webp" alt="caic task displaying an interactive diagram that explains light refraction in water" width="1280" height="800" loading="lazy" decoding="async">
  <figcaption>Agents can present interactive generative UI directly in a task.</figcaption>
</figure>

## Quick start

```bash
curl -fsSL https://caic.xyz/install.sh | bash
```

See [Installation](./installation) for full setup, and [Configuration](./configuration) for config file reference and service setup.

## Documentation

- [Installation](./installation): prerequisites, platform notes, from-source builds
- [Configuration](./configuration): config file reference, auth modes, HTTPS exposure
- [GitHub Integration](./github): automatic PR creation and CI monitoring
- [GitLab Integration](./gitlab): automatic MR creation and CI monitoring
- [Voice](./voice): hands-free supervision with embedded, standalone, or fully local gateways
- [MCP Server](./mcp): connect external MCP clients over OAuth
- [Android App](./android): voice-first companion app
- [Architecture](./architecture): system components, task lifecycle, relay, startup
- [Design](./design): design rationale and core principles
- [Security](./security): authentication, credential handling, isolation model

## Getting help

- GitHub issues: [caic-xyz/caic](https://github.com/caic-xyz/caic/issues)
- Discord: [caic-xyz community](https://discord.gg/caic){.discord-cta}
- Include `caic -version` output and the error message when reporting issues
