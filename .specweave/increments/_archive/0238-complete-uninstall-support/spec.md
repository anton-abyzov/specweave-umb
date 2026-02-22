---
increment: 0238-complete-uninstall-support
title: Complete uninstall support for specweave and vskill
type: feature
priority: P1
status: completed
created: 2026-02-18T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 80
---

# Feature: Complete Uninstall Support

## Overview

Add uninstall/remove commands at all levels: `vskill remove` for individual skills, `specweave uninstall` for full project cleanup, and npm preuninstall lifecycle scripts for `npm uninstall -g` cleanup.

## User Stories

### US-001: Remove a single skill (P1)
**Project**: vskill

**As a** developer
**I want** to remove an installed skill via `vskill remove <skill-name>`
**So that** I can cleanly uninstall skills I no longer need

**Acceptance Criteria**:
- [x] **AC-US1-01**: `vskill remove <name>` removes skill files from all detected agent directories (local + global)
- [x] **AC-US1-02**: Lockfile is updated via `removeSkillFromLock()` after removal
- [x] **AC-US1-03**: `--global` flag limits removal to global agent directories only
- [x] **AC-US1-04**: `--local` flag limits removal to local agent directories only
- [x] **AC-US1-05**: `--force` skips confirmation prompt
- [x] **AC-US1-06**: Confirmation prompt shown before deletion (skipped with --force or non-TTY)
- [x] **AC-US1-07**: Graceful handling when skill directories don't exist
- [x] **AC-US1-08**: Error when skill not in lockfile (unless --force)

---

### US-002: Uninstall SpecWeave from a project (P1)
**Project**: specweave

**As a** developer
**I want** to run `specweave uninstall` to completely remove SpecWeave from my project
**So that** I can cleanly decommission the framework without manual cleanup

**Acceptance Criteria**:
- [x] **AC-US2-01**: `.specweave/` directory is deleted
- [x] **AC-US2-02**: SW-managed sections stripped from CLAUDE.md (user content preserved)
- [x] **AC-US2-03**: SW-managed sections stripped from AGENTS.md (user content preserved)
- [x] **AC-US2-04**: Files deleted entirely when 100% SW-managed (no user content)
- [x] **AC-US2-05**: SpecWeave git pre-commit hook removed (non-SW hooks untouched)
- [x] **AC-US2-06**: All locally installed skills removed from agent directories
- [x] **AC-US2-07**: `vskill.lock` deleted
- [x] **AC-US2-08**: `--keep-data` archives `.specweave/` to `.specweave-backup-{timestamp}/`
- [x] **AC-US2-09**: `--dry-run` shows removal manifest without deleting anything
- [x] **AC-US2-10**: `--force` skips confirmation prompt
- [x] **AC-US2-11**: `--global` additionally cleans global agent dirs, plugin cache, shell env vars
- [x] **AC-US2-12**: Summary printed after completion with counts

---

### US-003: npm uninstall cleanup (P2)
**Project**: specweave, vskill

**As a** developer
**I want** `npm uninstall -g specweave` / `npm uninstall -g vskill` to clean up global artifacts
**So that** no orphaned files remain after package removal

**Acceptance Criteria**:
- [x] **AC-US3-01**: vskill preuninstall warns about remaining global skill directories
- [x] **AC-US3-02**: specweave preuninstall advises running `specweave uninstall` first
- [x] **AC-US3-03**: specweave preuninstall cleans `~/.claude/plugins/cache/specweave/`
- [x] **AC-US3-04**: Scripts are standalone `.cjs` files (no build step dependency)

## Out of Scope

- Uninstalling from child repos in umbrella projects (user runs per-repo)
- Removing npm global package itself (npm handles that)
- Removing user's project source code

## Dependencies

- Existing `uninstallGitHooks()` in specweave
- Existing `removeSkillFromLock()` in vskill
- Existing `parseFile()` in instruction-file-merger.ts
