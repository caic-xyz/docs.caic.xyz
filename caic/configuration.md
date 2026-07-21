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
| `-config-dir` | `~/.config/caic` | Override the config directory. |
| `-print-url` | — | Print the server URL and exit. Verifies the port is available. |
| `-version` | — | Print version and exit. |

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
| `auto_update` | `"50 4 * * *"` | Cron schedule for auto-update (checks GitHub Releases). Supports cron step syntax (`*/N`, `start/N`, e.g. `*/15 * * * *`). Set to `""` to disable |

#### `[core.env]`

Environment variables inherited by the server process. Falls back to the host environment when not set.

| Key | Purpose |
|---|---|
| `TAILSCALE_API_KEY` | Tailscale API key for ephemeral container nodes. Obtain from [Tailscale admin](https://login.tailscale.com/admin/settings/keys) |
| `GEMINI_API_KEY` | Gemini API key for the embedded voice gateway and title generation. Obtain from [Google AI Studio](https://aistudio.google.com/app/apikey) |
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

When enabled, caic checks [GitHub Releases](https://github.com/caic-xyz/caic/releases) on the given cron schedule and replaces the binary in place when a new version is found. The schedule accepts cron step syntax (`*/N`, `start/N`), so `*/15 * * * *` checks every 15 minutes. The binary self-update triggers the config watcher, causing a restart with the new version.

```toml
[core]
# Disable auto-update:
auto_update = ""
```

### Preferences

`~/.config/caic/preferences.json` stores per-user settings independent of `config.toml`. Edit it directly or through the Settings UI, which exposes the container image, CPU architecture and platform, CPU cores, the preferred runtime when both Docker and Podman are available, well-known caches (now opt-in), custom cache mappings, custom host mounts (with enabled and read-only toggles), auto-fix CI and PR toggles, per-model thinking effort, and version info with manual update.

caic detects every available container runtime at startup. When more than one is available, choose the default for new tasks in Settings. Each task keeps the runtime it was created with. Sudo is unavailable with rootless Podman, so select Docker for sudo-enabled tasks.

### `[server]`

| Key | Default | Description |
|---|---|---|
| `http` | `":2242"` | HTTP listen address. Port-only addresses (`:2242`) bind to localhost. Use `"0.0.0.0:2242"` to listen on all interfaces |
| `external_url` | `"auto"` | Public base URL. `"auto"` locks from the first FQDN request. Set explicitly for OAuth and webhooks |
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
| `"github"` | GitHub webhook IPs (fetched live from `api.github.com/meta`). Needed for the GitHub App |
| `"anthropic"` | Published Anthropic outbound IPs. Needed for Claude MCP clients |
| `"openai"` | Published ChatGPT integration and Codex cloud IPs. Needed for ChatGPT MCP clients |
| CIDR range | e.g. `"203.0.113.0/24"` |
| Country code | ISO 3166-1 alpha-2 (e.g. `"CA"`, `"US"`); requires `geo_db` |

Named origins (`local`, `tailscale`, `github`, `anthropic`, `openai`) resolve before country lookups.

```toml
[server]
geo_db = "GeoLite2-Country.mmdb"
allow_origins = ["local", "tailscale", "github", "CA"]
```

### `[voice-gateway]`

Voice availability is derived automatically from your configuration:

- **Standalone gateway**: set `url` to advertise a separate voice gateway you run elsewhere.
- **Embedded**: leave `url` empty and set `GEMINI_API_KEY` (in `[core.env]`). caic hosts the gateway in-process.
- **Disabled**: leave `url` empty and `GEMINI_API_KEY` unset.

| Key | Default | Description |
|---|---|---|
| `url` | — | URL of a standalone voice gateway. When set, caic advertises it instead of hosting one |

#### `[voice-gateway.config]`

Runtime config for the embedded gateway, used only when caic hosts it in-process. The API key is always read from `GEMINI_API_KEY`.

| Key | Default | Description |
|---|---|---|
| `model` | `"gemini-3.1-flash-live-preview"` | Gemini Live model for the embedded gateway |
| `backend` | `"gemini-live"` | `"gemini-live"` uses Gemini Live. `"local-stack"` runs a local, half-duplex stack instead |

#### `[voice-gateway.config.server]`

| Key | Default | Description |
|---|---|---|
| `webrtc_udp_port` | `0` | UDP port for WebRTC ICE. `0` = OS-assigned ephemeral port. A value `>0` pins a static port; open it for UDP traffic in your firewall. Requires `GEMINI_API_KEY` |

With `backend = "local-stack"`, voice runs half-duplex with managed llama.cpp servers for speech recognition and the LLM plus KittenTTS for speech synthesis. Omit the local-stack tables to let caic manage the default Qwen3 ASR model and Gemma LLM, or point them at servers you run yourself. See [`contrib/voice-gateway-config.toml`](https://github.com/caic-xyz/caic/blob/main/contrib/voice-gateway-config.toml) for the full template.

```toml
[voice-gateway.config]
backend = "gemini-live"

[voice-gateway.config.server]
webrtc_udp_port = 3479
```

### `[ai]`

LLM provider for title generation and commit descriptions.

| Key | Default | Description |
|---|---|---|
| `provider` | auto-detect | Provider name. When unset, probes in this order: `codex`, `opencode`, `claudecode`, then any other available provider |
| `model` | cheapest | Model name or alias. Uses the provider's cheapest model when unset |

Available providers: see the [genai providers](https://pkg.go.dev/github.com/maruel/genai/providers) package.

```toml
[ai]
provider = "codex"
model = "gpt-5-mini"
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

Available harness names: `claude`, `codex`, `opencode`, `pi`.

### `[github.*]`

GitHub settings live in three subsections by authentication method. See [GitHub Integration](./github) for full setup instructions.

`[github.pat]`:

| Key | Default | Description |
|---|---|---|
| `token` | — | Personal access token. Falls back to `gh auth token` when unset and OAuth is not configured |

`[github.oauth]`:

| Key | Default | Description |
|---|---|---|
| `client_id` | — | OAuth app client ID. Mutually exclusive with a PAT |
| `client_secret` | — | OAuth app client secret. Required when `client_id` is set |
| `allowed_users` | — | GitHub usernames permitted to log in. When unset, any GitHub user who completes OAuth can log in |

`[github.app]` (layered on top of PAT or OAuth, not mutually exclusive):

| Key | Default | Description |
|---|---|---|
| `id` | — | GitHub App ID |
| `private_key_pem` | — | Path to GitHub App PEM private key file. Relative to the config directory |
| `allowed_owners` | — | GitHub orgs/users allowed to install the app. Installs from other accounts are rejected |
| `webhook_secret` | — | HMAC-SHA256 secret for webhook verification. Generate with `openssl rand -hex 32` |

### `[gitlab.*]`

The top-level `[gitlab]` table holds instance settings; credentials live in subsections by authentication method. See [GitLab Integration](./gitlab) for full setup instructions.

`[gitlab]`:

| Key | Default | Description |
|---|---|---|
| `url` | — | GitLab instance URL. Empty targets gitlab.com; set only for a self-hosted instance |
| `webhook_secret` | — | Shared secret for webhook verification. Generate with `openssl rand -hex 32` |

`[gitlab.pat]`:

| Key | Default | Description |
|---|---|---|
| `token` | — | Personal access token (scope: `api`). Mutually exclusive with OAuth |

`[gitlab.oauth]`:

| Key | Default | Description |
|---|---|---|
| `client_id` | — | OAuth app client ID. Mutually exclusive with a PAT |
| `client_secret` | — | OAuth app client secret. Required when `client_id` is set |
| `allowed_users` | — | GitLab usernames permitted to log in. When unset, any GitLab user who completes OAuth can log in |

### `[google.oauth]`

Google Sign-In authenticates dashboard users only. It does not provide forge access for repositories, CI, PRs, or MRs. Configure GitHub or GitLab for forge operations.

| Key | Default | Description |
|---|---|---|
| `client_id` | — | Google OAuth client ID |
| `client_secret` | — | Google OAuth client secret. Required when `client_id` is set |
| `allowed_users` | — | Google account emails permitted to log in. When unset, any Google user who completes OAuth can log in |

Use `https://<your-domain>/auth/google/callback` as the authorized redirect URI in Google Cloud Console.

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
