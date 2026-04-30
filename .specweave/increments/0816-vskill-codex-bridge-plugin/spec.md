# Spec: vskill `codex-bridge` plugin (dual-manifest)

## Background

OpenAI Codex (the agentic coding CLI) shipped a plugin/skill system in late 2025 with conventions deliberately near-identical to Anthropic Claude Code's: `SKILL.md` with YAML frontmatter, `.codex-plugin/plugin.json` (vs `.claude-plugin/plugin.json`), `AGENTS.md` (vs `CLAUDE.md`). Within four months, 32+ tools (Claude Code, Codex, Cursor, Windsurf, Copilot, Gemini CLI, Replit, Devin, Zed) adopted the Anthropic Agent Skills open spec.

vskill is already multi-agent aware at the **installer** layer (it knows about `codex` and `cursor` and emits to `.codex/skills/` and `.cursor/skills/`), but its **marketplace** ships only `.claude-plugin/marketplace.json`. A Codex user running `codex plugin marketplace add anton-abyzov/vskill` finds nothing, because Codex looks for `.agents/plugins/marketplace.json`. None of the 8 existing plugins ship a `.codex-plugin/plugin.json` either.

This increment ships **one demonstrator plugin** that proves the dual-manifest pattern end-to-end and establishes the authoring template for future plugins.

## User Stories

### US-001: Author a cross-runtime plugin
**Project**: vskill

**As a** vskill plugin author
**I want** a documented dual-manifest pattern (`.claude-plugin/` + `.codex-plugin/` + cross-compatible `SKILL.md`)
**So that** my plugin works in both Claude Code and OpenAI Codex without forking the skill source

**Acceptance Criteria**:
- [x] **AC-US1-01**: A new plugin directory `plugins/codex-bridge/` exists in the vskill repo with `.claude-plugin/plugin.json` and `.codex-plugin/plugin.json` manifests
- [x] **AC-US1-02**: The plugin contains one demo skill (`agents-md-author`) whose `SKILL.md` frontmatter has ONLY `name` + `description` (Codex strict-mode compatible, also valid for Claude Code)
- [x] **AC-US1-03**: The `.codex-plugin/plugin.json` schema conforms to OpenAI's published spec at developers.openai.com/codex/plugins/build (kebab-case `name`, semver `version`, `skills[]` array, optional `interface{}`)
- [x] **AC-US1-04**: A `README.md` in the plugin root documents the dual-target authoring pattern with concrete file-layout reference and the strict-mode frontmatter rule

### US-002: Install in both runtimes
**Project**: vskill

**As a** Claude Code or Codex user
**I want** to install `codex-bridge` via my native CLI
**So that** I can use the `agents-md-author` skill regardless of which runtime I prefer

**Acceptance Criteria**:
- [x] **AC-US2-01**: `npx vskill install --plugin-dir <vskill> --plugin codex-bridge -y` materializes `.claude/skills/codex-bridge/agents-md-author/SKILL.md` and `.codex/skills/codex-bridge/agents-md-author/SKILL.md` in a fresh project (15 agents covered)
- [x] **AC-US2-02**: `codex plugin marketplace add <local vskill path>` discovers `codex-bridge` via the new `.agents/plugins/marketplace.json` at the vskill repo root (registers `[marketplaces.vskill]` in ~/.codex/config.toml)
- [x] **AC-US2-03**: Equivalent cache evidence — `[marketplaces.vskill]` entry in ~/.codex/config.toml with `source_type = "local"`, mirroring the shape of `[marketplaces.openai-bundled]`. Plus: `codex exec` with the plugin enabled successfully ran the skill end-to-end
- [x] **AC-US2-04**: SKILL.md content is byte-identical between `.claude/skills/codex-bridge/agents-md-author/SKILL.md` and `.codex/skills/codex-bridge/agents-md-author/SKILL.md` (verified by `diff -q` returning empty)

### US-003: Marketplace registry integrity
**Project**: vskill

**As a** vskill maintainer
**I want** the new plugin registered in both marketplaces (`.claude-plugin/marketplace.json` + new `.agents/plugins/marketplace.json`)
**So that** it appears in `vskill list` / `codex plugin marketplace` discovery without breaking existing 8 plugins

**Acceptance Criteria**:
- [x] **AC-US3-01**: `.claude-plugin/marketplace.json` `plugins[]` length is 9 (was 8) and includes a `codex-bridge` entry with kebab-case name, semver version, source `./plugins/codex-bridge`, and category `development`
- [x] **AC-US3-02**: A new top-level `.agents/plugins/marketplace.json` exists at the vskill repo root with exactly one plugin entry pointing to `./plugins/codex-bridge`
- [x] **AC-US3-03**: Existing 8 plugins still install successfully via vskill (no regression — `skills` plugin still installs `scout/SKILL.md` cleanly to .claude/skills/skills/scout/SKILL.md)

## Non-Goals (Follow-up Increments)

- Migrating the existing 8 plugins to dual-manifest
- Adding a `vskill --target codex|claude|both` runtime feature that auto-emits the dual layout
- Publishing `codex-bridge` to verified-skill.com (separate publish flow once approved)
- Adding `.app.json` (App connectors) or `hooks.json` to the demo plugin

## Test Plan Summary

End-to-end install verification in `/tmp/codex-bridge-test/` covering:
- Test A: vskill install lands in both `.claude/` and `.codex/`
- Test B: `codex plugin marketplace add` discovers and caches the plugin
- Test C: SKILL.md frontmatter is strict-mode (only `name` + `description`)
- Test D: `.codex-plugin/plugin.json` conforms to OpenAI's published schema
- Test E: vskill marketplace registry has 9 plugins; Codex marketplace has 1
- Test F: cleanup tmpdir + Codex marketplace
