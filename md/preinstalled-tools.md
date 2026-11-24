---
# preinstalled tools inventory: languages, editors, debuggers, browsers, AI agents, package managers
---

# Preinstalled Tools

Every md container ships with a curated set of development tools, pre-configured and ready to use. The full inventory is available at `/home/user/src/tool_versions.md` inside the container, generated at image build time.

## Core utilities

bash, git, curl, wget, rsync, jq, grep, ripgrep, less, man, file, find, xargs, sed, awk, col, bubblewrap, inotifywait, `/usr/bin/time` (GNU time), xvfb, tmux, tokei, xxd, sudo

## Editors

nvim (vi, vim, vimdiff)

## Browsers

google-chrome (amd64), chromium (arm64 fallback), chrome-devtools-mcp

## Languages & runtimes

| Language   | Toolchain                                                                          |
| ---------- | ---------------------------------------------------------------------------------- |
| Go         | `go`, `gofmt` (latest stable)                                                      |
| Node.js    | `node` (v26 via nvm), `npm`, `npx`, standalone `pnpm` in `~/.local/share/pnpm/bin` |
| TypeScript | `tsc`, `tsx`, `eslint`                                                             |
| Rust       | `rustc`, `cargo`, `rustup`, `cargo-binstall`                                       |
| Python     | `python3`, `uv`, `pylint`, `ruff`                                                  |
| Java       | `java` (JDK 21, headless)                                                          |
| R          | `R`                                                                                |

## Package managers

`npm`, `pnpm` (standalone), `bun`, `pip` (via uv), `cargo`

## Build tools

build-essential, cmake, ninja-build, ccache, make, gcc, g++, arm-linux-gnueabi-gcc, gettext (`msgfmt`), gradle, golangci-lint, actionlint, shellcheck, shfmt, libsodium-dev, protobuf-compiler, cargo-binstall, pylint, ruff, uv, asciinema

## AI coding agents

| Agent            | Binary          |
| ---------------- | --------------- |
| Antigravity      | `agy`           |
| Claude Code      | `claude`        |
| Codex            | `codex`         |
| DeepSeek Harness | `dsh`           |
| Kilo Code        | `kilo`          |
| OpenCode         | `opencode`      |
| Amp CLI          | `amp`           |
| Pi               | `pi`            |
| Qwen Code        | `qwen`          |
| Kimi             | `kimi`          |
| Agent Browser    | `agent-browser` |

## Containers

podman (rootless inside the container)

## Virtualization

qemu-kvm, libvirt-clients, libguestfs-tools (`guestfish`, `guestmount`, `virt-inspector`)

## Android

android-sdk, gradle, adb, sdkmanager

## Database

sqlite3

## Debugging & profiling

binwalk, strace, lsof, dlv (Go debugger), lldb / rust-lldb, objdump, aarch64-linux-gnu-objdump, arm-linux-gnueabi-objdump, radare2 (r2)

## Networking

curl, wget, net-tools, iproute2, ping, fping, traceroute, tcptraceroute, nmap, tcpdump, dig, host, nslookup, whois, sshpass, tailscale

## GitHub

`gh` CLI

## Compression & media

brotli, zstd, unzip, ffmpeg, imagemagick, GStreamer and WebKitGTK runtime libraries

## 3D libraries

3MF, CGAL, Eigen, Boost, TBB, MPFR, double-conversion, and libzip

## Embedded

flex, bison, gperf, dfu-util, libusb-1.0-0, pahole (dwarves), libelf-dev

## Math

bc

## Version report

The exact versions of every tool are captured at image build time:

```bash
# Inside the container
cat ~/src/tool_versions.md
```

This is regenerated whenever the `md-user` image is rebuilt: weekly for `:latest`, on-demand with `md build-image`.
