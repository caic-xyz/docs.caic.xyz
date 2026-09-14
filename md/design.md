---
# design rationale: why generated Dockerfile, rebuild triggers, cache injection, env injection, agent mounts
---

# Design

This page explains the key design decisions behind md: why things work the way they do, and the trade-offs that were considered.

## Core principles

### Isolation by construction

Each container is locked to a single repository-branch pair. You can:

- Run multiple agents on different branches of the same repo
- Switch your local branches without affecting running agents
- Run tests in parallel without conflicts
- Delete containers cleanly without touching your local checkout

**Containers share no mounts, caches, or state with each other.**

### Explicit Git synchronization

The host and container have separate Git repositories. Changes made inside the container stay there until you explicitly run `md pull`. Starting a container adds a container-specific remote to the host checkout, but does not move your host branches. `md push` moves host state into the container. `md pull` is the only regular synchronization command that integrates container work into existing host branches, while `md fork` creates new host branches for the fork.

### Stable integration points

Agents often amend, reset, or rebase their work. md therefore keeps a Git integration point for each mapped branch rather than relying on the branch's earlier commit remaining in its history. `md diff` compares the checked-out container branch with that point and shows work not yet integrated into the host. `md diff --full` uses the upstream merge base when you need the whole branch instead.

Integration points move only after a successful synchronization. A failed pull leaves unapplied work visible. A push moves the point to the pushed host commit, so the next `md diff` is empty. Forks start with inherited committed work integrated into their new host branches, while inherited uncommitted work remains visible.

md keeps the commits needed by integration points reachable and disables pruning of unreachable Git objects inside containers. Long-lived containers can therefore use more disk space after repeated rebases, resets, and amendments.

### Remote state without credentials

md transfers the host checkout's cached remote-tracking refs into the container at startup and before synchronization commands. It also preserves every mapped branch's upstream and effective push remote. This supports offline rebases and triangular workflows without putting repository credentials in the container. The trade-off is that the container sees the host's last fetched state. A network push from inside the container still requires credentials. See [Syncing](./commands#syncing) for the refresh workflow.

### Warm caches by default

All well-known build caches (Go modules, Cargo registries, npm, pip, Gradle, Maven, pnpm, Bun, uv, Android keys) are baked into the container image at build time. This avoids the slow cold-start problem where a fresh container downloads hundreds of megabytes before the first `npm install`.

### Works with Docker or Podman

md prefers Docker when both runtime commands are installed and selects Podman automatically only when the `docker` command is absent. You can force a choice with `--runtime docker` or `--runtime podman`. Explicitly select Podman when a compatibility shim provides a command named `docker`.

Docker and rootful Podman adapt the container user to the host UID and GID. Rootless Podman instead maps the host user to the image's fixed UID/GID `1000:1000`. This keeps bind-mounted configuration writable without recursively changing ownership across the container home. When a rootless Podman fork is created from a snapshot, md restores user ownership inside the fork before work resumes.

## How the specialized image is built

On `md start`, md generates a Dockerfile at runtime and builds the specialized image on top of the `md-user` image. The Dockerfile adds three things:

- **SSH host key and authorized_keys**: baked in so the container is ready for SSH without manual setup
- **Build caches**: copied from your host using `--build-context`, so cache directories are read directly in-place without copying into the build context
- **Empty agent config directories**: pre-created with correct ownership so runtime bind-mounts work

The image is built with `--no-cache` to ensure layers always rebuild correctly. The generated Dockerfile looks like:

```dockerfile
FROM ghcr.io/caic-xyz/md-user:latest
COPY --chown=root:root ssh_host_ed25519_key /etc/ssh/ssh_host_ed25519_key
COPY --chown=user:user authorized_keys /home/user/.ssh/authorized_keys
COPY --from=cache-go-mod --chown=user:user [".", "/home/user/go/pkg/mod/"]
COPY --from=cache-cargo-registry --chown=user:user [".", "/home/user/.cargo/registry/"]
RUN chmod 0600 /etc/ssh/ssh_host_ed25519_key && \
    mkdir -p /home/user/go/pkg/mod /home/user/.cargo/registry && \
    chown user:user /home/user/go/pkg/mod /home/user/.cargo/registry
CMD ["/root/start.sh"]
```

## When images get rebuilt

md tracks several pieces of information to decide whether the specialized image needs rebuilding:

1. **Base image changed**: the published user image has been updated on the registry
2. **SSH keys changed**: the md key pair was regenerated
3. **Cache set changed**: you added, removed, or changed a cache directory on the host

Only caches whose host directories **currently exist** are tracked. If you remove `~/.cache/pip`, the pip cache is silently excluded; no rebuild is triggered. If you later re-create it, the cache set changes and triggers a rebuild.

For images pulled from a registry, md checks whether a newer version is available without downloading it: a quick metadata check, not a full image pull. If a later pull fails and a local copy already exists, md warns and rebuilds from that local copy. This keeps existing environments usable during registry outages.

## Cache injection design

### Shallow caches

Some host directories contain a few needed files alongside large unwanted subtrees. For example, `~/.android` has `debug.keystore` and `adbkey` (a few KB) but also `avd/` and `cache/` directories (gigabytes).

The `android-keys` cache uses shallow mode: only top-level files are copied, subdirectories are ignored.

### Stale BuildKit cache

If a cache file is present during one build but deleted from the host before the next build, BuildKit may fail with a cache checksum error. md detects this and automatically prunes the BuildKit cache before retrying.

### Parallel startup

While the container boots (sshd startup, Tailscale connection), the host works in parallel:

1. Waits for TCP connectivity on the SSH port
2. Sends `.env` files
3. Pushes git repositories (all repos in parallel, not sequentially)

This reduces total startup latency. The `.env` transfer doubles as the SSH readiness check.

## Agent configuration

Agent config directories are bind-mounted into the container, not copied into the image. This means settings persist across container rebuilds.

md mounts all configured harness directories from your host. This includes home paths, XDG config paths, and XDG data and state paths. The full list is in [Configuration](./configuration#agent-configuration-files).

The `~/.config/md` directory is mounted read-only to prevent accidental modification of SSH keys from inside the container. `~/.agents` is always mounted regardless of which harnesses you use, so you can maintain a centralized AGENTS.md and skills directory.

On the host, md creates a `~/.claude.json` → `~/.claude/claude.json` symlink so Claude Code can find its configuration at the home-directory level.

## Environment injection

Environment variables reach the container through three mechanisms, merged in order:

1. **`.env` file** in each mapped repository root: repo-specific secrets sent at startup
2. **`~/.config/md/env`**: global defaults for all your containers
3. **`--github` flag** at startup: injects `GITHUB_TOKEN`

These are merged into `/home/user/.env` inside the container. The file is sourced during shell initialization, making the variables available to all processes.

The `--github` flag tries `$GITHUB_TOKEN` first, then falls back to `gh auth token` from the GitHub CLI.

## AI commit message pipeline

When `md pull` generates commit messages, it derives an input budget from the model's context window. Set the default with `GIT_DESC_TOKENS` or override it for one pull with `--tokens`. It defaults to 64000 tokens and must be at least 8000. md conservatively estimates three characters per token and reserves one quarter of the window for instructions, reasoning, and the answer.

The generation prompt defaults to a rationale body. It permits a subject-only message only for an obviously trivial, self-explanatory change. Changes that affect behavior, interfaces, dependencies, data, architecture, or multiple meaningful concerns require a body. The prompt asks the model to limit every message line to 120 characters.

Before contacting the model, md asks Git for a normalized patch with fixed `a/` and `b/` prefixes, path quoting, line indicators, context size, rename detection, and submodule formatting. It disables color, external diff drivers, text conversion, and relative paths so your Git configuration cannot unexpectedly change the model input. md then removes diff metadata that does not help describe the change, omits the contents of deleted and lock files, and truncates unusually long lines. It handles larger diffs through a progressive reduction pipeline:

1. **Full diff**: if the cleaned diff fits, generate a commit message directly.
2. **Reduced context**: trim context to three lines around each change.
3. **Omitted bodies**: replace test and JSON/YAML file bodies with an omission marker while retaining their filenames.
4. **Balanced parts**: split between files and hunks where possible. An oversized hunk is split between lines, so one large generated or modified file cannot exceed the budget by itself. Each part receives shorter metadata that omits recent commit details already available to the final request.
5. **Parallel summaries**: summarize up to four parts concurrently, then synthesize one commit message. If the summaries themselves exceed the budget, split oversized responses and merge them in additional rounds until the final request fits.

md prints progress when it reduces or splits a large diff and while it merges summaries. Every model request must succeed and return content. A failed part is never silently discarded. md reports the generation failure and uses its fixed fallback commit message.
