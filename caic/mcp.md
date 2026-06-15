# MCP Server

caic exposes a Model Context Protocol (MCP) endpoint at `/api/caic/v1/mcp`. It lets MCP clients such as Claude and ChatGPT view and drive your coding tasks over JSON-RPC. Through it a client can list and inspect tasks, create and manage them, and work with your repositories, all using the same permissions you grant.

## What it exposes

The endpoint serves both tools and resources:

- **Tools**: list tasks, get task detail, read an agent's last message, get usage, send a message, answer a question, create a task, fork a task, stop, revive, or purge a task, clone a repository, push a task branch, and fix a PR's CI.
- **Resources**: read-only views of your repositories and tasks, addressable by path or task number.

Some tools require a linked forge. Pushing a task branch or fixing a PR's CI needs a connected GitHub or GitLab identity. See [GitHub](./github) and [GitLab](./gitlab) for linking a forge.

## Connecting a client

Remote clients connect over OAuth 2.0 using the Authorization Code flow with PKCE and Dynamic Client Registration, so you do not pre-register each client by hand. Point your client at your caic server's base URL and start the connection. The client discovers the endpoint, registers itself, and sends you to caic to sign in and approve access.

### Consent and scopes

After you sign in, caic shows a consent screen listing the permissions the client requested. You grant any subset of them, or deny entirely. The read-only permissions are pre-selected; broader permissions are not, so you opt in deliberately.

The scopes are:

| Scope | Grants |
|---|---|
| `caic:mcp.read` | Use basic MCP tools including usage and non-task resources |
| `caic:tasks.read` | Read task information |
| `caic:tasks.write` | Create and manage tasks |
| `caic:tasks.admin` | Administer tasks (cancel, delete) |
| `caic:repos.write` | Manage repositories |

The grant covers caic MCP only. No GitHub, GitLab, OpenAI, or Anthropic credentials are shared with the client.

## Reaching a non-loopback server

caic enforces an origin allowlist. For a hosted client to reach a server that binds a non-loopback address, add the matching named origin to `allow_origins` in your config: `"anthropic"` for Claude and `"openai"` for ChatGPT. See [Configuration](./configuration) for the full list of named origins.

```toml
[server]
allow_origins = ["local", "tailscale", "anthropic"]
```

The MCP endpoint is disabled when OAuth login is not configured and the server binds a non-loopback address, so an exposed server never serves MCP without authentication. To use MCP off localhost, configure OAuth login first. See [Security](./security) for the full reasoning.

## Revoking access

You can revoke a client's grant at any time from **Settings** in the web app. Revoking immediately cuts off the client's access; it would have to go through consent again to reconnect.
