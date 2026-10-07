---
# caic and md: user guides for parallel coding agents and isolated containers.
layout: home
hero:
  name: caic + md
  text: Put your agents to work.
  tagline: Run coding tasks in separate containers. Follow the work, review the changes, and keep moving from your desktop or phone.
  actions:
    - theme: brand
      text: Install caic
      link: /caic/installation
    - theme: alt
      text: Explore the workflow
      link: /caic/tasks
    - theme: alt
      text: Use md from the terminal
      link: /md/
features:
  - title: A workspace for each task
    details: Your repositories stay separate while agents work in parallel. Choose Docker or Podman and the harness that fits the task.
    link: /caic/tasks
  - title: Review before you ship
    details: Follow agent output, inspect commits and diffs, and push changes with GitHub or GitLab integration.
    link: /caic/tasks#review-and-push
  - title: Keep the conversation going
    details: Reconnect after a restart, revive a retained workspace, or fork with a handoff when work needs a fresh start.
    link: /caic/recovery
---

<div class="home-showcase">
<figure>
  <picture><source media="(max-width: 600px)" width="390" height="844" srcset="/screenshots/frontend/mobile/overview.webp"><img class="docs-screenshot" src="/screenshots/frontend/desktop/overview.webp" alt="caic task dashboard with concurrent tasks grouped by repository and their agent states" width="1280" height="800" fetchpriority="high"></picture>
  <figcaption>One view of your coding tasks, from the first prompt to the final review.</figcaption>
</figure>
<div class="home-links">
<section><h2>caic</h2><p>The server and web app for parallel coding tasks. Start here for installation, workflow, configuration, and security.</p><a href="/caic/">caic documentation →</a></section>
<section><h2>md</h2><p>The container toolkit behind caic. Use it directly from your terminal for branch workspaces and reusable development environments.</p><a href="/md/">md documentation →</a></section>
<section><h2>Go Mode</h2><p>The separate Android shell and shared voice stack. Connect caic to native voice, notifications, and device integrations.</p><a href="https://docs.gomode.dev/">Go Mode documentation ↗</a></section>
</div>
</div>
