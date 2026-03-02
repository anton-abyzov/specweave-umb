---
increment: 0373-fix-install-tracking-callback
title: "Fix install tracking callback"
type: bug
priority: P1
status: planned
created: 2026-02-25
structure: user-stories
test_mode: TDD
coverage_target: 80
---

# Feature: Fix install tracking callback

## Overview

The `reportInstall()` callback that tracks skill installations on the platform is broken across multiple code paths in the vskill CLI and the platform API endpoint. Three categories of bugs prevent accurate install tracking: missing calls in 3 install paths, wrong skill names sent in 2 paths, and missing URL decoding on the platform endpoint.

## User Stories

### US-001: Install tracking fires on all install paths (P1)
**Project**: specweave

**As a** platform operator
**I want** every successful skill/plugin install to be tracked via `reportInstall()`
**So that** install counts on the platform dashboard are accurate

**Acceptance Criteria**:
- [ ] **AC-US1-01**: `installPluginDir()` calls `reportInstall(pluginName)` after successful plugin installation
- [ ] **AC-US1-02**: `installRepoPlugin()` calls `reportInstall(pluginName)` after successful remote plugin installation
- [ ] **AC-US1-03**: `installAllRepoPlugins()` inherits tracking from `installRepoPlugin()` -- no separate fix needed, verified by US1-02

---

### US-002: Correct skill name sent to reportInstall (P1)
**Project**: specweave

**As a** platform operator
**I want** `reportInstall()` to send the canonical skill name that matches the platform DB
**So that** the API call doesn't 404 and install counts are attributed to the correct skill

**Acceptance Criteria**:
- [ ] **AC-US2-01**: `tryNativeClaudeInstall()` does NOT call `reportInstall()` with plugin name (this is handled by the parent `installPluginDir` function which should report per-plugin, not per-skill)
- [ ] **AC-US2-02**: `installFromRegistry()` uses `detail.name` (canonical registry name) instead of the user-input `skillName` when calling `reportInstall()`

---

### US-003: Platform endpoint decodes URL-encoded skill names (P1)
**Project**: specweave

**As a** platform developer
**I want** the POST /api/v1/skills/[name]/installs endpoint to decode URL-encoded skill names
**So that** skill names with special characters (e.g. `@`, spaces) match the DB lookup

**Acceptance Criteria**:
- [ ] **AC-US3-01**: The route handler applies `decodeURIComponent()` to the `name` param before DB lookup
- [ ] **AC-US3-02**: Test covers URL-encoded skill name being properly decoded and matched

## Functional Requirements

### FR-001: Add reportInstall to installPluginDir
Add `reportInstall(pluginName).catch(() => {})` at end of `installPluginDir()` (after lockfile write, before/during summary print).

### FR-002: Add reportInstall to installRepoPlugin
Add `reportInstall(pluginName).catch(() => {})` at end of `installRepoPlugin()` (after lockfile write, before/during summary print).

### FR-003: Remove reportInstall from tryNativeClaudeInstall
Remove the `reportInstall(pluginName)` call from `tryNativeClaudeInstall()` since the parent function (`installPluginDir`) will handle reporting. This avoids double-reporting when native install succeeds.

### FR-004: Fix installFromRegistry to use canonical name
Change `reportInstall(skillName)` to `reportInstall(detail.name)` in `installFromRegistry()`.

### FR-005: Add decodeURIComponent to platform route
Apply `decodeURIComponent()` to the `name` parameter extracted from the URL before using it in DB queries.

## Success Criteria

- All 5 install paths (installPluginDir, installRepoPlugin, installAllRepoPlugins, installFromRegistry, installSingleSkillLegacy) correctly track installs
- No double-reporting from tryNativeClaudeInstall + installPluginDir
- URL-encoded skill names correctly decoded on platform
- Existing tests pass, new tests cover the fixes

## Out of Scope

- Changing the reportInstall API signature or adding batch reporting
- Adding retry logic for failed reportInstall calls
- Refactoring the install functions to share common code

## Dependencies

- vskill CLI: `repositories/anton-abyzov/vskill/src/commands/add.ts`
- vskill CLI: `repositories/anton-abyzov/vskill/src/api/client.ts`
- vskill-platform: `repositories/anton-abyzov/vskill-platform/src/app/api/v1/skills/[name]/installs/route.ts`
