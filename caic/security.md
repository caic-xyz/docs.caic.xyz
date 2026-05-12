---
# security model: authentication, forge tokens, IP geo, webhooks, SSH isolation, container sandbox, secret scanning, voice security
---

# Security

This page documents the security boundaries of caic: how authentication works, where credentials live, what is isolated, and what network exposure exists.

## Authentication

### JWT sessions

When OAuth login is configured, caic uses HS256 JWTs for session management. The session secret is randomly generated on first launch and stored in `~/.config/caic/settings.json`. It never leaves the server.

Sessions are delivered as:

- **Cookie** (`caic_session`): for the web UI, set with `HttpOnly`, `SameSite=Lax`, and `Secure` (when accessed over HTTPS)
- **Authorization: Bearer** header: for Android and API clients

Tokens expire after a fixed duration. There is no refresh token mechanism — when a session expires, you re-authenticate. This keeps the authentication surface small and auditable.

### OAuth 2.0 login

caic implements the OAuth 2.0 Authorization Code flow for GitHub and GitLab, using only Go's standard library (no third-party OAuth libraries). The flow:

1. User clicks "Login with GitHub/GitLab"
2. Browser redirects to the provider's authorize endpoint
3. User authorizes the caic OAuth app
4. Provider redirects back with an authorization code
5. caic exchanges the code for an access token
6. caic fetches the user's profile to verify identity
7. JWT session is issued

**Allowed users**: when OAuth is configured, the `oauth_allowed_users` list is mandatory. Only users on this list can log in, regardless of whether the OAuth app is authorized. This prevents anyone with a GitHub/GitLab account from accessing your caic instance.

**CSRF protection**: the OAuth flow uses a state cookie with HMAC verification. The state value is randomly generated per login attempt.

### No-auth mode

When no OAuth provider is configured (the default), caic runs without authentication. All API routes are accessible. This is appropriate for single-user setups behind Tailscale or on a local machine where network access already implies trust.

## Network security

### HTTP listener

By default, caic listens on `localhost:2242`. The `localizeAddr` function ensures that port-only addresses like `:2242` bind to `127.0.0.1`, not `0.0.0.0`. To listen on all interfaces, you must explicitly set the bind address to `0.0.0.0:2242`.

### IP geolocation allowlisting

caic supports country-level access control using MaxMind GeoLite2 databases. When a `geo_db` file is configured, every HTTP request is geolocated and checked against an allowlist:

| Allowlist value | Matches |
|---|---|
| `local` | Loopback and RFC 1918 private addresses |
| `tailscale` | Tailscale CGNAT range (`100.64.0.0/10`) |
| `github` | GitHub webhook IPs (fetched live from `api.github.com/meta`) |
| Country code | ISO 3166-1 alpha-2 (e.g. `CA`, `US`, `DE`) |
| CIDR range | e.g. `203.0.113.0/24` |

Requests from non-allowed IPs receive HTTP 403. Geo-lookup results are logged for every request.

The default allowlist is `["local", "tailscale", "github"]`, which blocks all internet traffic except GitHub webhooks.

### External URL and HTTPS

When OAuth is configured, `external_url` must use `https://`. This ensures redirect URIs and callback URLs are secure. For local deployments, use Tailscale Serve or Caddy as a reverse proxy with automatic TLS. See [Configuration](./configuration) for HTTPS exposure options.

### Webhook security

GitHub and GitLab webhooks are verified with HMAC-SHA256 signatures. Each webhook endpoint (`/webhooks/github`, `/webhooks/gitlab`) validates the signature before processing the payload. Without a configured `webhook_secret`, webhook endpoints return 404.

Webhook IPs for GitHub are additionally verified against the live GitHub meta API, ensuring webhook requests originate from GitHub's infrastructure.

## Credential handling

### What the server stores

| Credential | Storage | Notes |
|---|---|---|
| Forge tokens (PAT) | `config.toml` (plaintext) | Set restrictive file permissions |
| OAuth client secrets | `config.toml` (plaintext) | Set restrictive file permissions |
| GitHub App private key | PEM file in config directory | Path configured, not content |
| Gemini API key | `config.toml` or `GEMINI_API_KEY` env var | For title generation and voice |
| Tailscale API key | `config.toml` or `TAILSCALE_API_KEY` env var | For ephemeral container nodes |
| Webhook secrets | `config.toml` (plaintext) | HMAC secrets for webhook verification |
| Session secret | `settings.json` (plaintext) | Auto-generated on first launch |
| User data | `users.json` | OAuth tokens and user profiles |

All config files live in `~/.config/caic/`. Set `chmod 700` on this directory to prevent other users from reading credentials.

### What the container does NOT have access to

- Your host SSH keys: the container uses md's generated key pair
- Your forge tokens: unless you explicitly pass `GITHUB_TOKEN` via core env
- The caic server's session secret
- OAuth client secrets or webhook secrets
- Docker socket

### Token auto-detection

When no GitHub token is configured, caic tries `gh auth token` from the GitHub CLI. This is convenient for single-user setups but means the token lives in the caic process memory. The token is only used for forge API calls, never sent to containers unless `GITHUB_TOKEN` is explicitly configured in core env.

### Masked logging

API keys and tokens are masked in log output. Only the last few characters are shown, enough to identify which key is in use without exposing the full secret.

## Container isolation

caic uses md containers, which provide:

- **No shared mounts between containers**: each task has its own filesystem
- **No host file access**: the agent works in the container's copy of the repository, not the host checkout
- **SSH-only access**: caic communicates with containers over SSH, not Docker exec. This means the container's SSH security model applies (key auth only, no password)
- **Restricted capabilities**: containers run with minimum Linux capabilities. `--privileged` is never used, the host network is never shared, and no host PID or IPC namespaces are exposed

See [md Security](../md/security) for the full container security model.

## Secret scanning on push

Before pushing changes to a remote, caic scans the diff for:

- AWS access keys (`AKIA*`)
- GitHub personal access tokens (`ghp_*`, `github_pat_*`)
- Private keys (PEM, OpenSSH)
- Hardcoded credentials in config files

Found issues are reported to the agent so it can fix them before the push. This is a safety net, not a security boundary: an agent could still exfiltrate data through other channels.

## WebRTC voice security

The voice bridge connects the web UI or Android app to Gemini Live via WebRTC:

1. Client obtains a short-lived JWT from the `/api/v1/voice/token` endpoint
2. Client establishes a WebRTC connection to the caic server
3. Server bridges WebRTC audio to Gemini's WebSocket API

The voice bridge uses a standalone JWT secret, not the session secret. Audio data never touches disk and is processed in-memory through opus codec wrappers. The WebRTC implementation uses Pion with an IPv4-only network transport to minimize the network attack surface.

## Server restarts and credential hygiene

On server restart:

- In-memory credentials (token caches, session state) are lost — they must be re-read from config
- The `settings.json` session secret is re-loaded from disk
- OAuth user data is re-read from `users.json`

No credentials are persisted in container labels, environment variables, or other transient state.

## What is NOT protected

caic does not:

- Encrypt data at rest (config files, logs, caches)
- Sandbox the agent from the internet (the container has full outbound access)
- Audit agent actions for data exfiltration
- Limit what an agent can commit or push

If you need outbound network restrictions, use Tailscale ACLs or Docker network policies at the container level (see [md Security](../md/security#restricting-outbound-access)).
