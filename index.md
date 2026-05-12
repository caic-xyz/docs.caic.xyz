---
# docs.caic.xyz
layout: home

hero:
  name: caic.xyz
  tagline: AI coding agents in isolated containers
  actions:
    - theme: brand
      text: Get started with caic
      link: /caic/
    - theme: brand
      text: Get started with md
      link: /md/

features:
  - title: Install
    details: "curl -fsSL https://caic.xyz/install.sh | bash"
  - title: caic
    details: Server that manages multiple AI coding agents running in parallel in isolated Docker containers. Access from phone, web UI, or Android app.
    link: /caic/
  - title: md
    details: CLI that creates branch-locked containers for AI agents. Safe parallel work across multiple branches without conflicts. Powers caic.
    link: /md/
---

## caic

Manage multiple AI coding agents in parallel from a single web UI. Each task runs in its own isolated container — create, monitor, and interact with agents in real time.

![caic web UI showing an agent working on a task](/screenshots/task-detail.webp)

## md in 30 seconds

md creates branch-locked containers so agents can work safely without touching your local checkout.

<AsciinemaPlayer src="/md-quickstart.cast" />

[md on GitHub →](https://github.com/caic-xyz/md)

## Join the community

[Join us on Discord](https://discord.gg/caic) — get help, share feedback, and follow development.
