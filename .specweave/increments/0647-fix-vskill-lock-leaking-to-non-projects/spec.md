---
increment: 0647-fix-vskill-lock-leaking-to-non-projects
title: Fix vskill.lock leaking to non-SpecWeave directories
type: bug
priority: P1
status: completed
created: 2026-03-27T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
tasksCompleted: 5
tasksTotal: 5
---

# Feature: Fix vskill.lock leaking to non-SpecWeave directories

## Overview

`specweave update` creates `vskill.lock` in whatever directory it runs from, even non-SpecWeave projects. The root cause is `copyPluginSkillsToProject()` writing bundled plugin state to a per-project lockfile instead of the global `~/.specweave/plugins-lock.json`. The native CLI path (`installPlugin()`) already uses the global lockfile correctly — the fallback path does not.

## User Stories

### US-001: Bundled plugin state uses global lockfile
**Project**: specweave

**As a** SpecWeave user
**I want** `specweave update` to not create `vskill.lock` in my project directory
**So that** non-SpecWeave projects and arbitrary directories stay clean

**Acceptance Criteria**:
- [x] **AC-US1-01**: `copyPluginSkillsToProject()` uses `ensureGlobalLockfile()` instead of `ensureLockfile(projectRoot)` for hash-checking
- [x] **AC-US1-02**: `copyPluginSkillsToProject()` uses `writeGlobalLockfile()` instead of `writeLockfile(lock, projectRoot)` for state persistence
- [x] **AC-US1-03**: Global lockfile access has try/catch with in-memory fallback (same pattern as `installPlugin()`)
- [x] **AC-US1-04**: Cross-platform: works on macOS, Linux, and Windows via `os.homedir()`

### US-002: Defense-in-depth cleanup of legacy project lockfiles
**Project**: specweave

**As a** SpecWeave user upgrading from an older version
**I want** existing project-level `vskill.lock` files with bundled entries to be migrated to the global lockfile
**So that** stale lockfiles from before this fix are cleaned up

**Acceptance Criteria**:
- [x] **AC-US2-01**: `refresh-plugins` runs `migrateBundledToGlobalLock()` after the install loop (not just before)
