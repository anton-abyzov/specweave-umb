# Tasks: Plugin Caching Hardening

### T-001: Add validatePluginCache and post-install validation
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02 | **Status**: [x] completed
**Test Plan**: Given a plugin cache with missing plugin.json → When validatePluginCache runs → Then returns `{ valid: false }` with error

### T-002: Sort version directories in plugin-scanner
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03 | **Status**: [x] completed
**Test Plan**: Given cache with dirs "1.0.0" and "2.0.0" → When getInstalledPlugins runs → Then version is "2.0.0"

### T-003: Add logging to all empty catches in plugin-copier
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02 | **Status**: [x] completed
**Test Plan**: Given lockfile write fails → When installPlugin runs → Then warning is logged

### T-004: Fix refresh-plugins error tracking and exit code
**User Story**: US-002 | **Satisfies ACs**: AC-US2-03, AC-US2-04, AC-US2-05 | **Status**: [x] completed
**Test Plan**: Given plugin install fails → When refreshPluginsCommand runs → Then process.exitCode is 1

### T-005: Add Phase 2.5 stale version pruning to cleanup-stale-plugins
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-03 | **Status**: [x] completed
**Test Plan**: Given cache with versions "1.0.0" and "1.0.323" → When cleanup runs → Then only active version remains

### T-006: Backup settings.json before overwrite and fix error logging
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US2-06 | **Status**: [x] completed
**Test Plan**: Given corrupt settings.json → When enablePluginsInSettings runs → Then .bak file is created

### T-007: Core plugin failure detection in plugin-installer
**User Story**: US-004 | **Satisfies ACs**: AC-US4-02 | **Status**: [x] completed
**Test Plan**: Given sw plugin fails but other succeeds → When installAllPlugins runs → Then returns success: false

### T-008: Optional strict mode in plugin-loader
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01 | **Status**: [x] completed
**Test Plan**: Given plugin with zero components → When loadFromDirectory({ strict: true }) → Then throws ManifestValidationError

### T-009: Stale version dir health check in plugins-checker
**User Story**: US-003 | **Satisfies ACs**: AC-US3-02 | **Status**: [x] completed
**Test Plan**: Given plugin with 2 version dirs → When check runs → Then returns warn status
