# Installation

## Prerequisites

- Docker or Podman

## Install

```bash
curl caic.xyz/install.sh | bash
```

This installs both `caic` and `md` binaries.

## Install from source

### Dependencies

- Go 1.25+
- Docker or Podman

### Build and install

```bash
go install github.com/caic-xyz/md/cmd/md@latest
```

**Recommended:** Also install [git-maruel](https://github.com/maruel/git-maruel) for the `git squash` and `git rb` helpers.

## Next steps

- [Commands](./commands) — full command reference
- [Configuration](./configuration) — caches, environment variables
- [Harnesses](./harnesses) — agent-specific setup (Claude Code, Codex, Gemini, etc.)
- [Tailscale](./tailscale) — remote access over your tailnet
