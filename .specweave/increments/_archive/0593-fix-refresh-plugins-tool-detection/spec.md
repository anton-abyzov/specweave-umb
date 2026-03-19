---
increment: 0593-fix-refresh-plugins-tool-detection
title: Fix refresh-plugins to detect project AI tool
type: bug
priority: P1
status: completed
created: 2026-03-19T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Fix refresh-plugins to detect project AI tool

## Overview

`specweave refresh-plugins` always prioritizes Claude CLI when globally available, ignoring the project's configured AI tool adapter. When a user has Claude CLI installed globally but their project uses OpenCode, Cursor, Windsurf, or another AI tool (stored in `config.adapters.default`), plugins are incorrectly installed via `claude plugin install` or copied to `.claude/skills/` instead of the correct tool-specific directory (e.g., `.opencode/skills/`, `.cursor/skills/`).

The adapter infrastructure already exists — `init` stores the adapter in `config.adapters.default`, each adapter has a `compilePlugin()` method and knows its skills directory — but `refresh-plugins` never reads the config or uses the adapter system.

## Root Cause

1. `refresh-plugins.ts` (line 119-125): Only calls `detectClaudeCli()`, never reads `config.adapters.default` from `.specweave/config.json`
2. `plugin-copier.ts` (line 658): `copyPluginSkillsToProject()` hardcodes `.claude/skills/` as the target directory
3. Claude-specific operations (`enablePluginsInSettings`, `cleanupStalePlugins`, `migrateUserLevelPlugins`) run unconditionally regardless of adapter

## User Stories

### US-001: Adapter-aware plugin installation (P1)
**Project**: specweave

**As a** developer using a non-Claude AI tool (e.g., OpenCode, Cursor, Windsurf)
**I want** `specweave refresh-plugins` to detect my project's configured adapter and install plugins to the correct tool-specific directory
**So that** my AI tool can discover and use SpecWeave skills without manual file copying

**Acceptance Criteria**:
- [x] **AC-US1-01**: When `config.adapters.default` is set to a non-Claude adapter (e.g., `opencode`), `refresh-plugins` copies skills to that adapter's skills directory (e.g., `.opencode/skills/`) instead of `.claude/skills/`
- [x] **AC-US1-02**: When `config.adapters.default` is `claude` or unset, `refresh-plugins` uses native `claude plugin install` if CLI is available, falling back to `.claude/skills/` copy (existing behavior preserved)
- [x] **AC-US1-03**: When `config.adapters.default` is set to an adapter name not in the known mapping, `refresh-plugins` falls back to Claude behavior and logs a warning
- [x] **AC-US1-04**: The mode display message reflects the actual target tool and directory, not always "Claude CLI" or ".claude/skills/"
- [x] **AC-US1-05**: Claude-specific operations (`enablePluginsInSettings`, `cleanupStalePlugins`, `migrateUserLevelPlugins`) only execute when the adapter is `claude`

---

### US-002: Configurable skills target directory in copyPluginSkillsToProject (P1)
**Project**: specweave

**As a** developer maintaining the plugin-copier module
**I want** `copyPluginSkillsToProject()` to accept a configurable target skills directory
**So that** it can write skills to any adapter's directory, not just `.claude/skills/`

**Acceptance Criteria**:
- [x] **AC-US2-01**: `copyPluginSkillsToProject()` accepts an optional `targetSkillsDir` parameter that overrides the default `.claude/skills/` path
- [x] **AC-US2-02**: When `targetSkillsDir` is provided, skills are copied to `{projectRoot}/{targetSkillsDir}/{skillName}/SKILL.md` with all subdirectories preserved
- [x] **AC-US2-03**: When `targetSkillsDir` is not provided, behavior is identical to current (`.claude/skills/`)
- [x] **AC-US2-04**: Hooks directory copying (`.claude/hooks/`) is only performed when the target is `.claude/skills/` (hooks are Claude-specific)

## Functional Requirements

### FR-001: Read adapter from project config
`refreshPluginsCommand()` must read `config.adapters.default` from `.specweave/config.json` via `readConfig()` before deciding the installation method. This replaces the current logic that only calls `detectClaudeCli()`.

### FR-002: Adapter-to-directory mapping
A static mapping from adapter name to skills directory, derived from existing adapter `compilePlugin()` implementations:

| Adapter | Skills Directory |
|---------|-----------------|
| `claude` (or unset) | Native CLI or `.claude/skills/` fallback |
| `cursor` | `.cursor/skills/` |
| `opencode` | `.opencode/skills/` |
| `windsurf` | `.windsurf/skills/` |
| `copilot` | `.github/skills/` |
| `cline` | `.cline/skills/` |
| `codex` | `.codex/skills/` |
| `aider` | `.aider/skills/` |
| `trae` | `.trae/skills/` |
| `zed` | `.zed/skills/` |
| `tabnine` | `.tabnine/skills/` |
| `kimi` | `.kimi/skills/` |
| `jetbrains` | `.junie/skills/` |
| `amazonq` | `.amazonq/skills/` |
| `continue` | `.continue/skills/` |
| `antigravity` | `.agent/skills/` |
| `generic` | `.agents/skills/` |

### FR-003: Claude-only operations gating
The following must only execute when adapter is `claude`:
- `enablePluginsInSettings()` (writes to `~/.claude/settings.json`)
- `cleanupStalePlugins()` (cleans Claude settings)
- `migrateUserLevelPlugins()` (Claude plugin scope migration)
- Hook file copying to `.claude/hooks/` in `copyPluginSkillsToProject()`
- `detectClaudeCli()` call (no need to probe for Claude CLI when not using it)

### FR-004: No Claude CLI for non-Claude adapters
When adapter is NOT `claude`, never call `claude plugin install` — always use direct file copy to the adapter's skills directory.

## Success Criteria

- All existing tests pass (no regression for Claude adapter path)
- `refresh-plugins` correctly targets the configured adapter's skills directory
- Unit tests cover: Claude default, explicit non-Claude adapter, missing/unknown adapter fallback, unset adapter

## Out of Scope

- Adapter auto-detection at refresh time (we read config, not re-detect)
- Hooks installation for non-Claude adapters (hooks are Claude-specific infrastructure)
- Changes to `specweave init` flow (adapter selection already works correctly there)
- Changes to adapter `compilePlugin()` methods (those are for `vskill install`, not bundled plugins)
- Gemini adapter (uses AGENTS.md compilation, no skills directory — not applicable to file-copy flow)

## Dependencies

- `config.adapters.default` field in `.specweave/config.json` (already exists, set by `specweave init`)
- `readConfig()` from `src/core/config/config-manager.ts` (already exists)
- Adapter skills directory conventions (already established in each adapter's `compilePlugin()` method)
