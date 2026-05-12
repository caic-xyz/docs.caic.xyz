---
# Configuration file reference: config.toml sections, keys, defaults, and environment variables
---

# Configuration

All configuration is in a single TOML file at `~/.config/caic/config.toml`. See [`contrib/config.toml`](https://github.com/caic-xyz/caic/blob/main/contrib/config.toml) for a documented template.

## Quick start

The [install script](./installation) creates a default `config.toml` automatically. To customize:

```bash
$EDITOR ~/.config/caic/config.toml
```

caic watches `config.toml` for changes and restarts automatically when the file is saved.

Without a config file, caic starts with sensible defaults: listens on `localhost:2242`, uses the current directory as root, and auto-detects the GitHub token from `gh auth token`.

## CLI flags

| Flag | Default | Description |
|---|---|---|
| `-config-dir` | `~/.config/caic` | Override the config directory |
| `-version` | — | Print version and exit |
| `-print-url` | — | Print the server URL and exit (port must be available) |

## Directories

caic uses two directories, following the [XDG Base Directory](https://specifications.freedesktop.org/basedir-spec/latest/) convention:

| Directory | Default | Env override | Contents |
|---|---|---|---|
| Config | `~/.config/caic/` | `XDG_CONFIG_HOME` | `config.toml`, `settings.json`, `users.json`, `preferences.json`, PEM keys, MMDB files |
| Cache | `~/.cache/caic/` | `XDG_CACHE_HOME` | Task logs, CI cache, harness model cache |

Relative paths in the config file (e.g. `geo_db`, `app_private_key_pem`) are resolved against the config directory.

## Config reference

### `[core]`

| Key | Default | Description |
|---|---|---|
| `root` | `"."` | Parent directory containing git repositories managed by caic. Tilde (`~`) is expanded to the user's home directory |
| `auto_update` | `"50 4 * * *"` | Cron schedule for auto-update (checks GitHub Releases). Set to `""` to disable |

#### `[core.env]`

Environment variables inherited by the server process. Falls back to the host environment when not set.

| Key | Purpose |
|---|---|
| `TAILSCALE_API_KEY` | Tailscale API key for ephemeral container nodes. Obtain from [Tailscale admin](https://login.tailscale.com/admin/settings/keys) |
| `GEMINI_API_KEY` | Gemini API key for voice agent (WebRTC bridge) and title generation. Obtain from [Google AI Studio](https://aistudio.google.com/app/apikey) |
| `HTTP_PROXY` / `HTTPS_PROXY` / `NO_PROXY` | Proxy settings for forge API calls (GitHub, GitLab) when the server is behind a corporate proxy |
| `ANTHROPIC_API_KEY` / `OPENAI_API_KEY` / etc | Optional API keys for LLM generated commit description |

```toml
[core]
root = "~/projects"

[core.env]
TAILSCALE_API_KEY = "tskey-api-..."
GEMINI_API_KEY = "AIza..."
```

#### Auto-update

When enabled, caic checks [GitHub Releases](https://github.com/caic-xyz/caic/releases) on the given cron schedule and replaces the binary in place when a new version is found. The binary self-update triggers the config watcher, causing a restart with the new version.

```toml
[core]
# Disable auto-update:
auto_update = ""
```

### `[server]`

| Key | Default | Description |
|---|---|---|
| `http` | `":2242"` | HTTP listen address. Port-only addresses (`:2242`) bind to localhost. Use `"0.0.0.0:2242"` to listen on all interfaces |
| `external_url` | `"auto"` | Public base URL. `"auto"` locks from the first FQDN request. Set explicitly for OAuth and webhooks |
| `webrtc_port` | `0` | UDP port for WebRTC ICE. `0` = enabled with ephemeral port; `-1` = disabled. Requires `GEMINI_API_KEY` in `core.env`. Open this port for UDP traffic if using a static port |
| `geo_db` | — | Path to a [MaxMind GeoLite2](https://dev.maxmind.com/geoip/geolite2-free-geolocation-data) MMDB file for country-code resolution. If unset and `GeoLite2-Country.mmdb` exists in the config directory, it is used automatically |
| `allow_origins` | `["local", "tailscale", "github"]` | Allowlist for incoming HTTP requests. Unmatched IPs get HTTP 403 |

#### `external_url` rules

- `"auto"` (default): hostname locked from the first request with a fully qualified domain name
- Explicit value: must be a valid URL with a host and no path (e.g. `https://caic.example.com`). Trailing slashes are stripped
- When OAuth is configured and explicit: must use `https://`

#### `allow_origins` values

| Value | Matches |
|---|---|
| `"local"` | Loopback and RFC 1918 private addresses |
| `"tailscale"` | Tailscale CGNAT range (`100.64.0.0/10`) |
| `"github"` | GitHub webhook IPs (fetched live from `api.github.com/meta`) |
| CIDR range | e.g. `"203.0.113.0/24"` |
| Country code | ISO 3166-1 alpha-2 (e.g. `"CA"`, `"US"`); requires `geo_db` |

```toml
[server]
geo_db = "GeoLite2-Country.mmdb"
allow_origins = ["local", "tailscale", "github", "CA"]
```

### `[ai]`

LLM provider for title generation and commit descriptions.

| Key | Default | Description |
|---|---|---|
| `provider` | auto-detect | Provider name. When unset, probes in this order: `codex`, `opencode`, `claudecode`, `gemini`, then any other available provider |
| `model` | cheapest | Model name or alias. Uses the provider's cheapest model when unset |

Available providers: see the [genai providers](https://pkg.go.dev/github.com/maruel/genai/providers) package.

When provider is `gemini`, the `GEMINI_API_KEY` from `[core.env]` is used automatically.

```toml
[ai]
provider = "gemini"
model = "gemini-2.5-flash"
```

### `[harness]`

Per-harness environment variables injected into containers. Each harness has its own `[env]` table of `KEY = "VALUE"` pairs. These supplement the automatic `*_API_KEY` forwarding and are also used when refreshing model lists at startup.

```toml
[harness.claude.env]
ANTHROPIC_API_KEY = "sk-..."

[harness.codex.env]
# Codex configuration is primarily via its own config file:
# https://developers.openai.com/codex/config-reference

[harness.opencode.env]
# OpenCode configuration: https://opencode.ai/docs/config/

[harness.pi.env]
DEEPSEEK_API_KEY = "sk-..."
GEMINI_API_KEY = "AIza..."
OPENROUTER_API_KEY = "sk-or-..."
```

Available harness names: `claude`, `codex`, `gemini`, `kilo`, `opencode`, `pi`.

### `[github]`

See [GitHub Integration](./github) for full setup instructions.

| Key | Default | Description |
|---|---|---|
| `token` | — | Personal access token. Mutually exclusive with `oauth_client_id`. Falls back to `gh auth token` when unset and OAuth is not configured |
| `oauth_client_id` | — | OAuth app client ID. Mutually exclusive with `token` |
| `oauth_client_secret` | — | OAuth app client secret. Required when `oauth_client_id` is set |
| `oauth_allowed_users` | — | GitHub usernames permitted to log in. **Required** when OAuth is configured |
| `app_id` | — | GitHub App ID. Independent of PAT/OAuth |
| `app_private_key_pem` | — | Path to GitHub App PEM private key file. Relative to the config directory |
| `app_allowed_owners` | — | GitHub orgs/users allowed to install the app. Installs from other accounts are rejected |
| `webhook_secret` | — | HMAC-SHA256 secret for webhook verification. Generate with `openssl rand -hex 32` |

### `[gitlab]`

See [GitLab Integration](./gitlab) for full setup instructions.

| Key | Default | Description |
|---|---|---|
| `token` | — | Personal access token (scope: `api`). Mutually exclusive with `oauth_client_id` |
| `oauth_client_id` | — | OAuth app client ID. Mutually exclusive with `token` |
| `oauth_client_secret` | — | OAuth app client secret. Required when `oauth_client_id` is set |
| `oauth_allowed_users` | — | GitLab usernames permitted to log in. **Required** when OAuth is configured |
| `url` | `"https://gitlab.com"` | GitLab instance URL. Must be a valid URL with no path |
| `webhook_secret` | — | Shared secret for webhook verification. Generate with `openssl rand -hex 32` |

### `[debug]`

| Key | Default | Description |
|---|---|---|
| `log_level` | `"info"` | Log verbosity: `debug`, `info`, `warn`, `error` |
| `no_log_time` | `false` | Omit timestamps from log output. Useful under systemd |
| `pprof` | `false` | Expose `/debug/pprof/*` profiling endpoints |
| `cpuprofile` | — | Write CPU profile to this file path |
| `memprofile` | — | Write heap profile on shutdown |
| `trace` | — | Write execution trace to this file path |

## Environment variables

| Variable | Purpose |
|---|---|
| `GEMINI_API_KEY` | Fallback when `[core.env] GEMINI_API_KEY` is not set |
| `TAILSCALE_API_KEY` | Fallback when `[core.env] TAILSCALE_API_KEY` is not set |
| `XDG_CONFIG_HOME` | Override the config base directory (default: `~/.config`) |
| `XDG_CACHE_HOME` | Override the cache base directory (default: `~/.cache`) |

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

With Tailscale, set `external_url` to your tailnet hostname:

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

For dynamic DNS, [ddns-updater](https://github.com/qdm12/ddns-updater) works well with Caddy.
