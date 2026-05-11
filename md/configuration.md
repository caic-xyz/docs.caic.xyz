---
# environment variables, agent config mounts, build cache injection, cache names and paths
---

# Configuration

## Container naming

Containers are named `md-<repo-name>-<branch-name>`. Each is locked to a repo-branch pair. Repo-less containers (started outside a git repo) get random names: `md-agent-<hex>`.

## What's inside every container

Each md container includes:

- **Isolated git clone**: `~/src/<repo-name>` tracks a `base` branch matching your local branch
- **User-mapped permissions**: runs as your local user ID for correct file permissions
- **SSH access**: `ssh md-<repo>-<branch>` with StrictHostKeyChecking
- **Preinstalled tools**: [full inventory](./preinstalled-tools)
- **Shell environment**: PATH and env vars available in all bash invocations (interactive, non-interactive, login, and non-login)

## Environment variables

Env vars reach the container through three mechanisms, merged in order:

1. **`.env` file** in your repository root: repo-specific secrets (auto-mounted)
2. **`~/.config/md/env`**: global defaults for all your containers
3. **`--github` flag**: injects `GITHUB_TOKEN` at startup

```bash
# ~/.config/md/env
ANTHROPIC_API_KEY=your_key
OPENAI_API_KEY=your_key
```

These are merged into `/home/user/.env` inside the container. See [Design](./design#environment-injection) for how this works.

### GitHub token

```bash
# Option 1: environment variable
export GITHUB_TOKEN=ghp_...

# Option 2: gh CLI
gh auth login

# Then use --github flag
md start --github
```

The `--github` flag tries `$GITHUB_TOKEN` first, then falls back to `gh auth token`.

## Agent configuration files

These host directories are automatically bind-mounted into each container:

- `~/.amp`, `~/.claude`, `~/.codex`, `~/.gemini`, `~/.kilocode`, `~/.kimi`, `~/.pi`, `~/.qwen`
- `~/.config/agents`, `~/.config/amp`, `~/.config/goose`, `~/.config/opencode`
- `~/.local/share/amp`, `~/.local/share/goose`, `~/.local/share/opencode`
- `~/.local/state/opencode`
- `~/.android` (ADB keys)

The `~/.config/md` directory is mounted **read-only** to prevent accidental modification of SSH keys from inside the container.

`~/.config/agents` is always mounted, regardless of which harnesses you use. This is the recommended place for a centralized AGENTS.md and skills directory. See [Harnesses](./harnesses#centralizing-agentsmd) for setup instructions.

## Build cache injection

md bakes your local build-tool caches into the container image at build time. This avoids slow cold-start downloads: the container starts with warm caches.

Caches are included only when the host directory exists; missing directories are silently skipped. The image is rebuilt when the active cache set changes, the `md-user` image is updated on the registry, or SSH keys change.

### Default caches

| Cache name | Host path | Container path |
|---|---|---|
| `bun` | `~/.bun/install/cache` | `/home/user/.bun/install/cache` |
| `cargo` | `~/.cargo/registry`, `~/.cargo/git` | `/home/user/.cargo/{registry,git}` |
| `go-mod` | `~/go/pkg/mod` | `/home/user/go/pkg/mod` |
| `gradle` | `~/.gradle/caches`, `~/.gradle/wrapper/dists` | `/home/user/.gradle/{caches,wrapper/dists}` |
| `maven` | `~/.m2/repository` | `/home/user/.m2/repository` |
| `npm` | `~/.npm` | `/home/user/.npm` |
| `pip` | `~/.cache/pip` | `/home/user/.cache/pip` |
| `pnpm` | `~/.local/share/pnpm/store` | `/home/user/.local/share/pnpm/store` |
| `uv` | `~/.cache/uv` | `/home/user/.cache/uv` |
| `android-keys` | `~/.android` (top-level files only) | `/home/user/.android` |

```bash
md start -no-cache go-mod -no-cache cargo   # skip specific caches
md start -no-caches                           # disable all caches
md start -no-caches -cache go-mod            # only go-mod
md start -cache /path/to/my/cache:/home/user/.mycache  # custom cache
```

## GitHub authentication inside the container

The container does not have access to your host GitHub credentials. To authenticate from inside:

```bash
gh auth login
```

Or use `md start --github` to inject `GITHUB_TOKEN` at startup.

## Chrome/Chromium

Chrome and Chromium are preinstalled with initial preferences configured for a clean first-run experience. md handles the required security options automatically so Chrome's sandbox works inside the container.
