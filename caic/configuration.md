# Configuration

All configuration is via environment variables. Flags take precedence when set. See [`contrib/caic.env`](https://github.com/caic-xyz/caic/blob/main/contrib/caic.env) for a template.

## Core variables

| Variable | Flag | Required | Default | Description |
|---|---|---|---|---|
| `CAIC_HTTP` | `-http` | Yes | — | HTTP listen address (e.g. `:8080`). Port-only addresses listen on localhost. Use `0.0.0.0:8080` to listen on all interfaces. |
| `CAIC_ROOT` | `-root` | Yes | — | Parent directory containing your git repositories. Each subdirectory is a repo caic can manage. |
| `CAIC_LOG_LEVEL` | `-log-level` | No | `info` | Log verbosity: `debug`, `info`, `warn`, `error`. |
| `CAIC_LLM_PROVIDER` | — | No | — | AI provider for LLM features (title generation). E.g. `anthropic`, `gemini`, `openaichat`. |
| `CAIC_LLM_MODEL` | — | No | — | Model name for LLM features (e.g. `claude-haiku-4-5-20251001`). |
| `GEMINI_API_KEY` | — | No | — | Gemini API key for the Gemini Live voice agent. |
| `TAILSCALE_API_KEY` | — | No | — | Tailscale API key for Tailscale ephemeral node. |

## Running

```bash
# Via flags:
caic -http :8080 -root ~/src

# Via environment variables:
CAIC_HTTP=:8080 CAIC_ROOT=~/src caic
```

## systemd user service

```bash
mkdir -p ~/.config/systemd/user ~/.config/caic
cp contrib/caic.service ~/.config/systemd/user/
cp contrib/caic.env ~/.config/caic/caic.env
# Edit ~/.config/caic/caic.env to set CAIC_HTTP, CAIC_ROOT, and any API keys.
systemctl --user daemon-reload
systemctl --user enable --now caic
```

View logs:

```bash
journalctl --user -u caic -f
```

When caic is reinstalled (binary replaced), the service detects the change and restarts automatically.

## IP geolocation and country allowlist

caic can optionally resolve client IP addresses to country codes using a [MaxMind](https://www.maxmind.com/) MMDB file and enforce a country-based allowlist.

| Variable | Description |
|---|---|
| `CAIC_IPGEO_DB` | Path to MMDB file. Relative paths resolve against `~/.config/caic/`. |
| `CAIC_IPGEO_ALLOWLIST` | Comma-separated list of permitted values. Unlisted IPs get HTTP 403. |

Allowlist values: `local` (loopback + RFC-1918), `tailscale` (100.64.0.0/10), or ISO 3166-1 alpha-2 country codes.

```bash
# Allow only Tailscale and Canadian connections:
CAIC_IPGEO_DB=GeoLite2-Country.mmdb
CAIC_IPGEO_ALLOWLIST=tailscale,CA

# Allow only local and Tailscale (no MMDB needed):
CAIC_IPGEO_ALLOWLIST=tailscale,local
```

## HTTPS exposure

OAuth login and webhooks require `CAIC_EXTERNAL_URL`. Webhooks additionally require GitHub to reach caic from the internet.

> **Warning:** enable OAuth authentication **before** exposing caic on the internet.

### Tailscale Serve (private, tailnet only)

```bash
tailscale serve --bg 8080
CAIC_EXTERNAL_URL=https://<hostname>.<tailnet>.ts.net
```

### Tailscale Funnel (public, webhooks supported)

```bash
tailscale funnel 8080
CAIC_EXTERNAL_URL=https://<hostname>.<tailnet>.ts.net
```

### Caddy + DDNS (home server)

```
<your-domain> {
    reverse_proxy localhost:8080
}
```

```
CAIC_EXTERNAL_URL=https://<your-domain>
```
