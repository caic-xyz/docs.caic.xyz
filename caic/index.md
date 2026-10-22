# caic

caic runs coding agents in parallel on your own machine. Each task gets an [md](../md/) container with its own repository copies. The web app gives you one place to create tasks, follow the work, review changes, and continue the conversation.

## Start with a task

[Install caic](./installation), set your repository root in [Configuration](./configuration), then open the dashboard. Choose repositories, a harness, a model, and a prompt. caic prepares the workspace and streams the agent's output as it works.

<figure class="docs-figure">
  <img class="docs-screenshot" src="/screenshots/frontend/desktop/overview.webp" alt="caic task dashboard showing parallel tasks grouped by repository and their agent states" width="1280" height="800" loading="lazy" decoding="async">
  <figcaption>Follow your tasks and see which ones need attention.</figcaption>
</figure>

## What you can do

- Run **Claude Code, Codex, OpenCode, or Pi**. Experimental **Antigravity** support uses the `agy` CLI.
- Choose **Docker or Podman** for new tasks and work across multiple repositories.
- Follow streamed output, tool calls, native subagents, structured questions, and plans.
- Review commits and file diffs, preview documents, media, and CAD models, and inspect task usage, machine health, and server metrics.
- Push changes with [GitHub](./github) or [GitLab](./gitlab) integration and follow CI.
- [Revive or fork](./recovery) retained work, including after a quota limit or failed session.
- Use a desktop or mobile browser, [voice](./voice), [MCP access](./mcp), or the separate [Go Mode Android shell](./android).

caic runs on Linux, macOS, and Windows through WSL2. The server is a single Go binary with the web app included.

## Choose your next step

| Guide                               | Use it to                                                      |
| ----------------------------------- | -------------------------------------------------------------- |
| [Installation](./installation)      | Install, verify, and run the server                            |
| [Task workflow](./tasks)            | Create, steer, review, and push a task                         |
| [Recovery and handoffs](./recovery) | Continue retained work or change harnesses                     |
| [Configuration](./configuration)    | Set repositories, runtimes, storage, authentication, and voice |
| [Security](./security)              | Understand shared state, credentials, and network exposure     |
| [Architecture](./architecture)      | Understand task lifecycle and restart recovery                 |

Repository copies stay separate, but harness state, caches, and configured host mounts can be shared. Read [Security](./security) before exposing the server or adding writable host mounts.

## Getting help

Report issues at [caic-xyz/caic](https://github.com/caic-xyz/caic/issues), or join the [community on Discord](https://discord.gg/caic). Include your `caic -version` output and the error message.
