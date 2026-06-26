---
# GitLab Integration: PAT and OAuth setup for MRs, CI monitoring, and webhooks
---

# GitLab Integration

caic integrates with GitLab for automatic merge request creation and CI monitoring. The forge is detected automatically from your repository's git remote URL — including self-hosted instances.

Config keys are documented in [Configuration](./configuration#gitlab). This page walks through setup for each integration mode.

## Features

- **MR creation**: after syncing a task branch, caic opens a merge request with the task title and agent summary
- **CI monitoring**: polls pipeline status every 15-30 seconds, notifies the agent when CI passes or fails
- **Webhooks** (optional): real-time pipeline events instead of polling

## Choosing a mode

| Mode | Best for | Auth |
|---|---|---|
| PAT | Single user, headless | Token in config |
| OAuth | Multiple users with login | Login via GitLab |

PAT and OAuth are mutually exclusive.

## Self-hosted GitLab

If you use a self-hosted GitLab instance, set the `url` in your config:

```toml
[gitlab]
url = "https://gitlab.example.com"
```

This works for both PAT and OAuth modes.

## PAT setup

For single-user deployments.

1. [Create a personal access token](https://gitlab.com/-/user_settings/personal_access_tokens) with the `api` scope
2. Add to `~/.config/caic/config.toml`:
   ```toml
   [gitlab.pat]
   token = "glpat-..."
   ```

For self-hosted, create the token at your instance's settings page and include `url` as shown above.

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
