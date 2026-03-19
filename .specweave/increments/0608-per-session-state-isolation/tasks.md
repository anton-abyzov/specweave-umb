# Tasks

## Phase 1: Foundation

### T-001: Add parseHookInput() to platform.ts
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 | **Status**: [ ] pending
**Test**: Given hook stdin contains JSON with session_id -> When parseHookInput() is called -> Then it returns typed object with session_id

### T-002: Create SessionStateManager class
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03, AC-US1-04, AC-US1-05 | **Status**: [ ] pending
**Test**: Given a session_id -> When createSessionDir() is called -> Then per-session directory with lock.json is created

### T-003: Tests for SessionStateManager
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03, AC-US1-04 | **Status**: [ ] pending
**Test**: Given dead session dirs exist -> When gcDeadSessions() runs -> Then dead sessions are removed

## Phase 2: Wiring + Locking

### T-004: Update session-start.ts to use parseHookInput
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03 | **Status**: [ ] pending
**Test**: Given SessionStart hook fires with session_id in stdin -> When hook runs -> Then session dir is created and env is bridged

### T-005: Tests for session-start hook
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02 | **Status**: [ ] pending
**Test**: Given session_id in stdin -> When session-start runs -> Then CLAUDE_SESSION_ID written to env_file

### T-006: Fix shouldSkipLocks() in lock-manager.ts
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01 | **Status**: [ ] pending
**Test**: Given VSCODE_PID is set -> When LockManager is created -> Then locks are NOT skipped

### T-007: Update lock-manager tests
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01 | **Status**: [ ] pending
**Test**: Given VSCode environment -> When acquire() is called -> Then lock is actually acquired

### T-008: Extract FileLock to src/utils/file-lock.ts
**User Story**: US-002 | **Satisfies ACs**: AC-US2-03 | **Status**: [ ] pending
**Test**: Given FileLock imported from utils/file-lock -> When acquire/release called -> Then locking works correctly

### T-009: Protect ActiveIncrementManager.writeState() with FileLock
**User Story**: US-002 | **Satisfies ACs**: AC-US2-02 | **Status**: [ ] pending
**Test**: Given concurrent writeState calls -> When both execute -> Then no data corruption

### T-010: Update active-increment-manager tests
**User Story**: US-002 | **Satisfies ACs**: AC-US2-02 | **Status**: [ ] pending
**Test**: Given FileLock wrapping writeState -> When test runs -> Then locking behavior verified

## Phase 3: Per-Session Auto Mode

### T-011: Add sessionId to AutoModeFlag type
**User Story**: US-003 | **Satisfies ACs**: AC-US3-02 | **Status**: [ ] pending
**Test**: Given AutoModeFlag -> When sessionId field set -> Then type accepts it

### T-012: Update auto.ts for per-session auto-mode.json
**User Story**: US-001 | **Satisfies ACs**: AC-US1-05 | **Status**: [ ] pending
**Test**: Given CLAUDE_SESSION_ID env var set -> When auto command runs -> Then auto-mode.json written to per-session dir

### T-013: Update cancel-auto.ts for per-session cleanup
**User Story**: US-001 | **Satisfies ACs**: AC-US1-06 | **Status**: [ ] pending
**Test**: Given CLAUDE_SESSION_ID env var set -> When cancel-auto runs -> Then per-session state cleaned

### T-014: Update auto-status.ts for per-session state
**User Story**: US-001 | **Satisfies ACs**: AC-US1-07 | **Status**: [ ] pending
**Test**: Given CLAUDE_SESSION_ID env var set -> When auto-status runs -> Then per-session state shown

### T-015: Update stop-auto-v5.sh for session-aware stop
**User Story**: US-001 | **Satisfies ACs**: AC-US1-08 | **Status**: [ ] pending
**Test**: Given session_id in stdin -> When stop hook fires -> Then per-session auto-mode.json checked first

### T-016: Tests for auto command per-session changes
**User Story**: US-001 | **Satisfies ACs**: AC-US1-05, AC-US1-06, AC-US1-07 | **Status**: [ ] pending
**Test**: Given per-session auto mode -> When auto/cancel-auto/auto-status run -> Then per-session paths used

### T-017: Tests for stop hook per-session changes
**User Story**: US-001 | **Satisfies ACs**: AC-US1-08 | **Status**: [ ] pending
**Test**: Given session_id available -> When stop hook runs -> Then per-session auto-mode.json takes priority
