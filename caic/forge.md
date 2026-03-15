# Forge Integration

caic supports GitHub and GitLab for automatic PR/MR creation and CI monitoring. The forge is detected automatically from the repository's git remote URL.

## PR/MR creation

After a successful sync to the task's branch, caic automatically opens a pull request (GitHub) or merge request (GitLab) against the base branch. The title comes from the task title and the body from the agent's result summary. The PR/MR number appears as a link in the task detail header.

## CI monitoring

After PR/MR creation, caic polls CI status every 15 seconds (GitHub check-runs or GitLab pipeline statuses):

- **CI: passed** — all checks succeeded; the agent is notified with a summary
- **CI: failed** — one or more checks failed; the agent is notified with names and URLs of failing checks so it can act on them

## GitHub

caic supports three GitHub integration modes. They are not mutually exclusive — PAT or OAuth handles forge operations while GitHub App handles webhooks independently.

| | **GitHub PAT** | **GitHub OAuth** | **GitHub App** |
|---|---|---|---|
| **Use case** | Single-user | Multi-user with login | Org-wide automation |
| **User auth** | ❌ | ✅ Login via GitHub | ❌ |
| **Webhooks** | ❌ polling only | ❌ polling only | ✅ |
| **Auto task creation** | ❌ | ❌ | ✅ |
| **Env vars** | `GITHUB_TOKEN` | `CAIC_EXTERNAL_URL` + `GITHUB_OAUTH_CLIENT_ID` + `GITHUB_OAUTH_CLIENT_SECRET` + `GITHUB_OAUTH_ALLOWED_USERS` | `CAIC_EXTERNAL_URL` + `GITHUB_APP_ID` + `GITHUB_APP_PRIVATE_KEY_PEM` + `GITHUB_WEBHOOK_SECRET` |

### GitHub PAT

[Create a fine-grained token](https://github.com/settings/personal-access-tokens/new) with `pull_requests: write` and `checks: read` permissions.

```bash
GITHUB_TOKEN=<your-token>
```

If unset, caic auto-detects the token from `gh auth token`.

### GitHub OAuth

1. Create a [GitHub OAuth app](https://github.com/settings/applications/new)
   - Callback URL: `https://<your-domain>/api/v1/auth/github/callback`
2. Set environment variables:
   ```
   CAIC_EXTERNAL_URL=https://<your-domain>
   GITHUB_OAUTH_CLIENT_ID=<client-id>
   GITHUB_OAUTH_CLIENT_SECRET=<client-secret>
   GITHUB_OAUTH_ALLOWED_USERS=alice,bob
   ```

### GitHub App

Enables real-time webhooks and automatic task creation for issues, PRs, and `@caic` mentions.

1. [Create a GitHub App](https://github.com/settings/apps/new)
   - Webhook URL: `https://<your-domain>/webhooks/github`
   - Permissions: Issues (read/write), Pull requests (read/write), Checks (read)
   - Events: Issues, Pull requests, Issue comments, Check suites
2. Generate a private key from the app settings
3. Install the app on your org or repositories (app must be public for org installs)
4. Set environment variables:
   ```
   GITHUB_WEBHOOK_SECRET=<webhook-secret>
   GITHUB_APP_ID=<app-id>
   GITHUB_APP_PRIVATE_KEY_PEM=private-key.pem  # relative to ~/.config/caic/
   GITHUB_APP_ALLOWED_OWNERS=my-org  # optional
   ```

Automatic task creation triggers:

| Event | Condition | Action |
|---|---|---|
| Issue opened | Issue has `caic` label | Agent fixes the issue |
| PR opened/reopened | Targets the default branch | Agent reviews/fixes the PR |
| Comment created | Body contains `@caic` | Agent acts on the comment |

## GitLab

| | **GitLab PAT** | **GitLab OAuth** |
|---|---|---|
| **Use case** | Single-user | Multi-user with login |
| **User auth** | ❌ | ✅ |
| **Env vars** | `GITLAB_TOKEN` | `CAIC_EXTERNAL_URL` + `GITLAB_OAUTH_CLIENT_ID` + `GITLAB_OAUTH_CLIENT_SECRET` + `GITLAB_OAUTH_ALLOWED_USERS` |

For self-hosted GitLab, also set `GITLAB_URL=https://<your-gitlab-instance>`.

### GitLab webhooks (optional)

Webhooks deliver CI status in real time instead of waiting up to 30s for the next poll cycle.

1. In project **Settings → Webhooks**:
   - URL: `https://<your-domain>/webhooks/gitlab`
   - Secret token: `openssl rand -hex 32`
   - Enable: Pipeline events
2. Set: `GITLAB_WEBHOOK_SECRET=<the secret>`
