# Installation

## Prerequisites

- Docker installed and running

## Install

```bash
curl -fsSL https://caic.xyz/install.sh | bash
```

The install script:

1. Downloads the latest `caic` and `md` binaries to `~/.local/bin/`
2. Copies a default `config.toml` to `~/.config/caic/` (if not already present)
3. Installs and starts a system service (systemd on Linux, launchd on macOS)

After installation, caic is running on `http://localhost:2242` using the current directory as root.

Set `NO_SERVICE=1` to skip service installation:

```bash
NO_SERVICE=1 curl -fsSL https://caic.xyz/install.sh | bash
```

If the GitHub release API is rate-limited, set `GITHUB_TOKEN` for authentication:

```bash
GITHUB_TOKEN=ghp_... curl -fsSL https://caic.xyz/install.sh | bash
```

## systemd user service (Linux)

The install script sets up the systemd service automatically. To install manually:

```bash
mkdir -p ~/.config/systemd/user ~/.config/caic
cp contrib/caic.service ~/.config/systemd/user/
cp contrib/config.toml ~/.config/caic/config.toml
# Edit ~/.config/caic/config.toml

systemctl --user daemon-reload
systemctl --user enable --now caic
```

View logs:

```bash
journalctl --user -o cat -f -u caic
```

caic watches its own executable and `config.toml` for changes and restarts automatically when either is modified.

## launchd user agent (macOS)

The install script sets up the launchd agent automatically. To install manually:

```bash
mkdir -p ~/.config/caic
cp contrib/config.toml ~/.config/caic/config.toml
# Edit ~/.config/caic/config.toml

cp contrib/com.caic.caic.plist ~/Library/LaunchAgents/
# Edit ~/Library/LaunchAgents/com.caic.caic.plist to set the binary path.

launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.caic.caic.plist
```

View logs:

```bash
tail -f /tmp/caic.log
```

## Install from source

### Dependencies

- Go 1.25+
- Docker installed and running

### Build and install

```bash
go install github.com/caic-xyz/caic/backend/cmd/caic@latest
```

When installing from source, copy [`contrib/config.toml`](https://github.com/caic-xyz/caic/blob/main/contrib/config.toml) and the service file manually. See [Configuration](./configuration) for details.

## Next steps

- [Configure caic](./configuration) — config file, auth modes, service management
- [GitHub integration](./github) — connect GitHub for automatic PR creation
- [GitLab integration](./gitlab) — connect GitLab for automatic MR creation
- [Android app](./android) — build and install the companion app
