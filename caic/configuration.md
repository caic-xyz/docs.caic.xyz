# Configuration

All configuration is in a single TOML file at `~/.config/caic/config.toml`. See [`contrib/config.toml`](https://github.com/caic-xyz/caic/blob/main/contrib/config.toml) for a documented template.

## Quick start

The [install script](./installation) creates a default `config.toml` automatically. To customize:

```bash
# Edit the config file created by the install script:
$EDITOR ~/.config/caic/config.toml
```

caic watches `config.toml` for changes and restarts automatically when the file is saved.

Without a config file, caic starts with sensible defaults: listens on `:2242`, uses the current directory as root, and auto-detects the GitHub token from `gh auth token`.

## CLI flags

| Flag | Default | Description |
|---|---|---|
| `-config-dir` | `~/.config/caic` | Override the config directory. |
| `-version` | — | Print version and exit. |

## Directories

caic uses two directories, following the [XDG Base Directory](https://specifications.freedesktop.org/basedir-spec/latest/) convention:

| Directory | Default | Env override | Contents |
|---|---|---|---|
| Config | `~/.config/caic/` | `XDG_CONFIG_HOME` | `config.toml`, PEM keys, MMDB files |
| Cache | `~/.cache/caic/` | `XDG_CACHE_HOME` | Logs and cache files |

Relative paths in the config file (e.g. `geo_db`, `app_private_key_pem`) are resolved against the config directory.

## Config reference

### `[core]`

| Key | Default | Description |
|---|---|---|
| `root` | `"."` | Parent directory containing git repositories managed by caic. Tilde (`~`) is expanded to the user's home directory. |
| `auto_update` | `"50 4 * * *"` | Cron schedule for auto-update (checks GitHub Releases). Set to `""` to disable. |
| `tailscale_api_key` | — | Tailscale API key for ephemeral nodes. Obtain from [Tailscale admin](https://login.tailscale.com/admin/settings/keys). |

#### Auto-update

When enabled, caic checks [GitHub Releases](https://github.com/caic-xyz/caic/releases) on the given cron schedule (local time) and replaces the binary in place when a new version is found. caic watches its own executable for changes and exits; the systemd `Restart=always` directive then restarts the service with the new binary.

```toml
[core]
# Check for updates every 6 hours:
auto_update = "50 */6 * * *"

# Disable auto-update:
auto_update = ""
```

### `[server]`

| Key | Default | Description |
|---|---|---|
| `http` | `":2242"` | HTTP listen address. Port-only addresses (`:2242`) bind to localhost. Use `"0.0.0.0:2242"` to listen on all interfaces. |
| `external_url` | `"auto"` | Public base URL. `"auto"` locks from the first FQDN request. Set explicitly for OAuth and webhooks. |
| `webrtc_port` | `0` | UDP port for WebRTC ICE (single-port mux). `0` disables WebRTC voice. Requires `libopus-dev` at build time (`CGO_ENABLED=1`). Open this port in your firewall for UDP traffic. |
| `geo_db` | — | Path to a [MaxMind GeoLite2](https://dev.maxmind.com/geoip/geolite2-free-geolocation-data) MMDB file for country-code resolution. Relative paths resolve against the config directory. If omitted, `GeoLite2-Country.mmdb` in the config directory is used automatically when present. |
| `allow_origins` | `["local", "tailscale", "github"]` | Allowlist for incoming requests on the web server. Unmatched IPs get HTTP 403. |

#### `external_url` rules

- When set to `"auto"` (default): the hostname is locked from the first request with a fully qualified domain name.
- When set explicitly: must be a valid URL with a host and no path (e.g. `https://caic.example.com`). Trailing slashes are stripped automatically.
- When OAuth is configured and `external_url` is set explicitly: must use `https://`.

#### `allow_origins` values

| Value | Matches |
|---|---|
| `"local"` | Loopback and RFC 1918 private addresses |
| `"tailscale"` | Tailscale CGNAT range (`100.64.0.0/10`) |
| `"github"` | GitHub webhook IPs (fetched live from `api.github.com/meta`) |
| CIDR range | e.g. `"203.0.113.0/24"` |
| Country code | ISO 3166-1 alpha-2 (e.g. `"CA"`, `"US"`, `"DE"`); requires `geo_db` |

```toml
[server]
geo_db = "GeoLite2-Country.mmdb"  # Default value
allow_origins = ["local", "tailscale", "github", "CA"]  # Only allow IP addresses from Canada
```

### `[ai]`

| Key | Default | Description |
|---|---|---|
| `provider` | auto-detect | LLM provider for title generation and commit descriptions. |
| `model` | cheapest | Model name or alias. Uses the provider's cheapest model when unset. |
| `gemini_api_key` | — | Gemini API key for Gemini Live voice agent and title generation. Falls back to `GEMINI_API_KEY` environment variable. Obtain from [Google AI Studio](https://aistudio.google.com/app/apikey). |

#### Provider auto-detection order

When `provider` is unset, caic probes available providers in this order and uses the first one found:

1. `codex` (Codex)
2. `opencode` (OpenCode)
3. `claudecode` (Claude Code)
4. `gemini` (Gemini)
5. Any other available provider

See the [genai providers](https://pkg.go.dev/github.com/maruel/genai/providers) package for the full list of supported backends.

### `[github]`

See [GitHub Integration](./github) for full setup instructions.

Summary of config keys:

| Key | Default | Description |
|---|---|---|
| `token` | — | Personal access token. Mutually exclusive with `oauth_client_id`. If unset and OAuth is not configured, caic falls back to `gh auth token` from the [GitHub CLI](https://cli.github.com/). |
| `oauth_client_id` | — | OAuth app client ID. Mutually exclusive with `token`. |
| `oauth_client_secret` | — | OAuth app client secret. Required when `oauth_client_id` is set. |
| `oauth_allowed_users` | — | GitHub usernames permitted to log in. **Required** when OAuth is configured. |
| `app_id` | — | GitHub App ID. Independent of PAT/OAuth. |
| `app_private_key_pem` | — | Path to GitHub App PEM private key file. Relative paths resolve against the config directory. |
| `app_allowed_owners` | — | GitHub orgs/users allowed to install the app. Installs from other accounts are rejected. |
| `webhook_secret` | — | HMAC-SHA256 secret for webhook verification. Generate with `openssl rand -hex 32`. |

### `[gitlab]`

See [GitLab Integration](./gitlab) for full setup instructions.

Summary of config keys:

| Key | Default | Description |
|---|---|---|
| `token` | — | Personal access token (scope: `api`). Mutually exclusive with `oauth_client_id`. |
| `oauth_client_id` | — | OAuth app client ID. Mutually exclusive with `token`. |
| `oauth_client_secret` | — | OAuth app client secret. Required when `oauth_client_id` is set. |
| `oauth_allowed_users` | — | GitLab usernames permitted to log in. **Required** when OAuth is configured. |
| `url` | `"https://gitlab.com"` | GitLab instance URL. Must be a valid URL with no path. |
| `webhook_secret` | — | Shared secret for webhook verification. Generate with `openssl rand -hex 32`. |

### `[debug]`

| Key | Default | Description |
|---|---|---|
| `log_level` | `"info"` | Log verbosity: `debug`, `info`, `warn`, `error`. |
| `no_log_time` | `false` | Omit timestamps from log output. Useful when running under systemd (which adds its own timestamps). |
| `pprof` | `false` | Expose `/debug/pprof/*` profiling endpoints on the HTTP server. |
| `cpuprofile` | — | Write CPU profile to this file path while running. |
| `memprofile` | — | Write heap profile to this file path on shutdown. |
| `trace` | — | Write execution trace to this file path while running. |

## Environment variables

| Variable | Purpose |
|---|---|
| `GEMINI_API_KEY` | Fallback for `ai.gemini_api_key` when not set in config. |
| `XDG_CONFIG_HOME` | Override the config base directory (default: `~/.config`). |
| `XDG_CACHE_HOME` | Override the cache base directory (default: `~/.cache`). |

## HTTPS exposure

Setting `external_url` explicitly is recommended for OAuth login and webhooks so redirect URIs and callback URLs are stable. Webhooks additionally require the forge (GitHub/GitLab) to reach caic from the internet.

### Tailscale Serve (private, tailnet only)

```bash
tailscale serve --bg 2242
```

### Tailscale Funnel (public, webhooks supported)

```bash
tailscale funnel 2242
```

### Tailscale external url

You can optionally set the `external_url` to the public hostname of your tailnet; the default `"auto"` value
should catch it automatically:

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

You can optionally set the `external_url` to the public hostname of your tailnet; the default `"auto"` value
should catch it automatically:

```toml
[server]
external_url = "https://<your-domain>"
```

I (Marc-Antoine) personally use [github.com/qdm12/ddns-updater](https://github.com/qdm12/ddns-updater).
