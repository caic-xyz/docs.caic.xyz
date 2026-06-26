---
# GitHub Integration: PAT, OAuth, and GitHub App setup for PRs, CI monitoring, and webhooks
---

# GitHub Integration

caic integrates with GitHub for automatic pull request creation and CI monitoring. The forge is detected automatically from your repository's git remote URL — no configuration needed for detection.

Config keys are documented in [Configuration](./configuration#github). This page walks through setup for each integration mode.

## Features

- **PR creation**: after syncing a task branch, caic opens a pull request with the task title and agent summary
- **CI monitoring**: polls check-runs every 15-30 seconds, notifies the agent when CI passes or fails
- **Webhooks** (GitHub App): real-time events instead of polling
- **Bot automation** (GitHub App): auto-creates tasks from issues, PRs, and `@caic` comments

## Choosing a mode

| Mode | Best for | Auth | Webhooks | Bot |
|---|---|---|---|---|
| PAT | Single user, headless | Token in config | No | No |
| OAuth | Multiple users with login | Login via GitHub | No | No |
| GitHub App | Org-wide automation | App installation | Yes | Yes |

GitHub App can be layered on top of PAT, OAuth, or both. A PAT can also provide server-level GitHub credentials when no user token is available.

## PAT setup

For single-user deployments.

1. [Create a fine-grained token](https://github.com/settings/personal-access-tokens/new) with:
   - Repository access: select your repositories
   - Permissions: `Pull requests` (read/write), `Checks` (read)
2. Add to `~/.config/caic/config.toml`:
   ```toml
   [github.pat]
   token = "github_pat_..."
   ```

If no token is set and no OAuth is configured, caic falls back to `gh auth token` from the GitHub CLI automatically.

See your tokens at [github.com/settings/personal-access-tokens](https://github.com/settings/personal-access-tokens).

## OAuth setup

For multi-user deployments where each user logs in with their GitHub account.

1. [Create a GitHub OAuth app](https://github.com/settings/applications/new)
   - Callback URL: `https://<your-domain>/auth/github/callback`
2. Add to `~/.config/caic/config.toml`:
   ```toml
   [server]
   external_url = "https://<your-domain>"

   [github.oauth]
   client_id = "<client-id>"
   client_secret = "<client-secret>"
   allowed_users = ["alice", "bob"]
   ```

`allowed_users` restricts login to the listed GitHub usernames. Leave it unset to allow any GitHub user who completes the OAuth flow. Set it to keep login private.

### Granting organization access

If your repositories are in an organization:

1. Visit [github.com/settings/applications](https://github.com/settings/applications)
2. Select your OAuth app
3. Under "Organization access", click **Grant**

Verify at `https://github.com/organizations/<org>/settings/oauth_application_policy` — the app should appear as Approved.

Manage your OAuth apps at [github.com/settings/developers](https://github.com/settings/developers).

## GitHub App setup

For org-wide automation with webhooks and bot-driven task creation.

1. [Create a GitHub App](https://github.com/settings/apps/new)
   - Webhook URL: `https://<your-domain>/webhooks/github`
   - Permissions: **Issues** (read/write), **Pull requests** (read/write), **Checks** (read)
   - Events: Issues, Pull requests, Issue comments, Check suites
2. Generate a private key from the app settings and save the `.pem` file to `~/.config/caic/`
3. Install the app on your organization or repositories (the app must be public for org installs)
4. Add to `~/.config/caic/config.toml`:
   ```toml
   [github.app]
   id = 12345
   private_key_pem = "private-key.pem"
   allowed_owners = ["my-org"]
   webhook_secret = "<webhook-secret>"
   ```

Generate a webhook secret: `openssl rand -hex 32`.

### Bot triggers

When installed, the bot automatically creates tasks from forge events:

| Event | Condition | Action |
|---|---|---|
| Issue opened | Issue has `caic` label | Agent fixes the issue |
| PR opened | Targets the default branch | Agent reviews the PR |
| Comment created | Body contains `@caic` | Agent acts on the instruction |

The bot posts comments with links back to your caic instance.

See your apps at [github.com/settings/apps](https://github.com/settings/apps) and installations at [github.com/settings/installations](https://github.com/settings/installations).
