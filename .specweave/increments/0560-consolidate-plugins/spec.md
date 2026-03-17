---
increment: 0560-consolidate-plugins
title: Consolidate 8 Core Plugins into 1 Unified Plugin
type: feature
priority: P1
status: completed
created: 2026-03-17T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Consolidate 8 Core Plugins into 1 Unified Plugin

## Overview

Merge 7 satellite plugins (specweave-github, specweave-jira, specweave-ado, specweave-release, specweave-diagrams, specweave-media, specweave-docs) into the core `specweave` plugin. This is a **packaging refactor** — no new features, no behavior changes.

### Current State

8 separate plugin directories under `plugins/`, each registered independently in `marketplace.json`:

| Plugin | Marketplace Name | Skills | Commands | Lib Files |
|--------|-----------------|--------|----------|-----------|
| specweave (core) | `sw` | 28 | 29 | ~129 |
| specweave-github | `sw-github` | 4 | 10 | ~94 |
| specweave-jira | `sw-jira` | 3 | 11 | ~60 |
| specweave-ado | `sw-ado` | 4 | 11 | ~54 |
| specweave-release | `sw-release` | 1 | 5 | ~4 |
| specweave-diagrams | `sw-diagrams` | 1 | 1 | 0 |
| specweave-media | `sw-media` | 3 | 0 | 0 |
| specweave-docs | `docs` | 0 | 7 | 0 |

**Total**: 44 skills, 74 commands across 8 plugins, installed via 8 separate `claude plugin install` calls.

### Target State

1 unified plugin (`sw`) containing all 44 skills and 74 commands. Single install, single hash, single lockfile entry.

### Key Constraints

- **Option B**: All user-facing skill names (e.g., `sw-github:push`, `sw-jira:sync`, `sw-ado:status`) remain unchanged
- **Domain-prefixed collisions**: Commands with identical names across plugins (clone, close, create, pull, push, reconcile, status, sync, cleanup-duplicates) already use plugin namespace prefixes — these are preserved
- **Lockfile migration**: Users have per-plugin SHA entries in `plugins-lock.json` and per-project `vskill.lock` that must migrate to a single consolidated entry
- **Progressive loading**: PLUGINS-INDEX.md trigger-based lazy loading must continue working with the unified structure

---

## User Stories

### US-001: Plugin Directory Consolidation (P1)
**Project**: specweave

**As a** SpecWeave maintainer
**I want** all 7 satellite plugin directories merged into the core `specweave` plugin
**So that** there is a single source of truth for all bundled functionality, reducing maintenance overhead and simplifying the build/release process

**Acceptance Criteria**:
- [x] **AC-US1-01**: Skills from all 7 satellite plugins are moved into `plugins/specweave/skills/` with their existing directory names preserved (e.g., `github-sync/`, `jira-mapper/`, `ado-sync/`, `release-expert/`, `diagrams/`, `image/`, `video/`, `remotion/`)
- [x] **AC-US1-02**: Commands from all 7 satellite plugins are moved into `plugins/specweave/commands/` with domain-prefixed filenames to avoid collisions (e.g., `github-sync.md`, `jira-sync.md`, `ado-sync.md`)
- [x] **AC-US1-03**: Lib directories from specweave-github, specweave-jira, specweave-ado, and specweave-release are moved into `plugins/specweave/lib/integrations/` (github/, jira/, ado/) and `plugins/specweave/lib/features/` (release/)
- [x] **AC-US1-04**: The 7 satellite plugin directories (`plugins/specweave-github/`, `plugins/specweave-jira/`, `plugins/specweave-ado/`, `plugins/specweave-release/`, `plugins/specweave-diagrams/`, `plugins/specweave-media/`, `plugins/specweave-docs/`) are deleted after migration
- [x] **AC-US1-05**: The core plugin's `.claude-plugin/plugin.json` is updated to reflect the expanded skill/command count
- [x] **AC-US1-06**: All internal import paths within moved lib files are updated to resolve correctly from their new locations
- [x] **AC-US1-07**: Post-task-completion hook scripts from satellite plugins (github, jira, ado, release) are consolidated into the core plugin's hook infrastructure

---

### US-002: Backward-Compatible Skill Names (P1)
**Project**: specweave

**As a** SpecWeave user
**I want** all existing skill names to continue working after the consolidation
**So that** my workflows, documentation references, and muscle memory are not disrupted

**Acceptance Criteria**:
- [x] **AC-US2-01**: All `sw-github:*` skill invocations (`sw-github:push`, `sw-github:close`, `sw-github:sync`, `sw-github:pr-review`) resolve to the same SKILL.md files as before consolidation
- [x] **AC-US2-02**: All `sw-jira:*` skill invocations (`sw-jira:sync`, `sw-jira:mapper`, `sw-jira:resource-validator`) resolve correctly
- [x] **AC-US2-03**: All `sw-ado:*` skill invocations (`sw-ado:sync`, `sw-ado:mapper`, `sw-ado:multi-project`, `sw-ado:resource-validator`) resolve correctly
- [x] **AC-US2-04**: All `sw-release:*`, `sw-diagrams:*`, `sw-media:*` skill invocations resolve correctly
- [x] **AC-US2-05**: The `docs:*` command-only plugin's 7 commands remain accessible under their existing names
- [x] **AC-US2-06**: SKILL.md files preserve their existing trigger patterns, descriptions, and activation keywords so that auto-detection continues to work
- [x] **AC-US2-07**: The PLUGINS-INDEX.md trigger-to-plugin mapping table is updated to point all triggers to the unified `specweave` plugin while preserving the trigger keywords themselves

---

### US-003: Hook and Command Collision Resolution (P1)
**Project**: specweave

**As a** SpecWeave maintainer
**I want** hook and command name collisions resolved via domain-prefixing
**So that** the unified plugin has no ambiguous command names and hooks dispatch correctly

**Acceptance Criteria**:
- [x] **AC-US3-01**: Commands that share names across plugins (clone, close, create, pull, push, reconcile, status, sync, cleanup-duplicates) use domain-prefixed filenames in the unified `commands/` directory (e.g., `github-clone.md`, `ado-clone.md`, `jira-clone.md`)
- [x] **AC-US3-02**: The core `specweave` plugin's `hooks.json` is the single hook registration file — no duplicate hook registrations from satellite plugins
- [x] **AC-US3-03**: Post-task-completion hooks from github/jira/ado/release are merged into a single dispatcher that routes by integration type (determined by increment config or project settings)
- [x] **AC-US3-04**: No two command files in the unified `commands/` directory have the same filename
- [x] **AC-US3-05**: Command file content preserves any plugin-specific namespace references (e.g., `sw-github:` prefix in command descriptions) so the CLI continues to route correctly

---

### US-004: Marketplace and Plugin Installer Updates (P1)
**Project**: specweave

**As a** SpecWeave user running `specweave init` or `specweave refresh-plugins`
**I want** the plugin installation to install a single unified plugin instead of 8 separate ones
**So that** installation is faster and produces a cleaner plugin state

**Acceptance Criteria**:
- [x] **AC-US4-01**: `marketplace.json` contains exactly 1 plugin entry (`sw`) instead of 8, with the source pointing to `./plugins/specweave`
- [x] **AC-US4-02**: `plugin-copier.ts` (`installPlugin` function) installs the single unified plugin in one `claude plugin install` call instead of 8
- [x] **AC-US4-03**: `plugin-copier.ts` (`copyPluginSkillsToProject` function) copies all skills from the unified plugin directory including the newly merged skills
- [x] **AC-US4-04**: The `refresh-plugins` CLI command works correctly with the single-plugin marketplace
- [x] **AC-US4-05**: The `uninstall` CLI command correctly removes the unified plugin and all its skills
- [x] **AC-US4-06**: The `detect-intent` CLI command resolves integration-specific intents (e.g., "sync to GitHub") to the unified plugin's skills
- [x] **AC-US4-07**: The `plugin-scope.ts` configuration is updated — the 7 satellite plugin scope entries are removed or consolidated into the single `sw` entry
- [x] **AC-US4-08**: The `installation-health-checker.ts` (doctor) validates the single-plugin installation correctly and detects stale satellite plugin remnants

---

### US-005: Test Migration (P2)
**Project**: specweave

**As a** SpecWeave developer
**I want** all existing tests to pass after the plugin consolidation
**So that** we have confidence the refactor introduced no regressions

**Acceptance Criteria**:
- [x] **AC-US5-01**: All existing unit tests in `tests/` that reference satellite plugin paths are updated to use the new unified plugin paths
- [x] **AC-US5-02**: Tests for `plugin-copier.ts` are updated to verify single-plugin installation instead of 8-plugin installation
- [x] **AC-US5-03**: Tests for `marketplace.json` parsing validate the single-entry format
- [x] **AC-US5-04**: Integration tests that verify skill resolution (e.g., `sw-github:push` resolves to the correct SKILL.md) pass with the new directory structure
- [x] **AC-US5-05**: The `installation-health-checker` test suite validates detection of stale satellite plugin remnants
- [x] **AC-US5-06**: `npx vitest run` passes with 0 failures after all migrations

---

### US-006: Documentation Updates (P2)
**Project**: specweave

**As a** SpecWeave user or contributor reading the docs
**I want** documentation to accurately reflect the unified plugin structure
**So that** I understand the current architecture and don't follow stale installation instructions

**Acceptance Criteria**:
- [x] **AC-US6-01**: `docs-site/docs/overview/plugins-ecosystem.md` is updated to describe the unified plugin architecture instead of 8 separate plugins
- [x] **AC-US6-02**: `docs-site/docs/guides/lazy-plugin-loading.md` is updated to reflect how progressive loading works within the single plugin
- [x] **AC-US6-03**: `docs-site/docs/guides/github-integration.md` references the unified plugin structure
- [x] **AC-US6-04**: `docs-site/docs/enterprise/azure-devops-migration.md` references the unified plugin
- [x] **AC-US6-05**: Plugin-internal documentation files (`PLUGIN.md`, `COMMANDS-VS-SKILLS-ANALYSIS.md`, `SKILLS-VS-AGENTS.md`, `FINAL-AUDIT-RECOMMENDATIONS.md`, `VALIDATION-REPORT.md`) in the old satellite directories are removed or consolidated
- [x] **AC-US6-06**: `PLUGINS-INDEX.md` is updated to reflect 1 plugin with 44 skills instead of 8 plugins with distributed skills
- [x] **AC-US6-07**: The features page (`VerifiedSkillsSection.tsx` or `features.md`) is updated with current stats (100K+ verified skills)
- [x] **AC-US6-08**: CLAUDE.md and AGENTS.md references to individual plugin names are updated where they describe the plugin architecture

---

### US-007: Lockfile Migration (P2)
**Project**: specweave

**As a** SpecWeave user upgrading from multi-plugin to unified-plugin
**I want** my lockfile to be automatically migrated so the upgrade is seamless
**So that** I don't experience duplicate installs, stale hash checks, or broken `refresh-plugins`

**Acceptance Criteria**:
- [x] **AC-US7-01**: On first run after upgrade, the global `~/.specweave/plugins-lock.json` entries for `sw-github`, `sw-jira`, `sw-ado`, `sw-release`, `sw-diagrams`, `docs`, `sw-media` are removed and replaced with a single `sw` entry
- [x] **AC-US7-02**: Per-project `vskill.lock` files with satellite plugin entries are migrated: satellite entries removed, single `sw` entry added with fresh SHA
- [x] **AC-US7-03**: The migration is idempotent — running it multiple times produces the same result
- [x] **AC-US7-04**: Legacy plugin cache directories under `~/.claude/plugins/cache/specweave/` for satellite plugins are cleaned up
- [x] **AC-US7-05**: The migration runs automatically during `specweave init` or `specweave refresh-plugins` — no manual user action required
- [x] **AC-US7-06**: If migration fails (e.g., permission error), the error is logged but does not block plugin installation — a fresh install is performed instead

---

### US-008: Build and Copy Script Updates (P2)
**Project**: specweave

**As a** SpecWeave maintainer running the build pipeline
**I want** build scripts to work correctly with the unified plugin structure
**So that** `npm run build` and distribution packaging produce a correct single-plugin artifact

**Acceptance Criteria**:
- [x] **AC-US8-01**: `scripts/build/copy-plugin-js.js` copies the unified plugin directory correctly (single source, all subdirectories)
- [x] **AC-US8-02**: The npm package includes the unified plugin directory structure in the published artifact
- [x] **AC-US8-03**: `npm run build` completes without errors referencing old satellite plugin paths
- [x] **AC-US8-04**: The published package size does not increase beyond 5% (consolidation should not add significant overhead)

---

## Functional Requirements

### FR-001: Skill Name Preservation
User-facing skill names (`sw-github:push`, `sw-jira:sync`, etc.) are routing identifiers, not filesystem paths. The SKILL.md files define their own activation triggers and names. Moving SKILL.md files to new directories does not change their invocation names as long as the SKILL.md content is preserved.

### FR-002: Single Plugin Install
After consolidation, `installPlugin('sw', specweaveRoot)` in `plugin-copier.ts` must install all 44 skills and 74 commands in a single operation. The 7 satellite `installPlugin` calls are removed.

### FR-003: Progressive Loading Compatibility
The `PLUGINS-INDEX.md` progressive loading pattern (scan index, match triggers, load content) continues to work. The index maps triggers to sections within the unified plugin rather than separate plugin directories.

### FR-004: Lockfile Schema Compatibility
The `VskillLock` interface and lock format (`version: 1`) remain unchanged. Only the entries change (7 satellite entries replaced by 1 unified entry). No lockfile version bump needed.

### FR-005: Hook Dispatcher Consolidation
Post-task-completion hooks from github/jira/ado/release are consolidated into the core hook infrastructure. The hook dispatcher determines which integration to notify based on the increment's external sync configuration (checking `metadata.json` `externalLinks` or project config).

---

## Success Criteria

- `specweave init` installs 1 plugin instead of 8 (measurable via lockfile entry count)
- All 44 skills resolve correctly when invoked by name
- All 74 commands are accessible
- `npx vitest run` passes with 0 failures
- `marketplace.json` has exactly 1 plugin entry
- No references to satellite plugin directories remain in source code (verified by grep)
- Plugin installation time reduced (fewer CLI calls)

---

## Out of Scope

- **New features**: This is a packaging refactor only — no new skills, commands, or behaviors
- **Skill renaming**: Skill names remain unchanged (Option B)
- **Plugin API changes**: The `plugin-loader.ts`, `plugin-copier.ts` public APIs remain compatible
- **Third-party plugin support**: This only consolidates first-party bundled plugins
- **Progressive loading redesign**: The trigger-based lazy loading pattern is preserved, not redesigned
- **Docs site rebuild**: Only content updates to existing pages — no new pages or structural changes
- **Version bump**: The marketplace version stays at the current release version

---

## Dependencies

- **No external dependencies**: This is an internal refactoring of the specweave repository
- **Build system**: Relies on `scripts/build/copy-plugin-js.js` being updated in the same increment
- **Claude Code plugin system**: Assumes `claude plugin install` CLI works with the consolidated plugin directory structure (no changes to Claude Code itself)
- **Test infrastructure**: Vitest must be available for regression testing
