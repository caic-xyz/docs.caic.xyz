---
# CLI reference: start, run, fork, pull, push, diff, build-image, prune, cache flags, VNC
---

# Commands

## Global flags

Place global flags before the command, for example `md --runtime podman start`.

| Flag | Description |
|---|---|
| `--runtime <runtime>` | Select container runtime: `docker` or `podman` (default: auto-detect) |
| `--control-master` | Enable SSH ControlMaster connection multiplexing (disabled on Windows) |
| `-v, --verbose` | Enable debug logging |

Commands that expose flags also accept `-v` and `--verbose` after the command.

## Command summary

| Command | Description |
|---|---|
| `md start` | Create or revive a branch-locked container, then open an SSH session |
| `md run <command>` | Run a command in a temporary container, then remove it |
| `md fork` | Snapshot a container and continue in a new container on fresh branches |
| `md list` | List md containers |
| `md diff` | Show container work that has not been integrated into the host |
| `md pull` | Integrate container work into host branches |
| `md push` | Replace container branches with host state after creating backups |
| `md stop` | Stop a container while preserving its filesystem |
| `md purge` | Permanently remove a container; `md kill` is an alias |
| `md sudo-password` | Print a container's random sudo password |
| `md vnc` | Open a container's VNC desktop |
| `md build-image` | Build the local `md-root-local` and `md-user-local` images |
| `md prune` | Remove unused md images and build cache from all available runtimes |
| `md version` | Print version information |
| `md help` | Print command help |
| `md ssh` | Remind you to use `ssh md-<repo>-<branch>` directly |

## Container lifecycle

| Command | Description |
|---|---|
| `md start` | Create and start a container for the current branch; SSH in automatically |
| `md start -display` | Start with X11/VNC desktop environment |
| `md start -tailscale` | Start with [Tailscale](./tailscale) networking |
| `md start -usb` | Start with USB device passthrough (for ADB, Linux only) |
| `md start -no-ssh` | Start container without opening an SSH session |
| `md run <cmd>` | Start a temporary container, run a command, then clean up |
| `md fork` | Snapshot a running or stopped container and create a new one on fresh branches |
| `md list` | List all md containers |
| `md list --json` | List containers as JSON |
| `md list --stats` | Include resource usage stats (CPU, memory, disk, network) |
| `md sudo-password` | Print the container's random sudo password |
| `md stop` | Stop the container (preserves filesystem for later revival) |
| `md start` (on stopped container) | Revive a stopped container (re-queries SSH port, restores SSH config) |
| `md purge [container]` | Stop and permanently remove the container |

Re-running `md start` from a repo whose container is stopped or exited is the supported way to revive it. md prints `Reviving stopped container` and reuses the existing container with a fresh SSH port. It preserves the container's branches and integration points instead of resetting them from the host. If the container is already running, `md start` returns an error and tells you to `ssh` in instead.

## List output

`md list` accepts `--json` for machine-readable output and `--stats` to add CPU, memory, network, and disk usage.

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
| `--usb` | Pass through raw USB devices and attached USB serial adapters (Linux only) |
| `--github` | Inject `GITHUB_TOKEN` into the container |
| `--no-ssh` | Don't SSH into the container after starting |
| `--cpus <n>` | Max CPU cores (default: `NumCPU - 2`, minimum 2; 0 = no limit) |
| `--label key=value`, `-l` | Add a container label (repeatable) |
| `--extra-repo path[:branch1[,branch2...]]`, `-e` | Map an additional git repository and optionally one or more branches (repeatable) |
| `--extra-branch <name>` | Map an additional branch from the primary repository (repeatable) |
| `--tags <regexp>` | Select tags to map (default: all tags); use `--tags ''` to map none |
| `--docker-flag "arg1 arg2"` | Extra flags passed verbatim to `docker` or `podman run` (shell-quoted, repeatable) |
| `--cache <name>` | Add a well-known cache or a custom `host:container[:ro]` directory (repeatable) |
| `--no-cache <name>` | Exclude a default well-known cache (repeatable) |
| `--no-caches` | Disable all default caches |
| `--mount host:container[:ro]` | Bind-mount a host directory into the running container (repeatable) |
| `--sudo` | Enable root access with a random password; grants `SYS_ADMIN` and `/dev/fuse` |
| `-q` | Suppress informational output |

Every mapped branch must exist on the host and have an upstream. This remains required when you revive, synchronize, diff, or fork a container. If a branch or upstream is missing, md stops and explains how to repair it. `md start` transfers mapped branches, selected tags, and all remote-tracking refs cached by the host. Other local branches do not become container branches unless a mapped branch tracks one as its upstream. md preserves each mapped branch's upstream and effective push remote. The refs in the container are only as current as the host checkout. Run `git fetch` on the host first when current remote state matters, then run `md diff`, `md pull`, or `md push` to refresh the cached remote refs in the container.

An upstream can be another local branch through Git's `.` remote. md mirrors that local branch so the upstream also resolves in the container. A non-primary mapped branch cannot track the primary branch because a fork renames the primary while additional branches keep their names.

md refuses to start when any mapped repository and branch pair is already assigned to another container. Purge that container first or choose a different branch.

Repository-local Git hooks are available in the container when `core.hooksPath` is a relative path that stays within the repository. Absolute paths, home-relative paths, and paths that escape the repository are not transferred.

## Access

| Command | Description |
|---|---|
| `ssh md-<repo>-<branch>` | SSH into the container directly |
| `md vnc` | Open VNC connection to the container desktop |

`md vnc`, `md stop`, `md purge`, and `md sudo-password` auto-detect the container from your current repository and branch. Run them from inside the repository with no arguments. Each also accepts a container name as a positional argument, or `-b/--branch <name>` and `-r/--repo <path>` to select a container.

## Syncing

| Command | Description |
|---|---|
| `md diff` | Show checked-out container branch changes since their last integration into the host, including uncommitted and untracked files |
| `md diff --full` | Show the whole checked-out branch from its upstream merge base |
| `md diff --all` | Show diffs for all repositories in the container |
| `md pull` | Commit pending container changes and integrate the current repository's mapped branches into the host |
| `md pull --all` | Pull every repository mapped into the container |
| `md push` | Back up the current repository's container branches, then replace them with host state |
| `md push --all` | Push every repository mapped into the container |

`md diff` moves no branch and leaves the container's Git index untouched. It refreshes cached remote refs and runs with Git locks disabled, so it is safe to run while an agent is working. During an interrupted rebase in the container, it identifies the branch from the rebase state and still compares against that branch's integration point. Extra arguments are forwarded to `git diff`, for example `md diff --stat` or `md diff --name-only`. With `--exit-code` or `--quiet`, it preserves Git's exit status: 0 for no differences, 1 for differences, and 2 for an error.

If the checked-out branch was created inside the container and has no integration point, `md diff` shows the whole branch. If the branch includes a newer upstream than its integration point, the output may include upstream commits. md reports either case on standard error. Use `md diff --full` when you want the branch comparison with its upstream.

Before diffing, md verifies that every mapped host branch still has the upstream recorded in the container. If an upstream changed, use `md pull` or `md push` to update the container's branch configuration.

The sync commands accept `-b/--branch <name>` and `-r/--repo <path>` to select a container. They also have these command-specific flags:

| Command | Flag | Description |
|---|---|---|
| `diff` | `--all` | Operate on all repositories in the container |
| `diff` | `--full` | Compare the whole branch with its upstream merge base |
| `pull` | `--all` | Operate on all repositories in the container |
| `pull` | `-n, --no-describe` | Use a fixed commit message instead of an AI-generated description |
| `pull` | `--tokens <count>` | Set the model context window used for AI commit descriptions |
| `push` | `--all` | Operate on all repositories in the container |

`md pull` fast-forwards when the host branch is behind the container. It rebases host-only commits when both sides advanced. When the container rewrote history, it resets a host branch that has not advanced or rebases host-only commits onto the rewritten history. These operations can rewrite host commit IDs. During a reset, an untracked host file is overwritten if the container now tracks the same path. md refuses to begin if the host has tracked changes or a rebase in progress.

If integration conflicts, md leaves the rebase unresolved for you to inspect. The host checkout may be on another mapped branch where that rebase was needed. Resolve the conflict and run `git rebase --continue`, then run `md pull` again so md records the current integration points. If you instead run `git rebase --abort`, that branch and later mapped branches remain unintegrated. Running `md pull` again retries the integration and may produce the same conflict. Successfully integrated branches remain integrated if a later mapped branch fails. Integration points move only after every mapped branch succeeds, so `md diff` may continue to show work that already reached the host after a partial failure.

`md push` first commits Git-visible container changes and creates backup branches inside the container. It creates `backup-<timestamp>` at the checked-out commit and `backup-<timestamp>-<n>-<sanitized-branch>` for each mapped branch. Characters such as `/` become `-` in the sanitized branch name. To recover, enter the container, run `git branch --list 'backup-*'`, and check out or reset to the backup you need. md has no separate restore command.

The check for uncommitted changes on mapped host branches happens after this backup. A refused push can therefore still commit pending container changes and create the backup branches. If the check passes, md resets the mapped container branches to the host branches. Ignored untracked files in the container are not part of the backup and can be overwritten when the host tracks the same path.

For the complete behavioral model, see [Git model: host branches, container branches, and what each command does](https://github.com/caic-xyz/md/blob/main/docs/GIT_MODEL.md).

## Fork

`md fork` snapshots a running or stopped container's entire filesystem (installed packages, build artifacts, agent state) and creates a new container where each repo is checked out on a fresh branch.

```bash
# Fork the current container
md fork

# Fork a specific container by name
md fork -source md-myrepo-main

# Fork with extra repos and VNC
md fork -e ../other-project -display
```

Fork flags:

| Flag | Description |
|---|---|
| `-s, --source <name>` | Source container name (default: auto-detect from repo) |
| `-b, --branch <name>` | Branch used to auto-detect the source container |
| `-r, --repo <path>` | Repository used to auto-detect the source container |
| `-e, --extra-repo path[:branch1[,branch2...]]` | Add another repository to the fork (repeatable) |
| `--tags <regexp>` | Select tags for added repositories; source repositories inherit their existing selection |
| `--display[=false]` | Enable or disable the desktop (default: inherit) |
| `--tailscale[=false]` | Enable or disable Tailscale (default: inherit) |
| `--usb[=false]` | Enable or disable USB passthrough (default: inherit) |
| `--sudo[=false]` | Enable or disable sudo access (default: inherit) |
| `--github` | Inject `GITHUB_TOKEN` into the fork |
| `--no-ssh` | Do not open an SSH session after forking |
| `--cpus <n>` | Maximum CPU cores (0 means no limit) |
| `--docker-flag "arg1 arg2"` | Pass extra flags to `docker run` or `podman run` (repeatable) |
| `-l, --label key=value` | Add a container label (repeatable) |
| `-q` | Suppress informational output |

Each repository gets a unique destination primary branch derived from its source primary branch, for example `main` becomes `main-0`, then `main-1`. Additional mapped branches keep their names. Committed source work is anchored in the new host branches and starts integrated, so it does not appear in `md diff`. Inherited uncommitted work still appears. The source container is unchanged. If setup fails, md removes the partial fork and rolls back branch changes that have not moved concurrently.

## Run

`md run <cmd>` starts a temporary container, runs a command, and cleans up everything:

```bash
md run -- npm test
md run -- cargo check
md run --image ghcr.io/caic-xyz/md-user:2025-05-09 -- npm ci
```

Run flags:

| Flag | Description |
|---|---|
| `-b, -branch <name>` | Branch to use (default: current branch) |
| `-r, -repo <path>` | Path to git repository (default: current directory) |
| `--image <ref>` | Full base image |
| `--tag <tag>` | Tag for the default base image |
| `--platform <platform>` | Build and run for `linux/amd64` or `linux/arm64` |
| `--tags <regexp>` | Select tags to map (default: no tags); use `.*` to include all tags |
| `--cache <name>` | Add a well-known cache or custom `host:container[:ro]` directory (repeatable) |
| `--no-cache <name>` | Exclude a default cache (repeatable) |
| `--no-caches` | Disable all default caches |
| `--mount host:container[:ro]` | Bind-mount a host directory into the container (repeatable) |
| `--extra-repo path[:branch1[,branch2...]]`, `-e` | Map an additional repository (repeatable) |
| `--github` | Inject `GITHUB_TOKEN` into the container |
| `--env NAME` | Copy an environment variable from the host (repeatable) |
| `--env NAME=value` | Set an environment variable only for this run (repeatable) |
| `--env NAME=` | Remove an inherited environment variable for this run (repeatable) |
| `--apply-patch` | Pull repository changes from the temporary container into the host before cleanup |
| `--cpus <n>` | Maximum CPU cores (0 means no limit) |
| `--docker-flag "arg1 arg2"` | Extra flags passed verbatim to `docker` or `podman run` (repeatable) |

`--apply-patch` requires a Git repository. It attempts to integrate the temporary container's changes before removing the container, including when the command fails. The command's nonzero exit status is still returned.

## Workflows

### Multi-repo containers

Map multiple repositories into a single container with `--extra-repo`:

```bash
# Start with main project + dependency
md start -r ~/src/backend -e ~/src/shared-lib

# Specify branches explicitly
md start -b feature-x -e ~/src/shared-lib:feature-x
```

All repositories are transferred into `~/src/<name>` inside the container. The first repository is primary; extras are synchronized alongside it. `md diff`, `md pull`, and `md push` operate on the repository matching your current directory. Use `--all` to operate on all repositories:

```bash
md diff --all      # show diffs for every repo
md pull --all      # pull changes from every repo
```

### Multiple branches from one repository

Map extra branches from the primary repository when one task needs to compare or update related work:

```bash
# Start on the current branch and map two more branches
md start --extra-branch release --extra-branch docs
```

The current branch, or the branch passed with `--branch`, remains primary and is checked out initially. `md diff` reports the branch currently checked out in the container. `md pull`, `md push`, and `md fork` cover every mapped branch.

### Fork workflow

Fork a running agent's container to try a different approach without losing progress:

```bash
# Agent is working in md-myrepo-feature-x
# You want to try a different approach:
md fork              # creates md-myrepo-feature-x-0
ssh md-myrepo-feature-x-0
# Work on the fork. If it works out:
md pull -b feature-x-0              # pull changes back from the fork
md purge md-myrepo-feature-x-0      # clean up the fork
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

# Pass a temporary API key without saving it in a file
md run --env MY_API_KEY -- npm test

# Keep a one-shot command's changes
md run --apply-patch -- npm run format
```

## AI commit messages

`md pull` can generate commit messages using an LLM. It analyzes the diff and recent commit history to produce a conventional commit message. The prompt defaults to a rationale body and permits its omission only for an obviously trivial, self-explanatory change. It asks the model to wrap body lines at 80 columns.

### Setup

Set the provider and model via environment variables; the full list of acceptable `ASK_PROVIDER` values is from [genai](https://github.com/maruel/genai#scoreboard):

```bash
export ASK_PROVIDER=deepseek
export ASK_MODEL=deepseek-v4-flash
export GIT_DESC_TOKENS=64000
```

If not set, md auto-discovers available providers on your system. It prefers CLI-based providers in this order: `pi`, `codex`, `opencode`, `claudecode`, then any others alphabetically. The model defaults to a cheap/fast option.

For an OpenAI-compatible endpoint, set `ASK_PROVIDER=openaicompatible`, set `ASK_REMOTE` to the endpoint URL, and set `ASK_API_KEY_NAME` to the name of the environment variable that contains its API key. Pass `-n` or `--no-describe` to `md pull` when you want a fixed commit message without contacting a provider.

`GIT_DESC_TOKENS` sets the default model context window used to budget requests. It defaults to 64000 and must be at least 8000. Use `md pull --tokens <count>` for a one-off override. For large diffs, md reports its reduction and summarization progress while keeping every request within this budget. See [Design](./design#ai-commit-message-pipeline) for details.

## Build

### `md build-image`

Builds the `md-root-local` and `md-user-local` container images from the source embedded in your installed `md` binary. Use it when you want local base images without pulling them from `ghcr.io`.

```bash
md build-image
```

The first build takes several minutes because it builds the root image and then the user image on top. Subsequent builds are faster thanks to layer caching.

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

Removes unused `md-specialized-*` and `md-fork-*` images no longer referenced by any container. Without `--runtime`, it checks each installed supported runtime and cleans each runtime's build cache. Pass `--runtime docker` or `--runtime podman` before `prune` to operate on only that runtime.

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
