---
increment: 0536-plugin-discover-scope-fix
title: Fix plugin Discover tab scope mismatch
type: bugfix
priority: P0
status: completed
created: 2026-03-15T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Fix Plugin Discover Tab Scope Mismatch

## Problem Statement

Claude Code's `/plugin` Discover tab only shows `sw` as installed (checkmark) while the Installed tab correctly shows all 8 SpecWeave plugins as enabled. The root cause is a scope mismatch: `sw` installs at `user` scope (via `scopeOverrides`) while all other SpecWeave plugins default to `project` scope (via `specweaveScope: 'project'`). Claude Code's Discover tab only recognizes user-scoped plugins as "installed."

Additionally, the `specweave init` flow (`installAllPlugins()`) never calls `enablePluginsInSettings()`, so plugins are not registered in `~/.claude/settings.json` during initial setup. The `refresh-plugins` command does call it, but only when `useNativeCli` is true, meaning direct-copy installs skip settings enablement entirely.

## Goals

- All SpecWeave plugins appear as installed in Claude Code's Discover tab
- Init and refresh-plugins flows both produce consistent settings state
- No manual intervention required after `specweave init` or `specweave refresh-plugins`

## User Stories

### US-001: Consistent Plugin Scope (P0)
**Project**: specweave

**As a** SpecWeave user
**I want** all SpecWeave plugins to install at user scope
**So that** Claude Code's Discover tab recognizes them as installed

**Acceptance Criteria**:
- [x] **AC-US1-01**: Given `DEFAULT_PLUGIN_SCOPE_CONFIG` in `plugin-scope.ts`, when `specweaveScope` is read, then its value is `'user'`
- [x] **AC-US1-02**: Given the `sw` entry in `scopeOverrides`, when `specweaveScope` is already `'user'`, then the `sw` override is removed as redundant
- [x] **AC-US1-03**: Given a SpecWeave plugin name (e.g., `frontend`, `sw-github`), when `getPluginScope()` is called, then it returns `'user'`

---

### US-002: Settings Enablement on Init (P0)
**Project**: specweave

**As a** SpecWeave user running `specweave init` for the first time
**I want** plugins to be enabled in `~/.claude/settings.json` automatically
**So that** Claude Code recognizes all plugins without requiring a separate `refresh-plugins` run

**Acceptance Criteria**:
- [x] **AC-US2-01**: Given `installAllPlugins()` completes successfully, when the function returns, then `enablePluginsInSettings()` has been called with all successfully installed plugin names
- [x] **AC-US2-02**: Given `installAllPlugins()` installs 6 of 8 plugins successfully, when `enablePluginsInSettings()` is called, then only the 6 successful plugin names are passed (failed plugins are excluded)
- [x] **AC-US2-03**: Given `enablePluginsInSettings()` fails (returns false), when `installAllPlugins()` continues, then it logs a warning but does not fail the overall installation

---

### US-003: Settings Enablement Regardless of Install Method (P1)
**Project**: specweave

**As a** SpecWeave user running `specweave refresh-plugins`
**I want** plugins to be enabled in settings regardless of whether Claude CLI is available
**So that** direct-copy installs (non-Claude editors) also get proper settings registration

**Acceptance Criteria**:
- [x] **AC-US3-01**: Given `useNativeCli` is false, when `refreshPluginsCommand()` completes with installed plugins, then `enablePluginsInSettings()` is still called
- [x] **AC-US3-02**: Given `useNativeCli` is true, when `refreshPluginsCommand()` completes with installed plugins, then `enablePluginsInSettings()` is called (existing behavior preserved)

## Out of Scope

- Migrating existing project-scoped plugin entries to user scope (users run `refresh-plugins` to fix)
- Changes to Claude Code's Discover tab logic itself (upstream, not our code)
- Supporting mixed scope strategies (some plugins user, some project) beyond LSP plugins

## Technical Notes

### Dependencies
- `enablePluginsInSettings()` from `claude-plugin-enabler.ts` -- already exists, just not called in all paths

### Constraints
- `enablePluginsInSettings()` writes to `~/.claude/settings.json` -- must handle missing file and directory gracefully (it already does)

### Architecture Decisions
- Removing the `sw` scope override is a cleanup: when `specweaveScope` is `'user'`, having `scopeOverrides.sw = 'user'` is a no-op that adds confusion
- LSP plugins remain at `project` scope -- they are language-specific and should not pollute global settings

## Non-Functional Requirements

- **Compatibility**: Works on macOS, Linux, and Windows (path.join handles OS differences)
- **Idempotency**: Running init or refresh-plugins multiple times produces the same settings state
- **Performance**: No measurable impact -- `enablePluginsInSettings()` is a single JSON file read/write

## Edge Cases

- **No settings.json exists**: `enablePluginsInSettings()` creates the file and directory (already handled)
- **Corrupt settings.json**: `enablePluginsInSettings()` resets to empty object (already handled via catch)
- **Zero successful installs**: `enablePluginsInSettings()` should not be called with an empty array
- **Concurrent runs**: Two `specweave init` processes writing `settings.json` simultaneously could conflict -- accepted risk, same as current behavior for `refresh-plugins`

## Risks

| Risk | Probability | Impact | Severity | Mitigation |
|------|-------------|--------|----------|------------|
| Existing users with project-scoped plugins see duplicates | 0.3 | 2 | 0.6 | `enablePluginsInSettings` is idempotent; refresh-plugins cleans up |
| Breaking change for users who intentionally use project scope | 0.1 | 3 | 0.3 | `scopeOverrides` config still allows per-plugin overrides |

## Success Metrics

- All 8 SpecWeave plugins show checkmarks in Claude Code's Discover tab after `specweave init`
- `specweave refresh-plugins` produces identical settings state regardless of `useNativeCli` value
- No regression in existing unit tests for `getPluginScope()`
