# Configuration

All configuration is in a single TOML file at `~/.config/caic/config.toml`. See [`contrib/config.toml`](https://github.com/caic-xyz/caic/blob/main/contrib/config.toml) for a documented template.

## Quick start

The [install script](./installation) creates a default `config.toml` automatically. To customize:

```bash
# Edit the config file created by the install script:
$EDITOR ~/.config/caic/config.toml
```

Without a config file, caic starts with sensible defaults: listens on `:2242`, uses the current directory as root, and auto-detects the GitHub token from `gh auth token`.

## Config reference

### `[core]`

| Key | Default | Description |
|---|---|---|
| `root` | `"."` | Parent directory containing git repositories managed by caic. |
| `auto_update` | `"50 4 * * *"` | Cron schedule for auto-update (checks GitHub Releases). Set to `"off"` to disable. |
| `tailscale_api_key` | — | Tailscale API key for ephemeral nodes. Obtain from [Tailscale admin](https://login.tailscale.com/admin/settings/keys). |

### `[server]`

| Key | Default | Description |
|---|---|---|
| `http` | `":2242"` | HTTP listen address. Port-only addresses listen on localhost. Use `"0.0.0.0:2242"` to listen on all interfaces. |
| `external_url` | `"auto"` | Public base URL. `"auto"` locks from the first FQDN request. Set explicitly for OAuth and webhooks. |
| `webrtc_port` | `0` | UDP port for WebRTC ICE (single-port mux). `0` disables WebRTC voice. Requires `libopus-dev` at build time. |
| `geo_db` | — | Path to a [MaxMind](https://www.maxmind.com/) MMDB file for country-code resolution. Relative paths resolve against `~/.config/caic/`. Auto-detected if `GeoLite2-Country.mmdb` exists in the config directory. |
| `allow_origins` | `["local", "tailscale", "github"]` | Allowlist for incoming requests. Unmatched IPs get HTTP 403. |

**`allow_origins` values:**

- `"local"` — loopback and RFC-1918 private addresses
- `"tailscale"` — Tailscale CGNAT range (`100.64.0.0/10`)
- `"github"` — GitHub webhook IPs (fetched from `api.github.com/meta`)
- CIDR ranges — e.g. `"203.0.113.0/24"`
- Country codes — ISO 3166-1 alpha-2 (e.g. `"CA"`, `"US"`); requires `geo_db`

```toml
[server]
geo_db = "GeoLite2-Country.mmdb"
allow_origins = ["local", "tailscale", "github", "CA"]
```

### `[ai]`

| Key | Default | Description |
|---|---|---|
| `provider` | auto-detect | LLM provider for title generation and commit descriptions. Auto-detects the best available provider when unset. |
| `model` | cheapest | Model name or alias. Uses the provider's cheapest model when unset. |
| `gemini_api_key` | — | Gemini API key for voice agent and title generation. Falls back to `GEMINI_API_KEY` environment variable. |

### `[github]`

See [GitHub Integration](./github) for full setup instructions.

### `[gitlab]`

See [GitLab Integration](./gitlab) for full setup instructions.

### `[debug]`

| Key | Default | Description |
|---|---|---|
| `log_level` | `"info"` | Log verbosity: `debug`, `info`, `warn`, `error`. |
| `no_log_time` | `false` | Omit timestamps from log output. |
| `pprof` | `false` | Expose `/debug/pprof/*` profiling endpoints. |
| `cpuprofile` | — | Write CPU profile to file. |
| `memprofile` | — | Write heap profile to file on shutdown. |
| `trace` | — | Write execution trace to file. |

## Running

```bash
# Default config directory:
caic

# Custom config directory:
caic -config-dir /path/to/config
```

## systemd user service (Linux)

The [install script](./installation) sets up the systemd service automatically. To install manually:

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
journalctl --user -u caic -f
```

When caic is reinstalled (binary replaced), the service detects the change and restarts automatically.

## launchd user agent (macOS)

The [install script](./installation) sets up the launchd agent automatically. To install manually:

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

## HTTPS exposure

OAuth login and webhooks require `external_url` to be set explicitly. Webhooks additionally require GitHub to reach caic from the internet.

> **Warning:** enable OAuth authentication **before** exposing caic on the internet.

### Tailscale Serve (private, tailnet only)

```bash
tailscale serve --bg 2242
```

```toml
[server]
external_url = "https://<hostname>.<tailnet>.ts.net"
```

### Tailscale Funnel (public, webhooks supported)

```bash
tailscale funnel 2242
```

```toml
[server]
external_url = "https://<hostname>.<tailnet>.ts.net"
```

### Caddy + DDNS (home server)

```
<your-domain> {
    reverse_proxy localhost:2242
}
```

```toml
[server]
external_url = "https://<your-domain>"
```
