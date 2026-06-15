---
# CLI reference: start, run, fork, pull, push, diff, build-image, prune, cache flags, VNC
---

# Commands

## Global flags

These flags apply to all `md` commands:

| Flag | Description |
|---|---|
| `--runtime <runtime>` | Select container runtime: `docker` or `podman` (default: auto-detect) |
| `--control-master` | Enable SSH ControlMaster connection multiplexing (disabled on Windows) |
| `-v, --verbose` | Verbose output |

## Container lifecycle

| Command | Description |
|---|---|
| `md start` | Create and start a container for the current branch; SSH in automatically |
| `md start -display` | Start with X11/VNC desktop environment |
| `md start -tailscale` | Start with [Tailscale](./tailscale) networking |
| `md start -usb` | Start with USB device passthrough (for ADB, Linux only) |
| `md start -no-ssh` | Start container without opening an SSH session |
| `md run <cmd>` | Start a temporary container, run a command, then clean up |
| `md fork` | Snapshot a running container and create a new one on fresh branches |
| `md list` | List all md containers |
| `md list --json` | List containers as JSON |
| `md list --stats` | Include resource usage stats (CPU, memory, disk, network) |
| `md sudo-password` | Print the container's random sudo password |
| `md stop` | Stop the container (preserves filesystem for later revival) |
| `md start` (on stopped container) | Revive a stopped container (re-queries SSH port, restores SSH config) |
| `md purge` | Stop and permanently remove the container |

Re-running `md start` from a repo whose container is stopped or exited is the supported way to revive it. md prints `Reviving stopped container` and reuses the existing container with a fresh SSH port; it does not create a duplicate. If the container is already running, `md start` returns an error and tells you to `ssh` in instead.

## List output

`md list --json` emits one object per container. The `name`, `state`, `uptime`, and `ssh_port` fields are always present. The remaining fields appear only when they apply:

| Field | When present |
|---|---|
| `name` | Always |
| `state` | Always |
| `uptime` | Always |
| `ssh_port` | Always |
| `vncPort` | Container started with `--display` |
| `display` | Container started with `--display` |
| `tailscale` | Container started with `--tailscale` |
| `fqdn` | Tailscale is enabled (the container's tailnet name) |
| `sudo` | Container started with `--sudo` |
| `usb` | Container started with `--usb` |
| `repos` | Container has one or more mapped repos |
| `stats` | `--stats` was passed (CPU, memory, network, disk) |

## Start flags

| Flag | Description |
|---|---|
| `-b, -branch <name>` | Branch to use (default: current branch) |
| `-r, -repo <path>` | Path to git repository (default: current directory) |
| `--image <ref>` | Full base Docker image (e.g. `ghcr.io/caic-xyz/md-user:2026-05-09`) |
| `--tag <tag>` | Tag for the default base image (`ghcr.io/caic-xyz/md-user:<tag>`) |
| `--platform <platform>` | Build and run for `linux/amd64` or `linux/arm64` (default: host architecture) |
| `--display`, `-d` | Enable X11/VNC virtual desktop (port 5901) |
| `--tailscale` | Enable [Tailscale](./tailscale) networking |
| `--usb` | Pass through USB devices (`/dev/bus/usb`, Linux only) |
| `--github` | Inject `GITHUB_TOKEN` into the container |
| `--no-ssh` | Don't SSH into the container after starting |
| `--cpus <n>` | Max CPU cores (default: `NumCPU - 2`, minimum 2; 0 = no limit) |
| `--label key=value`, `-l` | Add Docker container label (repeatable) |
| `--extra-repo path[:branch]`, `-e` | Map an additional git repository (repeatable) |
| `--docker-flag "arg1 arg2"` | Extra flags passed verbatim to `docker run` (shell-quoted, repeatable) |
| `--cache <name>` | Add a well-known cache or a custom `host:container[:ro]` directory (repeatable) |
| `--mount host:container[:ro]` | Bind-mount a host directory into the running container (repeatable) |
| `--sudo` | Enable root access with a random password; grants `SYS_ADMIN` and `/dev/fuse` |
| `-q, --quiet` | Suppress informational output |
| `--control-master` | Enable SSH ControlMaster connection multiplexing |

## Access

| Command | Description |
|---|---|
| `ssh md-<repo>-<branch>` | SSH into the container directly |
| `md vnc` | Open VNC connection to the container desktop |

`md vnc` auto-detects the container from your current repository and branch, the same way `md stop` and `md purge` do. Run it from inside the repo directory with no arguments. You can also pass a container name as a positional argument, or target a specific container with `-b/--branch` and `-r/--repo`.

## Syncing

| Command | Description |
|---|---|
| `md diff` | Show changes vs. base branch (`git diff base`). Extra args forwarded to git, e.g. `md diff --stat` |
| `md diff --all` | Show diffs for all repos in the container |

`md diff` is non-mutating. It leaves the container's git index untouched and runs with git locks disabled, so it is safe to run while an agent is working in the container. Untracked files still appear in the diff.
| `md pull` | Pull changes from container and integrate into local branch |
| `md pull --all` | Pull changes for all repos |
| `md fetch` | Fetch changes from container without integrating (updates remote-tracking ref) |
| `md push` | Force-push local state into the container; creates a backup branch inside |

## Fork

`md fork` snapshots a running container's entire filesystem (installed packages, build artifacts, agent state) and creates a new container where each repo is checked out on a fresh branch.

```bash
# Fork the current container
md fork

# Fork a specific container by name
md fork -source md-myrepo-main

# Fork with extra repos and VNC
md fork -e ../other-project -display
```

Fork flags mirror `md start` plus:

| Flag | Description |
|---|---|
| `-s, --source <name>` | Source container name (default: auto-detect from repo) |
| `--sudo` | Enable root access with a random password; grants `SYS_ADMIN` and `/dev/fuse` |
| `-q, --quiet` | Suppress informational output |

Each repo (source and extra) gets a unique destination branch derived from its source branch (e.g. `main` → `main-0`, then `main-1`, etc.).

## Run

`md run <cmd>` starts a temporary container, runs a command, and cleans up everything:

```bash
md run -- npm test
md run -- cargo check
md run --image ghcr.io/caic-xyz/md-user:2025-05-09 -- npm ci
```

Supports: `--image`, `--tag`, `--platform`, `--repo`, `--branch`, `--github`, `--cpus`, `--docker-flag`, `--mount`, and all cache flags.

## Workflows

### Multi-repo containers

Map multiple repositories into a single container with `--extra-repo`:

```bash
# Start with main project + dependency
md start -r ~/src/backend -e ~/src/shared-lib

# Specify branches explicitly
md start -b feature-x -e ~/src/shared-lib:feature-x
```

All repos are cloned into `~/src/<name>` inside the container. The first repo is primary; extras are pushed alongside it. `md diff`, `md pull`, and `md push` operate on the repo matching your current directory. Use `--all` to operate on all repos:

```bash
md diff --all      # show diffs for every repo
md pull --all      # pull changes from every repo
```

### Fork workflow

Fork a running agent's container to try a different approach without losing progress:

```bash
# Agent is working in md-myrepo-feature-x
# You want to try a different approach:
md fork              # creates md-myrepo-feature-x-0
ssh md-myrepo-feature-x-0
# Work on the fork. If it works out:
md pull              # pull changes back from the fork
md purge             # clean up the fork
# If the original approach was better:
md purge md-myrepo-feature-x-0  # discard the fork
```

The fork preserves the entire filesystem (installed packages, build artifacts, agent history) so you don't lose context. Each repo gets a unique divergent branch.

### CI / one-shot runs

`md run` starts a container, runs a command, and cleans up. Ideal for CI:

```bash
# Run tests in a clean environment
md run -- npm test
md run -- cargo test
md run -- go test ./...

# Run a linter on a specific branch without checking out
md run -b feature-x -- golangci-lint run ./...

# Custom image + specific version
md run --image ghcr.io/caic-xyz/md-user:2026-05-09 -- npm ci && npm test

# Pass through GitHub token for private repos
md run --github -- npm install
```

## AI commit messages

`md pull` can generate commit messages using an LLM. It analyzes the diff and recent commit history to produce a conventional commit message.

### Setup

Set the provider and model via environment variables; the full list of acceptable `ASK_PROVIDER` values is from [genai](https://github.com/maruel/genai#scoreboard):

```bash
export ASK_PROVIDER=deepseek
export ASK_MODEL=deepseek-v4-flsah
```

If not set, md auto-discovers available providers on your system. It prefers CLI-based providers in this order: `pi`, `codex`, `opencode`, `claudecode`, then any others alphabetically. The model defaults to a cheap/fast option.

For large diffs, md uses a progressive reduction pipeline to fit within the LLM's context window. See [Design](./design#ai-commit-message-pipeline) for details.

## Build

### `md build-image`

Builds the `md-root-local` and `md-user-local` Docker images from the embedded source. Use this when:

- You're contributing changes to the container Dockerfiles or setup scripts
- You want to test a change to the container's preinstalled tools
- You want fully local images without pulling from `ghcr.io`

```bash
md build-image
```

The first build takes several minutes (two full Docker builds: root image, then user image on top). Subsequent builds are faster thanks to layer caching.

A `GITHUB_TOKEN` is recommended to avoid rate limits when installing tools like Neovim and rust-analyzer:

```bash
export GITHUB_TOKEN=ghp_...
md build-image
```

Once built, use the local images:

```bash
md start -image md-user-local
```

By default `md build-image` targets your host architecture. Pass `--platform linux/amd64` or `--platform linux/arm64` to build for a different architecture. The platform is part of the specialized image hash, so cross-architecture builds and runs produce distinct images.

### `md prune`

Removes unused `md-specialized-*` and `md-fork-*` images no longer referenced by any container. Also cleans the Docker build cache.

## Cache flags

| Flag | Description |
|---|---|
| `--no-cache <name>` | Exclude a specific default cache (repeatable) |
| `--no-caches` | Disable all default caches |
| `--cache <name>` | Add a well-known cache (use with `--no-caches`) or custom `host:container[:ro]` |

Caches are baked into the image at build time. Only caches whose host directories exist are included; missing directories are silently skipped. The image rebuilds only when the active cache set changes.

For custom caches, append `:ro` to make the copied directory read-only inside the container. The container path accepts `~` or a leading `~/`, which expand to `/home/user`. For a live bind-mount that reflects host changes at runtime, use `--mount` instead of `--cache`. See [Configuration](./configuration#mount-vs-cache) for the difference.

### Well-known caches

| Cache name | Host path | Description |
|---|---|---|
| `bun` | `~/.bun/install/cache` | Bun package manager |
| `cargo` | `~/.cargo/registry`, `~/.cargo/git` | Rust cargo registry and git checkouts |
| `go-mod` | `~/go/pkg/mod` | Go module cache |
| `gradle` | `~/.gradle/caches`, `~/.gradle/wrapper/dists` | Gradle caches and wrapper |
| `maven` | `~/.m2/repository` | Maven repository |
| `npm` | `~/.npm` | npm cache |
| `pip` | `~/.cache/pip` | Python pip cache |
| `pnpm` | `~/.local/share/pnpm/store` | pnpm store |
| `uv` | `~/.cache/uv` | UV Python package manager |
| `android-keys` | `~/.android` (shallow) | Android debug keystore and ADB keys |

## Remote GUI (VNC)

Enable at startup, then open:

```bash
md start -display
md vnc
```

The DISPLAY environment variable is automatically set in SSH sessions, so X11 apps launched from SSH appear on the VNC desktop.

**Recommended VNC clients:**
- **Windows**: RealVNC Viewer, TightVNC, UltraVNC
- **macOS**: Built-in VNC or RealVNC Viewer
- **Linux**: `tigervnc-viewer`, `vinagre`, or `vncviewer`
