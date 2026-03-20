# Spec: Fix Plugin Caching Silent Failures

## US-001: Plugin Installation Validation
**Project**: specweave

**As a** SpecWeave user
**I want** plugin installation to validate cache integrity after install
**So that** corrupt or partial installs are detected immediately instead of silently succeeding

**Acceptance Criteria**:
- [ ] **AC-US1-01**: After `claude plugin install` exits 0, validate cache contains `.claude-plugin/plugin.json` and at least one of `skills/`, `hooks/`, `commands/`
- [ ] **AC-US1-02**: If validation fails, return `{ success: false }` with descriptive error message
- [ ] **AC-US1-03**: Plugin scanner sorts version directories (semver descending) before selecting

## US-002: Error Visibility
**Project**: specweave

**As a** SpecWeave user
**I want** plugin errors to be logged instead of silently swallowed
**So that** I can diagnose plugin issues without guessing

**Acceptance Criteria**:
- [ ] **AC-US2-01**: All empty catch blocks in plugin-copier.ts log at debug or warn level
- [ ] **AC-US2-02**: Lockfile write failures log a warning (not silently swallowed)
- [ ] **AC-US2-03**: `refresh-plugins` sets `process.exitCode = 1` when plugins fail
- [ ] **AC-US2-04**: Quiet mode still tracks errors internally (returns error count to callers)
- [ ] **AC-US2-05**: Native CLI fallback logs at warn level
- [ ] **AC-US2-06**: `enablePluginsInSettings` always logs errors (not gated on DEBUG env)

## US-003: Stale Cache Cleanup
**Project**: specweave

**As a** SpecWeave user
**I want** old version directories to be automatically cleaned up
**So that** stale cache dirs don't interfere with plugin loading

**Acceptance Criteria**:
- [ ] **AC-US3-01**: Phase 2.5 in cleanup-stale-plugins prunes version subdirs that don't match the active version from installed_plugins.json
- [ ] **AC-US3-02**: `specweave doctor` warns about multiple version directories per plugin
- [ ] **AC-US3-03**: Uninstall-without-reinstall warning is always shown (not gated on verbose flag)

## US-004: Settings Safety
**Project**: specweave

**As a** SpecWeave user
**I want** settings.json to be backed up before being overwritten on corruption
**So that** I don't lose all my settings when JSON is invalid

**Acceptance Criteria**:
- [ ] **AC-US4-01**: Before replacing corrupt settings.json with `{}`, create a `.bak` backup
- [ ] **AC-US4-02**: Core plugin (sw) failure in batch install returns `success: false` overall

## US-005: Strict Plugin Loading
**Project**: specweave

**As a** developer
**I want** optional strict mode in plugin-loader
**So that** health checks can detect plugins with zero components

**Acceptance Criteria**:
- [ ] **AC-US5-01**: `loadFromDirectory()` accepts optional `{ strict: true }` that throws if plugin has zero skills + agents + commands
