---
increment: 0595-help-skill-discovery
---

# Architecture Plan

## Approach

Single SKILL.md file — no phases, no TypeScript, no CLI changes. The skill is a prompt that instructs the AI to gather context via CLI commands and display organized help output.

## Components

1. **SKILL.md** (`plugins/specweave/skills/help/SKILL.md`) — Prompt-based skill with frontmatter. Gathers context via `specweave status --json` and `specweave analytics --since 30d --json`, then formats output by workflow stage.

2. **Plugin registration** — Add `"help"` to `plugin.json` provides.skills array.

3. **Doc fixes** — Replace "framework" with "tool"/"SpecWeave" in 4 critical doc files. Preserve legitimate tech stack framework references.

4. **Help docs page** (`docs/commands/help.md`) — New page documenting the command.

## Key Decisions

- **No CLI command**: The skill IS the help. No `specweave help` binary command needed.
- **No phases**: Output-only skill, single SKILL.md is sufficient.
- **Graceful degradation**: If analytics/status commands fail, skip those sections silently.
