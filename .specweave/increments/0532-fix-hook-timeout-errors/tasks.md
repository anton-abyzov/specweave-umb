# Tasks: Fix PostToolUse/PreToolUse Edit Hook Errors

## Phase 1: Fix PreToolUse Crash Bug

### T-001: Fix `set -e` in pre-tool-use.sh
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02 | **Status**: [x] completed

Change `set -e` to `set +e` in `pre-tool-use.sh` to match all other hook scripts' non-blocking pattern.

**File**: `repositories/anton-abyzov/specweave/plugins/specweave/hooks/v2/dispatchers/pre-tool-use.sh`

**Test Plan**:
- Given pre-tool-use.sh is executed
- When jq fails or stdin parsing has issues
- Then the script does not crash and returns `{"decision":"allow"}`

## Phase 2: Fix PostToolUse Timeout

### T-002: Add timeout override for post-tool-use.sh in fail-fast-wrapper.sh
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01 | **Status**: [x] completed

Add `post-tool-use.sh` to the timeout case statement with 15s timeout.

**File**: `repositories/anton-abyzov/specweave/plugins/specweave/hooks/universal/fail-fast-wrapper.sh`

**Test Plan**:
- Given fail-fast-wrapper.sh wraps post-tool-use.sh
- When post-tool-use.sh runs its synchronous + background work
- Then it has 15s instead of 5s to complete

### T-003: Move task-ac-sync-guard.sh to background execution
**User Story**: US-002 | **Satisfies ACs**: AC-US2-02, AC-US2-03, AC-US2-04 | **Status**: [x] completed

Change `safe_run_sync` to `safe_run_background` for task-ac-sync-guard.sh in post-tool-use.sh.

**File**: `repositories/anton-abyzov/specweave/plugins/specweave/hooks/v2/dispatchers/post-tool-use.sh`

**Test Plan**:
- Given a task is marked complete in tasks.md
- When post-tool-use.sh dispatches task-ac-sync-guard.sh
- Then it runs in background (non-blocking)
- And AC checkboxes in spec.md are still updated correctly

## Phase 3: Deploy

### T-004: Refresh plugin cache
**User Story**: US-001, US-002 | **Satisfies ACs**: AC-US1-02, AC-US2-03 | **Status**: [x] completed

Run `specweave refresh-plugins` to propagate source changes to `~/.claude/plugins/cache/`.
