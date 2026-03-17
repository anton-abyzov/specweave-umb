---
increment: 0554-hook-reliability-phase2
tasks_total: 10
tasks_completed: 10
---

# Tasks: Fix Remaining Hook Reliability Issues

All work is in `repositories/anton-abyzov/specweave/plugins/specweave/`.
TDD mode active — every task must be RED→GREEN→REFACTOR before marking complete.

Implementation order (from plan.md): Fix 3 (jq guards) → Fix 4 (bare paths) → Fix 2 (dashboard normalization) → Fix 1 (PreToolUse + matcher_content).

---

## US-004: Null-coalescing for jq length operations

### T-001: Add `// []` null-coalescing to auto-status.sh jq length calls
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01
**Status**: [x] Completed
**Test**: Given auto-status.sh reads a session.json where `incrementQueue`, `completedIncrements`, and `failedIncrements` are all `null` or absent, when lines 132-134 execute, then `QUEUE_LENGTH`, `COMPLETED_COUNT`, and `FAILED_COUNT` all evaluate to `0` with no jq error exit

### T-002: Add `// []` null-coalescing to cancel-auto.sh and user-prompt-submit.sh
**User Story**: US-004 | **Satisfies ACs**: AC-US4-02, AC-US4-03
**Status**: [x] Completed
**Test**: Given cancel-auto.sh receives a session with null `completedIncrements` and user-prompt-submit.sh receives context_json with null `projects` and null `routing.skills`, when jq length is evaluated, then all return `0` without crashing — and the fix form is `.field // [] | length` (not the incorrect `.field | length // 0` pattern)

---

## US-005: Bare relative path elimination

### T-003: Add walk-up root detection to startup-health-check.sh
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01
**Status**: [x] Completed
**Test**: Given startup-health-check.sh is invoked with `PWD` set to a subdirectory three levels below the project root, when the script initializes, then it walks up to find `.specweave/`, sets `PROJECT_ROOT`, and all subsequent `.specweave/` references (including `AUTO_MODE_FILE` and `STATE_DIR`) use `$PROJECT_ROOT` as prefix with no path errors

### T-004: Add walk-up root detection to status-completion-guard.sh
**User Story**: US-005 | **Satisfies ACs**: AC-US5-02
**Status**: [x] Completed
**Test**: Given status-completion-guard.sh runs from a subdirectory, when the script initializes, then `AUTO_STATE_FILE` and `DONE_MARKER` are constructed with the detected `$_ROOT` prefix rather than bare `.specweave/` — and the guard reads the correct files under the actual project root

### T-005: Add walk-up root detection to increment-existence-guard.sh
**User Story**: US-005 | **Satisfies ACs**: AC-US5-03
**Status**: [x] Completed
**Test**: Given increment-existence-guard.sh runs from `repositories/anton-abyzov/specweave/` while the project root is three directories up, when the guard reaches the `find` commands for spec.md files, then it uses `"$_ROOT/.specweave/increments"` as the base path and correctly discovers increment spec files

---

## US-002: Dashboard cache normalization and fallback path

### T-006: Add normalize_type_key and normalize_priority_key to update-dashboard-cache.sh
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02
**Status**: [x] Completed
**Test**: Given update-dashboard-cache.sh processes a metadata.json with `priority: "medium"` and `type: "enhancement"`, when normalization runs, then the type counter key is `feature` and the priority counter key is `P1` — matching rebuild-dashboard-cache.sh output with no phantom keys like `byType["enhancement"]` or `byPriority["medium"]`

### T-007: Fix rebuild fallback path in update-dashboard-cache.sh to use BASH_SOURCE
**User Story**: US-002 | **Satisfies ACs**: AC-US2-03
**Status**: [x] Completed
**Test**: Given update-dashboard-cache.sh is invoked with no cache file present and `PROJECT_ROOT` is unset, when the rebuild fallback branch executes, then the path is resolved via `$(dirname "${BASH_SOURCE[0]}")` pointing to the scripts/ directory and rebuild-dashboard-cache.sh is called without a "file not found" error

---

## US-003: matcher_content false positive elimination

### T-008: Scope PostToolUse matcher_content in hooks.json and settings.json
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-03, AC-US3-04
**Status**: [x] Completed
**Test**: Given hooks.json PostToolUse and `.claude/settings.json` both have `matcher_content: "\\.specweave/increments/"`, when updated, then both use `"file_path"\\s*:\\s*"[^"]*\\.specweave/increments/"` — and a Write payload whose *content* (not file_path) contains `.specweave/increments/0001-foo` does not match the updated regex

---

## US-001: PreToolUse matcher_content and early file_path exit

### T-009: Add matcher_content to PreToolUse entry in hooks.json
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US3-02
**Status**: [x] Completed
**Test**: Given hooks.json has a PreToolUse `Write|Edit` entry with no `matcher_content`, when the file is updated, then a `matcher_content` field with the file_path-scoped regex `"file_path"\\s*:\\s*"[^"]*\\.specweave/increments/` is present on that entry and the JSON remains valid

### T-010: Replace bare path check and add early exit in pre-tool-use.sh
**User Story**: US-001, US-005 | **Satisfies ACs**: AC-US1-02, AC-US1-03, AC-US5-04
**Status**: [x] Completed
**Test**: Given pre-tool-use.sh is invoked from a subdirectory and INPUT contains a file_path outside `.specweave/increments/`, when the script executes, then (1) it locates project root via a walk-up loop capped at 50 iterations, (2) exits code 0 before any jq invocation, and (3) when no `.specweave/` ancestor exists at all, walk-up terminates at filesystem root and the script exits allowing the operation
