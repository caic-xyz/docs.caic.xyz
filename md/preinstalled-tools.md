<!-- preinstalled tools inventory: languages, editors, debuggers, browsers, AI agents, package managers -->
# Preinstalled Tools

Every md container ships with a curated set of development tools, pre-configured and ready to use. The full inventory is available at `/home/user/src/tool_versions.md` inside the container, generated at image build time.

## Core utilities

bash, git, curl, wget, rsync, jq, grep, ripgrep, less, file, find, xargs, sed, awk, bubblewrap, xvfb, tokei, xxd

## Editors

nvim (vi, vim, vimdiff)

## Browsers

google-chrome (amd64), chromium (arm64 fallback), chrome-devtools-mcp

## Languages & runtimes

| Language | Toolchain |
|---|---|
| Go | `go`, `gofmt` (latest stable) |
| Node.js | `node` (v24 via nvm), `npm`, `npx` |
| TypeScript | `tsc`, `tsx`, `eslint` |
| Rust | `rustc`, `cargo`, `rustup`, `cargo-binstall` |
| Python | `python3`, `uv`, `pylint`, `ruff` |
| Java | `java` (JRE) |
| R | `R` |

## Package managers

`npm`, `pnpm`, `bun`, `pip` (via uv), `cargo`

## Build tools

cmake, ninja-build, ccache, make, gcc, g++, gradle, maven, golangci-lint, actionlint, shellcheck, shfmt

## AI coding agents

| Agent | Binary |
|---|---|
| Claude Code | `claude` |
| Codex | `codex` |
| Gemini CLI | `gemini` |
| Kilo Code | `kilo` |
| OpenCode | `opencode` |
| Amp CLI | `amp` |
| Pi | `pi` |
| Qwen Code | `qwen-code` |

## Containers

podman (rootless inside the container)

## Virtualization

qemu-kvm, libvirt-clients

## Android

android-sdk, gradle, adb, sdkmanager

## Debugging & profiling

strace, lsof, dlv (Go debugger), lldb / rust-lldb, objdump, radare2 (r2)

## Networking

curl, wget, net-tools, iproute2, nmap, dig, host, nslookup, whois, tailscale

## GitHub

`gh` CLI

## Compression & media

brotli, zstd, unzip, ffmpeg, imagemagick

## Embedded

flex, bison, gperf, dfu-util, libusb-1.0-0

## Version report

The exact versions of every tool are captured at image build time:

```bash
# Inside the container
cat ~/src/tool_versions.md
```

This is regenerated whenever the `md-user` image is rebuilt: weekly for `:latest`, on-demand with `md build-image`.
