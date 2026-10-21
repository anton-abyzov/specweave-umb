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

### T-010: Correct per-agent membership and semantic-version status
- AC: AC-US3-02, AC-US3-03, AC-US3-04, AC-US3-05, AC-US4-04 | Files: repositories/anton-abyzov/vskill/src/eval-server/install-state-routes.ts, repositories/anton-abyzov/vskill/src/eval-server/remove-skill-routes.ts, repositories/anton-abyzov/vskill/src/eval-server/installed-skill-paths.ts, repositories/anton-abyzov/vskill/src/eval-server/__tests__/, repositories/anton-abyzov/vskill/src/eval-ui/src/components/InstallTargetsModal.tsx, repositories/anton-abyzov/vskill/src/eval-ui/src/components/__tests__/, repositories/anton-abyzov/vskill/src/eval-ui/src/utils/ | Test: cd /Users/antonabyzov/.specwithcode/m4/worktrees/vskill-0850-status-completion && PATH=/Users/antonabyzov/.nvm/versions/node/v22.20.0/bin:$PATH npx vitest run src/eval-server/__tests__/install-state-routes.test.ts src/eval-server/__tests__/remove-skill-routes.test.ts src/eval-ui/src/components/__tests__/InstallTargetsModal.test.tsx --maxWorkers=1 --no-file-parallelism

Fresh review on October 21, 2026 found that scope-wide lock agents falsely mark a removed skill installed when another skill remains, and prerelease/build suffixes produce incorrect update badges. Use actual per-agent files with shared-reader semantics, correct SemVer precedence, and fixtures covering remove followed by refresh. Prior completed tasks remain historical; this is an additive correction.

### T-011: Verify and close 0850
- AC: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04, AC-US3-05, AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04 | Files: .specweave/increments/0850-studio-install-feedback-and-status/reports/ | Test: cd /Users/antonabyzov/.specwithcode/m4/worktrees/vskill-0850-status-completion && PATH=/Users/antonabyzov/.nvm/versions/node/v22.20.0/bin:$PATH npm run build
- Dependencies: T-010

Require fresh-context acceptance review, scoped coverage, built-UI headless smoke, and the project-required manual UI acceptance before recording completion. Coordinate the release owner and retain all worktrees under the incident cleanup hold. Verify and close 0850.
