# GitLab Integration

caic integrates with GitLab.com for automatic merge request creation and CI monitoring. Forge API operations currently use GitLab.com. A self-hosted URL can be configured for OAuth login, but repository, merge request, and CI API operations do not yet use that URL.

Config keys are documented in [Configuration](./configuration#gitlab). This page walks through setup for each integration mode.

## Features

- **MR creation**: after syncing a task branch, caic opens a merge request with the task title and agent summary
- **CI monitoring**: polls pipeline status every 15-30 seconds, notifies the agent when CI passes or fails
- **Webhooks** (optional): real-time pipeline events instead of polling

## Choosing a mode

| Mode  | Best for                  | Auth             |
| ----- | ------------------------- | ---------------- |
| PAT   | Single user, headless     | Token in config  |
| OAuth | Multiple users with login | Login via GitLab |

PAT and OAuth are mutually exclusive.

## Self-hosted OAuth login

To authenticate dashboard users through a self-hosted GitLab instance, set its `url`:

```toml
[gitlab]
url = "https://gitlab.example.com"
```

This changes OAuth login only. caic's forge API client still targets GitLab.com, so self-hosted repository, merge request, and CI operations are not supported.

## PAT setup

For single-user deployments.

1. [Create a personal access token](https://gitlab.com/-/user_settings/personal_access_tokens) with the `api` scope
2. Add to `~/.config/caic/config.toml`:
   ```toml
   [gitlab.pat]
   token = "glpat-..."
   ```

The PAT forge integration currently supports GitLab.com only.

## OAuth setup

For multi-user deployments where each user logs in with their GitLab account.

1. [Create a GitLab OAuth app](https://gitlab.com/-/user_settings/applications)
   - Redirect URI: `https://<your-domain>/auth/gitlab/callback`
   - Scopes: `api`, `read_user`
2. Add to `~/.config/caic/config.toml`:
   ```toml
   [server]
   external_url = "https://<your-domain>"

   [gitlab.oauth]
   client_id = "<application-id>"
   client_secret = "<secret>"
   allowed_users = ["alice", "bob"]
   ```

`allowed_users` restricts login to the listed GitLab usernames. Leave it unset to allow any GitLab user who completes the OAuth flow. Set it to keep login private.

## Webhooks (optional)

Webhooks deliver CI status in real time instead of waiting for the poll cycle.

1. In your project, go to **Settings > Webhooks**:
   - URL: `https://<your-domain>/webhooks/gitlab`
   - Secret token: generate with `openssl rand -hex 32`
   - Enable: Pipeline events
2. Add to `~/.config/caic/config.toml`:
   ```toml
   [gitlab]
   webhook_secret = "<the secret>"
   ```

Without webhooks, caic polls pipeline status every 15-30 seconds.
