---
# caic architecture: system components, container model, relay, task lifecycle, startup/adoption, forge/CI, SSE streaming, WebRTC voice, API design
---

# Architecture

caic is a Go HTTP server with an embedded SolidJS web UI that orchestrates AI coding agents running in isolated [md](../md/) containers. This page explains the system structure: what happens when you create a task, how restarts work, and how the pieces fit together.

## System components

```
┌─────────────────────────────────────────────────────────┐
│ HOST                                                    │
│                                                         │
│  ┌──────────┐  HTTP/SSE   ┌──────────────┐              │
│  │ Web UI   │◄───────────►│ caic server  │              │
│  │ (SolidJS)│             │ (Go binary)  │              │
│  └──────────┘             └──────┬───────┘              │
│                             │    │                      │
│  ┌──────────┐               │    │                      │
│  │ Android  │◄──HTTP/SSE────┘    │                      │
│  └──────────┘                    │                      │
│                                  │                      │
│  ┌───────────────────────────────┼───────────────────┐  │
│  │ CONTAINER (per task)          │                   │  │
│  │                 ┌─────────┐   │                   │  │
│  │     relay.py ◄──┤ SSH     │◄──┘                   │  │
│  │       │         └─────────┘                       │  │
│  │       │ stdout/stdin (NDJSON)                     │  │
│  │  ┌────▼─────┐                                     │  │
│  │  │ agent CLI│  (Claude Code, Codex, Gemini, etc.) │  │
│  │  └──────────┘                                     │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

Each task runs in its own Docker container. The caic server communicates with the container over SSH. Inside the container, a Python relay daemon manages the agent process and survives SSH disconnects.

## How tasks work

A task is a unit of work: a prompt given to an AI coding agent working on a specific repository and branch. Tasks have a defined lifecycle. A task starts in Pending and progresses through setup states (Branching, Provisioning, Starting) to Running. When the agent finishes a turn, it transitions to Waiting, Asking, or HasPlan depending on the output. Sending a new prompt brings it back to Running — this cycle repeats for each turn until you stop or purge the task.

Pulling and Pushing are transient states during sync. Stopped preserves the container for later revival; Purged permanently deletes it.

Key states:

| State | What's happening |
|---|---|
| **Pending** | Task created, queued |
| **Branching** | Creating a dedicated git branch on the host |
| **Provisioning** | Launching the Docker container |
| **Starting** | Connecting the agent backend |
| **Running** | Agent is actively producing output |
| **Waiting** | Agent finished a turn, awaiting user input |
| **Asking** | Agent asked a question via `AskUserQuestion` |
| **HasPlan** | Agent finished planning and produced a plan file |
| **Stopping** | Graceful shutdown in progress |
| **Stopped** | Container stopped but preserved (can be revived) |
| **Purging** | Container being permanently deleted |
| **Failed** | Task encountered an error |
| **Purged** | Task is final, log archived |

### How tasks are created

A task is initiated via the web UI or API with a prompt, choosing a repository (or multiple repositories), branch, and agent harness. The server then:

1. Creates a dedicated branch (`caic-N`) on the host
2. Launches an md container with that branch checked out
3. Deploys the relay daemon and agent-specific files into the container
4. Starts the agent and captures its session ID for future resumes
5. Streams all agent output back as SSE events

Tasks can span multiple repositories, allowing the agent to work across related codebases in a single task. Each task is fully isolated: two tasks on the same repository use different branches and different containers. They cannot interfere with each other.

### Git model

Each task gets a dedicated branch like `caic-0`, `caic-1`, etc. The number increments per repository. The task starts from the repository's default branch (or a user-selected base). When the agent commits changes, they land on the task's branch. Only at sync time are those changes pushed to the remote. Until then, everything is local.

For tasks spanning multiple repositories, each repository gets its own dedicated branch. The agent works across all repos within the same task, and changes are pushed together at sync time.

## The relay: agent persistence

The relay is a Python daemon (`relay.py`) that runs inside each container and manages the agent subprocess. It is the reason caic can survive server restarts without losing agent sessions.

### Why a relay

Without the relay, the agent process would die every time the SSH connection dropped (server restart, network hiccup, laptop sleep). The relay decouples the agent's lifetime from the SSH connection:

- **Relay daemon**: runs as a background process inside the container, owns the agent's stdin/stdout
- **SSH attach client**: connects the caic server to the relay over a Unix socket

When the server restarts, SSH connections are severed, but the relay and agent keep running. On restart, caic discovers the container, reads the relay's output log to restore state, and attaches a new SSH client to the live relay.

### Output persistence

All agent output (and user inputs) are written to an append-only `output.jsonl` file inside the container. This log is the source of truth for conversation recovery. On restart, caic reads it from the last byte offset it saw, so no messages are lost.

### Diff tracking

The relay periodically checks `git diff` in the container and emits diff stat messages. These show up in the UI as real-time file change counts while the agent works.

## Server startup and container adoption

When caic starts, it goes through a phased initialization:

1. **Parallel I/O**: discovers git repositories under the root directory, loads purged task logs from disk, and lists Docker containers — all concurrently
2. **Runner init**: creates a runner per discovered repository, which scans git branches and initializes agent backends
3. **Log loading**: loads recently-active purged tasks (last 14 days, up to 5 per repo) from JSONL log files so their history appears in the UI
4. **Container adoption**: for each running Docker container with a caic label, checks whether the relay is alive and auto-reattaches

Container adoption is the key to zero-loss restarts. It checks:

- The container's `caic` label (proving caic started it)
- The `harness` label (which agent is running)
- Whether the relay daemon is still alive (socket + PID check)
- Reads the relay's `output.jsonl` to restore message history

If the relay is alive, caic spawns a background goroutine to reattach, and the task resumes streaming as if nothing happened. If the relay is dead, the relay log tail is captured for diagnostics and the task is marked waiting so you can restart it.

### Container death detection

caic watches Docker events for container die events. When a container exits, the corresponding task is archived as Stopped. It can be revived later — the container's filesystem is preserved.

## Agent backend abstraction

caic supports multiple AI coding agents through a shared backend interface. Each agent is implemented as a separate package:

| Harness | Protocol | Wire format |
|---|---|---|
| Claude Code | SSH + relay | NDJSON `stream-json` |
| Codex | SSH + relay | NDJSON |
| Gemini CLI | SSH + relay | NDJSON `stream-json` |
| Kilo Code | SSH + relay | HTTP SSE (via bridge) |
| OpenCode | SSH + relay | ACP (JSON-RPC) |
| Pi | SSH + relay | NDJSON |

Each backend is responsible for parsing its agent's wire format into normalized message types (text, tool use, results, diffs, etc.) that the server can stream to clients without knowing which agent produced them.

The abstractions are layered:

- **Container layer** (`internal/container`): wraps md's Docker operations (launch, stop, fork, revive)
- **Task layer** (`internal/task`): orchestrates a single task's lifecycle (runner, session management, git operations)
- **Agent layer** (`internal/agent`): SSH session management, message parsing, relay deployment

## API design

### REST + SSE

The API is JSON-over-HTTP with Server-Sent Events for real-time streaming:

- **REST endpoints** for task creation, input, sync, stop, purge — standard JSON request/response
- **SSE endpoints** for live task events (agent output, state changes, stats) and task list updates
- **WebSocket** for VNC display streaming (one connection per task)

### Authentication

When auth is enabled (OAuth configured), all API routes except auth endpoints require a valid JWT session. The JWT is sent as a cookie (`caic_session`) or `Authorization: Bearer` header (for Android and API clients).

Routes for `/api/v1/auth/` are always public. Webhook endpoints (`/webhooks/github`, `/webhooks/gitlab`) have their own HMAC signature verification.

### Response compression

To minimize bandwidth, API responses are compressed. The server supports zstd (preferred), brotli, and gzip. Static frontend assets are precompressed with brotli at build time.

### Code generation

The API types and routes are defined in Go structs with declarative annotations. A code generator produces typed clients for TypeScript, Kotlin (Android), and Swift. The generated SDKs are checked into the repository and never edited manually.

See the full [API reference](https://github.com/caic-xyz/caic/blob/main/sdk/API.md) for endpoint details.

## Forge integration

caic integrates with GitHub and GitLab for automatic pull/merge request creation and CI monitoring.

### PR/MR creation flow

1. Agent finishes work and commits changes to the task branch
2. User triggers sync (or auto-sync configured)
3. Changes are pushed to the remote
4. caic creates a PR/MR with the task title and agent result summary
5. CI monitoring begins

### CI monitoring

After PR creation, caic monitors CI status:

- **Polling**: every 15-30 seconds, checks check-run/pipeline status
- **Webhooks**: when configured, receives push events that trigger immediate re-check

When CI passes or fails, the agent is notified with a summary so it can act on feedback. An auto-fix loop allows the agent to iterate on CI failures automatically.

### Auth modes

Different levels of forge integration are available:

| Mode | Config | Capabilities |
|---|---|---|
| PAT | `[github] token` or `[gitlab] token` | Single-user, polling only |
| OAuth | `oauth_client_id` + `oauth_client_secret` | Multi-user with login, polling only |
| GitHub App | `app_id` + `app_private_key_pem` | Webhooks, auto task creation from issues/PRs/comments |

See [GitHub Integration](./github) and [GitLab Integration](./gitlab) for setup details.

### Bot automation

When a GitHub App is configured, caic can automatically create tasks in response to forge events:

- **Issue opened** with `caic` label: agent fixes the issue
- **PR opened** targeting the default branch: agent reviews the PR
- **Comment `@caic`**: agent acts on the instruction

The bot's comments include links back to the caic instance so you can follow the agent's work.

## WebRTC voice

caic supports voice interaction via a WebRTC-to-Gemini-WebSocket bridge. When configured with a Gemini API key and an open UDP port, the server can relay audio from the web UI or Android app to Gemini Live for voice conversations with the agent.

## Container stats

While tasks are running, caic polls Docker every 5 seconds for container resource metrics: CPU percentage, memory usage, network I/O, block I/O, and disk usage. These are streamed to the UI as stats events.

## Configuration watching

caic watches its own executable and `config.toml` for changes. When either is modified, it triggers a graceful shutdown. Combined with systemd's `Restart=always` or launchd's `KeepAlive`, this enables seamless restarts after a config change or binary update.

## Auto-update

When enabled (the default), caic checks GitHub Releases on a configurable cron schedule and replaces the binary in place when a new version is found. The binary self-update triggers the watch mechanism, causing a restart onto the new version.
