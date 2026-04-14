# GitLab Integration

caic supports GitLab for automatic MR creation and CI monitoring. The forge is detected automatically from the repository's git remote URL.

## MR creation

After a successful sync to the task's branch, caic automatically opens a merge request against the base branch. The title comes from the task title and the body from the agent's result summary. The MR number appears as a link in the task detail header.

## CI monitoring

After MR creation, caic polls CI status every 15 seconds (GitLab pipeline statuses):

- **CI: passed** — all checks succeeded; the agent is notified with a summary
- **CI: failed** — one or more checks failed; the agent is notified with names and URLs of failing checks so it can act on them

## Integration modes

All settings go in the `[gitlab]` section of `~/.config/caic/config.toml`.

| | **GitLab PAT** | **GitLab OAuth** |
|---|---|---|
| **Use case** | Single-user | Multi-user with login |
| **User auth** | No | Yes |
| **Config keys** | `[gitlab] token` | `[gitlab] oauth_client_id` + `oauth_client_secret` + `oauth_allowed_users` |

For self-hosted GitLab, also set `url`:

```toml
[gitlab]
url = "https://<your-gitlab-instance>"
```

## GitLab PAT

[Create a personal access token](https://gitlab.com/-/user_settings/personal_access_tokens) with `api` scope.

```toml
[gitlab]
token = "<your-token>"
```

## GitLab OAuth

Also requires `[server] external_url` to be set (see [Configuration](./configuration)).

1. Create a [GitLab OAuth app](https://gitlab.com/-/user_settings/applications)
   - Redirect URI: `https://<your-domain>/api/v1/auth/gitlab/callback`
   - Scopes: `api`, `read_user`
2. Add to `config.toml`:
   ```toml
   [server]
   external_url = "https://<your-domain>"

   [gitlab]
   oauth_client_id = "<application-id>"
   oauth_client_secret = "<secret>"
   oauth_allowed_users = ["alice", "bob"]
   ```

For self-hosted GitLab, also set:
```toml
[gitlab]
url = "https://<your-gitlab-instance>"
```

## Webhooks (optional)

Webhooks deliver CI status in real time instead of waiting up to 30s for the next poll cycle.

1. In project **Settings > Webhooks**:
   - URL: `https://<your-domain>/webhooks/gitlab`
   - Secret token: `openssl rand -hex 32`
   - Enable: Pipeline events
2. Add to `config.toml`:
   ```toml
   [gitlab]
   webhook_secret = "<the secret>"
   ```
