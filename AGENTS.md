# AGENTS.md — Documentation generation guide

The documentation website at [docs.caic.xyz](https://docs.caic.xyz) serves **end users** of [caic](https://github.com/caic-xyz/caic) and [md](https://github.com/caic-xyz/md). It is built with [VitePress](https://vitepress.dev/) and deployed to Cloudflare Pages.

## Audience and scope

Everything in these docs targets **end users** — people installing, configuring, and using caic and md. Write for someone who wants to get things done, not for someone reading the source code.

### In scope

- Features and how to use them
- Configuration options and their effects
- Workflows and patterns (multi-repo, fork, CI)
- Troubleshooting common issues
- Architecture at a level that helps users understand behavior (image layers, build triggers, container lifecycle)
- Security boundaries that affect user decisions (what's isolated, what's shared, how to restrict)

### Out of scope

- Internal implementation details: function names, file paths within the source tree, Go types, internal label keys
- Build system internals: CI workflow file names, Dockerfile paths, setup script numbering
- Developer documentation: how to contribute, how to run tests, how the code is structured
- Speculation about future features

### Anti-patterns

These are things that look reasonable but don't belong in end-user docs. When in doubt, ask: "Would a user need to know this to use the tool?"

| Instead of this... | ...do this |
|---|---|
| "`imageBuildNeeded()` in `docker.go` checks..." | "md checks whether the image needs rebuilding." |
| "We chose the COPY approach over `docker cp` because..." | Just describe the current behavior. Users don't need the decision history. |
| A table with `~/.claude, ~/.codex, etc.` that looks exhaustive | Either list everything, or write prose and link to the full list. |
| "`md.base_digest` label stores the..." | Users don't care about image labels. Describe the _trigger_ ("rebuilds when the image changes"), not the _mechanism_. |
| Dockerfile examples with `LABEL md.cache_key=...` lines | Show only the parts that explain what's added (SSH keys, caches). Drop tracking labels. |
| "per-user layer", "on top of the base" | "host-specific layer", "on top of the `md-user` image". Prefer specific names. |

## What goes where

Each page has a distinct purpose. Before writing, pick the right one.

| Page | Purpose | Good for | Not for |
|---|---|---|---|
| **index.md** | Landing page, elevator pitch, doc index | Quick start, problem statement, link to all pages | Any detailed content |
| **commands.md** | Reference for every flag and subcommand | Tables, flag lists, one-line examples | Long-form explanations of how features work internally |
| **configuration.md** | What users can configure and where files live | Env vars, cache tables, agent config paths | Architecture diagrams, design rationale |
| **installation.md** | How to install and verify | Prerequisites, platform notes, upgrade steps | Post-install usage |
| **harnesses.md** | Agent-specific setup | Config file paths, symlink recipes, Claude Code settings | General architecture |
| **preinstalled-tools.md** | Reference inventory of container contents | What's available inside the container | How things are installed |
| **tailscale.md** | Tailscale setup and usage | ACL config, SSH over tailnet, cleanup | General networking security |
| **architecture.md** | How the system is structured at a high level | Image layers, startup flow, container lifecycle | Design rationale (that's design.md) |
| **design.md** | Why things work the way they do | Cache injection strategy, rebuild logic, env injection chain | What the commands are (that's commands.md) |
| **security.md** | Security model and boundaries | Isolation, capabilities, credential handling, outbound restrictions | Tailscale setup (that's tailscale.md) |

## Last synced

The docs were last reconciled against these upstream commits. When updating, review the upstream log since these hashes (`git log <hash>..HEAD`) to focus only on the delta. Update this block after each sync.

| Repo | Tag | Commit | Date |
|---|---|---|---|
| caic | `v0.11.0` | `74f06f35` | 2026-07-20 |
| md | `post-v0.18.0` | `cdd03c6` | 2026-09-14 |

## Source of truth

Always read the upstream source files before writing or updating documentation. Extract user-facing information — ignore implementation details.

| Doc section | Upstream source | What to extract |
|---|---|---|
| `caic/*` | `/home/user/src/caic/README.md`, `AGENTS.md` | Feature descriptions, install steps, workflows |
| `md/*` | `/home/user/src/md/README.md`, `AGENTS.md` | Same — user-facing features and behavior |
| `md/commands.md` | `/home/user/src/md/cmd/md/main.go` | CLI flags, defaults, help text. Not the Go implementation. |
| `md/configuration.md` | `/home/user/src/md/AGENTS.md` | Cache injection behavior, shell env, Chrome config. Not build labels. |
| `md/harnesses.md` | `/home/user/src/md/AGENTS.md` | Agent list, config paths, skills directories |
| `md/security.md` | `/home/user/src/md/docs/NETWORKING.md`, `/home/user/src/md/AGENTS.md` | Capabilities, isolation model, outbound restriction options |
| `md/preinstalled-tools.md` | `/home/user/src/md/rsc/user/home/user/src/AGENTS.md` | Tool inventory and categories |
| `md/design.md` | `/home/user/src/md/AGENTS.md` | Design decisions explained in user terms, not code terms |

These paths assume the projects are checked out under `/home/user/src/`.

When writing user-facing pages, reference static resources (config templates, Dockerfiles, tool lists) with GitHub permalinks, not local filesystem paths. For example, `https://github.com/caic-xyz/md/blob/main/rsc/user/home/user/src/AGENTS.md` for `/home/user/src/AGENTS.md`.

## Conventions

### Frontmatter

Only the home page (`index.md`) uses VitePress frontmatter (`layout: home`). All other pages are plain markdown.

### Headings

- Each page starts with a single `# H1` matching the page title
- Use `##` for major sections, `###` for subsections
- Do not use H4 or deeper

### Links

- Cross-links between pages use relative paths without `.md` extension: `[Commands](./commands)`, `[md](../md/)`
- External links use full URLs

### Code blocks

Always specify the language: ` ```bash `, ` ```json `, ` ```go `, etc.

### Tables

Prefer pipe tables for reference material (env vars, commands, flags, options). Only use tables when the list is exhaustive — a partial table with "etc." is misleading. If you can't list everything, use prose and link to the full reference.

### Writing style

- Be concise. Users are reading to solve a problem, not to appreciate prose.
- Use "you" and "your" — speak directly to the user.
- Prefer concrete examples over abstract descriptions.
- Explain *why* a feature exists or a choice was made when it helps the user understand behavior.
- Never reference source files, function names, or internal types.
- Cross-link to related pages rather than duplicating content.
- Use specific, concrete terms: write "`md-user` image", not "the base". Write "host-specific layer", not "per-user layer".
- **Do not use em-dashes or hyphens to separate clauses in prose.** Write two sentences instead of joining them with `—`.
- **Do not overwrite user-authored content.** When editing existing pages, change only what was asked. Preserve example values, phrasing, and structure unless explicitly told to replace them.

## Adding a new page

1. Create the markdown file in the appropriate directory (`caic/` or `md/`)
2. Add it to the sidebar in `.vitepress/config.ts` under the correct section
3. Link to it from the relevant overview page (`index.md`)
4. Run `python3 scripts/update_agents_file_index.py` to update the file index below

## Updating the sidebar

The sidebar is defined in `.vitepress/config.ts`. When adding a page, add an entry to the `items` array for the corresponding section:

```ts
{ text: 'Page Title', link: '/md/page-name' }
```

## Build

```bash
pnpm install
pnpm run build    # output: .vitepress/dist/
pnpm run dev      # local dev server
```

## Deploy

Deployed automatically to Cloudflare Pages on push. To deploy manually:

```bash
pnpm run build
wrangler pages deploy
```

## Pre-publish checklist

**The build must pass (`pnpm run build`) before any change is committed or deployed.** No exceptions.

Before considering a doc change done, verify:

- [ ] No source file paths (`.go`, `.py`, `.ts`) in user-facing pages
- [ ] No function names, Go types, or internal label keys
- [ ] No descriptions of rejected alternatives or implementation history
- [ ] Tables are exhaustive or replaced with prose + link
- [ ] Dockerfile examples show only end-user-relevant lines (SSH keys, caches, not LABEL)
- [ ] Cross-links use relative paths without `.md` extension
- [ ] Content is in the right page per the "What goes where" table
- [ ] `pnpm run build` succeeds
- [ ] `python3 scripts/update_agents_file_index.py` has been run

<!-- BEGIN FILE INDEX -->
## File Index

Autogenerated from first-line comments. Run scripts/update_agents_file_index.py to refresh.

- `.vitepress/config.ts`: VitePress site configuration.
- `.vitepress/theme/index.ts`: VitePress theme with medium-zoom and Asciinema player.
- `README.md`: docs.caic.xyz
- `caic/android.md`: Android App
- `caic/architecture.md`: caic architecture: system components, container model, relay, task lifecycle, startup/adoption, forge/CI, SSE streaming, WebRTC voice, API design
- `caic/configuration.md`: Configuration file reference: config.toml sections, keys, defaults, and environment variables
- `caic/design.md`: design rationale: relay, container-per-task, Go+SolidJS, sessions, adoption, task model, config watching
- `caic/github.md`: GitHub Integration: PAT, OAuth, and GitHub App setup for PRs, CI monitoring, and webhooks
- `caic/gitlab.md`: GitLab Integration: PAT and OAuth setup for MRs, CI monitoring, and webhooks
- `caic/index.md`: caic
- `caic/installation.md`: Installation
- `caic/mcp.md`: MCP Server
- `caic/security.md`: security model: authentication, forge tokens, GitHub token injection, sudo access, IP geo, webhooks, SSH isolation, container sandbox, secret scanning, voice security
- `caic/voice.md`: Voice
- `index.md`: docs.caic.xyz
- `md/architecture.md`: md image hierarchy, build pipeline, container lifecycle, submodule handling, startup flow
- `md/commands.md`: CLI reference: start, run, fork, pull, push, diff, build-image, prune, cache flags, VNC
- `md/configuration.md`: environment variables, agent config mounts, build cache injection, cache names and paths
- `md/design.md`: design rationale: why generated Dockerfile, rebuild triggers, cache injection, env injection, agent mounts
- `md/harnesses.md`: AI coding agent harnesses: Claude Code, Codex, Pi, Qwen, Kilo, OpenCode, Goose, Kimi, Amp
- `md/index.md`: branch-locked containers for AI coding agents
- `md/installation.md`: prerequisites, curl install, from source, platform notes, verification, upgrade, uninstall
- `md/preinstalled-tools.md`: preinstalled tools inventory: languages, editors, debuggers, browsers, AI agents, package managers
- `md/security.md`: security model: SSH isolation, Linux capabilities, sudo access, credential isolation, network restrictions, Tailscale
- `md/tailscale.md`: Tailscale networking inside containers: SSH over tailnet, VNC, HTTPS, ACL policy, ephemeral nodes
- `pnpm-workspace.yaml`: pnpm allowed build scripts for pnpm v11.
- `scripts/record-demo.py`: Record a quick-start asciinema demo for md.
- `scripts/update-screenshots.sh`: Update documentation screenshots from caic.
- `scripts/update_agents_file_index.py`: Update AGENTS.md files (containing a file index marker) with an auto-generated index.
<!-- END FILE INDEX -->
