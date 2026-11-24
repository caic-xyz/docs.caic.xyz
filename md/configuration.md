---
# environment variables, agent config mounts, build cache injection, cache names and paths
---

# Configuration

## Container naming

Containers are named `md-<repo-name>-<branch-name>`. Each is locked to a repo-branch pair. Repo-less containers (started outside a git repo) get random names: `md-agent-<hex>`.

## What's inside every container

Each md container includes:

- **Isolated Git checkout**: `~/src/<repo-name>` is synchronized explicitly with your host checkout
- **User-mapped permissions**: Docker and rootful Podman use your host user ID. Rootless Podman maps your host user to the container's fixed `1000:1000` user
- **SSH access**: `ssh md-<repo>-<branch>` with StrictHostKeyChecking
- **Preinstalled tools**: [full inventory](./preinstalled-tools)
- **Shell environment**: PATH and env vars available in all bash invocations (interactive, non-interactive, login, and non-login)

## Environment variables

Env vars reach the container through three mechanisms, merged in order:

1. **`.env` file** in each mapped repository root: repo-specific secrets sent at startup
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

These host directories are automatically bind-mounted into each container. The XDG entries use `XDG_CONFIG_HOME`, `XDG_DATA_HOME`, and `XDG_STATE_HOME` when you have set them. The table shows their default paths.

| Purpose                              | Host paths                                                                 | Access     |
| ------------------------------------ | -------------------------------------------------------------------------- | ---------- |
| Shared agent instructions and skills | `~/.agents`                                                                | Read-write |
| Amp                                  | `~/.amp`, `~/.config/amp`, `~/.local/share/amp`                            | Read-write |
| Android and ADB                      | `~/.android`                                                               | Read-write |
| Antigravity                          | `~/.gemini`                                                                | Read-write |
| Claude Code                          | `~/.claude`                                                                | Read-write |
| Codex                                | `~/.codex`                                                                 | Read-write |
| DeepSeek Harness                     | `~/.dsh`                                                                   | Read-write |
| Goose                                | `~/.config/goose`, `~/.local/share/goose`                                  | Read-write |
| Kilo Code                            | `~/.kilocode`                                                              | Read-write |
| Kimi                                 | `~/.kimi`                                                                  | Read-write |
| OpenCode                             | `~/.config/opencode`, `~/.local/share/opencode`, `~/.local/state/opencode` | Read-write |
| Pi                                   | `~/.pi`                                                                    | Read-write |
| Qwen Code                            | `~/.qwen`                                                                  | Read-write |
| md configuration                     | `~/.config/md`                                                             | Read-only  |

If one of these directories contains a symlink to another directory, md also mounts the resolved target so the link continues to work in the container.

The `~/.config/md` directory is mounted **read-only** to prevent accidental modification of SSH keys from inside the container.

`~/.agents` is always mounted, regardless of which harnesses you use. This is the recommended place for a centralized AGENTS.md and skills directory. See [Harnesses](./harnesses#sharing-the-same-agents-md-across-harnesses) for setup instructions.

## Self-hosted models

When configuring a custom LLM provider that runs on your host machine, use `host.docker.internal` instead of `localhost`. The container cannot reach `localhost` on your host directly.

For example, in `~/.pi/agent/models.json` with Pi and llama.cpp:

```json
{
  "providers": {
    "llama-cpp": {
      "baseUrl": "http://host.docker.internal:8081/v1",
      "api": "openai-completions",
      "apiKey": "none",
      "models": [
        {
          "id": "my-model",
          "input": ["text", "image"]
        }
      ]
    }
  }
}
```

This works with Podman and with Docker Desktop on macOS, Linux, and Windows. On Linux with Docker Engine, you may need to pass the host mapping explicitly:

```bash
md start --docker-flag='--add-host=host.docker.internal:host-gateway'
```

## Build cache injection

md bakes your local build-tool caches into the container image at build time. This avoids slow cold-start downloads: the container starts with warm caches.

Caches are included only when the host directory exists; missing directories are silently skipped. The image is rebuilt when the active cache set changes, the `md-user` image is updated on the registry, or SSH keys change.

### Default caches

| Cache name     | Host path                                     | Container path                              |
| -------------- | --------------------------------------------- | ------------------------------------------- |
| `bun`          | `~/.bun/install/cache`                        | `/home/user/.bun/install/cache`             |
| `cargo`        | `~/.cargo/registry`, `~/.cargo/git`           | `/home/user/.cargo/{registry,git}`          |
| `go-mod`       | `~/go/pkg/mod`                                | `/home/user/go/pkg/mod`                     |
| `gradle`       | `~/.gradle/caches`, `~/.gradle/wrapper/dists` | `/home/user/.gradle/{caches,wrapper/dists}` |
| `maven`        | `~/.m2/repository`                            | `/home/user/.m2/repository`                 |
| `npm`          | `~/.npm`                                      | `/home/user/.npm`                           |
| `pip`          | `~/.cache/pip`                                | `/home/user/.cache/pip`                     |
| `pnpm`         | `~/.local/share/pnpm/store`                   | `/home/user/.local/share/pnpm/store`        |
| `uv`           | `~/.cache/uv`                                 | `/home/user/.cache/uv`                      |
| `android-keys` | `~/.android` (top-level files only)           | `/home/user/.android`                       |

```bash
md start -no-cache go-mod -no-cache cargo   # skip specific caches
md start -no-caches                           # disable all caches
md start -no-caches -cache go-mod            # only go-mod
md start -cache /path/to/my/cache:/home/user/.mycache  # custom cache
md start -cache /path/to/refdata:~/refdata:ro          # read-only, tilde path
```

For custom caches, append `:ro` to make the directory read-only inside the container. The container path may use `~` or a leading `~/`, which expand to `/home/user`.

### Mount vs. cache {#mount-vs-cache}

`--cache` and `--mount` both bring a host directory into the container, but they behave differently:

|                           | `--cache host:container[:ro]`     | `--mount host:container[:ro]` |
| ------------------------- | --------------------------------- | ----------------------------- |
| When applied              | Build time                        | Runtime                       |
| Relationship to host      | One-way copy baked into the image | Live bind-mount               |
| Host changes after start  | Not reflected (frozen at build)   | Reflected immediately         |
| Triggers an image rebuild | Yes, when the cache set changes   | No                            |

Use `--cache` for warm package-manager caches that you don't need to stay in sync with the host. Use `--mount` when you want the container to see host changes live, for example a shared dataset or a directory you edit on the host while an agent works. Append `:ro` to either for a read-only directory, and use `~` or `~/` in the container path to mean `/home/user`.

```bash
md start --mount ~/datasets:~/datasets        # live, read-write
md start --mount ~/secrets:~/secrets:ro       # live, read-only
```

## GitHub authentication inside the container

The container does not have access to your host GitHub credentials. To authenticate from inside:

```bash
gh auth login
```

Or use `md start --github` to inject `GITHUB_TOKEN` at startup.

## Chrome/Chromium

Chrome and Chromium are preinstalled with initial preferences configured for a clean first-run experience. md handles the required security options automatically so Chrome's sandbox works inside the container.
