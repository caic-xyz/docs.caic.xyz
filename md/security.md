---
# security model: SSH isolation, Linux capabilities, sudo access, credential isolation, network restrictions, Tailscale
---

# Security

This page documents the security boundaries of md containers: what is isolated, what is shared, and how to restrict outbound network access.

## Network isolation

### Inbound: 127.0.0.1 only

All container ports are bound to `127.0.0.1`, never `0.0.0.0`. SSH and VNC are only accessible from the host machine, not from other machines on your network. The host port is randomly assigned on each start.

```bash
$ md list
Container          Status     Repos           Uptime  Features
--------------------------------------------------------------
md-myrepo-main     running    myrepo:main     47m40s  display
$ grep Port ~/.ssh/config.d/md-myrepo-main.conf
  Port 54321
```

### Outbound: unrestricted by default

The container uses Docker's default bridge network, which allows full outbound internet access. This is intentional: AI coding agents need to install packages, clone repositories, call APIs, and access documentation.

### Restricting outbound access

For sensitive workloads, two approaches are available:

**Tailscale ACLs**: when the container is connected via `--tailscale`, outbound access can be controlled through Tailscale ACL policies. See [Tailscale](./tailscale) for setup.

**Docker network restrictions**: pass `--docker-flag` to `md start` for Docker-level network controls. For example, to block all outbound traffic:

```bash
docker network create --internal restricted
md start --docker-flag='--network restricted'
```

This blocks outbound routing at the Docker level. SSH access still works (host to container via the mapped port), but the container cannot reach the internet.

## SSH security

### Key architecture

md manages two SSH key pairs, automatically generated on first use:

| Key | Location | Purpose |
|---|---|---|
| **User key** | `~/.ssh/md` | Client identity: authenticates from host to container |
| **Host key** | `~/.config/md/ssh_host_ed25519_key` | Server identity: the container's SSH host key |

Both are ed25519 keys. The user public key is baked into the container image as `authorized_keys`. The host key is baked in so the container always presents the same identity.

### Authentication

Each container gets a dedicated SSH configuration at `~/.ssh/config.d/<container-name>.conf`:

```
Host md-myrepo-main
  HostName 127.0.0.1
  Port 54321
  User user
  IdentityFile ~/.ssh/md
  IdentitiesOnly yes
  UserKnownHostsFile ~/.ssh/config.d/md-myrepo-main.known_hosts
  StrictHostKeyChecking yes
  PreferredAuthentications publickey
```

Only the md-user key is accepted. Password authentication is disabled.

### Host key trust

Each container gets its own `known_hosts` file with the host key pinned to `[127.0.0.1]:<port>`. `StrictHostKeyChecking` is enabled: SSH refuses connection if the host key changes (which would happen if the container was purged and recreated with new keys; delete the `known_hosts` file to re-establish trust).

## Linux capabilities

Docker containers run with restricted capabilities by default. md adds only the minimum needed:

| Capability | Why | Risk |
|---|---|---|
| `SYS_PTRACE` | strace, gdb, delve, lldb | Scoped to container PID namespace: cannot attach to host processes |
| `seccomp=unconfined` | Chrome sandbox, strace, bpf | Does **not** grant capabilities: only removes syscall allowlist |
| `apparmor=unconfined` (Docker only) | Chrome namespace creation | Container-scoped |
| `NET_ADMIN`, `NET_RAW` (with `--tailscale`) | TUN device for Tailscale (plus `--device=/dev/net/tun`) | Required for Tailscale to function |
| `SYS_ADMIN` (with `--sudo`) | Root access, `/dev/fuse` | Grants full root within the container; for rootless Podman fuse mounts |

What is **not** added:
- `--privileged` is never used
- No host network mode (`--network host`)
- No host PID or IPC namespace sharing
- No Docker socket access

## Sudo access

When `--sudo` is passed, md generates a random password per container and configures `sudo` to accept it. The password is never baked into the image or stored on disk inside the container. It is stored as a Docker label on the container, so each container gets a unique, ephemeral credential.

```bash
md start --sudo
md sudo-password   # prints the container's random password
```

The password grants root **within the container's user namespace only**. It does not grant host root, and it is useless if the container is destroyed and recreated (a new password is generated). This avoids shipping a shared or static root credential in the image while still letting agents or CI scripts escalate when needed.

Running rootless Podman inside the container (nested containers) requires `--sudo` for the `SYS_ADMIN` capability and `/dev/fuse`, and your host must run a rootful Docker or Podman daemon. Rootless Docker or Podman hosts cannot supply the nested capabilities and are not supported for this use.

## Credential isolation

### What the container does NOT have access to

- Your host SSH keys: the container has its own generated key pair
- Your host `.gitconfig`: the container gets a template
- Your GitHub credentials: unless you use `--github` or `gh auth login` inside the container
- Your host environment variables: only `GITHUB_TOKEN` (with `--github`) and variables from `.env` files

### API keys

API keys for AI providers (Anthropic, OpenAI, Google, etc.) are injected via `.env` files or `~/.config/md/env`. These are read at startup and sent over the SSH channel to `/home/user/.env` inside the container.

Since the SSH channel is encrypted and goes through `127.0.0.1`, keys never traverse the network.

### Docker build secrets

When building images locally (`md build-image`), the `GITHUB_TOKEN` is passed as a Docker build secret, preventing it from appearing in image layers or build logs.

## Filesystem isolation

### What is shared with the host

- **Agent config directories**: bind-mounted read-write (e.g. `~/.claude`, `~/.config/opencode`)
- **Build caches**: baked into image at build time (one-way copy, not live-mount)
- **`/etc/localtime`**: bind-mounted read-only (timezone sync, on Linux, macOS, and Windows)
- **`/dev/bus/usb`**: with `--usb` flag (Linux only)

### What is NOT shared

- The host git checkout: the container has its own clone
- Home directory contents other than agent config paths
- `/proc`, `/sys`, `/dev` (container has its own namespaces)
- Docker socket

## Tailscale

Tailscale networking, including ephemeral vs. browser-authenticated nodes, ACL policy, and cleanup, is documented in [Tailscale](./tailscale).
