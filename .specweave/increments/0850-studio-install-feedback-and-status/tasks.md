# Tasks — 0850

### T-001: Scope-aware path in InstallTargetsModal
**Satisfies**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04 | **Status**: [ ] pending
**Test**: Given scope=project When modal renders Then each row shows agent.resolvedLocalDir. Given scope=user Then shows resolvedGlobalDir.

### T-002: Persistent done phase
**Satisfies**: AC-US2-01, AC-US2-02 | **Status**: [ ] pending
**Test**: Given install succeeds When phase transitions to done Then modal stays mounted and footer shows Done button.

### T-003: Server-side install logging
**Satisfies**: AC-US2-04 | **Status**: [ ] pending
**Test**: Given multi-install job starts When job finishes Then console.log("[install]") appears twice (start + result) in server stdout.

### T-004: Copy path button on success rows
**Satisfies**: AC-US2-03 | **Status**: [ ] pending
**Test**: Given installed result When user clicks Copy path Then navigator.clipboard.writeText is called with the absolute path.

### T-005: Install-state fetch on modal mount
**Satisfies**: AC-US3-01 | **Status**: [ ] pending
**Test**: Given modal opens Then GET /api/studio/install-state?skill=… fires exactly once.

### T-006: Per-agent install-state badges
**Satisfies**: AC-US3-02, AC-US3-03, AC-US3-04 | **Status**: [ ] pending
**Test**: Given installed at target version Then "Installed v<X>". Given target > installed Then "Update v<old>→v<new>". Given target < installed Then "Newer v<installed>".

### T-007: Remove endpoint + route registration
**Satisfies**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04 | **Status**: [ ] pending
**Test**: Given valid POST Then 200 with removed/errors/skipped arrays. Given non-localhost Then 403. Given invalid agent id Then 400. Given last skill ref Then lockfile entry dropped.

### T-008: Remove link in already-installed rows
**Satisfies**: AC-US3-05 | **Status**: [ ] pending
**Test**: Given installed row When Remove clicked Then POST fires, row flips to "Not installed", server file removed.

### T-009: Build + restart studio + manual smoke
**Status**: [ ] pending
**Test**: Given fresh build When user installs appstore at project scope Then modal shows project path, persists done, badge flips to "Installed v<X>"; remove flips back to "Not installed".
