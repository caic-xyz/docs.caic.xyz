# Installation

## Prerequisites

- **Docker or Podman** installed and running

caic uses Docker when both runtime commands are installed, and Podman when only Podman is installed. [Configuration](./configuration) covers choosing the runtime for new tasks.

## Install

```bash
curl -fsSL https://caic.xyz/install.sh | bash
```

The install script:

1. Downloads the latest `caic` and `md` binaries to `~/.local/bin/`
2. Copies a default `config.toml` to `~/.config/caic/` (if not already present)
3. Installs and starts a system service (systemd on Linux, launchd on macOS)

After installation, caic is running on `http://localhost:2242`. The default `root = "."` is resolved from the service working directory, not from the directory where you invoked the installer. The systemd unit uses your home directory. Set an explicit `[core] root` in `~/.config/caic/config.toml` before adding repositories.

Set `NO_SERVICE=1` to skip service installation:

```bash
curl -fsSL https://caic.xyz/install.sh | NO_SERVICE=1 bash
```

If the GitHub release API is rate-limited, set `GITHUB_TOKEN` for authentication:

```bash
export GITHUB_TOKEN="ghp_..."
curl -fsSL https://caic.xyz/install.sh | bash
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

caic imports `PATH`, `SSH_AUTH_SOCK`, and other exported values from your interactive login shell at startup. The unit starts without requiring a keyring socket. To use only the service environment instead, set `[core] shell_env = false` in `config.toml`.

The unit optionally reads `~/.config/caic/caic.env`. With `shell_env = false`, use this file for service-only environment overrides, such as adding `~/.local/bin` to `PATH`. The service starts normally when the file is absent.

## launchd user agent (macOS)

The install script sets up the launchd agent automatically. To install manually, publish the plist with your own absolute paths:

```bash
mkdir -p ~/.config/caic "$HOME/Library/LaunchAgents"
cp contrib/config.toml ~/.config/caic/config.toml
# Edit ~/.config/caic/config.toml

plist="$HOME/Library/LaunchAgents/com.caic.caic.plist"
logs="$HOME/Library/Logs/caic"
mkdir -p "$logs"
cp contrib/com.caic.caic.plist "$plist"
plutil -replace ProgramArguments.0 -string "$HOME/.local/bin/caic" -- "$plist"
plutil -replace StandardOutPath -string "$logs/stdout.log" -- "$plist"
plutil -replace StandardErrorPath -string "$logs/stderr.log" -- "$plist"
plutil -lint -- "$plist"

launchctl bootstrap gui/$(id -u) "$plist"
```

View logs:

```bash
tail -f "$HOME/Library/Logs/caic/stdout.log" "$HOME/Library/Logs/caic/stderr.log"
```

launchd starts caic directly, without a shell wrapper. To update an existing agent, replace its plist and run `launchctl bootout` then `launchctl bootstrap`. Log rotation needs separate configuration.

The launchd template does not set a working directory, so do not rely on the relative default `root = "."`. Set `[core] root` to an absolute repository parent directory.

## Install from source

See the [caic README](https://github.com/caic-xyz/caic#from-source) for building and installing `caic` from source with Go.

## Next steps

- [Configure caic](./configuration): config file, auth modes, service management
- [GitHub integration](./github): connect GitHub for automatic PR creation
- [GitLab integration](./gitlab): connect GitLab for automatic MR creation
- [Go Mode on Android](./android): connect the separate Android shell
