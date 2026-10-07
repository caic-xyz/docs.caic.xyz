# MCP Server

caic exposes a Model Context Protocol (MCP) endpoint at `/api/caic/v1/mcp`. Clients such as Claude and ChatGPT can inspect repositories and coding tasks, create or steer tasks, and perform approved repository actions.

## Tools and resources

| Tool                         | Scope               | What it does                                                         |
| ---------------------------- | ------------------- | -------------------------------------------------------------------- |
| `harnesses_list`             | `caic:mcp.read`     | List available harnesses, models, and reasoning effort options       |
| `repos_list`                 | `caic:mcp.read`     | List managed repositories                                            |
| `get_usage`                  | `caic:mcp.read`     | Read local and provider usage                                        |
| `tasks_list`                 | `caic:tasks.read`   | List tasks                                                           |
| `task_get_detail`            | `caic:tasks.read`   | Read one task's detail and recent output                             |
| `agent_last_message`         | `caic:tasks.read`   | Read an agent's most recent message                                  |
| `task_create`                | `caic:tasks.create` | Create a coding task                                                 |
| `task_send_message`          | `caic:tasks.write`  | Send a message to a task                                             |
| `task_answer_question`       | `caic:tasks.write`  | Answer a task's structured question                                  |
| `task_fork`                  | `caic:tasks.write`  | Fork a task                                                          |
| `task_stop`                  | `caic:tasks.write`  | Stop a task                                                          |
| `task_revive`                | `caic:tasks.write`  | Revive a stopped task                                                |
| `task_purge`                 | `caic:tasks.admin`  | Purge a task                                                         |
| `clone_repo`                 | `caic:repos.write`  | Clone a repository                                                   |
| `task_push_branch_to_remote` | `caic:repos.write`  | Push a task branch, or squash-push its changes to the default branch |
| `task_fix_pr`                | `caic:repos.write`  | Repair CI for an existing task's pull request                        |
| `bot_fix_ci`                 | `caic:repos.write`  | Create a task to repair CI on a repository's default branch          |

Repository and task list tools are paginated. The MCP `resources/list` response is paginated too. A response can contain fewer results than requested to stay within response-size limits. Continue with `nextCursor` until it is absent.

The current read-only resources are:

- `caic://repos/{path}` for one managed repository
- `caic://tasks/{id}` for one task
- `caic://usage` for local and provider usage
- `gomode://items` for native-client task summaries
- `gomode://notifications` for native-client notifications

The `caic:mcp.read` scope exposes repository and usage resources. The `caic:tasks.read` scope exposes task resources plus the two `gomode://` resources. Resource instances outside the approved scopes are omitted from `resources/list`.

Clients that support subscriptions can listen for task or repository changes. When a client subscribes, caic delivers the current state of each subscribed resource. A later notification invalidates the resource, so read it again to get the latest state.

Some tools require a linked forge identity. Pushing a branch, repairing pull request CI, or repairing default-branch repository CI needs connected [GitHub](./github) or [GitLab](./gitlab) authority.

## Connecting a remote client

Remote clients can use OAuth 2.0 Authorization Code with PKCE or the Device Authorization Grant. Set `[server] external_url` to an explicit stable HTTPS URL. The default `"auto"` mode supports browser login and same-origin session MCP, but it cannot provide the immutable issuer required by remote MCP OAuth.

Most clients register through Dynamic Client Registration. A client that publishes an HTTPS Client ID Metadata Document can use that document as its client ID and authenticate with `private_key_jwt` instead.

Point the client at the full endpoint URL, for example `https://caic.example.com/api/caic/v1/mcp`. The client discovers the authorization service and opens caic so you can sign in and approve access.

### Consent and scopes

The consent screen lists the requested permissions. Read-only permissions are selected by default. Tools and resources that the approved scopes do not allow are omitted from discovery results.

| Scope               | Grants                                                                                                                                                |
| ------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| `caic:mcp.read`     | Use basic MCP tools, usage, and non-task resources                                                                                                    |
| `caic:tasks.read`   | Read task information                                                                                                                                 |
| `caic:tasks.create` | Create coding tasks                                                                                                                                   |
| `caic:tasks.write`  | Send and answer messages, fork tasks, and stop or revive existing tasks                                                                               |
| `caic:tasks.admin`  | Purge tasks                                                                                                                                           |
| `caic:repos.write`  | Clone repositories, push task branches or squash-push directly to default branches, repair pull request CI, and create default-branch CI repair tasks |

Grants created before the task-creation scope was introduced do not gain it automatically. Reapprove the client if it needs to create tasks.

The grant covers caic MCP only. caic does not disclose your GitHub, GitLab, OpenAI, or Anthropic credentials to the client.

### Device authorization

A device-capable client starts at `/oauth/device_authorization` and shows a code and verification URL. Open `/oauth/device`, sign in, and approve the displayed code. The client polls `/oauth/token` until approval completes.

Authorization Code consent lets you select a subset of the requested scopes. Device-code approval grants every scope the client requested, so review the requested permissions before approving the code.

## Reaching a non-loopback server

caic enforces an origin allowlist. Add the matching named origin for a hosted client: `"anthropic"` for Claude or `"openai"` for ChatGPT.

```toml
[server]
external_url = "https://caic.example.com"
allow_origins = ["local", "tailscale", "anthropic"]
```

The endpoint is disabled on a non-loopback listener when OAuth login is not configured. See [Configuration](./configuration) for HTTPS and origin setup, and [Security](./security) for the trust boundaries.

## Revoking access

Revoke a client's grant from **Settings** in the web app. Revocation takes effect immediately. The client must complete consent again before reconnecting.
