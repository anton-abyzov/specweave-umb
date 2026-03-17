---
increment: 0552-hook-error-reliability
generated: 2026-03-16
---

# Tasks: Fix Hook Error Reliability

## US-001: Null-Safe Dashboard Cache Updates

### T-001: Add null-coalescing to all 6 jq decrement operations
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03
**Status**: [x] completed
**Test**: Given `update-dashboard-cache.sh` is run against a cache JSON with one or more missing summary keys → When the script executes all 6 decrement operations → Then each uses `(.summary[$key] // 0) - 1` and produces no jq errors; existing non-null counters decrement correctly

---

## US-002: Scoped PostToolUse Hook for Increment Files

### T-002: Add matcher_content to close-completed-issues.sh hook config
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03
**Status**: [x] completed
**Test**: Given `.claude/settings.json` PostToolUse config for `close-completed-issues.sh` → When `matcher_content: ".specweave/increments/"` is added → Then editing a file outside `.specweave/increments/` does not trigger the hook, and editing `.specweave/increments/*/tasks.md` does trigger it

---

## US-003: Remove Dead Hook Config Entry

### T-003: Delete ac-status-sync.sh entry from settings.json, preserve script file
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02
**Status**: [x] completed
**Test**: Given `.claude/settings.json` contains a hook entry for `ac-status-sync.sh` → When the config entry is removed → Then grep for `ac-status-sync` in settings.json returns no results, and the `ac-status-sync.sh` script file still exists on disk

---

## US-004: Reset Stuck Circuit Breaker

### T-004: Delete stuck circuit breaker state file
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02
**Status**: [x] completed
**Test**: Given `.specweave/state/.hook-circuit-breaker-github-auto-create` contains value "3" → When `rm -f` is run on the file → Then the file no longer exists and a subsequent GitHub auto-create hook invocation is not short-circuited

---

## US-005: Remove Hookify Plugin Overhead

### T-005: Remove all hookify hook entries from project config
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01, AC-US5-02
**Status**: [x] completed
**Test**: Given `.claude/settings.json` contains hookify PreToolUse/PostToolUse entries → When all hookify entries are removed → Then grep for `hookify` in settings.json returns no results and no Python processes are spawned during subsequent tool calls

---

## US-006: NPM Patch Release

### T-006: Bump specweave package.json to 1.0.492 and publish
**User Story**: US-006 | **Satisfies ACs**: AC-US6-01, AC-US6-02
**Status**: [x] completed
**Test**: Given all fixes from T-001 through T-005 are applied → When `package.json` version is updated to "1.0.492" and the package is published → Then `npm show specweave version` returns "1.0.492" and the published package includes all five fixes with no feature flags
