---
# md image hierarchy, build pipeline, container lifecycle, submodule handling, startup flow
---

# Architecture

md uses a three-layer Docker image hierarchy. Understanding how the layers fit together helps you reason about build speed, cache behavior, and when images get rebuilt.

## Image hierarchy

```
ghcr.io/caic-xyz/md-root:latest     ← system packages (Debian, sshd, XFCE, Chrome, etc.)
  └── ghcr.io/caic-xyz/md-user:latest   ← language toolchains (Go, Node, Rust, Python, etc.)
        └── md-specialized-<hash>       ← host-specific layer (SSH host key, build caches, agent dir stubs)
```

The first two layers are pre-built and published weekly to GitHub Container Registry. The third layer is built locally on your machine when you run `md start` for the first time.

### Root image

Contains the operating system and system-level services: Debian stable, sshd, dbus, XFCE desktop, Chrome, Chromium, strace, and debugging tools. Changes infrequently: only when system packages or the container entrypoint change.

Rebuilt monthly. Default tag is `:latest`; pin to a version tag like `:2026-05-01` for reproducible environments.

### User image

Built on top of the root image. Contains language toolchains and AI coding agents: Go, Node.js, Bun, Rust, Python, R, Android SDK, and LLM tools (Claude Code, Codex, Gemini CLI, Kilo Code, OpenCode, Pi, Qwen Code). Also includes Neovim, git-maruel, and radare2.

Rebuilt weekly. Default tag is `:latest`; pin to a version tag like `:2026-05-01` for reproducible environments.

### Specialized image

Built on your machine when you run `md start`. It adds three things on top of the user image:

1. **Dedicated SSH credentials**: the container's host key (for server identity) and an `authorized_keys` file containing your md user public key at `~/.ssh/md`
2. **Build caches**: copies of your host's package manager caches (Go modules, Cargo registries, npm, etc.) so the container starts warm

The image name includes a hash of the base image and active cache configuration, so different cache setups produce distinct images.

This image is rebuilt automatically when:

- The base image has been updated on the registry
- Your SSH keys have changed (new key pair generated)
- The set of active caches has changed (you added or removed a cache directory)

## What happens during `md start`

```
1. Pull base image `md-user` (if updated on registry)
2. Build specialized image `md-specialized-*` (if SSH keys or caches changed)
3. Start container with docker run
   - Bind SSH port to 127.0.0.1 (random port)
   - Bind VNC port if --display (random port, 127.0.0.1 only)
   - Mount agent config directories from host
   - Add Tailscale capabilities if --tailscale
4. Wait for SSH to become ready
5. Send .env files into the container
6. Push git repositories from host to container (parallel per repo)
7. Set up git remotes on the host
8. Open SSH session (unless --no-ssh)
```

Each repo gets a `base` branch inside the container that mirrors the host branch it was started from. The container's working branch tracks `base`, so agents can `git diff base` to see their changes.

## How containers are named

Containers follow the pattern `md-<repo>-<branch>`:

```
md-myrepo-main
md-myrepo-feature-x
md-otherproject-fix-bug
```

Special characters in repo or branch names are sanitized to hyphens. When started outside a git repository, containers get random names like `md-agent-a1b2c3d4`.

## Container labels

md stores container metadata as Docker labels so that `md list` can reconstruct container state without a sidecar database. Labels are read-only after container creation.

| Label | Purpose |
|---|---|
| `md.repos` | Repository list (base64-encoded JSON) |
| `md.display` | VNC display enabled (`"1"` or empty) |
| `md.tailscale` | Tailscale networking enabled (`"1"` or empty) |
| `md.tailscale_ephemeral` | Tailscale node is ephemeral (`"1"` or empty) |
| `md.usb` | USB passthrough enabled (`"1"` or empty) |

You can add your own labels with `md start --label key=value` (repeatable). Custom labels are useful for automation: for example, caic adds `caic=<task-id>` and `harness=<name>` labels to track task ownership.

## SSH and networking

All ports are bound to `127.0.0.1`. No external network exposure from the host:

| Port | Purpose | When |
|---|---|---|
| Random → 22 | SSH access | Always |
| Random → 5901 | VNC desktop | With `--display` |

SSH uses key-based authentication only. md generates two key pairs on first use: a user key (`~/.ssh/md`) for client authentication and a host key (`~/.config/md/ssh_host_ed25519_key`) for server identity. Each container gets its own `known_hosts` entry with the host key pinned.

## Submodule handling

Git submodules are transferred from your host to the container without network access. The host's `.git/modules/` bare repositories are pushed via SSH into the container, and the container configures local file:// URLs so `git submodule update` works without fetching from the internet. This works for nested submodules at any depth.

## Shell environment

The container ensures PATH and environment variables are available in every bash invocation: interactive, non-interactive, login, and non-login. This matters because `ssh host command` runs a non-interactive shell that normally skips `.bashrc`.

Environment variables are loaded through modular scripts in `~/.config/bash.d/`, sourced via `BASH_ENV`. The chain handles:

- Tool PATH entries (Go, Node, Rust, Python, Android SDK, Bun)
- Git completions and prompt
- `.env` file and `~/.config/md/env` environment variables
- Shell editor configuration and aliases

## Disk management

### Image pruning

`md prune` removes specialized and fork images that are no longer referenced by any container. It also cleans the Docker build cache.

### Container cleanup

`md purge` removes the container, its SSH configuration, git remotes on the host, and (for non-ephemeral Tailscale nodes) the device from your tailnet. The container's filesystem is permanently deleted.

`md stop` preserves the container on disk. A subsequent `md start` revives it with a fresh SSH port and configuration.

## How forking works

`md fork` takes a snapshot of a running container's entire filesystem and creates a new container from it. Each repository gets a fresh branch name derived from the source (e.g. `main` → `main-0`).

This preserves installed packages, build artifacts, and agent history while letting you explore a different approach on divergent branches. The forked container is fully independent: deleting the source container has no effect on the fork.
