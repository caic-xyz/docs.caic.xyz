# Go Mode on Android

[Go Mode](https://gomode.dev/) is a separate Android shell for backend-hosted applications. Connect it to your caic server to use the same caic web frontend with native voice, notifications, screenshot capture, passkeys, and supported device integrations.

caic owns the task list, conversation, diffs, and widgets. Go Mode owns the native shell and its settings. See the [Go Mode Android guide](https://docs.gomode.dev/guide/android) for installation and native controls.

## Connect to caic

1. Make the caic server reachable from your phone. A private tailnet with [Tailscale Serve](./configuration#tailscale-serve-private-tailnet-only) is one option.
2. Open Go Mode settings and add your caic service URL, such as `https://caic.example.com`.
3. Open the service. The shell loads the caic web frontend and checks the service's Go Mode discovery manifest.

Native MCP-backed features depend on compatible service discovery and authentication. The web frontend can still load when compatibility checks fail. Read the [host integration guide](https://docs.gomode.dev/guide/host) if you are diagnosing compatibility.

## Use the hosted task UI

<figure class="docs-figure docs-figure--phone">
  <img class="docs-screenshot" src="/screenshots/frontend/mobile/overview.webp" alt="Mobile caic task list with concurrent agents and repository groups" width="390" height="844" loading="lazy" decoding="async">
  <figcaption>caic provides the task UI in mobile browsers and the Go Mode shell.</figcaption>
</figure>

Create, follow, and review tasks as described in [Task workflow](./tasks). Native notifications can report tasks that finish, need input, or become blocked. For hands-free task control, configure [caic voice](./voice) and follow the [Go Mode voice guide](https://docs.gomode.dev/guide/voice).

## Troubleshooting

- If the page cannot load, verify the service URL, network access, HTTPS, and caic's incoming origin allowlist.
- If the page loads but native features are unavailable, inspect discovery compatibility and MCP authentication.
- If voice cannot connect, confirm that caic advertises a gateway and that its signaling and UDP traffic are reachable.

See [Go Mode troubleshooting](https://docs.gomode.dev/guide/troubleshooting) for native shell diagnostics. Configure caic's authentication and network exposure in [Configuration](./configuration).
