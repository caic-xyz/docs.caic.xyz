---
# AI coding agent harnesses: Claude Code, Codex, Gemini, Pi, Qwen, Kilo, OpenCode, Goose, Kimi, Amp
---

# Harnesses

The container includes [`/home/user/src/AGENTS.md`](https://github.com/caic-xyz/md/blob/main/rsc/user/home/user/src/AGENTS.md) with information about preinstalled tools.

## Supported agents

| Agent | Config file |
|---|---|
| [amp](https://ampcode.com/manual#AGENTS.md) | `~/.config/amp/AGENTS.md` |
| [claude](https://www.anthropic.com/engineering/claude-code-best-practices) | `~/.claude/CLAUDE.md` |
| [codex](https://developers.openai.com/codex/guides/agents-md/) | `~/.codex/AGENTS.md` |
| [gemini](https://geminicli.com/docs/cli/gemini-md/) | `~/.gemini/GEMINI.md` |
| [kilo](https://kilo.ai/docs/agent-behavior/custom-rules) | `~/.kilocode/rules/*.md` |
| [opencode](https://opencode.ai/docs/rules/) | `~/.config/opencode/AGENTS.md` |
| [pi](https://github.com/badlogic/pi-mono/blob/main/packages/coding-agent/README.md) | `~/.pi/agent/AGENTS.md` |
| [qwen](https://qwenlm.github.io/qwen-code-docs/en/users/configuration/settings/) | `~/.qwen/QWEN.md` |
| [goose](https://block.github.io/goose/docs/) | `~/.config/goose/AGENTS.md` |
| [kimi](https://github.com/MoonshotAI/kimi-cli) | `~/.kimi/KIMI.md` |

## Sharing the same AGENTS.md across harnesses

By default, each harness looks for its own config file (e.g. `~/.claude/CLAUDE.md`, `~/.pi/agent/AGENTS.md`). If you'd prefer a single AGENTS.md shared across all your agents, symlinks make this easy:

```bash
mkdir -p ~/.config/agents ~/.config/amp ~/.claude ~/.codex ~/.config/goose ~/.gemini \
         ~/.kimi ~/.kilocode/rules ~/.config/opencode ~/.pi/agent ~/.qwen

echo "Read ~/AGENTS.md if present." >> ~/.config/agents/AGENTS.md
ln -s ../../.config/agents/AGENTS.md ~/.config/amp/AGENTS.md
ln -s ../.config/agents/AGENTS.md    ~/.claude/CLAUDE.md
ln -s ../.config/agents/AGENTS.md    ~/.codex/AGENTS.md
ln -s ../.config/agents/AGENTS.md    ~/.config/goose/AGENTS.md
ln -s ../.config/agents/AGENTS.md    ~/.gemini/AGENTS.md
ln -s ../.config/agents/AGENTS.md    ~/.kimi/KIMI.md
ln -s ../../.config/agents/AGENTS.md ~/.kilocode/rules/AGENTS.md
ln -s ../../.config/agents/AGENTS.md ~/.config/opencode/AGENTS.md
ln -s ../../.config/agents/AGENTS.md ~/.pi/agent/AGENTS.md
ln -s ../.config/agents/AGENTS.md    ~/.qwen/AGENTS.md
```

You can skip any harness you don't use. Each agent works fine with its own config file too: nothing requires symlinks.

## Sharing skills across harnesses

If you use multiple agents, you can share the same skills directory rather than copying skills into each harness's location:

```bash
mkdir -p ~/.config/agents/skills ~/.claude ~/.codex ~/.config/goose \
         ~/.gemini/antigravity ~/.kimi ~/.kilocode ~/.config/opencode ~/.pi/agent ~/.qwen

ln -s ../.config/agents/skills/          ~/.claude/skills
ln -s ../.config/agents/skills/          ~/.codex/skills
ln -s ../.config/agents/skills/          ~/.config/goose/skills
ln -s ../../.config/agents/skills/       ~/.gemini/antigravity/skills
ln -s ../.config/agents/skills/          ~/.gemini/skills
ln -s ../.config/agents/skills/          ~/.kimi/skills
ln -s ../.config/agents/skills/          ~/.kilocode/skills
```

Again, none of this is required. Each harness looks in its own directory by default.

Skills locations by harness:

| Agent | Skills path |
|---|---|
| amp | `~/.config/agents/skills/**/SKILL.md` |
| claude | `~/.claude/skills/<name>/SKILL.md` |
| codex | `~/.codex/skills/**/SKILL.md` |
| gemini | `~/.gemini/skills/<name>/SKILL.md` |
| kilo | `~/.kilocode/skills/<name>/SKILL.md` |
| opencode | `~/.config/opencode/skill/<name>/SKILL.md` |
| pi | `~/.pi/agent/skills/**/SKILL.md` |
| qwen | `~/.qwen/skills/<name>/SKILL.md` |
| goose | `~/.config/goose/skills/**/SKILL.md` |
| kimi | `~/.kimi/skills/<name>/SKILL.md` |
