---
# design rationale: relay, container-per-task, Go+SolidJS, sessions, adoption, task model, config watching
---

# Design

This page explains the key design decisions behind caic: why things work the way they do, and the trade-offs that were considered.

## Core principles

### One container, one task

Every task gets its own Docker container. This is the fundamental isolation boundary:

- Agents on different branches don't interfere with each other's working trees
- Server restarts don't kill running agents (the relay persists inside the container)
- You can delete a task's container without affecting anything else
- Resource limits apply per-task, not per-application

Containers share no state with each other by default. Configurable cache mounts (host directories mapped into containers) can be shared across tasks, which is useful for build caches and package managers. Well-known caches are opt-in: you enable the ones you want in the Settings UI. Each container is locked to a dedicated branch, and a task may span multiple repositories.

### Zero host modification

caic never modifies files on your host git checkout. Changes made by the agent stay inside the container until you explicitly sync (push). The host sees each task's branch as a regular git branch. You can inspect it, but the agent works in the container's copy.

For multi-repo tasks, the agent works in the container's copy of each repository. All changes are pushed together at sync time.

### Resilience by default

The server can crash. Your laptop can sleep. Docker can restart. In all these cases, the agent keeps running inside the container thanks to the relay, and caic reconnects without losing messages.

## Why a relay inside containers

The relay is the most important architectural decision in caic. Without it, agent sessions are fragile: every SSH disconnection kills the agent. With the relay, the agent process outlives any single connection.

### Alternatives considered

Running the agent directly over SSH is simpler: the server opens an SSH session, executes the agent CLI, and reads stdout. This works until the SSH connection drops. With direct SSH:

- The agent dies on every connection drop (server restart, network hiccup, laptop sleep)
- The server must buffer all agent output to survive restarts
- Recovery means restarting the agent with `--resume`, which may lose the last few messages

### How the relay solves this

The relay daemon runs as a background process inside each container:

1. It owns the agent subprocess (started via `setsid` so Ctrl+C doesn't propagate)
2. It writes all agent output to an append-only JSONL log
3. It listens on a Unix socket for attach/detach clients
4. On attach, it replays events from a byte offset — zero loss

The caic server never talks directly to the agent. Instead, it attaches over SSH to the relay. The relay bridges stdin/stdout between the SSH client and the agent process.

### Byte-offset reconnect

The simplest way to recover agent output is to re-read the entire log file. But conversation logs can be megabytes. The relay supports reconnection from a byte offset: the server remembers the last position it read, and on reattach, the relay replays only new messages.

### One client at a time

The relay enforces a single attached client. This prevents two server instances from sending conflicting commands to the same agent. It also simplifies state management: no need for multi-client coordination.

## Why Go + SolidJS

The server is a single Go binary with the web UI compiled in:

- **Single binary deployment**: no Node.js runtime needed on the server, no separate web server
- **Static compilation**: the binary contains everything — Go runtime, embedded frontend assets (precompressed with brotli), logos, and Python scripts for the relay
- **Low resource usage**: the server uses a few megabytes of memory at idle, important for long-running background services
- **SolidJS for the frontend**: reactive UI with fine-grained updates, no virtual DOM overhead

## Server startup design

### Parallel initialization

Server startup is phased to minimize latency:

1. **Parallel I/O phase**: repo discovery, log loading, and container listing run concurrently. These are I/O-bound and independent.
2. **Runner init phase**: after repos are known, runners are initialized in parallel (one per repo). Each runner scans git branches and initializes agent backends.
3. **Adoption phase**: uses the pre-fetched container list to adopt running tasks. Each container is processed concurrently.

The HTTP listener is opened before any of this work begins. This means the port conflict is detected immediately, not after minutes of initialization.

### Container adoption

On restart, caic list containers, verifies ownership, checks relay health, restores conversation state, and reattaches to live relays. This is complex but necessary: without adoption, every restart would orphan running agents.

Ownership is verified via Docker labels. A `caic` label containing the task ID proves that caic started the container. If the label is missing, the container is ignored even if it matches the naming pattern.

### Graceful shutdown

On SIGINT (Ctrl+C) or config/binary change, caic:

1. Cancels the server context
2. Closes all active WebRTC voice sessions
3. Gives the HTTP server 5 seconds to drain in-flight requests
4. Exits cleanly

The relay daemons inside containers are unaffected — they stay alive because the SSH connection drop doesn't send the null-byte sentinel.

## Authentication design

caic supports two authentication transport mechanisms:

- **Cookie** (`caic_session`): for the web UI, set automatically on login. SameSite=Lax prevents CSRF.
- **Authorization: Bearer**: for Android and API clients that can't use cookies easily.

Both carry the same HS256 JWT. The session secret is generated on first launch and stored in `settings.json`.

When no OAuth provider is configured, the auth middleware passes through — all routes are accessible without authentication. This is the default for single-user setups behind Tailscale or on a local machine.

## Forge abstraction

GitHub and GitLab forge detection is automatic from the git remote URL.

### Rate limiting with throttles

Each forge client gets its own rate-limit throttle. Before making an API call, the throttle checks whether the rate-limit budget is sufficient. If not, the call blocks until budget is replenished. This prevents 429 responses and ensures fair use across multiple tasks.

### CI cache

CI check results are cached to disk so that restarts don't lose CI state. When caic starts, it reloads the CI cache and re-monitors any branches that had active CI checks.

## Secret scanning on push

Before pushing changes to the remote, caic scans the diff for:

- AWS access keys, GitHub PATs/tokens, API secret keys
- Private key material (RSA, DSA, EC, OpenSSH, PGP)
- Hardcoded credentials in config files

This is a best-effort safety net. It catches the most common accidental credential leaks before they leave your machine. Found issues are reported to the agent so it can fix them before the push.

## Config watching

caic watches both its executable and `config.toml` for filesystem changes. When either is modified, the server gracefully shuts down. The systemd service manager (or launchd on macOS) then restarts it with the new binary or config.

This enables several workflows:

- **Config changes**: edit `config.toml`, save, and caic restarts with the new settings within seconds
- **Binary updates**: the auto-updater replaces the binary in place; the watcher detects the change and triggers a restart
- **Rebuilds**: `go install` replaces the binary; the watcher picks it up

## Title generation

When an agent finishes a turn, caic generates a short title (3-8 words) from the conversation using an LLM. The title appears in the task list so you can identify tasks at a glance.

The LLM provider is auto-detected from the available harnesses (preferring locally-available providers) and falls back to the cheapest model. Title generation is fire-and-forget: it runs asynchronously and does not block the agent's next turn.

## Usage tracking

caic tracks per-provider usage quotas (credits, tokens) so you can see how much budget remains. Usage fetchers support:

- **OAuth-based providers** (Anthropic, Codex): credential file watching with exponential backoff
- **API-key-based providers** (DeepSeek, OpenRouter): direct API calls with caching
