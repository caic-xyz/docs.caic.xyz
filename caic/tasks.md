# Task workflow

A task is a conversation with a coding agent in its own container. You choose the repositories and starting branches, then follow the work until you are ready to push the result.

## Create a task

1. Select one or more repositories from your configured root.
2. Choose a starting branch for each repository. caic adopts an available local branch with an upstream, or creates a task branch from your selection.
3. Choose a harness and model. Available models depend on the installed harness and its credentials.
4. Enter a concrete prompt and send it.

Use **Settings** to choose the default runtime, image, CPU settings, caches, and host mounts. Each task keeps the runtime it was created with. Sudo needs Docker; rootless Podman does not support it.

The agent edits repository copies inside the container. Your host checkout stays separate. Multi-repository tasks share one conversation and container.

## Follow and steer the work

The transcript streams agent text and tool calls. Expand a tool call to inspect its arguments and result. Native subagent and background-command cards show the activity the harness reports, including outcomes when available. The task header lists **Loaded skills** for the current context. The list resets after context compaction or a clear, while earlier loads stay linked in the transcript. Expand a past session to review its previous skills. Its info dialog reports the session's context compaction.

<figure class="docs-figure">
  <a class="docs-screenshot-link" href="/screenshots/frontend/desktop/task-detail.webp" target="_blank" rel="noopener"><img class="docs-screenshot" src="/screenshots/frontend/desktop/task-detail.webp" alt="Task transcript with streamed agent output, tool calls, repository state, and a message composer" width="1280" height="800" loading="lazy" decoding="async"></a>
  <figcaption>Send a follow-up when the agent finishes a turn.</figcaption>
</figure>

Follow the agent while it runs. When a task waits for another message or asks a structured question, respond to continue. A message you send while the agent works is queued and delivered after the current turn; later messages append to the same queued prompt. Choose **Edit**, or press `Arrow Up` in an empty composer, to move the queued prompt back into the composer. Agents can also render interactive widgets in the conversation.

<figure class="docs-figure">
  <a class="docs-screenshot-link" href="/screenshots/frontend/desktop/task-running.webp" target="_blank" rel="noopener"><img class="docs-screenshot" src="/screenshots/frontend/desktop/task-running.webp" alt="Running agent task with streamed output and tool activity" width="1280" height="800" loading="lazy" decoding="async"></a>
  <figcaption>Watch tool activity and output as the agent works.</figcaption>
</figure>

<figure class="docs-figure">
  <a class="docs-screenshot-link" href="/screenshots/frontend/desktop/task-ask.webp" target="_blank" rel="noopener"><img class="docs-screenshot" src="/screenshots/frontend/desktop/task-ask.webp" alt="A task asking a structured question with selectable answers" width="1280" height="800" loading="lazy" decoding="async"></a>
  <figcaption>Choose an answer or add your own response.</figcaption>
</figure>

When an agent presents a plan, review it before continuing.

<figure class="docs-figure">
  <a class="docs-screenshot-link" href="/screenshots/frontend/desktop/task-native-subagents.webp" target="_blank" rel="noopener"><img class="docs-screenshot" src="/screenshots/frontend/desktop/task-native-subagents.webp" alt="Delegated agent activity rendered within the task conversation" width="1280" height="800" loading="lazy" decoding="async"></a>
  <figcaption>Delegated work stays inside the task that owns it.</figcaption>
</figure>

Task cards show running background commands, subagents, and watches as icons beside the model, and a failed turn's error while the task waits.

<figure class="docs-figure">
  <a class="docs-screenshot-link" href="/screenshots/frontend/desktop/task-background.webp" target="_blank" rel="noopener"><img class="docs-screenshot" src="/screenshots/frontend/desktop/task-background.webp" alt="A running task with a background command, a watch, and a background subagent, counted by icons on its task card" width="1280" height="800" loading="lazy" decoding="async"></a>
  <figcaption>Background work keeps a task running and stays visible on its card and below the conversation.</figcaption>
</figure>

Agent links to generated images and files open in a document pane beside the conversation. Prompt images appear as thumbnails and open in the same pane. caic serves them from the task log, so they survive reloads. The conversation stays mounted while you read, and app-viewport full screen hides the surrounding chrome. caic previews Markdown with relative links and images, PDFs, audio, video, bounded text, and CAD models: STL, STEP or STP, compressed STEP, and 3MF with filament colors and printing plates where the file provides them. Mermaid diagrams render inline in Markdown. Other files offer a raw download. On mobile, the task and document use separate views. These files depend on the task's retained runtime, so save artifacts you need before purging it.

## Review and push

Open a repository's changes from the task card or task view. Check commit history, missing upstream commits, and file diffs. Expand individual files to read their changes.

<figure class="docs-figure">
  <a class="docs-screenshot-link" href="/screenshots/frontend/desktop/task-repository-changes.webp" target="_blank" rel="noopener"><img class="docs-screenshot" src="/screenshots/frontend/desktop/task-repository-changes.webp" alt="Repository changes view with commit history and an expanded code diff" width="800" height="720" loading="lazy" decoding="async"></a>
  <figcaption>Review the work in each repository before pushing.</figcaption>
</figure>

Choose the appropriate push action to send a task branch to its remote, or squash-push the changes to the default branch. caic scans for common secrets before pushing; treat this as a safety net, not a guarantee. When the repository has a pre-push hook, caic runs it inside the task container against the commit being pushed, and a rejection stops the push. The task timeline shows each push as one entry with the hook's output; cancel a running push from that entry. A multi-repository push can succeed for some repositories and fail for others. Inspect the result before retrying.

[GitHub](./github) and [GitLab](./gitlab) integration provide pull request or merge request creation and CI monitoring. Check your forge setup before enabling automatic CI repair or PR creation in **Settings**.

## Inspect usage and resources

Open task statistics to see token usage, cost, tool timing, sampled container resources, and the task's configured CPU ceiling when the runtime reports it. Task CPU usage stays aggregate because the runtime stream has no per-CPU breakdown, and an explicit ceiling excludes inherited cgroup limits and process affinity. The process view shows running processes in a continuous tree.

The account menu's **Monitoring** page groups three sections. **Usage** shows cross-task daily trends with range and subject filters. **System** shows live whole-machine CPU, memory, network, and filesystem history, including per-CPU meters and any sampling error. **Metrics** lists server operation measurements with counts, percentiles, and observed ranges. Whole-machine health also appears in the header as always-visible CPU and memory icons. Green means below 80%, orange means 80% or more, red means 90% or more, and gray means a sampling error or disconnected updates. The icons open **Monitoring > System**.

<figure class="docs-figure">
  <a class="docs-screenshot-link" href="/screenshots/frontend/desktop/task-stats.webp" target="_blank" rel="noopener"><img class="docs-screenshot" src="/screenshots/frontend/desktop/task-stats.webp" alt="Task statistics showing token usage, reported cost, and tool timing" width="1280" height="800" loading="lazy" decoding="async"></a>
  <figcaption>Compare token composition and time spent in tools.</figcaption>
</figure>

<figure class="docs-figure">
  <a class="docs-screenshot-link" href="/screenshots/frontend/desktop/task-resources.webp" target="_blank" rel="noopener"><picture>
    <source media="(max-width: 600px)" srcset="/screenshots/frontend/mobile/task-resources.webp" width="390" height="844">
    <img class="docs-screenshot" src="/screenshots/frontend/desktop/task-resources.webp" alt="Task resource history with CPU, memory, network throughput, and writable disk usage charts" width="1280" height="800" loading="lazy" decoding="async">
  </picture></a>
  <figcaption>Inspect sampled container resources. Network charts show receive and send rates.</figcaption>
</figure>

<figure class="docs-figure">
  <a class="docs-screenshot-link" href="/screenshots/frontend/desktop/usage.webp" target="_blank" rel="noopener"><img class="docs-screenshot" src="/screenshots/frontend/desktop/usage.webp" alt="Cross-task usage dashboard with daily token and cost trends" width="1280" height="800" loading="lazy" decoding="async"></a>
  <figcaption>Compare usage across tasks and days.</figcaption>
</figure>

When host CPU or memory is under pressure, the task list colors the tasks that contribute most to it.

Provider cards show available quota information. Support and freshness vary by provider; an unknown balance does not mean unlimited capacity.

## Work from your phone

The web app adapts to mobile browsers. Open a task to read results, send a message, or review changes. Connect the separate [Go Mode app](./android) for native capabilities.

<figure class="docs-figure docs-figure--phone">
  <a class="docs-screenshot-link" href="/screenshots/frontend/mobile/task-detail.webp" target="_blank" rel="noopener"><img class="docs-screenshot" src="/screenshots/frontend/mobile/task-detail.webp" alt="Mobile caic task conversation and follow-up controls" width="390" height="844" loading="lazy" decoding="async"></a>
  <figcaption>The same task conversation in a mobile browser.</figcaption>
</figure>

## Keyboard navigation

Press `?` or `F1` to open the shortcut reference. Arrow keys navigate task cards, `Page Up` and `Page Down` switch tasks, and `Tab` moves between task controls and the composer. Press `F4` to toggle [voice mode](./voice).

When work stops unexpectedly or reaches a quota limit, use [Recovery and handoffs](./recovery).
