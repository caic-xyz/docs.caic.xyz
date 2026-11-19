# Installation

## Prerequisites

- Linux or macOS on amd64 or arm64
- **Docker or Podman** installed and usable by your user

caic uses Docker when both runtime commands are installed, and Podman when only Podman is installed. [Configuration](./configuration) covers choosing the runtime for new tasks.

## Install

```bash
curl -fsSL https://caic.xyz/install.sh | bash
```

The install script takes no arguments. It:

1. Downloads the latest stable `caic` and `md` releases, verifies their SHA-256 checksums, and installs both binaries in `~/.local/bin/`
2. Copies a default `config.toml` to `~/.config/caic/`, or `$XDG_CONFIG_HOME/caic/` when set, if none exists
3. Installs and starts a user service

Run the same command to update. It keeps your configuration and settings. If a step fails after others completed, the script lists what it installed; correct the error and run it again.

After installation, caic is running on `http://localhost:2242`. The default `root = "."` resolves from the service working directory, not from the directory where you ran the installer. Set an explicit `[core] root` in `~/.config/caic/config.toml` before adding repositories.

| Platform | User service                | Logs                                                                  |
| -------- | --------------------------- | --------------------------------------------------------------------- |
| Linux    | systemd `caic.service`      | `journalctl --user -o cat -f -u caic`                                 |
| macOS    | launchd `com.fghbuild.caic` | `~/Library/Logs/caic/stdout.log` and `~/Library/Logs/caic/stderr.log` |

caic watches its own executable and `config.toml` and restarts when either changes.

caic imports `PATH`, `SSH_AUTH_SOCK`, and other exported values from your interactive login shell at startup. To use only the service environment instead, set `[core] shell_env = false` in `config.toml`. On Linux, the unit then reads service-only overrides, such as adding a directory to `PATH`, from the optional `~/.config/systemd/user/caic.env`.

On macOS, the launchd agent sets no working directory, so do not rely on the relative default `root = "."`. Set `[core] root` to an absolute repository parent directory.

### Upgrade from an earlier macOS agent

Earlier releases installed the launchd agent as `com.caic.caic`. The installer does not remove it, and both agents would run caic. Remove the old agent:

```bash
launchctl bootout "gui/$(id -u)/com.caic.caic"
rm ~/Library/LaunchAgents/com.caic.caic.plist
```

## Install from source

See the [caic README](https://github.com/caic-xyz/caic#from-source) for building and installing `caic` from source with Go.

## Next steps

- [Configure caic](./configuration): config file, auth modes, service management
- [GitHub integration](./github): connect GitHub for automatic PR creation
- [GitLab integration](./gitlab): connect GitLab for automatic MR creation
- [Go Mode on Android](./android): connect the separate Android shell
