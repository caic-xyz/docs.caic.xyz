---
# prerequisites, curl install, from source, platform notes, verification, upgrade, uninstall
---

# Installation

## Prerequisites

- **Docker or Podman**
- **git**

md uses Docker when both runtime commands are installed. It selects Podman automatically only when the `docker` command is not installed. Pass the global flag `--runtime docker` or `--runtime podman` before a command to select one explicitly. Use `--runtime podman` when a Podman compatibility shim provides the `docker` command.

### Platform-specific notes

| Platform | Recommendation |
|---|---|
| **Linux** | Docker Engine or Podman. Rootless Podman is supported. |
| **macOS** | [Docker Desktop](https://docs.docker.com/desktop/setup/install/mac-install/). |
| **Windows** | Docker Desktop with WSL2 backend. Run `md` from inside the WSL2 Linux distribution. |

Docker Desktop alternatives haven't been tested. Please let us know if you run into issues.

## Install

```bash
curl -fsSL https://caic.xyz/install.sh | bash
```

This installs both `caic` and `md` binaries to `~/.local/bin/`.

## Verify

```bash
md version

# Quick smoke test
md run -- echo "md works"
```

## Install from source

### Dependencies

- Go (recent version)
- Docker or Podman

### Build and install

```bash
go install github.com/caic-xyz/md/cmd/md@latest
```

**Recommended:** Also install [git-maruel](https://github.com/maruel/git-maruel) for the `git squash` and `git rb` helpers.

## Upgrading

```bash
curl -fsSL https://caic.xyz/install.sh | bash
```

Existing containers continue to work after upgrading. The container image is rebuilt on the next `md start` if the base image has changed.

To force a rebuild with the latest base image:

```bash
md prune    # remove unused md images and build caches from installed runtimes
md start    # will pull latest base and rebuild
```

## Uninstalling

```bash
# Purge all md containers first
for name in $(md list --json | jq -r '.[].name'); do
  md purge "$name"
done

# Remove md-specialized-* images
md prune

# Remove binaries
rm ~/.local/bin/md ~/.local/bin/caic
```

## Next steps

- [Commands](./commands): full command reference
- [Configuration](./configuration): caches, environment variables
- [Harnesses](./harnesses): agent-specific setup and persisted configuration
- [Tailscale](./tailscale): remote access over your tailnet
