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

### Zero host modification

md never modifies files on your host checkout. Changes made inside the container stay there until you explicitly `md pull`. The host sees the container as a git remote: your working tree is untouched.

### Warm caches by default

All well-known build caches (Go modules, Cargo registries, npm, pip, Gradle, Maven, pnpm, Bun, uv, Android keys) are baked into the container image at build time. This avoids the slow cold-start problem where a fresh container downloads hundreds of megabytes before the first `npm install`.

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

For images pulled from a registry, md checks whether a newer version is available without downloading it: a quick metadata check, not a full image pull.

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

md mounts all known agent directories from your host: home paths (`~/.claude`, `~/.codex`, `~/.pi`, and others), XDG config paths (`~/.config/opencode`, `~/.config/goose`), XDG data and state paths. The full list is in [Configuration](./configuration#agent-configuration-files).

The `~/.config/md` directory is mounted read-only to prevent accidental modification of SSH keys from inside the container. `~/.config/agents` is always mounted regardless of which harnesses you use, so you can maintain a centralized AGENTS.md and skills directory.

On the host, md creates a `~/.claude.json` → `~/.claude/claude.json` symlink so Claude Code can find its configuration at the home-directory level.

## Environment injection

Environment variables reach the container through three mechanisms, merged in order:

1. **`.env` file** in your repository root: repo-specific secrets (auto-mounted)
2. **`~/.config/md/env`**: global defaults for all your containers
3. **`--github` flag** at startup: injects `GITHUB_TOKEN`

These are merged into `/home/user/.env` inside the container. The file is sourced during shell initialization, making the variables available to all processes.

The `--github` flag tries `$GITHUB_TOKEN` first, then falls back to `gh auth token` from the GitHub CLI.

## AI commit message pipeline

When `md pull` generates commit messages, it handles diffs of any size through a progressive reduction pipeline:

1. **Full diff**: if the entire diff fits within the LLM's context window, generate a commit message directly
2. **Reduced context**: trim diff context lines to 3 per hunk, keeping only the most relevant surrounding code
3. **Filtered**: exclude test files, data files (`.json`, `.yaml`, `.yml`), and generated files (lock files, vendored dependencies). Each filter is applied progressively: a filter is skipped if it would eliminate all remaining files.
4. **Map-reduce**: split the remaining files into context-sized chunks, summarize each in parallel (up to 4 concurrent LLM calls), then synthesize a unified commit message from the summaries

At every step, the pipeline preserves an annotation listing which files were omitted, so the LLM knows they existed. This is the same pipeline used by caic for pull request descriptions.
