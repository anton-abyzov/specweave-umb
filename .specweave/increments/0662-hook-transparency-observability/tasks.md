# Tasks: Hook Transparency & Observability

## Phase 1: Semantic Prefixes + Cleanup (parallel)

### T-001: Add [GUARD]/[ERROR] semantic prefixes to hook-router
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04 | **Status**: [x] Completed
**Test Plan**:
- Given a handler returns `{decision: "block", reason: "..."}` normally
- When hook-router processes the result
- Then the reason is prefixed with `[GUARD]`
- Given a handler throws an exception
- When hook-router catches it
- Then the fallback reason is prefixed with `[ERROR]`
- Given pre-tool-use guards (status-completion, interview, increment-existence) block
- When the block flows through hook-router
- Then all carry `[GUARD]` prefix consistently
**Files**: `src/core/hooks/handlers/hook-router.ts`, `tests/unit/core/hooks/handlers/hook-router.test.ts`

### T-002: Fix ghost check-hooks references
**User Story**: US-006 | **Satisfies ACs**: AC-US6-01, AC-US6-03, AC-US6-04 | **Status**: [x] Completed
**Test Plan**:
- Given the codebase contains references to `check-hooks`
- When all stale references are replaced with `specweave hooks health`
- Then `grep -r "check-hooks" src/` returns zero matches
**Files**: `src/core/hooks/hook-health-tracker.ts`, `src/core/hooks/hook-logger.ts`, `src/core/hooks/hooks-checker.ts`

### T-003: Fix CLAUDE.md docs URL
**User Story**: US-006 | **Satisfies ACs**: AC-US6-02 | **Status**: [x] Completed
**Test Plan**:
- Given CLAUDE.md references `verified-skill.com` for docs
- When the URL is updated
- Then it references `spec-weave.com`
**Files**: `CLAUDE.md` (umbrella root)

## Phase 2: Structured Logging

### T-004: Wire HookLogger into hook-router for structured logging
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-03, AC-US2-04 | **Status**: [x] Completed
**Test Plan**:
- Given a hook executes (block or allow)
- When hook-router processes the result
- Then HookLogger.log() is called with hookName, decision, durationMs, toolName
- Given the structured log entry is written
- Then it contains timestamp, hookName, handler, decision, durationMs, reason (if blocked), toolName
- Given HookLogger is imported in hook-router
- Then no new npm dependencies are introduced
**Files**: `src/core/hooks/handlers/hook-router.ts`, `tests/unit/core/hooks/handlers/hook-router.test.ts`
**Dependencies**: T-001

### T-005: Add dual-write to logHook() in utils.ts
**User Story**: US-002 | **Satisfies ACs**: AC-US2-02 | **Status**: [x] Completed
**Test Plan**:
- Given logHook() is called with handler name and message
- When it writes the log entry
- Then it writes plaintext to hooks.log (backwards compat) AND structured JSON via HookLogger
**Files**: `src/core/hooks/handlers/utils.ts`, `tests/unit/core/hooks/handlers/utils-dual-write.test.ts`
**Dependencies**: T-004

## Phase 3: CLI Commands

### T-006: Create hooks-cmd.ts with `specweave hooks log` command
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04, AC-US3-05 | **Status**: [x] Completed
**Test Plan**:
- Given logs exist, when `hooks log` runs, then last 20 entries displayed in table format
- Given `--blocks-only` flag, when filtering, then only block decisions shown
- Given `--errors-only` flag, when filtering, then only [ERROR] entries shown
- Given `--last 5` flag, then exactly 5 entries shown
- Given `--hook pre-tool-use` flag, then only that hook's entries shown
**Files**: `src/cli/commands/hooks-cmd.ts`, `tests/unit/cli/commands/hooks-cmd.test.ts`
**Dependencies**: T-004, T-005

### T-007: Add `specweave hooks health` command
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04 | **Status**: [x] Completed
**Test Plan**:
- Given structured logs exist, when `hooks health` runs, then health report via HookHealthTracker + HealthReporter
- Given a hook has >90% success, then status shows OK
- Given a hook has 50-90% success, then status shows DEGRADED with recommendations
- Given no logs exist, then informative empty-state message displayed
**Files**: `src/cli/commands/hooks-cmd.ts`, `tests/unit/cli/commands/hooks-cmd.test.ts`
**Dependencies**: T-006

### T-008: Add `specweave hooks ls` command
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01, AC-US5-02, AC-US5-03, AC-US5-04 | **Status**: [x] Completed
**Test Plan**:
- Given plugin hooks exist, when `hooks ls` runs, then table with name, plugin, trigger type, critical flag
- Given HookScanner discovers hooks, when ls executes, then it uses HookScanner (no duplicate logic)
- Given no manifest file exists, when ls runs, then falls back to live scanning without error
- Given hooks are discovered, then output grouped by trigger type
**Files**: `src/cli/commands/hooks-cmd.ts`, `tests/unit/cli/commands/hooks-cmd.test.ts`
**Dependencies**: T-006

### T-009: Register hooks command group in bin/specweave.js
**User Story**: US-003, US-004, US-005 | **Satisfies ACs**: AC-US3-01, AC-US4-01, AC-US5-01 | **Status**: [x] Completed
**Test Plan**:
- Given the CLI is loaded
- When user runs `specweave hooks log|health|ls`
- Then the correct subcommand is dispatched
**Files**: `bin/specweave.js`
**Dependencies**: T-006, T-007, T-008

## Phase 4: Verification

### T-010: Integration test — semantic prefixes end-to-end
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02 | **Status**: [x] Completed
**Test Plan**:
- Given a full hook pipeline (stdin → hook-router → handler → stdout)
- When a guard blocks, then output JSON contains `[GUARD]` in reason
- When a handler throws, then output JSON contains `[ERROR]` in reason
**Files**: `tests/unit/core/hooks/handlers/hook-router.test.ts`
**Dependencies**: T-001, T-004

### T-011: Integration test — structured logging produces queryable data
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02 | **Status**: [x] Completed
**Test Plan**:
- Given hooks execute through the router
- When HookLogger writes entries
- Then HookHealthTracker.analyzeAll() returns valid health data
**Files**: `tests/unit/core/hooks/hooks-logging-integration.test.ts`
**Dependencies**: T-004, T-005

### T-012: Verify zero check-hooks references remain
**User Story**: US-006 | **Satisfies ACs**: AC-US6-03 | **Status**: [x] Completed
**Test Plan**:
- Given all cleanup is complete
- When grepping `src/` for `check-hooks`
- Then zero matches found
**Files**: `tests/unit/core/hooks/ghost-command-references.test.ts`
**Dependencies**: T-002
