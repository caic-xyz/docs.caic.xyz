# Design

This page explains the user-visible choices behind caic and how they affect everyday use.

## One container per task

Every task gets its own container. This keeps repository workspaces and processes separate, allows resource limits per task, and lets you remove one workspace without affecting another.

Repository workspaces and container filesystems are separate by default. md automatically mounts shared agent state such as `~/.agents` and the selected harness configuration, usually with write access. You can also share selected build caches or custom host mounts. Shared paths improve reuse but let tasks affect the same host data. See [Security](./security) before adding writable mounts.

## Repository copies and branches

Agents work on repository copies inside their containers rather than modifying your host checkout, so a task can rewrite history and switch branches without touching your working tree. Changes stay in the task until you push them. caic prefers to adopt a suitable local branch when one exists and creates a generated `caic-0` branch otherwise; [Architecture](./architecture#repository-and-branch-model) lists the exact rules, and multi-repository tasks apply the same choice to each repository.

## Persistent sessions

An agent keeps working when the server restarts or an SSH connection drops. A host sleep pauses local containers and agents, but their sessions survive and resume after the host wakes, so you can continue the same conversation. Only one caic server attaches to a task relay at a time, which prevents competing inputs to the same agent session.

## Fast startup and recovery

At startup, caic discovers repositories and running task containers concurrently. Live tasks are adopted first so active agents return quickly. Recent settled task history loads in the background and fills into the task list afterward.

Graceful server shutdown closes client connections but does not stop task relays. A service manager restarts caic after configuration changes, binary updates, or failures, and caic reconnects to the running tasks.

## Single-binary server

The caic binary contains the web app and the components needed to connect to task agents. This makes installation and updates simple, while task execution remains inside md containers.

The web UI handles dense task management on desktop and mobile browsers. The Android app hosts the same web UI and adds native voice, notifications, screenshot capture, passkeys, and device integration.

## Authentication choices

No-auth mode is convenient on localhost or a fully trusted private network. Configuring GitHub, GitLab, or Google login adds user identity and signed sessions. Forge authority remains separate: Google can authenticate a dashboard user, but only a linked GitHub or GitLab identity can perform forge actions.

External MCP clients receive their own OAuth grants. The consent screen exposes only the tools and resources permitted by the selected scopes, and grants can be revoked independently of dashboard sessions.

## Forge workflows

caic detects the forge from repository remotes. CI results are retained across restarts, and branches with active checks resume monitoring when the server returns. Before pushing, caic performs a best-effort scan for common secrets and asks the agent to fix findings.

## Configuration and updates

caic watches its configuration and executable. A change triggers graceful shutdown, after which systemd or launchd starts the updated server. The automatic updater uses the same mechanism.

Scheduled image pruning removes unused md-built images while keeping images required by active or stopped task containers.

## Titles and usage

caic generates short task titles asynchronously so title generation never blocks the next agent turn. It also tracks provider quota, token usage, and cost where each provider exposes that information. When a harness reports the model's context window, the task card shows token usage against it. The task UI combines these figures with runtime graphs so you can decide when to continue, fork, or switch agents.

## Native subagent activity

Coding agents often delegate work to subagents. caic surfaces that activity inside the task that spawned it rather than as separate tasks, because a native subagent has no independent container, branch, or session you can steer. Cards are keyed to the harness's own identity, so replayed history, context compaction, and a restored session refresh the same card instead of adding a duplicate.

caic shows only what the harness reports. It never invents a child outcome, so when a task settles while the last observation is still running, the card reports that the activity was last observed running with an unknown outcome. A batch card covers an entire orchestration of multiple agents. Member agents appear as their own cards only when the harness reports them. An active native subagent keeps the task Running, so background delegation is not mistaken for an idle turn.
