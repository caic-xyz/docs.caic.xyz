# GitHub Integration

caic supports GitHub for automatic PR creation and CI monitoring. The forge is detected automatically from the repository's git remote URL.

## PR creation

After a successful sync to the task's branch, caic automatically opens a pull request against the base branch. The title comes from the task title and the body from the agent's result summary. The PR number appears as a link in the task detail header.

## CI monitoring

After PR creation, caic polls CI status every 15 seconds (GitHub check-runs):

- **CI: passed** — all checks succeeded; the agent is notified with a summary
- **CI: failed** — one or more checks failed; the agent is notified with names and URLs of failing checks so it can act on them

## Integration modes

caic supports three GitHub integration modes. They are not mutually exclusive — PAT or OAuth handles forge operations while GitHub App handles webhooks independently.

| | **GitHub PAT** | **GitHub OAuth** | **GitHub App** |
|---|---|---|---|
| **Use case** | Single-user | Multi-user with login | Org-wide automation |
| **User auth** | No | Yes (login via GitHub) | No |
| **Webhooks** | No (polling only) | No (polling only) | Yes |
| **Auto task creation** | No | No | Yes |
| **Config keys** | `[github] token` | `[github] oauth_client_id` + `oauth_client_secret` + `oauth_allowed_users` | `[github] app_id` + `app_private_key_pem` + `webhook_secret` |

All settings go in the `[github]` section of `~/.config/caic/config.toml`.

## GitHub PAT

[Create a fine-grained token](https://github.com/settings/personal-access-tokens/new) with `pull_requests: write` and `checks: read` permissions.

```toml
[github]
token = "<your-token>"
```

If unset and OAuth is not configured, caic auto-detects the token from `gh auth token`.

See your current tokens at https://github.com/settings/personal-access-tokens


## GitHub OAuth

OAuth also requires `[server] external_url` to be set (see [Configuration](./configuration)).

1. Create a [GitHub OAuth app](https://github.com/settings/applications/new)
   - Callback URL: `https://<your-domain>/api/v1/auth/github/callback`
2. Add to `config.toml`:
   ```toml
   [server]
   external_url = "https://<your-domain>"

   [github]
   oauth_client_id = "<client-id>"
   oauth_client_secret = "<client-secret>"
   oauth_allowed_users = ["alice", "bob"]
   ```

See the GitHub OAuth Apps you created at https://github.com/settings/developers

See the GitHub OAuth Apps you installed at https://github.com/settings/applications. In particular, you need to
**Grant** access to your organizations you want to be able to access.


## GitHub App

Enables real-time webhooks and automatic task creation for issues, PRs, and `@caic` mentions.

Also requires `[server] external_url` to be set (see [Configuration](./configuration)).

1. [Create a GitHub App](https://github.com/settings/apps/new)
   - Webhook URL: `https://<your-domain>/webhooks/github`
   - Permissions: Issues (read/write), Pull requests (read/write), Checks (read)
   - Events: Issues, Pull requests, Issue comments, Check suites
2. Generate a private key from the app settings
3. Install the app on your org or repositories (app must be public for org installs)
4. Add to `config.toml`:
   ```toml
   [github]
   webhook_secret = "<webhook-secret>"
   app_id = 12345
   app_private_key_pem = "private-key.pem"  # relative to ~/.config/caic/
   app_allowed_owners = ["my-org"]           # optional
   ```

Automatic task creation triggers:

| Event | Condition | Action |
|---|---|---|
| Issue opened | Issue has `caic` label | Agent fixes the issue |
| PR opened/reopened | Targets the default branch | Agent reviews/fixes the PR |
| Comment created | Body contains `@caic` | Agent acts on the comment |

See the GitHub Apps you created at https://github.com/settings/apps

See how the GitHub Apps are installed at https://github.com/settings/installations


## Allowing OAuth app access

To grant access to an organization:
1. Visit https://github.com/settings/applications
2. Select your application.
3. Under "Organization access", click Grant.

Confirm it is connected by visiting `https://github.com/organizations/<org>/settings/oauth_application_policy` and checking that the application is listed as Approved.
