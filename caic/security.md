# Security

This page describes caic's trust boundaries: authentication, credential storage, container isolation, and network exposure.

## Authentication

### Dashboard sessions

When OAuth login is configured, caic issues signed sessions for the web UI, Android app, and API clients. Browser sessions use an `HttpOnly`, `SameSite=Lax` cookie that is marked `Secure` over HTTPS. Android and other API clients use an `Authorization: Bearer` header.

Dashboard sessions expire and require a new login. Forge access tokens are refreshed when the provider supplies a refresh token. MCP clients use a separate OAuth flow described in [MCP Server](./mcp).

caic supports login with GitHub, GitLab, and Google. Google authenticates dashboard access only and does not grant repository or forge authority. Set each provider's `allowed_users` list for a private deployment. Leaving it unset permits any account that completes that provider's login flow.

### No-auth mode

Without an OAuth login provider, ordinary enabled dashboard and API routes require no login. MCP is still disabled when the server listens on a non-loopback address, and webhook endpoints still require their configured secret verification. Use no-auth mode only on localhost or a network where every peer is trusted, such as a private tailnet.

## Network security

### Listener and origin allowlist

By default, port-only addresses such as `:2242` bind to localhost. You must explicitly use `0.0.0.0:2242` to listen on all IPv4 interfaces.

Every request is checked against `allow_origins`. The complete accepted value types are:

| Value            | Matches                                                                                              |
| ---------------- | ---------------------------------------------------------------------------------------------------- |
| `local`          | Unspecified, IPv4 link-local, RFC 1918, IPv6 ULA and link-local, and IPv4 or IPv6 loopback addresses |
| `tailscale`      | Tailscale CGNAT range (`100.64.0.0/10`)                                                              |
| `github`         | GitHub webhook addresses fetched from GitHub                                                         |
| `anthropic`      | Published Anthropic outbound addresses for Claude MCP clients                                        |
| `openai`         | Published ChatGPT integration and Codex cloud addresses                                              |
| ISO country code | Requests geolocated to that country; requires a configured GeoLite2 database                         |
| CIDR range       | Requests whose client address belongs to the range                                                   |

The default is `['local', 'tailscale', 'github']`. Unmatched requests receive HTTP 403.

If a reverse proxy terminates HTTPS, add only its direct peer addresses to `trusted_proxies`. caic accepts forwarded protocol, host, and client-IP headers only when the direct peer matches this list. Configure the edge proxy to strip client-supplied `Forwarded`, `X-Forwarded-*`, and `X-Real-IP` headers and replace them with values it observed. Adding client or public network ranges would let those clients influence origin checks and the address checked by `allow_origins`.

### External URL and HTTPS

The default `external_url = "auto"` supports browser login and same-origin session MCP after locking to the first fully qualified hostname. Remote MCP OAuth requires an explicit stable URL. When OAuth login is configured, explicit URLs must use HTTPS except for loopback development origins. Use HTTPS for any deployment exposed beyond a trusted local network.

Use Tailscale Serve or a TLS reverse proxy such as Caddy. See [Configuration](./configuration) for setup examples.

### Webhooks

GitHub and GitLab webhooks require a configured secret and are verified before their payloads are processed. Without a webhook secret, the endpoint is unavailable. GitHub webhook requests are also checked against GitHub's published address ranges.

## Credential handling

### Server-side storage

| Credential                                                                                    | Storage                                                          | Notes                                                                                                          |
| --------------------------------------------------------------------------------------------- | ---------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------- |
| Forge personal access tokens                                                                  | `config.toml` in plaintext                                       | Restrict file permissions                                                                                      |
| OAuth client secrets                                                                          | `config.toml` in plaintext                                       | Restrict file permissions                                                                                      |
| GitHub App private key                                                                        | PEM file in the config directory                                 | The config stores its path                                                                                     |
| Gemini API key                                                                                | `config.toml` or server environment                              | Used for title generation and embedded voice                                                                   |
| Tailscale API key                                                                             | `config.toml` or server environment                              | Used for ephemeral task nodes                                                                                  |
| Provider API keys                                                                             | `[core.env]`, a harness environment table, or server environment | Used for supported usage cards; `[core.env]` and server values can also support titles and commit descriptions |
| Harness environment credentials                                                               | `[harness.<name>.env]` in `config.toml`                          | Written into matching task containers and used for that harness's model refresh                                |
| Webhook secrets                                                                               | `config.toml` in plaintext                                       | Used to verify webhooks                                                                                        |
| Dashboard session secret and MCP issuer signing key                                           | `settings.json` in plaintext                                     | Generated on first launch                                                                                      |
| User profiles and forge OAuth tokens                                                          | `users.json`                                                     | Used for login and per-user forge access                                                                       |
| MCP clients, grants, hashed refresh-token family state, and private access-token signing keys | `oauth_refresh_tokens.json`                                      | Persists MCP authorization and revocation across restarts                                                      |

These files live under `~/.config/caic/`. Restrict that directory to your user, for example with `chmod 700 ~/.config/caic`.

### Container access

By default, a task does not receive host SSH keys, forge tokens, the caic session secret, OAuth client secrets, webhook secrets, or the container-runtime socket. Mounted harness state can contain its own provider credentials, so treat those mounts as credential-bearing.

md automatically bind-mounts shared agent state such as `~/.agents` and the selected harness's configuration directories into every applicable task. These mounts are generally writable, while md's own configuration mount is read-only. Tasks using the same harness can therefore read and change the same host-side agent state.

Custom host mounts and shared build caches expose additional selected host paths. Review each mapping in **Settings**, prefer read-only mounts when possible, and do not mount a directory containing unrelated secrets.

### GitHub token injection

If GitHub token injection is enabled for a task, caic resolves the token in this order:

1. The signed-in GitHub user's OAuth access token
2. The server-level personal access token
3. The result of `gh auth token` when neither of the first two is configured

The token is not baked into the container image. At startup, md combines any `.env` files from the selected repositories, explicit values from the selected `[harness.<name>.env]` table, and the optional injected GitHub token. It writes the result to `/home/user/.env` inside the task container over the encrypted SSH connection. These values persist in the task filesystem until you remove or purge the container. A newly started task receives the currently resolved token and configuration.

### Sudo access

When sudo is enabled, md generates a unique random password for the task container. It is not baked into the image and does not grant root access on the host. The credential is specific to that container and becomes useless when the container is deleted and recreated.

Sudo is unavailable with rootless Podman. Choose Docker for a task that needs sudo.

## Container isolation

Each task has its own container and receives copies of its selected repositories. Agents modify those copies rather than the host checkouts. The container filesystem and repository copies are separate, but the automatic agent and harness mounts described above are shared host paths.

Isolation changes when you enable custom mounts, shared caches, mounted harness configuration, network access, devices, display access, or sudo. These options are intentional trust decisions. A writable host mount lets the agent change that host path, and shared mounts let tasks affect one another through shared data.

md does not use privileged containers or share the host network, PID namespace, IPC namespace, or container-runtime socket. It grants the capabilities required by its networking model. See [md Security](../md/security) for the current container boundary and options for restricting outbound access.

## Secret scanning on push

Before pushing, caic scans changes for common credentials such as cloud access keys, GitHub tokens, private keys, and hardcoded config secrets. Findings are reported to the agent so they can be removed.

This scan is a safety net, not a security boundary. An agent still has outbound network access unless you restrict it.

## MCP security

On a non-loopback listener, caic disables MCP when OAuth login is not configured. Remote clients can use Authorization Code with PKCE or the Device Authorization Grant, both with rotating refresh tokens. Clients can register dynamically or use an HTTPS Client ID Metadata Document with `private_key_jwt`. DPoP-capable clients can use sender-constrained access tokens.

Consent grants only selected scopes:

| Scope               | Grants                                                                                                                                                |
| ------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| `caic:mcp.read`     | Basic MCP tools, usage, and non-task resources                                                                                                        |
| `caic:tasks.read`   | Read task information                                                                                                                                 |
| `caic:tasks.create` | Create coding tasks                                                                                                                                   |
| `caic:tasks.write`  | Send and answer messages, fork tasks, and stop or revive existing tasks                                                                               |
| `caic:tasks.admin`  | Purge tasks                                                                                                                                           |
| `caic:repos.write`  | Clone repositories, push task branches or squash-push directly to default branches, repair pull request CI, and create default-branch CI repair tasks |
| `caic:server.admin` | Read whole-machine CPU, memory, network, and filesystem statistics, and server health                                                                 |

Tools and resources outside the approved scopes are not exposed to the client. Authorization Code consent lets you approve a subset of requested scopes. In the device flow, the client starts at `/oauth/device_authorization`, you approve its code at `/oauth/device`, and it polls `/oauth/token`; approval grants every requested scope. Review those scopes before approving. Revoke a grant from **Settings** at any time. Add `anthropic` or `openai` to `allow_origins` only when the corresponding hosted client must reach caic. See [MCP Server](./mcp) for connection steps.

## Voice security

Voice can run through embedded Gemini Live, a standalone gateway, or a local model stack. WebRTC audio is processed in memory rather than saved by caic. Short-lived service-issued credentials authorize each voice session. A standalone gateway receives the public verification material but not caic's private signing key.

## What caic does not protect

caic does not encrypt configuration, logs, or caches at rest. It does not prevent an agent from reaching the internet, audit data exfiltration, or limit what an authorized agent can commit or push.

For stronger outbound controls, configure container-runtime network restrictions as described in [md Security](../md/security#restricting-outbound-access).
