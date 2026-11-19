# Configuration

All configuration is in a single TOML file at `~/.config/caic/config.toml`. See [`contrib/config.toml`](https://github.com/caic-xyz/caic/blob/main/contrib/config.toml) for a documented template.

## Quick start

The [install script](./installation) creates a default `config.toml` automatically. To customize:

```bash
$EDITOR ~/.config/caic/config.toml
```

caic watches `config.toml` for changes and restarts automatically when the file is saved.

Without a config file, caic listens on `localhost:2242`, uses the server process working directory as root, and auto-detects the GitHub token from `gh auth token`.

## CLI flags

| Flag          | Default          | Description                                                    |
| ------------- | ---------------- | -------------------------------------------------------------- |
| `-config-dir` | `~/.config/caic` | Override the config directory.                                 |
| `-print-url`  | Not set          | Print the server URL and exit. Verifies the port is available. |
| `-version`    | Not set          | Print version and exit.                                        |

## Directories

caic follows the [XDG Base Directory](https://specifications.freedesktop.org/basedir-spec/latest/) convention. `XDG_CONFIG_HOME` overrides the default config base, and `XDG_CACHE_HOME` overrides the default cache base.

The config directory defaults to `~/.config/caic/`. It contains `config.toml`, `settings.json`, `users.json`, `preferences.json`, and `oauth_refresh_tokens.json`. A systemd service can also read optional process environment from `caic.env`. User-supplied private keys and a GeoLite2 database can live here too.

The cache directory defaults to `~/.cache/caic/`. It contains task logs, CI results, harness model caches, the MCP audit log in `oauth_audit.jsonl`, and the downloaded origin cache in `ip-origins.json`.

Relative paths in the config file (e.g. `geo_db`, `app_private_key_pem`) are resolved against the config directory.

<figure class="docs-figure">
  <ThemedScreenshot light="/screenshots/frontend/desktop/settings-general-light.webp" dark="/screenshots/frontend/desktop/settings-general-dark.webp" alt="caic General Settings with container defaults and task automation controls" :width="1600" :height="900" />
  <figcaption>Set container defaults and task automation preferences.</figcaption>
</figure>

## Config reference

### `[core]`

| Key           | Default        | Description                                                                                                                                                                    |
| ------------- | -------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `root`        | `"."`          | Parent directory containing git repositories managed by caic. Tilde (`~`) is expanded to your home directory; relative paths resolve from the server process working directory |
| `shell_env`   | `true`         | Load exported values from your interactive login shell at startup on macOS and Linux. Shell exports replace inherited values such as `PATH` and `SSH_AUTH_SOCK`                |
| `auto_update` | `"50 4 * * *"` | Cron schedule for auto-update (checks GitHub Releases). Supports cron step syntax (`*/N`, `start/N`, e.g. `*/15 * * * *`). Set to `""` to disable                              |
| `repo_repack` | `"0 2 * * *"`  | Repack large host repositories on a cron schedule. Set to `""` to disable                                                                                                      |
| `prune`       | `"0 5 * * *"`  | Cron schedule for removing unused md-built images from every available container runtime. Set to `""` to disable                                                               |

**Shell environment**

Before starting the server, caic runs your interactive login shell once, without a terminal, and imports its exported values. This finds tools such as Git and npm when your startup scripts export their paths. `SHELL` selects the shell; otherwise caic reads the account database. The probe waits at most six seconds. On failure, caic logs a warning and keeps its inherited environment.

Shell exports replace inherited values, including `PATH` and `SSH_AUTH_SOCK`. Explicit `[core.env]` values still take precedence for caic's configured credentials. Process and session bookkeeping is unchanged. caic does not import aliases or functions, refresh version-manager settings per repository, unlock SSH keys, or repair a dead agent socket. Keep shell startup scripts responsive when no terminal is present.

Set `shell_env = false` to use only the service or terminal environment. On systemd, put service-only overrides in `~/.config/caic/caic.env` in that mode. Commands inside task containers still use the container environment.

```toml
[core]
shell_env = false
```

**`[core.env]`**

Feature and provider credentials that caic looks up by name. Depending on the feature, an omitted key can fall back to a harness environment table or the caic server process environment. Common values include `TAILSCALE_API_KEY` for ephemeral container nodes and provider keys used for generated titles, CI failure summaries, and commit messages. Embedded voice reads provider keys from the process environment instead. This table does not add arbitrary variables to the server process or task containers. Put service-wide variables such as `HTTP_PROXY`, `HTTPS_PROXY`, `NO_PROXY`, or `PATH` in the process environment. A systemd installation can set them in `~/.config/caic/caic.env`.

For supported provider usage cards, caic looks for the recognized API key first in `[core.env]`, then in any `[harness.<name>.env]` table, and finally in the server process environment. API-key usage cards are available for DeepSeek, OpenRouter, and Xiaomi. Claude Code and Codex usage cards use their authenticated sessions instead. Experimental Antigravity quota reporting uses the authenticated `agy` CLI. Title, summary, and commit-message generation reads provider keys from `[core.env]` and then the server process environment.

```toml
[core]
root = "~/projects"

[core.env]
TAILSCALE_API_KEY = "tskey-api-..."
GEMINI_API_KEY = "AIza..."
```

**Auto-update and image pruning**

When enabled, caic checks [GitHub Releases](https://github.com/caic-xyz/caic/releases) on the given cron schedule and replaces the binary in place when a new version is found. The schedule accepts cron step syntax (`*/N`, `start/N`), so `*/15 * * * *` checks every 15 minutes. The binary self-update triggers the config watcher, causing a restart with the new version.

```toml
[core]
# Disable auto-update:
auto_update = ""
```

Image pruning uses the same cron syntax. It removes md-built images that no container uses, while preserving images needed by active or stopped tasks.

### Preferences

`~/.config/caic/preferences.json` stores per-user settings independent of `config.toml`. Edit it directly or through the Settings UI, which exposes the container image, CPU architecture and platform, CPU cores, the preferred runtime when both Docker and Podman are available, well-known caches, custom cache mappings, custom host mounts, purge delay, auto-fix CI and PR toggles, per-model thinking effort, per-harness context compaction settings, per-harness model refresh, and version information with manual update checks.

The purge delay is the recovery window for an active or crashed task after you choose Purge. The default is 15 seconds and the allowed range is 10 seconds to 24 hours. Reviving the task during this window cancels deletion. Purging a task that is already stopped deletes it immediately.

<figure class="docs-figure">
  <ThemedScreenshot light="/screenshots/frontend/desktop/settings-mounts-light.webp" dark="/screenshots/frontend/desktop/settings-mounts-dark.webp" alt="caic Settings page with opt-in build caches and enabled custom host mounts" :width="1600" :height="900" />
  <figcaption>Configure reusable caches and host mounts for new tasks.</figcaption>
</figure>

caic detects every available container runtime at startup. When more than one is available, choose the default for new tasks in Settings. Each task keeps the runtime it was created with. Sudo is unavailable with rootless Podman, so select Docker for sudo-enabled tasks.

### `[server]`

| Key               | Default                            | Description                                                                                                                                                                                                                     |
| ----------------- | ---------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `http`            | `":2242"`                          | HTTP listen address. Port-only addresses (`:2242`) bind to localhost. Use `"0.0.0.0:2242"` to listen on all interfaces                                                                                                          |
| `external_url`    | `"auto"`                           | Public base URL. `"auto"` locks from the first fully qualified hostname and supports browser login plus same-origin MCP. Set an explicit stable URL for remote MCP OAuth and webhooks                                           |
| `trusted_proxies` | `[]`                               | CIDR ranges for direct reverse-proxy peers whose forwarded protocol, host, and client address caic may trust. Never include client networks                                                                                     |
| `geo_db`          | Not set                            | Path to a [MaxMind GeoLite2](https://dev.maxmind.com/geoip/geolite2-free-geolocation-data) MMDB file for country-code resolution. If unset and `GeoLite2-Country.mmdb` exists in the config directory, it is used automatically |
| `allow_origins`   | `["local", "tailscale", "github"]` | Allowlist for incoming HTTP requests. Unmatched IPs get HTTP 403                                                                                                                                                                |

**`external_url` rules**

- `"auto"` (default): the hostname is locked from the first request with a fully qualified domain name. Browser OAuth login and same-origin, session-authenticated MCP work in this mode.
- Explicit value: remote MCP OAuth and stable webhook callbacks require a fixed URL with a host and no path, such as `https://caic.example.com`. Trailing slashes are stripped.
- When OAuth login is configured, an explicit URL must use `https://`, except for a loopback development origin. Use HTTPS for every deployment exposed beyond a trusted local network.

When a reverse proxy terminates HTTPS, list only the proxy addresses that connect directly to caic. caic honors forwarded protocol, host, and client-IP headers only when the direct peer matches this list. Configure the edge proxy to strip client-supplied forwarding headers and replace them with the address it observed.

**`allow_origins` values**

| Value         | Matches                                                                                              |
| ------------- | ---------------------------------------------------------------------------------------------------- |
| `"local"`     | Unspecified, IPv4 link-local, RFC 1918, IPv6 ULA and link-local, and IPv4 or IPv6 loopback addresses |
| `"tailscale"` | Tailscale CGNAT range (`100.64.0.0/10`)                                                              |
| `"github"`    | GitHub webhook IPs (fetched live from `api.github.com/meta`). Needed for the GitHub App              |
| `"anthropic"` | Published Anthropic outbound IPs. Needed for Claude MCP clients                                      |
| `"openai"`    | Published ChatGPT integration and Codex cloud IPs. Needed for ChatGPT MCP clients                    |
| CIDR range    | e.g. `"203.0.113.0/24"`                                                                              |
| Country code  | ISO 3166-1 alpha-2 (e.g. `"CA"`, `"US"`); requires `geo_db`                                          |

Named origins (`local`, `tailscale`, `github`, `anthropic`, `openai`) resolve before country lookups.

```toml
[server]
geo_db = "GeoLite2-Country.mmdb"
allow_origins = ["local", "tailscale", "github", "CA"]
```

### `[voice-gateway]`

`mode` selects how caic serves [Go Mode voice](https://docs.gomode.dev/guide/voice). Voice is disabled until you set it.

| Key                       | Default                            | Description                                                             |
| ------------------------- | ---------------------------------- | ----------------------------------------------------------------------- |
| `mode`                    | `"disabled"`                       | `"disabled"`, `"embedded"` to host the gateway in caic, or `"external"` |
| `webrtc_udp_port`         | `0`                                | Embedded: UDP port for WebRTC audio. `0` selects an ephemeral port      |
| `stun_servers`            | `["stun:stun.l.google.com:19302"]` | Embedded: STUN servers clients use to learn their public address        |
| `url`                     | Not set                            | External: HTTPS URL of the standalone gateway                           |
| `instance_id`             | Not set                            | External: unique identifier for this caic instance                      |
| `token_mode`              | `"scoped"`                         | External: session credential mode, `"scoped"` or `"oauth"`              |
| `signing_private_key_pem` | Not set                            | External: PKCS#8 Ed25519 private key file for `"scoped"` tokens         |

Embedded mode reads its voice choices from `voice-choices.toml` beside `config.toml`, or uses the defaults built into the release. caic owns the HTTP listener, so configure HTTP through `[server] http`. Open `webrtc_udp_port` in your firewall for remote WebRTC clients. `stun_servers = []` keeps clients from contacting any STUN server; that works when clients reach the UDP port directly or through its UPnP mapping.

External mode requires an explicit HTTPS `[server] external_url`, except for loopback development. Scoped tokens require a signing key; OAuth tokens use caic's authorization-server key instead and require a configured dashboard login provider. The gateway must trust the same service, issuer, and token mode. See [Voice](./voice#standalone-gateway) for a complete example.

```toml
[voice-gateway]
mode = "embedded"
webrtc_udp_port = 3479
```

### `[ai]`

LLM provider for task titles, CI failure summaries, and commit messages.

| Key        | Default     | Description                                                                                                       |
| ---------- | ----------- | ----------------------------------------------------------------------------------------------------------------- |
| `provider` | auto-detect | Provider name. When unset, probes `codex`, `claudecode`, `opencode`, `pi`, `antigravity`, then the others by name |
| `model`    | cheapest    | Model name or alias. Uses the provider's cheapest model when unset                                                |

Command-line agents (`codex`, `claudecode`, `dsh`, `antigravity`, `opencode`, `pi`) use their own login and run without their coding-agent prompt, tools, or user configuration. API providers include `anthropic`, `gemini`, `openai`, and `openrouter`; see the [genai providers](https://pkg.go.dev/github.com/maruel/genai/providers) package for the full list.

```toml
[ai]
provider = "codex"
model = "gpt-5-mini"
```

### `[harness]`

Explicit environment variables to write into containers for a selected harness. Each harness has its own `[env]` table of `KEY = "VALUE"` pairs. These values are also available when caic refreshes that harness's model list, and recognized provider keys can enable supported usage cards. Use the Models section of **Settings** to refresh an installed harness's model list on demand, for example after changing provider credentials. Only harnesses that can discover their own models offer a refresh button. caic does not automatically forward other `*_API_KEY` variables. If you enable GitHub token injection for a task, caic also adds the resolved `GITHUB_TOKEN`.

```toml
[harness.claude.env]
ANTHROPIC_API_KEY = "sk-..."

[harness.codex.env]
# Codex configuration is primarily via its own config file:
# https://developers.openai.com/codex/config-reference

[harness.dsh.env]
DEEPSEEK_API_KEY = "sk-..."

[harness.opencode.env]
# OpenCode configuration: https://opencode.ai/docs/config/

[harness.pi.env]
DEEPSEEK_API_KEY = "sk-..."
GEMINI_API_KEY = "AIza..."
OPENROUTER_API_KEY = "sk-or-..."
```

Available harness names: `antigravity` (experimental), `claude`, `codex`, `dsh` (DeepSeek Harness), `opencode`, `pi`.

Setting `ANTHROPIC_API_KEY` can make Claude Code use API billing instead of your subscription. When caic detects a Claude Code OAuth session, it avoids forwarding this key so the subscription remains in use.

### `[github.*]`

GitHub settings live in three subsections by authentication method. See [GitHub Integration](./github) for full setup instructions.

`[github.pat]`:

| Key     | Default | Description                                                                                 |
| ------- | ------- | ------------------------------------------------------------------------------------------- |
| `token` | Not set | Personal access token. Falls back to `gh auth token` when unset and OAuth is not configured |

`[github.oauth]`:

| Key             | Default | Description                                                                                      |
| --------------- | ------- | ------------------------------------------------------------------------------------------------ |
| `client_id`     | Not set | OAuth app client ID. Mutually exclusive with a PAT                                               |
| `client_secret` | Not set | OAuth app client secret. Required when `client_id` is set                                        |
| `allowed_users` | Not set | GitHub usernames permitted to log in. When unset, any GitHub user who completes OAuth can log in |

`[github.app]` (layered on top of PAT or OAuth, not mutually exclusive):

| Key               | Default | Description                                                                             |
| ----------------- | ------- | --------------------------------------------------------------------------------------- |
| `id`              | Not set | GitHub App ID                                                                           |
| `private_key_pem` | Not set | Path to GitHub App PEM private key file. Relative to the config directory               |
| `allowed_owners`  | Not set | GitHub orgs/users allowed to install the app. Installs from other accounts are rejected |
| `webhook_secret`  | Not set | HMAC-SHA256 secret for webhook verification. Generate with `openssl rand -hex 32`       |

### `[gitlab.*]`

The top-level `[gitlab]` table holds the OAuth login URL and webhook secret. Credentials live in subsections by authentication method. See [GitLab Integration](./gitlab) for current GitLab.com forge support and setup instructions.

`[gitlab]`:

| Key              | Default | Description                                                                                |
| ---------------- | ------- | ------------------------------------------------------------------------------------------ |
| `url`            | Not set | Self-hosted GitLab URL for OAuth login only. Forge API operations currently use gitlab.com |
| `webhook_secret` | Not set | Shared secret for webhook verification. Generate with `openssl rand -hex 32`               |

`[gitlab.pat]`:

| Key     | Default | Description                                                         |
| ------- | ------- | ------------------------------------------------------------------- |
| `token` | Not set | Personal access token (scope: `api`). Mutually exclusive with OAuth |

`[gitlab.oauth]`:

| Key             | Default | Description                                                                                      |
| --------------- | ------- | ------------------------------------------------------------------------------------------------ |
| `client_id`     | Not set | OAuth app client ID. Mutually exclusive with a PAT                                               |
| `client_secret` | Not set | OAuth app client secret. Required when `client_id` is set                                        |
| `allowed_users` | Not set | GitLab usernames permitted to log in. When unset, any GitLab user who completes OAuth can log in |

### `[google.oauth]`

Google Sign-In authenticates dashboard users only. It does not provide forge access for repositories, CI, PRs, or MRs. Configure GitHub or GitLab for forge operations.

| Key             | Default | Description                                                                                           |
| --------------- | ------- | ----------------------------------------------------------------------------------------------------- |
| `client_id`     | Not set | Google OAuth client ID                                                                                |
| `client_secret` | Not set | Google OAuth client secret. Required when `client_id` is set                                          |
| `allowed_users` | Not set | Google account emails permitted to log in. When unset, any Google user who completes OAuth can log in |

Use `https://<your-domain>/auth/google/callback` as the authorized redirect URI in Google Cloud Console.

### `[debug]`

| Key           | Default  | Description                                           |
| ------------- | -------- | ----------------------------------------------------- |
| `log_level`   | `"info"` | Log verbosity: `debug`, `info`, `warn`, `error`       |
| `no_log_time` | `false`  | Omit timestamps from log output. Useful under systemd |
| `pprof`       | `false`  | Expose `/debug/pprof/*` profiling endpoints           |
| `cpuprofile`  | Not set  | Write CPU profile to this file path                   |
| `memprofile`  | Not set  | Write heap profile on shutdown                        |
| `trace`       | Not set  | Write execution trace to this file path               |

## Environment variables

`TAILSCALE_API_KEY` and title provider keys fall back to the server process environment when absent from `[core.env]`. Embedded voice reads provider keys only from the process environment. That environment includes values imported from your login shell, unless `shell_env` is false. Provider usage lookup also checks harness environment tables before the process environment, as described above. `XDG_CONFIG_HOME` and `XDG_CACHE_HOME` change the base directories described above. Set proxy variables and other service-wide values in the process environment rather than `[core.env]`.

## HTTPS exposure

Set `external_url` explicitly for remote MCP OAuth and webhooks so issuer, redirect, and callback URLs stay stable. Webhooks also require the forge to reach caic from the internet.

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

```text
<your-domain> {
    reverse_proxy localhost:2242
}
```

```toml
[server]
external_url = "https://<your-domain>"
trusted_proxies = ["127.0.0.1/32", "::1/128"]
```

Use the actual direct-peer address when Caddy runs on another host or network. Do not add public client ranges.

For dynamic DNS, [ddns-updater](https://github.com/qdm12/ddns-updater) works well with Caddy.
