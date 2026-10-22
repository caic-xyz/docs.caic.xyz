---
# md image hierarchy, build pipeline, container lifecycle, submodule handling, startup flow
---

# Architecture

md uses a three-layer container image hierarchy with Docker or Podman. Understanding how the layers fit together helps you reason about build speed, cache behavior, and when images get rebuilt.

## Image hierarchy

```text
ghcr.io/caic-xyz/md-root:latest     ← system packages (Debian, sshd, XFCE, Chrome, etc.)
  └── ghcr.io/caic-xyz/md-user:latest   ← language toolchains (Go, Node, Rust, Python, etc.)
        └── md-specialized-<hash>       ← host-specific layer (SSH host key, build caches, agent dir stubs)
```

The first two layers are pre-built and published weekly to GitHub Container Registry. The third layer is built locally on your machine when you run `md start` for the first time.

### Root image

Contains the operating system and system-level services: Debian stable, sshd, dbus, XFCE desktop, Chrome, Chromium, strace, and debugging tools. Changes infrequently: only when system packages or the container entrypoint change.

Rebuilt monthly. Default tag is `:latest`; pin to a version tag like `:2026-05-01` for reproducible environments.

### User image

Built on top of the root image. Contains language toolchains and AI coding agents: Go, Node.js, Bun, Rust, Python, R, Android SDK, and LLM tools (Claude Code, Codex, Kilo Code, OpenCode, Pi, Qwen Code). Also includes Neovim, git-maruel, and radare2.

Rebuilt weekly. Default tag is `:latest`; pin to a version tag like `:2026-05-01` for reproducible environments.

### Specialized image

Built on your machine when you run `md start`. It adds three things on top of the user image:

1. **Dedicated SSH credentials**: the container's host key (for server identity) and an `authorized_keys` file containing your md user public key at `~/.ssh/md`
2. **Build caches**: copies of your host's package manager caches (Go modules, Cargo registries, npm, etc.) so the container starts warm
3. **Agent config mount points**: empty directories with the ownership needed for host config bind mounts

The image name includes a hash of the base image and active cache configuration, so different cache setups produce distinct images.

The image is rebuilt automatically when:

- The base image has been updated on the registry
- Your SSH keys have changed (new key pair generated)
- The set of active caches has changed (you added or removed a cache directory)
- The reusable image is missing, for example after `md prune`

md verifies the runtime image before reusing a cached build decision, so pruning or replacing an image cannot make the next launch reuse a missing or stale image.

If a registry pull fails but md already has a local copy of the remote base image, md warns and keeps using the local copy. A first run with no local base image still fails.

## What happens during `md start`

```text
1. Create any missing mapped host branch from the repository's cached default remote branch, and configure a mapped branch without an upstream to track it
2. Pull base image `md-user` (if updated on registry, or use the local copy if the pull fails and one exists)
3. Build specialized image `md-specialized-*` (if SSH keys or caches changed)
4. Start container with the selected runtime
   - Bind SSH port to 127.0.0.1 (random port)
   - Bind VNC port if --display (random port, 127.0.0.1 only)
   - Mount agent config directories from host
   - Grant the standard debugging and container-network capabilities
   - Pass through the TUN device if --tailscale or --sudo
   - Pass through raw USB and attached USB serial adapters if --usb
5. Wait for SSH to become ready
6. Send .env files into the container
7. Transfer mapped branches, cached remote refs, and selected tags into the container (parallel per repository)
8. Configure branch upstreams and remotes in the container, and copy the host's global and repository-specific Git names and emails
9. Add a container remote to each host checkout
10. Record the initial Git integration point for each mapped branch
11. Open SSH session (unless --no-ssh)
```

The first mapped branch is checked out in the container. Each mapped branch keeps the same upstream and effective push remote as its host branch, and the host's remotes are configured in the container. The container also receives every remote-tracking ref already cached in the host checkout, so commands such as `git rebase origin/main` work without network access. Network operations from the container still require credentials. See [Syncing](./commands#syncing) for how to refresh the container's view of remote state.

md records the container commit most recently established in the host branch as an integration point. `md diff` compares against this point, so it continues to show unintegrated work after an agent amends, resets, or rebases commits. `md diff --full` instead compares the whole checked-out branch with its upstream merge base.

On the host, the container-specific remote keeps a remote-tracking ref for each mapped branch. These refs record the container commits the host saw during synchronization. `md pull` integrates from them. Only `md pull` moves existing host branches, while `md fork` creates new ones.

### Container runtime

md uses Docker when both runtime commands are installed. It selects Podman automatically only when the `docker` command is not installed. To force one, place `--runtime docker` or `--runtime podman` before the command. Use `--runtime podman` when a Podman compatibility shim provides the `docker` command. The selected runtime owns that command's containers and images.

With rootless Podman, the host user maps to the image's fixed `user` account at UID/GID `1000:1000`. This keeps host config mounts writable even when your host UID and GID differ. Docker and rootful Podman instead adapt the container account to your host IDs.

### Mapping multiple repos

Each repo is mounted under `~/src/` using its directory name. When two mapped repos share the same base name, md mounts them under disambiguated paths relative to their common parent directory instead of letting them collide. For example, mapping `~/work/api` and `~/play/api` mounts them as `~/src/work/api` and `~/src/play/api`.

## How containers are named

Containers follow the pattern `md-<repo>-<branch>`:

```text
md-myrepo-main
md-myrepo-feature-x
md-otherproject-fix-bug
```

Special characters in repo or branch names are sanitized to hyphens. When started outside a git repository, containers get random names like `md-agent-a1b2c3d4`.

## Saved container settings

Each container retains its mapped repositories and whether display, Tailscale, USB, and sudo access were enabled. md reads these settings from the selected runtime, so commands such as `md list`, `md start` on a stopped container, and `md fork` do not need a sidecar database.

You can add your own runtime labels with `md start --label key=value` (repeatable). Custom labels are useful when another tool needs to associate a container with external work.

## SSH and networking

All ports are bound to `127.0.0.1`. No external network exposure from the host:

| Port          | Purpose     | When             |
| ------------- | ----------- | ---------------- |
| Random → 22   | SSH access  | Always           |
| Random → 5901 | VNC desktop | With `--display` |

SSH uses key-based authentication only. md generates two key pairs on first use: a user key (`~/.ssh/md`) for client authentication and a host key (`~/.config/md/ssh_host_ed25519_key`) for server identity. Each container gets its own `known_hosts` entry with the host key pinned.

## Submodule handling

Git submodules are transferred from your host to the container without network access. The container configures local URLs so `git submodule update` works without fetching from the internet. This works for nested submodules at any depth. The `--tags` expression used for the parent repository also filters tags in initialized submodules.

## Shell environment

The container ensures PATH and environment variables are available in every bash invocation: interactive, non-interactive, login, and non-login. This matters because `ssh host command` runs a non-interactive shell that normally skips `.bashrc`.

Environment variables are loaded through modular scripts in `~/.config/bash.d/`, sourced via `BASH_ENV`. The chain handles:

- Tool PATH entries (Go, Node, Rust, Python, Android SDK, Bun)
- Git completions and prompt
- `.env` file and `~/.config/md/env` environment variables
- Shell editor configuration and aliases

## Disk management

### Image pruning

`md prune` removes specialized and fork images that are no longer referenced by any container. Without a global `--runtime` selection, it checks every installed supported runtime and cleans each runtime's build cache.

### Container cleanup

`md purge` removes the container, its SSH configuration, git remotes on the host, and (for non-ephemeral Tailscale nodes) the device from your tailnet. The container's filesystem is permanently deleted.

`md stop` preserves the container on disk. A subsequent `md start` revives it with a fresh SSH port and configuration.

## How forking works

`md fork` takes a snapshot of a running or stopped container's entire filesystem and creates a new container from it. Each repository gets a fresh primary branch name derived from the source, for example `main` becomes `main-0`. Additional mapped branches keep their names.

This preserves installed packages, build artifacts, agent history, commits, and uncommitted changes while letting you explore a different approach. md creates the new primary branches on the host and treats inherited committed work as already integrated. Inherited uncommitted work remains visible in `md diff`. The source container is unchanged, and deleting it has no effect on the fork.

Display, Tailscale, USB, and sudo settings are inherited from the source. Override any of them with `--display`, `--tailscale`, `--usb`, or `--sudo`. Add `=false` to disable an inherited setting, for example `md fork --usb=false`.

## Shallow repositories and submodules

md supports shallow host repositories and preserves the Git history needed for task synchronization. Submodules can be shallow or detached; md prepares their mapped state so work can proceed in the container. Before starting, initialize the submodules your task needs in the host checkout.
