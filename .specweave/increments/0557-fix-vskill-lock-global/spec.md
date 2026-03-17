---
increment: 0557-fix-vskill-lock-global
title: Separate global plugin lock from project-scoped skill lock
status: completed
priority: P1
type: bugfix
created: 2026-03-17T00:00:00.000Z
---

# Separate Global Plugin Lock from Project-Scoped Skill Lock

## Problem Statement

`specweave update` and `specweave refresh-plugins` unconditionally create a `vskill.lock` file in the user's current working directory. This happens because `installPlugin()` in `plugin-copier.ts` calls `getProjectRoot()` for the lockfile path, and `getProjectRoot()` falls back to `process.cwd()` when no `.specweave/config.json` is found. Bundled plugins (sw, sw-github, etc.) are global -- they install to `~/.claude/plugins/cache/` -- but their hash cache writes to whatever directory the user happens to be in. This pollutes non-SpecWeave projects with stale `vskill.lock` files.

## Goals

- Bundled plugin hash tracking uses a global lockfile at `~/.specweave/plugins-lock.json`
- Project-scoped skill tracking via `vskill.lock` remains unchanged
- Existing bundled entries in project `vskill.lock` files are migrated to the global lock on first run
- No `vskill.lock` is created in non-SpecWeave directories

## User Stories

### US-001: Global Lock for Bundled Plugins
**Project**: specweave
**As a** developer using specweave in multiple projects
**I want** bundled plugin hashes stored in a single global location
**So that** `vskill.lock` files stop appearing in unrelated project directories

**Acceptance Criteria**:
- [x] **AC-US1-01**: Given `installPlugin()` is called for a bundled plugin, when it writes the hash cache, then the entry is written to `~/.specweave/plugins-lock.json` (not to `getProjectRoot()/vskill.lock`)
- [x] **AC-US1-02**: Given `~/.specweave/` does not exist, when `installPlugin()` runs, then it creates the directory before writing `plugins-lock.json`
- [x] **AC-US1-03**: Given `plugins-lock.json` already exists with entries, when a new plugin is installed, then existing entries are preserved and the new entry is merged
- [x] **AC-US1-04**: Given `installPlugin()` is called with `force: false` and the hash in `plugins-lock.json` matches, then installation is skipped (existing skip logic works with new path)

### US-002: Refresh-Plugins Uses Global Lock
**Project**: specweave
**As a** developer running `specweave refresh-plugins`
**I want** the command to read/write the global lock for bundled plugins
**So that** it no longer depends on `getProjectRoot()` for lockfile purposes

**Acceptance Criteria**:
- [x] **AC-US2-01**: Given `refresh-plugins` runs with native CLI mode, when `installPlugin()` is called, then it uses `~/.specweave/plugins-lock.json` for hash comparison
- [x] **AC-US2-02**: Given `refresh-plugins` runs with direct-copy fallback mode, when `copyPluginSkillsToProject()` is called, then it still uses the project-local `vskill.lock` for project-scoped skill tracking (unchanged behavior)
- [x] **AC-US2-03**: Given `refresh-plugins` runs the stale lockfile cleanup (Step 0.5), when `getProjectRoot()` is called, then it is only used for orphaned child lock cleanup -- not for bundled plugin lock reads

### US-003: Migration from Project Lock to Global Lock
**Project**: specweave
**As a** developer upgrading specweave
**I want** existing bundled plugin entries migrated from project `vskill.lock` to global `plugins-lock.json`
**So that** the transition is seamless with no re-downloads

**Acceptance Criteria**:
- [x] **AC-US3-01**: Given a project `vskill.lock` contains bundled plugin entries (source: `local:specweave`), when migration runs, then those entries are copied to `~/.specweave/plugins-lock.json`
- [x] **AC-US3-02**: Given migration moves all entries out of a project `vskill.lock`, when the lock has no remaining skill entries, then the empty `vskill.lock` file is deleted
- [x] **AC-US3-03**: Given `~/.specweave/plugins-lock.json` already has an entry for a plugin being migrated, when the project lock has a newer `installedAt` timestamp, then the global entry is updated; otherwise the existing global entry is kept
- [x] **AC-US3-04**: Given migration has already run (no bundled entries in project lock), when `installPlugin()` is called again, then migration is not re-attempted (idempotent)

## Out of Scope

- Changing `vskill.lock` format or behavior for user-installed skills (`vskill install`)
- Modifying `copyPluginSkillsToProject()` lockfile behavior (project-scoped by design)
- Changing how `getProjectRoot()` or `findProjectRoot()` resolve paths
- Removing the `vskill.lock` concept entirely

## Technical Notes

### Dependencies
- `plugin-copier.ts` -- primary change target (lock path routing, new `getGlobalLockDir()`)
- `refresh-plugins.ts` -- remove `getProjectRoot()` usage for bundled lockfile purposes
- `cleanup-stale-plugins.ts` -- add migration function, call during refresh

### Constraints
- `plugins-lock.json` must use the same `VskillLock` interface structure for compatibility
- Migration must be safe to run multiple times (idempotent)
- `~/.specweave/` directory creation must handle permission errors gracefully

### Architecture Decisions
- **Global lock path**: `~/.specweave/plugins-lock.json` -- separate from `~/.claude/` to avoid conflicts with Claude Code's own plugin management
- **Lock format reuse**: Same `VskillLock` interface, different filename to clearly distinguish from project `vskill.lock`
- **Migration in cleanup module**: Fits naturally alongside existing stale lockfile cleanup functions

## Non-Functional Requirements

- **Performance**: No measurable change -- identical file I/O volume, just different paths
- **Compatibility**: Must work on macOS, Linux, and Windows (home directory resolution via `os.homedir()`)
- **Security**: `~/.specweave/` inherits user-level permissions, no escalation

## Edge Cases

- **No home directory**: `os.homedir()` returns empty string -- fall back to project lock behavior
- **Permission denied on ~/.specweave/**: `mkdirSync` fails -- log warning, fall back to project lock
- **Concurrent runs**: Two `specweave refresh-plugins` processes running simultaneously -- last write wins (acceptable for hash cache)
- **Empty vskill.lock after migration**: File should be deleted, not left as `{"skills": {}}`
- **Mixed lock**: Project `vskill.lock` has both bundled and user-installed entries -- only migrate bundled entries, leave user entries intact

## Risks

| Risk | Probability | Impact | Severity | Mitigation |
|------|-------------|--------|----------|------------|
| Migration corrupts project vskill.lock | 0.1 | 7 | 0.7 | Read-then-write with entry-level granularity; only delete bundled entries |
| Permission errors on ~/.specweave/ in CI | 0.2 | 3 | 0.6 | Graceful fallback to project lock on any global lock write failure |
| Concurrent migration race condition | 0.1 | 2 | 0.2 | Idempotent migration; last-write-wins is acceptable for hash cache |

## Success Metrics

- Running `specweave update` in a non-SpecWeave directory no longer creates `vskill.lock`
- `~/.specweave/plugins-lock.json` exists after first `specweave refresh-plugins` run
- Existing project `vskill.lock` files with only bundled entries are cleaned up after migration
