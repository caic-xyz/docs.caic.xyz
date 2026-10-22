# Architecture

caic is a local server and web app that orchestrates AI coding agents in [md](../md/) containers. This page explains task workspaces, lifecycle, restart recovery, and forge integration. The separate [Go Mode](https://docs.gomode.dev/guide/architecture) project owns the Android shell, reusable browser voice components, MCP/OAuth transport, and voice gateway. caic owns its product UI, task APIs, login policy, and task-specific tools.

## System overview

```text
caic web UI / Go Mode shell
          |
       HTTP/SSE
          |
     caic server
          |
         SSH
          |
 one md container per task
          |
   relay and agent CLI
```

Each task runs in its own Docker or Podman container. caic talks to the task over SSH. A relay inside the container keeps the agent alive across SSH disconnects and lets caic reconnect after a server restart. When both runtimes are available, you can choose one for each new task.

## Task lifecycle

A task combines a prompt, one or more repositories, a branch choice, and an agent harness. It moves through setup states before the agent runs. After a turn, it waits for another message, asks a structured question, or presents a plan.

| State            | What is happening                                                                                          |
| ---------------- | ---------------------------------------------------------------------------------------------------------- |
| **Pending**      | Task is queued                                                                                             |
| **Branching**    | Branches and repository workspaces are prepared                                                            |
| **Provisioning** | The task container is starting                                                                             |
| **Starting**     | caic is connecting to the agent                                                                            |
| **Running**      | The agent is producing output                                                                              |
| **Waiting**      | The turn finished and the agent can receive another message                                                |
| **Asking**       | The agent needs an answer                                                                                  |
| **HasPlan**      | The agent produced a plan for review                                                                       |
| **Pulling**      | Changes are being read from the task workspace                                                             |
| **Pushing**      | Changes are being pushed to the remote                                                                     |
| **Stopping**     | Graceful shutdown is in progress                                                                           |
| **Stopped**      | The container is stopped and can be revived                                                                |
| **Crashed**      | An active agent session failed or its container ran out of memory; the retained container can be revived   |
| **Purging**      | Container deletion is in progress                                                                          |
| **Failed**       | Setup, branch allocation, fork, revival, or runtime destruction failed; inspect the task error for details |
| **Purged**       | The task is final and its log is archived                                                                  |

Choosing Purge on an active or crashed task first stops it, then waits for the configured recovery window. Reviving during that window cancels deletion. The default delay is 15 seconds and can be set from 10 seconds to 24 hours in **Settings**. A task that is already Stopped is deleted immediately when purged.

An ordinary container exit records the task as Stopped. An out-of-memory event while an agent is active records it as Crashed, and unexpected runtime destruction records it as Failed.

## Repository and branch model

caic discovers Git repositories under the configured root. When you create a task, you can select one or more repositories and choose what to do with each branch:

- **Adopt** keeps working on a selected local branch when it has an upstream and no other non-final task is associated with it. Stopped and crashed tasks still retain their branch association.
- **Branch off** creates a new branch such as `caic-0`. This is used for remote branches, untracked or busy local branches, and normal work from a default or selected base.

The agent receives a copy of each selected repository inside its container. It does not edit the host checkout. Changes remain local to the task until you push them. A multi-repository task pushes its repository changes together.

The task card summarizes each repository's Git operation, conflicts, uncommitted changes, and ahead or behind state. The diff view lists task commits and changed files first. Open a file to load its patch on demand, and retry inline if a patch fails to load. Binary files show their byte-size transition instead of line counts.

<figure class="docs-figure">
  <a class="docs-screenshot-link" href="/screenshots/frontend/desktop/task-repository-changes.webp" target="_blank" rel="noopener"><img class="docs-screenshot" src="/screenshots/frontend/desktop/task-repository-changes.webp" alt="caic repository changes view showing a task branch ahead of upstream, committed and uncommitted files, and an expanded line-by-line patch" width="800" height="720" loading="lazy" decoding="async"></a>
  <figcaption>Open a task's repository summary to review commits and uncommitted changes file by file.</figcaption>
</figure>

## Forks and handoffs

Forking creates a separate workspace from a running, stopped, or crashed task. The new task snapshots the source container filesystem and repository workspace, including installed tools, while receiving its own branches. It starts with clean message history and uses the selected prompt or generated handoff as its initial context.

Before starting the fork, you can edit its prompt or generate an editable handoff summarizing the original request, recent conversation, and current changes. You can also add repositories, switch the harness, model, or effort, and change task options such as Tailscale, display, USB, sudo, or GitHub token injection.

When a task is blocked by provider quota, **Continue in new agent** opens this fork flow with a generated handoff and recommends harnesses with available quota. You can review the handoff and recommendation before starting the replacement task.

## Session persistence

The relay records the conversation inside the task container and owns the agent process independently of the server's SSH connection. If caic restarts or the connection drops, the relay and agent keep running. caic reconnects, restores the missed output, and resumes streaming.

When caic starts, it discovers repositories and live task containers first. It adopts healthy live tasks without waiting for archived history. Recent settled tasks then load in the background, so older entries can appear shortly after the live task list becomes available.

If a task container exits normally, caic records it as Stopped. Its filesystem remains available for revival until you purge it.

## Task inspection

caic streams agent output, state changes, repository changes, and runtime metrics to connected clients. The task view provides:

- token usage, provider quota, cost, and resource charts
- CPU, memory, network, storage I/O, and disk usage
- committed changes associated with each completed turn
- a process tree with resource details and actions to send TERM or KILL
- launch configuration, image, platform, caches, mounts, and diagnostics
- confirmed skill loads for the current context, with links to each `SKILL.md`

A document pane opens task files beside the conversation. It previews Markdown, images, PDFs, audio, video, bounded text, and CAD models in STL, STEP, and 3MF form, renders Mermaid diagrams inline, and offers a raw download for other files. See [Task workflow](./tasks#follow-and-steer-the-work).

The header shows always-visible whole-machine CPU and memory levels from the task-list stream. Green means below 80%, orange means 80% or more, red means 90% or more, and gray means a sampling error or disconnected updates. The account menu's **Monitoring** page adds cross-task usage, live machine history, and server operation metrics. See [Task workflow](./tasks#inspect-usage-and-resources).

Tasks also show native subagent activity reported by the harness. This is work the agent delegated to its own subagents, shown inside the task that spawned it rather than as separate tasks. Each card lists the observed status, a duration when the harness reports both start and end, and the prompt and result when the harness exposes them. Cards render inline in the transcript, below the item that last changed their status, so their position matches when the work happened. Claude Code, Codex, OpenCode, and Pi report native subagents, and some harnesses also report orchestration batches. caic shows only what the harness reports and never invents an outcome, so activity whose last observation is still running is shown as last observed running with an unknown outcome. A task stays Running after its trailing result only while a background delegation is running. A foreground card that the harness never settles falls back to Waiting instead of pinning the task, and the task returns to Waiting, Asking, or HasPlan when the last background card settles.

<figure class="docs-figure">
  <a class="docs-screenshot-link" href="/screenshots/frontend/desktop/task-native-subagents.webp" target="_blank" rel="noopener"><img class="docs-screenshot" src="/screenshots/frontend/desktop/task-native-subagents.webp" alt="caic task transcript with native subagent and batch cards rendered inline, showing identity, group, prompt, result, and status" width="1280" height="800" loading="lazy" decoding="async"></a>
  <figcaption>Native subagent and batch cards appear inline in the transcript as the harness reports them.</figcaption>
</figure>

Stopped tasks retain a disk-usage summary so you can identify large workspaces before purging them.

## API and clients

The web app and Android app use a JSON HTTP API plus Server-Sent Events for live updates. VNC display sessions use WebSocket. The MCP endpoint lets approved external clients manage tasks through OAuth.

See the [API reference](https://github.com/caic-xyz/caic/blob/main/sdk/caic/API.md) for endpoint details and [MCP Server](./mcp) for client setup.

## Forge integration

caic detects GitHub and GitLab from repository remotes. When you push a task, it can open a pull or merge request with the task title and agent summary, monitor CI, and return failures to the agent. Optional auto-fix can let the agent iterate on failed checks. GitLab forge operations currently support GitLab.com only; a configured self-hosted GitLab URL affects OAuth login, not repository, merge request, or CI API operations.

| Mode                  | Configuration                        | Capabilities                                              |
| --------------------- | ------------------------------------ | --------------------------------------------------------- |
| Personal access token | `[github.pat]` or `[gitlab.pat]`     | Single-user forge access and CI polling                   |
| OAuth                 | `[github.oauth]` or `[gitlab.oauth]` | Per-user login, forge access, and CI polling              |
| GitHub App            | `[github.app]` with PAT or OAuth     | Webhooks and automatic tasks from supported GitHub events |

A configured GitHub App can react to a labeled issue, a pull request targeting the default branch, or an `@caic` comment. See [GitHub Integration](./github) and [GitLab Integration](./gitlab).

## Voice

The web UI and Android app can stream WebRTC audio to embedded Gemini Live, a standalone gateway, or a local model stack. See [Voice](./voice) for usage and [Configuration](./configuration) for gateway options.

## Updates and image maintenance

caic watches its executable and configuration. Saving a configuration change or replacing the binary triggers a graceful restart under systemd or launchd. Running agent sessions remain inside their containers and are adopted after restart.

By default, caic checks for a release daily at 04:50 and removes unused md-built images daily at 05:00. Both schedules are configurable or can be disabled.
