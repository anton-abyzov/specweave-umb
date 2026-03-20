---
increment: 0636-plugin-caching-review-followup
title: "Plugin Caching Review Follow-up"
type: refactor
priority: P2
status: planned
created: 2026-03-20
structure: user-stories
test_mode: none
coverage_target: 0
---

# Spec: Plugin Caching Review Follow-up

## US-001: Shared Semver Sort Utility
**Project**: specweave

**As a** developer
**I want** a single semver sort utility used across all plugin code
**So that** NaN-unsafe duplicated sort logic is eliminated

**Acceptance Criteria**:
- [ ] **AC-US1-01**: `compareSemverDesc(a, b)` extracted to `utils/semver-sort.ts` with NaN handling for non-numeric segments
- [ ] **AC-US1-02**: `plugin-copier.ts` `validatePluginCache` uses the shared sort
- [ ] **AC-US1-03**: `plugin-scanner.ts` uses the shared sort

## US-002: Complete Silent Catch Logging
**Project**: specweave

**As a** SpecWeave user
**I want** all remaining empty catch blocks to log at debug or warn level
**So that** no plugin errors are silently swallowed

**Acceptance Criteria**:
- [ ] **AC-US2-01**: All 8 remaining empty catches in `plugin-copier.ts` log via `consoleLogger.debug` or `consoleLogger.warn`
- [ ] **AC-US2-02**: Both catches in `plugin-scanner.ts` (lines ~52, ~110) log at debug level
- [ ] **AC-US2-03**: 3 new Phase 2.5 catches in `cleanup-stale-plugins.ts` log at debug level
- [ ] **AC-US2-04**: 6 catches in `refresh-plugins.ts` (getAvailablePlugins + steps 0.5-0.7, 4c, 4d) log at debug level
- [ ] **AC-US2-05**: Inner backup catch in `claude-plugin-enabler.ts` logs at warn level

## US-003: Phase 2.5 Safety Hardening
**Project**: specweave

**As a** SpecWeave user
**I want** Phase 2.5 stale version cleanup to use safe deletion patterns
**So that** TOCTOU races and symlink attacks cannot cause data loss

**Acceptance Criteria**:
- [ ] **AC-US3-01**: Phase 2.5 uses atomic rename-then-delete pattern (consistent with Phase 2)
- [ ] **AC-US3-02**: Phase 2.5 checks for symlinks and verifies resolved path stays under cache base before deletion

## US-004: Settings Backup Improvements
**Project**: specweave

**As a** SpecWeave user
**I want** settings.json backup to be reliable and non-destructive
**So that** repeated corruption events don't overwrite earlier backups

**Acceptance Criteria**:
- [ ] **AC-US4-01**: Backup reuses already-read `content` variable instead of re-reading file
- [ ] **AC-US4-02**: Backup uses timestamped filename (`.bak.{timestamp}`) instead of fixed `.bak`

## US-005: Clean Error Return Values
**Project**: specweave

**As a** developer
**I want** `refreshPluginsCommand` to return plain-text error messages
**So that** callers can programmatically inspect errors without ANSI codes

**Acceptance Criteria**:
- [ ] **AC-US5-01**: `errors` array contains plain text strings (no chalk/ANSI formatting)
- [ ] **AC-US5-02**: Console output still uses chalk formatting for visual display

## US-006: Type Design Improvements
**Project**: specweave

**As a** developer
**I want** stronger type contracts for plugin validation results
**So that** impossible states are prevented at compile time

**Acceptance Criteria**:
- [ ] **AC-US6-01**: `validatePluginCache` uses a discriminated union return type (`{ valid: true } | { valid: false; error: string }`)
- [ ] **AC-US6-02**: `refreshPluginsCommand` return type extracted to named `RefreshResult` interface
- [ ] **AC-US6-03**: `installed_plugins.json` entries have runtime shape validation before property access

## US-007: Multi-Marketplace Doctor Check
**Project**: specweave

**As a** SpecWeave user
**I want** `specweave doctor` to check all marketplace caches for stale versions
**So that** non-specweave marketplace stale dirs are also detected

**Acceptance Criteria**:
- [ ] **AC-US7-01**: `checkStaleVersionDirs` iterates all marketplace subdirs under `~/.claude/plugins/cache/`, not just `specweave`
