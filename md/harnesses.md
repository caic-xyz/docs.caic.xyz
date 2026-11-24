---
# AI coding agent harnesses: Claude Code, Codex, DeepSeek Harness, Pi, Qwen, Kilo, OpenCode, Goose, Kimi, Amp, Antigravity
---

# Harnesses

The container includes [`/home/user/src/AGENTS.md`](https://github.com/caic-xyz/md/blob/main/rsc/user/home/user/src/AGENTS.md) with information about preinstalled tools.

## Supported agents

| Agent                                                                                | Instruction file               | Host config mounted automatically |
| ------------------------------------------------------------------------------------ | ------------------------------ | --------------------------------- |
| [amp](https://ampcode.com/manual#AGENTS.md)                                          | `~/.config/amp/AGENTS.md`      | Yes                               |
| [claude](https://www.anthropic.com/engineering/claude-code-best-practices)           | `~/.claude/CLAUDE.md`          | Yes                               |
| [codex](https://developers.openai.com/codex/guides/agents-md/)                       | `~/.codex/AGENTS.md`           | Yes                               |
| [kilo](https://kilo.ai/docs/agent-behavior/custom-rules)                             | `~/.kilocode/rules/*.md`       | Yes                               |
| [opencode](https://opencode.ai/docs/rules/)                                          | `~/.config/opencode/AGENTS.md` | Yes                               |
| [pi](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/README.md) | `~/.pi/agent/AGENTS.md`        | Yes                               |
| [qwen](https://qwenlm.github.io/qwen-code-docs/en/users/configuration/settings/)     | `~/.qwen/QWEN.md`              | Yes                               |
| [goose](https://block.github.io/goose/docs/)                                         | `~/.config/goose/AGENTS.md`    | Yes                               |
| [kimi](https://github.com/MoonshotAI/kimi-cli)                                       | `~/.kimi/KIMI.md`              | Yes                               |

Antigravity is also available in specialized images through `agy`. md shares its host Gemini state at `~/.gemini`, which can contain credentials. This state is writable and shared with other applicable tasks. Antigravity integration in caic is experimental.

DeepSeek Harness is also available in specialized images through `dsh`. md shares its host data directory at `~/.dsh` and the shared `~/.agents` directory, so settings, credentials, plugins, and sessions persist across containers. This state is writable and shared with other applicable tasks. Run `dsh web` inside the container to launch its Web UI.

## Sharing the same AGENTS.md across harnesses

By default, each harness looks for its own config file (e.g. `~/.claude/CLAUDE.md`, `~/.pi/agent/AGENTS.md`). If you'd prefer a single AGENTS.md shared across all your agents, symlinks make this easy:

```bash
mkdir -p ~/.agents ~/.config/amp ~/.claude ~/.codex ~/.config/goose \
         ~/.kimi ~/.kilocode/rules ~/.config/opencode ~/.pi/agent ~/.qwen

echo "Read ~/AGENTS.md if present." >> ~/.agents/AGENTS.md
ln -s ../../.agents/AGENTS.md ~/.config/amp/AGENTS.md
ln -s ../.agents/AGENTS.md    ~/.claude/CLAUDE.md
ln -s ../.agents/AGENTS.md    ~/.codex/AGENTS.md
ln -s ../../.agents/AGENTS.md ~/.config/goose/AGENTS.md
ln -s ../.agents/AGENTS.md    ~/.kimi/KIMI.md
ln -s ../../.agents/AGENTS.md ~/.kilocode/rules/AGENTS.md
ln -s ../../.agents/AGENTS.md ~/.config/opencode/AGENTS.md
ln -s ../../.agents/AGENTS.md ~/.pi/agent/AGENTS.md
ln -s ../.agents/AGENTS.md    ~/.qwen/AGENTS.md
```

You can skip any harness you don't use. Each agent works fine with its own config file too: nothing requires symlinks.

## Sharing skills across harnesses

If you use multiple agents, you can share the same skills directory rather than copying skills into each harness's location:

```bash
mkdir -p ~/.agents/skills ~/.claude ~/.codex ~/.config/goose \
         ~/.kimi ~/.kilocode ~/.config/opencode ~/.pi/agent ~/.qwen

ln -s ../.agents/skills/                 ~/.claude/skills
ln -s ../.agents/skills/                 ~/.codex/skills
ln -s ../../.agents/skills/              ~/.config/goose/skills
ln -s ../.agents/skills/                 ~/.kimi/skills
ln -s ../.agents/skills/                 ~/.kilocode/skills
```

Again, none of this is required. Each harness looks in its own directory by default.

Skills locations by harness:

| Agent    | Skills path                                |
| -------- | ------------------------------------------ |
| amp      | `~/.agents/skills/**/SKILL.md`             |
| claude   | `~/.claude/skills/<name>/SKILL.md`         |
| codex    | `~/.codex/skills/**/SKILL.md`              |
| kilo     | `~/.kilocode/skills/<name>/SKILL.md`       |
| opencode | `~/.config/opencode/skill/<name>/SKILL.md` |
| pi       | `~/.pi/agent/skills/**/SKILL.md`           |
| qwen     | `~/.qwen/skills/<name>/SKILL.md`           |
| goose    | `~/.config/goose/skills/**/SKILL.md`       |
| kimi     | `~/.kimi/skills/<name>/SKILL.md`           |
