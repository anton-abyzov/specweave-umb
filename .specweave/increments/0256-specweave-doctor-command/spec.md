---
increment: 0256-specweave-doctor-command
title: "SpecWeave Doctor Command - Installation Health Scanner"
type: feature
priority: P1
status: planned
created: 2026-02-20
structure: user-stories
test_mode: test-after
coverage_target: 80
---

# Feature: SpecWeave Doctor Command - Installation Health Scanner

## Overview

The existing `specweave doctor` command has 7 health checkers (Environment, ProjectStructure, Configuration, Hooks, Plugins, Increments, Git). This increment adds a new **InstallationHealthChecker** that specifically targets the Claude Code plugin installation surface: ghost slash commands, stale cache directories, orphaned plugin files, command namespace pollution, and cache-vs-lockfile integrity mismatches. It also adds a `/sw:doctor` skill for interactive use and enhances the `--fix` flag to auto-remediate detected issues.

### Problem

After plugin installs/uninstalls/upgrades, several "ghosts" can linger:

1. **Ghost slash commands**: `PLUGIN.md`, `README.md`, `FRESHNESS.md` files that leaked into `~/.claude/commands/` appear as phantom `/sw:PLUGIN`, `/sw:README`, `/sw:FRESHNESS` commands in Claude Code.
2. **Stale IDE cache dirs**: Orphaned `temp_local_*` directories in `~/.claude/plugins/cache/` from interrupted installs.
3. **Orphaned plugin files**: Plugin entries in `installed_plugins.json` that reference cache paths which no longer exist, or cache directories that have no corresponding entry in the manifest.
4. **Command namespace pollution**: Non-command `.md` files in `~/.claude/commands/<plugin>/` subdirectories (e.g. knowledge-base, lib, templates) that Claude Code incorrectly treats as slash commands.
5. **Cache-lockfile hash mismatch**: The `vskill.lock` records a SHA for each installed skill; if the actual files in `~/.claude/commands/<name>/` have diverged (manual edits, partial install), the hash will not match.

## User Stories

### US-001: Ghost Slash Command Detection (P1)
**Project**: specweave

**As a** SpecWeave user
**I want** the doctor command to detect ghost slash commands (PLUGIN.md, README.md, FRESHNESS.md) leaked into `~/.claude/commands/`
**So that** I can remove them and keep my slash-command namespace clean

**Acceptance Criteria**:
- [x] **AC-US1-01**: Doctor scans `~/.claude/commands/` recursively for `.md` files matching the ghost pattern (PLUGIN.md, README.md, FRESHNESS.md) and reports each as a warning
- [x] **AC-US1-02**: Each ghost file reports its full path and which plugin directory it belongs to
- [x] **AC-US1-03**: With `--fix`, ghost files are deleted automatically
- [x] **AC-US1-04**: With `--fix`, a summary of deleted files is displayed

---

### US-002: Stale Cache Directory Detection (P1)
**Project**: specweave

**As a** SpecWeave user
**I want** the doctor command to detect stale/orphaned cache directories in `~/.claude/plugins/cache/`
**So that** disk space is not wasted on abandoned plugin artifacts

**Acceptance Criteria**:
- [x] **AC-US2-01**: Doctor detects `temp_local_*` directories in the plugin cache as orphaned
- [x] **AC-US2-02**: Doctor detects cache directories for plugins not referenced in `installed_plugins.json`
- [x] **AC-US2-03**: Each stale directory reports its path and age
- [x] **AC-US2-04**: With `--fix`, stale `temp_local_*` directories are removed
- [x] **AC-US2-05**: With `--fix`, unreferenced cache directories are NOT auto-removed (only reported with a warning) to avoid accidental data loss

---

### US-003: Cache-Lockfile Hash Integrity (P1)
**Project**: specweave

**As a** SpecWeave user
**I want** the doctor command to verify that the installed commands in `~/.claude/commands/<name>/` match the SHA recorded in `vskill.lock`
**So that** I know my plugin installation is consistent and not corrupted

**Acceptance Criteria**:
- [x] **AC-US3-01**: Doctor reads `vskill.lock` from the project root and computes the current hash of each installed skill directory using `computePluginHash()`
- [x] **AC-US3-02**: A mismatch between lockfile SHA and computed SHA is reported as a warning with both values shown
- [x] **AC-US3-03**: A skill listed in the lockfile but missing from `~/.claude/commands/` is reported as a failure
- [x] **AC-US3-04**: With `--fix`, hash mismatches trigger a `specweave refresh-plugins` suggestion (not auto-run, to avoid side effects)

---

### US-004: Command Namespace Pollution Detection (P2)
**Project**: specweave

**As a** SpecWeave user
**I want** the doctor command to detect `.md` files in internal plugin subdirectories that should not be treated as slash commands
**So that** my Claude Code command palette is not cluttered with non-functional entries

**Acceptance Criteria**:
- [x] **AC-US4-01**: Doctor scans `~/.claude/commands/` for `.md` files inside known internal directories (knowledge-base, lib, templates, scripts, hooks, .claude-plugin) and reports them
- [x] **AC-US4-02**: Each polluting file shows its path and the would-be command name Claude Code derives from it
- [x] **AC-US4-03**: With `--fix`, polluting `.md` files in internal directories are deleted
- [x] **AC-US4-04**: The `shouldSkipFromCommands()` filter logic from `plugin-copier.ts` is reused for detection consistency

---

### US-005: /sw:doctor Skill (P2)
**Project**: specweave

**As a** SpecWeave user
**I want** a `/sw:doctor` slash command that runs the doctor checks interactively
**So that** I can diagnose installation health without leaving Claude Code

**Acceptance Criteria**:
- [x] **AC-US5-01**: `/sw:doctor` skill exists as a SKILL.md file and invokes `specweave doctor` with appropriate flags
- [x] **AC-US5-02**: The skill supports an optional `--fix` argument to pass through to the CLI
- [x] **AC-US5-03**: Output is presented in a readable format within the conversation
- [x] **AC-US5-04**: The skill handles the case where `specweave` CLI is not installed (suggests `npm install -g specweave`)

## Functional Requirements

### FR-001: InstallationHealthChecker
New checker class implementing the `HealthChecker` interface at `src/core/doctor/checkers/installation-health-checker.ts`. Produces a `CategoryResult` with category name "Installation Health". Contains individual check methods for each US (ghost commands, stale cache, hash integrity, namespace pollution).

### FR-002: Fix Mode Integration
The checker must support the existing `--fix` flag from `DoctorOptions`. When `options.fix` is true, each check should auto-remediate where safe. The `determineFix()` function in `doctor.ts` should be extended to recognize installation health issues and suggest `specweave refresh-plugins` as the fix command.

### FR-003: Safety Boundary
`--fix` must NEVER delete files outside `~/.claude/` (safety boundary). All fixes must be idempotent (running `--fix` twice produces the same result).

## Success Criteria

- `specweave doctor` detects and reports all 5 issue categories when they exist
- `specweave doctor --fix` remediates ghost files, temp cache dirs, and namespace pollution
- Zero false positives on a clean installation
- All new checks have unit tests with >90% coverage
- `/sw:doctor` skill works in Claude Code sessions

## Out of Scope

- Modifying the existing 7 checkers (they stay as-is)
- Network-based checks (marketplace availability, npm version)
- Scanning third-party non-SpecWeave plugins for issues
- Auto-running `specweave refresh-plugins` (only suggest it)

## Dependencies

- Existing doctor infrastructure: `src/core/doctor/` module
- `shouldSkipFromCommands()` and `computePluginHash()` from `src/utils/plugin-copier.ts`
- `readLockfile()` from `src/utils/plugin-copier.ts`
