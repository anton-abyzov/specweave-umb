# Tasks: CLI-First Hook Architecture Rework

## Coverage Summary

| User Story | ACs | Tasks |
|---|---|---|
| US-001: Trim Hook Registrations | AC-US1-01, AC-US1-02, AC-US1-03 | T-001, T-002 |
| US-002: Hook Router Reduction | AC-US2-01, AC-US2-02, AC-US2-03 | T-003 |
| US-003: CLI Session Start | AC-US3-01..05 | T-004, T-005 |
| US-004: CLI Session End | AC-US4-01..04 | T-006, T-007 |
| US-005: CLI Sync Flush | AC-US5-01..03 | T-008, T-009 |
| US-006: CLI Analytics Push | AC-US6-01..03 | T-010, T-011 |
| US-007: Fix Error Logging | AC-US7-01..03 | T-012 |
| US-008: Test Log Isolation | AC-US8-01..02 | T-013 |
| US-009: Delete Stale Shell Tests | AC-US9-01..02 | T-014 |
| US-010: Update AGENTS.md | AC-US10-01..02 | T-015 |

---

## Phase 1: Core Logic Extraction

### T-001: Extract core modules for session lifecycle, event queue, and analytics writer
**User Story**: US-001, US-003, US-004, US-005, US-006 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04, AC-US3-05, AC-US4-01, AC-US4-02, AC-US4-03, AC-US5-01, AC-US5-02, AC-US6-01, AC-US6-02
**Status**: [ ] Not Started

Extract business logic from existing hook handlers into reusable core modules:

1. `src/core/session/session-lifecycle.ts` — extract from `src/core/hooks/handlers/session-start.ts`: stale auto-mode file cleanup (>24h), context-pressure.json + prompt-health-alert.json reset, baseline prompt health check + prompt-health.json write, per-session state dir creation via `session-state-manager.ts`, orphaned state file cleanup via `state-cleanup.ts`.

2. `src/core/session/reflect-checker.ts` — extract from `src/core/hooks/handlers/stop-reflect.ts`: read reflect config, log reflection intent when enabled.

3. `src/core/session/auto-scanner.ts` — extract from `src/core/hooks/handlers/stop-auto.ts`: scan pending tasks, log auto-mode state.

4. `src/core/sync/event-queue-ops.ts` — NOTE: `src/core/sync/event-queue.ts` already exists; create a new `event-queue-ops.ts` alongside it. Extract from `src/core/hooks/handlers/post-tool-use.ts` (queue append) and `src/core/hooks/handlers/stop-sync.ts` (flush + dedup by increment ID + clear).

5. `src/core/analytics/event-writer.ts` — extract from `src/core/hooks/handlers/post-tool-use-analytics.ts`: append skill/agent analytics events to `events.jsonl` with timestamp and plugin extraction.

All modules must be idempotent and never throw — catch and log errors, return gracefully.

**Test**: Given each existing handler file contains its business logic, when the core module is created and its unit tests run, then all functions produce identical outputs to the original handler for the same inputs and achieve 95%+ line coverage.

- **File**: `tests/unit/core/session/session-lifecycle.test.ts`, `tests/unit/core/session/reflect-checker.test.ts`, `tests/unit/core/session/auto-scanner.test.ts`, `tests/unit/core/sync/event-queue-ops.test.ts`, `tests/unit/core/analytics/event-writer.test.ts`
- **TC-001**: Given stale auto-mode files older than 24h exist in `.specweave/state/`, when `clearStaleAutoFiles()` is called, then those files are deleted and newer files are untouched.
- **TC-002**: Given `context-pressure.json` and `prompt-health-alert.json` exist, when `resetPressureFiles()` is called, then both files are removed or zeroed.
- **TC-003**: Given a fresh state dir, when `writeBaselineHealth()` is called, then `prompt-health.json` is created with valid JSON.
- **TC-004**: Given `--session-id abc123`, when `createSessionDir('abc123', stateDir)` is called, then a subdirectory `sessions/abc123/` is created under stateDir.
- **TC-005**: Given orphaned state files exist, when `cleanOrphaned()` is called, then they are removed without affecting valid state files.
- **TC-006**: Given reflect config has `enabled: true`, when `checkReflectConfig(configPath)` is called, then it returns `{ enabled: true }` and logs the intent.
- **TC-007**: Given reflect config has `enabled: false`, when `checkReflectConfig(configPath)` is called, then it returns `{ enabled: false }` and does not log.
- **TC-008**: Given a tasks dir with pending incomplete tasks, when `scanPendingTasks(projectRoot)` is called, then it returns an array of pending task descriptions.
- **TC-009**: Given `pending.jsonl` has 3 events for 2 distinct increment IDs, when `flushEventQueue(stateDir)` is called, then the queue is deduplicated to 2 unique increment IDs and the file is truncated.
- **TC-010**: Given `pending.jsonl` is empty, when `flushEventQueue(stateDir)` is called, then it returns `{ flushed: 0 }` with no error.
- **TC-011**: Given an event `{ type: 'skill', name: 'sw:pm', plugin: 'specweave' }`, when `appendAnalyticsEvent(analyticsDir, event)` is called, then `events.jsonl` gains one line of valid JSON with timestamp.
- **TC-012**: Given analytics dir does not exist, when `appendAnalyticsEvent(missingDir, event)` is called, then the directory is created and the event is written.

---

## Phase 2: New CLI Commands

### T-002: Trim generate-settings.ts — emit only PreToolUse and UserPromptSubmit hooks
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03
**Status**: [ ] Not Started

Modify `src/hooks/generate-settings.ts`:

1. Remove all entries from `COMMAND_EVENTS` array (or delete the constant entirely) — SessionStart, SessionEnd, Notification, SubagentStart, ConfigChange, PreCompact, TeammateIdle must no longer emit hook entries.
2. Trim `HTTP_EVENTS` to only `['PreToolUse', 'UserPromptSubmit']` — remove PostToolUse, Stop, SubagentStop, TaskCompleted, PostToolUseFailure, PermissionRequest.
3. In `writeSettings()`, actively remove stale hook keys from the merged output. Before writing, iterate the merged `hooks` object and delete any key that is not `PreToolUse` or `UserPromptSubmit`.

**Test**: Given `src/hooks/generate-settings.ts` and its existing test suite at `tests/unit/hooks/`, when `generateHooksSettings()` runs with httpMode true, then only PreToolUse and UserPromptSubmit keys appear in the returned hooks object, and when `writeSettings()` runs against a settings.json containing old hook keys (PostToolUse, Stop, SessionStart), then those keys are absent in the written output.

- **File**: `tests/unit/hooks/generate-settings.test.ts`
- **TC-001**: Given `httpMode: true` in config, when `generateHooksSettings()` runs, then the returned `hooks` object has exactly 2 keys: `PreToolUse` and `UserPromptSubmit`.
- **TC-002**: Given `httpMode: true`, when `generateHooksSettings()` runs, then no COMMAND_EVENTS keys appear in the output (no SessionStart, PreCompact, etc.).
- **TC-003**: Given an existing `settings.json` containing `{ hooks: { PostToolUse: [...], Stop: [...], SessionStart: [...], PreToolUse: [...], UserPromptSubmit: [...] } }`, when `writeSettings()` runs, then the written file contains only `PreToolUse` and `UserPromptSubmit` under `hooks`.
- **TC-004**: Given `httpMode: false` in config, when `generateHooksSettings()` runs, then it returns `{}` (unchanged behavior).

---

### T-003: Trim hook-router.ts and types.ts — retain only pre-tool-use and user-prompt-submit
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03
**Status**: [ ] Not Started

**Depends on**: T-004, T-006, T-008, T-010 (CLI commands must exist before handlers are removed)

Modify `src/core/hooks/handlers/hook-router.ts`:
- Remove entries for `post-tool-use`, `post-tool-use-analytics`, `session-start`, `pre-compact`, `stop-reflect`, `stop-auto`, `stop-sync` from the `HANDLERS` map.
- Keep only `user-prompt-submit` and `pre-tool-use`.

Modify `src/core/hooks/handlers/types.ts`:
- Remove `post-tool-use`, `post-tool-use-analytics`, `session-start`, `pre-compact`, `stop-reflect`, `stop-auto`, `stop-sync` from the `HookEventType` union.
- Keep only `user-prompt-submit` and `pre-tool-use`.
- Remove the 7 corresponding entries from `SAFE_DEFAULTS` map.

Delete handler files (after CLI commands are in place):
- `src/core/hooks/handlers/post-tool-use.ts`
- `src/core/hooks/handlers/post-tool-use-analytics.ts`
- `src/core/hooks/handlers/session-start.ts`
- `src/core/hooks/handlers/pre-compact.ts`
- `src/core/hooks/handlers/stop-reflect.ts`
- `src/core/hooks/handlers/stop-auto.ts`
- `src/core/hooks/handlers/stop-sync.ts`

Update `src/core/hooks/handlers/index.ts` to remove barrel exports for deleted files.

**Test**: Given the modified `hook-router.ts` and `types.ts`, when the router is inspected and unit-tested, then it contains exactly 2 handler entries and 2 type entries, and calling the router with a removed event type returns the safe default without crashing.

- **File**: `tests/unit/hooks/hook-router.test.ts`
- **TC-001**: Given the HANDLERS map, when inspected at runtime, then it has exactly 2 keys: `pre-tool-use` and `user-prompt-submit`.
- **TC-002**: Given the HookEventType union in types.ts, when inspected, then it contains exactly `pre-tool-use` and `user-prompt-submit`.
- **TC-003**: Given the SAFE_DEFAULTS map, when inspected, then it contains exactly 2 entries matching the remaining hook types.
- **TC-004**: Given `hookRouter('session-start', '{}')` is called after removal, when it runs, then it returns `{ continue: true }` (safe default) without throwing.
- **TC-005**: Given `hookRouter('pre-tool-use', validInput)` is called, when it runs, then it still routes correctly to the pre-tool-use handler.

---

### T-004: Create `specweave session start` CLI command
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04, AC-US3-05
**Status**: [ ] Not Started

**Depends on**: T-001 (core session-lifecycle module must exist)

Create `src/cli/commands/session.ts` implementing the `session` Commander group with `start`, `end`, and `compact` subcommands. This task covers `start` only (see T-006 for `end`).

The `start` subcommand must:
1. Import from `src/core/session/session-lifecycle.ts`
2. Call `clearStaleAutoFiles(stateDir)` (files older than 24h)
3. Call `resetPressureFiles(stateDir)` (context-pressure.json + prompt-health-alert.json)
4. Call `writeBaselineHealth(stateDir)` (prompt-health.json)
5. Accept `--session-id <id>` flag and call `createSessionDir(sessionId, stateDir)` when provided
6. Call `cleanOrphaned(stateDir)` to remove orphaned state files
7. Output human-readable status by default; `--json` emits `SessionCommandResult` JSON
8. Exit 0 on success, 1 on error (never crash)

Register `session` command in `bin/specweave.js` (or whichever main entrypoint registers commands).

**Test**: Given `src/cli/commands/session.ts` with a temp `.specweave/state/` dir, when `specweave session start` runs, then all 5 initialization steps execute and exit 0.

- **File**: `tests/unit/cli/commands/session.test.ts`
- **TC-001**: Given stale auto-mode files in state dir, when `sessionCommand('start', { projectRoot })` runs, then files older than 24h are deleted and exit code is 0.
- **TC-002**: Given `context-pressure.json` exists, when `sessionCommand('start', { projectRoot })` runs, then context-pressure.json is removed/reset.
- **TC-003**: Given a fresh state dir, when `sessionCommand('start', { projectRoot })` runs, then `prompt-health.json` is written with valid JSON.
- **TC-004**: Given `--session-id test-session-42`, when `sessionCommand('start', { projectRoot, sessionId: 'test-session-42' })` runs, then `sessions/test-session-42/` directory exists under stateDir.
- **TC-005**: Given orphaned state files, when `sessionCommand('start', { projectRoot })` runs, then orphaned files are cleaned.
- **TC-006**: Given `--json` flag, when `sessionCommand('start', { projectRoot, json: true })` runs, then stdout is valid `SessionCommandResult` JSON with `action: 'start'` and `success: true`.
- **TC-007**: Given `.specweave/` does not exist, when `sessionCommand('start', { projectRoot: '/missing' })` runs, then it exits with code 1 and prints an informative error message (does not crash).

---

### T-005: Unit tests for session start — integration with real filesystem
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04, AC-US3-05
**Status**: [ ] Not Started

**Depends on**: T-004

Write integration-level tests for `session start` using real temp directories (no mocks for fs operations). Tests must use `fs.mkdtempSync` or `os.tmpdir()` for isolation and clean up in `afterEach`.

**Test**: Given a real temp filesystem with a `.specweave/state/` directory, when each `session start` scenario is exercised end-to-end, then file system state matches expected outcomes and no files leak to other test runs.

- **File**: `tests/integration/cli/session-start.test.ts`
- **TC-001**: Given a temp project dir with stale auto-mode JSON files (mtime = 25h ago), when `specweave session start` runs, then files are gone and newer files are untouched.
- **TC-002**: Given a temp project dir, when `specweave session start --session-id s1` then `specweave session start --session-id s2` run sequentially, then both `sessions/s1/` and `sessions/s2/` exist independently.
- **TC-003**: Given a temp project dir, when `specweave session start` runs twice (idempotency check), then both runs succeed with exit 0 and no duplicate state corruption.

---

### T-006: Create `specweave session end` CLI command
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04
**Status**: [ ] Not Started

**Depends on**: T-001 (reflect-checker and auto-scanner modules must exist)

Add `end` subcommand to `src/cli/commands/session.ts`:

1. Import from `src/core/session/reflect-checker.ts` and `src/core/session/auto-scanner.ts`
2. Call `checkReflectConfig(configPath)` and log reflection intent if enabled (stop-reflect logic)
3. Call `scanPendingTasks(projectRoot)` and log pending task count if auto-mode is active (stop-auto logic)
4. Call `flushEventQueue(stateDir)` from `src/core/sync/event-queue-ops.ts` to deduplicate and clear pending.jsonl (stop-sync logic)
5. All 3 sub-operations run sequentially; errors in one do not abort the others
6. Exit 0 always (same contract as the old Stop hooks)

**Test**: Given `src/cli/commands/session.ts` end subcommand with temp dirs, when `specweave session end` runs under various state conditions, then all three sub-operations complete and the process exits 0.

- **File**: `tests/unit/cli/commands/session.test.ts` (extend existing file)
- **TC-001**: Given reflect config has `enabled: true`, when `sessionCommand('end', { projectRoot })` runs, then the reflect intent is logged to the session log.
- **TC-002**: Given an active auto-mode session with 3 pending tasks, when `sessionCommand('end', { projectRoot })` runs, then the auto-state scan log records 3 pending tasks.
- **TC-003**: Given `pending.jsonl` has 5 events across 3 increment IDs, when `sessionCommand('end', { projectRoot })` runs, then pending.jsonl is cleared and the log records 3 unique increments flushed.
- **TC-004**: Given all three sub-operations succeed, when `sessionCommand('end', { projectRoot })` runs, then process exits with code 0.
- **TC-005**: Given `checkReflectConfig` throws an error, when `sessionCommand('end', { projectRoot })` runs, then the error is logged but the other two sub-operations still run and exit is still 0.

---

### T-007: Integration tests for session end
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04
**Status**: [ ] Not Started

**Depends on**: T-006

Write integration-level tests for `session end` using real temp filesystem. Verify combined behavior.

**Test**: Given a real temp filesystem populated with reflect config, auto-mode state, and pending.jsonl, when `specweave session end` runs, then all three sub-operations produce correct file system outcomes.

- **File**: `tests/integration/cli/session-end.test.ts`
- **TC-001**: Given a temp project with reflect enabled and pending.jsonl having 2 events, when `specweave session end` runs, then pending.jsonl is empty and exit code is 0.
- **TC-002**: Given `specweave session end` runs on a project with no .specweave dir, then it exits 1 with an informative error.
- **TC-003**: Given `specweave session end` runs twice (idempotency), then both invocations exit 0 with no crash.

---

### T-008: Create `specweave sync flush` CLI command
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01, AC-US5-02, AC-US5-03
**Status**: [ ] Not Started

**Depends on**: T-001 (event-queue-ops module must exist)

Create `src/cli/commands/sync-flush.ts`:

1. Import from `src/core/sync/event-queue-ops.ts`
2. **Flush mode** (no `--queue` arg): Read `event-queue/pending.jsonl`, deduplicate by increment ID, log sync intent for each unique increment, truncate `pending.jsonl` to empty. Return `SyncFlushResult` with `mode: 'flush'`, `eventsFlushed`, `incrementIds`.
3. **Queue mode** (`--queue <json-string>`): Parse the JSON, append to `event-queue/pending.jsonl`. Return `SyncFlushResult` with `mode: 'queue'`, `eventsQueued: 1`.
4. **Dry-run mode** (`--dry-run`): Report what would be flushed without clearing the queue.
5. Handle missing `pending.jsonl` gracefully (treat as empty, no-op).
6. `--json` flag emits `SyncFlushResult` JSON; default is human-readable.
7. Exit 0 on success, 1 on error.

Register under the existing `sync` command group in the CLI entrypoint, or create a new `sync` group if one does not exist.

**Test**: Given `src/cli/commands/sync-flush.ts` with a temp state dir, when each flush/queue/dry-run scenario is exercised, then the correct file mutations occur and exit codes are correct.

- **File**: `tests/unit/cli/commands/sync-flush.test.ts`
- **TC-001**: Given `pending.jsonl` with 3 events for 2 increment IDs, when `syncFlushCommand({})` runs, then it deduplicates to 2 unique IDs, logs sync intent, and pending.jsonl is empty after the call.
- **TC-002**: Given empty `pending.jsonl`, when `syncFlushCommand({})` runs, then it returns `{ eventsFlushed: 0, incrementIds: [] }` and exits 0.
- **TC-003**: Given `{ queue: '{"event":"task.updated","incrementId":"0661"}' }`, when `syncFlushCommand({ queue: jsonStr })` runs, then pending.jsonl gains exactly one new line.
- **TC-004**: Given `pending.jsonl` with 5 events, when `syncFlushCommand({ dryRun: true })` runs, then it reports the events that would be flushed and pending.jsonl is unchanged.
- **TC-005**: Given missing `event-queue/` directory, when `syncFlushCommand({})` runs, then it returns `{ eventsFlushed: 0 }` with exit 0 (no crash).

---

### T-009: Integration tests for sync flush
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01, AC-US5-02, AC-US5-03
**Status**: [ ] Not Started

**Depends on**: T-008

Integration tests using real temp filesystem for `sync flush`.

**Test**: Given a real `.specweave/state/event-queue/pending.jsonl` populated with events, when `specweave sync flush` runs end-to-end, then the file system state matches expected outcomes with zero cross-test leakage.

- **File**: `tests/integration/cli/sync-flush.test.ts`
- **TC-001**: Given 4 events for 3 increments, when `specweave sync flush` runs, then pending.jsonl has 0 bytes after the call.
- **TC-002**: Given `specweave sync flush --queue` called 3 times with different events, then `specweave sync flush` flushes all 3 and pending.jsonl is empty.
- **TC-003**: Given `specweave sync flush --dry-run`, then a second `specweave sync flush` without dry-run still processes the original events (dry-run did not corrupt the queue).

---

### T-010: Create `specweave analytics push` CLI command
**User Story**: US-006 | **Satisfies ACs**: AC-US6-01, AC-US6-02, AC-US6-03
**Status**: [ ] Not Started

**Depends on**: T-001 (event-writer module must exist)

Create `src/cli/commands/analytics-push.ts`:

1. Import from `src/core/analytics/event-writer.ts`
2. Accept flags: `--type <skill|agent>` (required), `--name <string>` (required), `--plugin <string>` (optional)
3. If `--type` or `--name` are missing, exit code 1 and print usage help
4. Build an `AnalyticsEvent` with correct timestamp, extract plugin from `--plugin` flag (or from `--name` prefix for skill type if plugin not provided)
5. Call `appendAnalyticsEvent(analyticsDir, event)` — creates `analytics/` dir if missing
6. `--json` flag emits `AnalyticsPushResult` JSON; default is human-readable
7. Exit 0 on success, 1 on error

Register as `specweave analytics push` — extend the existing `analytics` command in `src/cli/commands/analytics.ts` or the CLI entrypoint.

**Test**: Given `src/cli/commands/analytics-push.ts` with a temp analytics dir, when each invocation scenario is run, then events.jsonl gains the correct entry or the correct error is raised.

- **File**: `tests/unit/cli/commands/analytics-push.test.ts`
- **TC-001**: Given `--type skill --name sw:pm`, when `analyticsPushCommand({ type: 'skill', name: 'sw:pm', projectRoot })` runs, then `events.jsonl` gains one line containing `"type":"skill"`, `"name":"sw:pm"`, and a valid ISO timestamp.
- **TC-002**: Given `--type skill --name sw:pm --plugin specweave`, when the command runs, then `events.jsonl` entry contains `"plugin":"specweave"`.
- **TC-003**: Given `--type agent --name general`, when the command runs, then `events.jsonl` gains one line containing `"type":"agent"`, `"name":"general"`.
- **TC-004**: Given missing `--type` flag, when the command runs, then it exits with code 1 and stdout/stderr contains usage help text.
- **TC-005**: Given missing `--name` flag, when the command runs, then it exits with code 1 and stdout/stderr contains usage help text.
- **TC-006**: Given analytics dir does not exist, when `analyticsPushCommand({ type: 'agent', name: 'explorer', projectRoot })` runs, then the directory is created and the event is written successfully.

---

### T-011: Integration tests for analytics push
**User Story**: US-006 | **Satisfies ACs**: AC-US6-01, AC-US6-02, AC-US6-03
**Status**: [ ] Not Started

**Depends on**: T-010

Integration tests for `specweave analytics push` using real temp filesystem.

**Test**: Given a real temp analytics directory, when `specweave analytics push` runs with various inputs, then `events.jsonl` grows correctly with valid JSONL and no cross-test contamination.

- **File**: `tests/integration/cli/analytics-push.test.ts`
- **TC-001**: Given 3 sequential `analytics push` calls with different names, when `events.jsonl` is read, then it has exactly 3 lines of valid JSON in order.
- **TC-002**: Given `analytics push` called twice in parallel (concurrent writes), then `events.jsonl` has 2 valid lines with no corruption (atomic append).

---

## Phase 3: Bug Fixes and Cleanup

### T-012: Fix empty catch blocks in hook handlers — add error logging
**User Story**: US-007 | **Satisfies ACs**: AC-US7-01, AC-US7-02, AC-US7-03
**Status**: [ ] Not Started

Audit and fix all empty or silent catch blocks across hook handler files. Files to update:

- `src/core/hooks/handlers/hook-router.ts` — ensure the outer catch calls `logHook(eventType, 'error: ' + String(err))` before returning `safeDefault`
- `src/core/hooks/handlers/pre-tool-use.ts` — `readJsonSafe` inner catch must call `logHook` or `appendLog` with the error message
- `src/core/hooks/handlers/post-tool-use.ts` (if not yet deleted) — any catch must log before return
- `src/core/hooks/handlers/post-tool-use-analytics.ts` (if not yet deleted) — same
- `src/core/hooks/handlers/stop-sync.ts` (if not yet deleted) — same
- `src/core/hooks/handlers/stop-auto.ts` (if not yet deleted) — same
- `src/core/hooks/handlers/stop-reflect.ts` (if not yet deleted) — same
- `src/core/hooks/handlers/session-start.ts` (if not yet deleted) — same
- `src/core/hooks/handlers/pre-compact.ts` (if not yet deleted) — same

For each catch block: change `catch { }` or `catch (e) { /* ignore */ }` to `catch (err) { logHook(context.logsDir, handlerName, String(err)); }` using the existing `logHook` or `appendLog` utility from `./utils.js`.

**Test**: Given a hook handler with an error-producing code path (mocked to throw), when the handler's catch block fires, then the error is written to the handler's log file and the safe default is still returned.

- **File**: `tests/unit/hooks/hook-error-logging.test.ts`
- **TC-001**: Given `pre-tool-use.ts` with `readJsonSafe` called on a corrupt JSON file, when the parse fails, then the error message appears in the handler's log file via `logHook`.
- **TC-002**: Given `hook-router.ts` where the dynamic import rejects, when the router catches the error, then it logs the error message and returns the safe default for that event type.
- **TC-003**: Given a handler that catches an error and logs it, when the same handler is called successfully (no error), then no additional error log lines are written to the log file.

---

### T-013: Isolate test log writes — use temp directories in hook handler tests
**User Story**: US-008 | **Satisfies ACs**: AC-US8-01, AC-US8-02
**Status**: [ ] Not Started

Update hook handler test files to create a unique temp directory per test for `logsDir` in `HookContext`. Applies to all test files in `tests/unit/hooks/` that construct a `HookContext` directly.

For each affected test file:
1. Add `import { mkdtempSync, rmSync } from 'fs'` and `import { tmpdir } from 'os'`
2. In `beforeEach`, set `context.logsDir = mkdtempSync(path.join(tmpdir(), 'sw-test-logs-'))`
3. In `afterEach`, call `rmSync(context.logsDir, { recursive: true, force: true })`

Files likely needing this change (verify by grepping for `HookContext`):
- `tests/unit/hooks/session-start.test.ts`
- `tests/unit/hooks/session-start-agent-type.test.ts`
- `tests/unit/hooks/session-start-plugin-health.test.ts`
- `tests/unit/hooks/session-start-session-state.test.ts`
- `tests/unit/hooks/stop-auto-v5-helpers.test.ts`
- `tests/unit/hooks/stop-reflect-logging.test.ts`
- `tests/unit/hooks/processor.test.ts`
- Any new test files for handlers created in T-012

**Test**: Given the updated hook handler test files, when two test suites run in parallel (simulated via `Promise.all` of async test functions), then each test's log output is isolated to its own temp directory and no log file from one test appears in another test's directory.

- **File**: Modifications to existing test files listed above; verification via `tests/unit/hooks/log-isolation.test.ts`
- **TC-001**: Given a `HookContext` created in `beforeEach` with `logsDir = mkdtempSync(...)`, when the test completes, then the temp dir path is unique for every test invocation.
- **TC-002**: Given a test that writes a log entry to `context.logsDir`, when `afterEach` runs, then the temp directory no longer exists on disk.
- **TC-003**: Given two tests that each write to their own `context.logsDir`, when both run, then neither test finds the other test's log entries in its own `logsDir`.

---

### T-014: Delete 4 stale v2 shell test files
**User Story**: US-009 | **Satisfies ACs**: AC-US9-01, AC-US9-02
**Status**: [ ] Not Started

Delete the following 4 files from `tests/unit/hooks/`:
- `interview-enforcement-guard.test.sh`
- `shell-injection.test.sh`
- `tdd-enforcement-guard.test.sh`
- `interview-gate-injection.test.sh`

After deletion, run `npx vitest run` to confirm no test failures are introduced. These shell tests are not executed by Vitest and test already-migrated shell hook functionality, so their deletion has no behavioral impact.

**Test**: Given the 4 `.test.sh` files exist in `tests/unit/hooks/` before the task, when they are deleted and `npx vitest run` executes, then exit code is 0 and no test failures reference the deleted files.

- **File**: `tests/unit/hooks/` (deletion verification only)
- **TC-001**: Given the 4 shell test files listed above, when they are deleted, then `ls tests/unit/hooks/*.test.sh` finds zero results (no `.test.sh` files remain).
- **TC-002**: Given the deletion, when `npx vitest run` runs the full test suite, then exit code is 0 and no test references the deleted filenames.

---

## Phase 4: Documentation

### T-015: Update AGENTS.md — document CLI-first hook architecture
**User Story**: US-010 | **Satisfies ACs**: AC-US10-01, AC-US10-02
**Status**: [ ] Not Started

Update `AGENTS.md` at the project root of `repositories/anton-abyzov/specweave/`. Add or update two sections:

**"Hook Architecture" section** — document:
- PreToolUse: the only active synchronous guard hook (blocks illegal tool calls before execution)
- UserPromptSubmit: the only active context injection hook (runs before prompt processing)
- All other events (SessionStart, PostToolUse, Stop, PreCompact) are no longer registered as hooks; they are CLI commands.

**"Session Lifecycle" section** — document:
- `specweave session start` replaces the SessionStart hook — call at the beginning of each AI session
- `specweave session end` replaces the Stop hook — call at the end of each AI session
- `specweave sync flush` replaces the PostToolUse event queue hook — call after modifying increment files
- `specweave analytics push --type <skill|agent> --name <name>` replaces the PostToolUse analytics hook

**Test**: Given the updated `AGENTS.md`, when its content is read, then it contains a "Hook Architecture" section listing PreToolUse and UserPromptSubmit as the only active hooks, and a "Session Lifecycle" section with `specweave session start` and `specweave session end` documented as replacements.

- **File**: `AGENTS.md` (in specweave repo root)
- **TC-001**: Given the updated AGENTS.md, when grepped for "Hook Architecture", then a section with PreToolUse and UserPromptSubmit is found.
- **TC-002**: Given the updated AGENTS.md, when grepped for "Session Lifecycle", then a section containing `specweave session start` and `specweave session end` is found.
- **TC-003**: Given the updated AGENTS.md, when grepped for "specweave sync flush", then usage documentation for the sync flush command is found.

---

## Phase 5: Verification

### T-016: Full test suite verification and smoke test
**User Story**: All | **Satisfies ACs**: All
**Status**: [ ] Not Started

**Depends on**: T-001 through T-015

Final verification pass:

1. Run `npx vitest run` from `repositories/anton-abyzov/specweave/` — must pass with 0 failures.
2. Verify `src/hooks/generate-settings.ts` outputs exactly 2 hook entries for httpMode=true.
3. Verify `src/core/hooks/handlers/hook-router.ts` HANDLERS map has exactly 2 entries.
4. Verify `src/core/hooks/handlers/types.ts` HookEventType has exactly 2 members.
5. Verify `tests/unit/hooks/` contains zero `.test.sh` files.
6. Verify `src/core/hooks/handlers/` contains no deleted handler files.
7. Smoke-test CLI commands exist and respond (exit 0 on `--help`):
   - `specweave session start --help`
   - `specweave session end --help`
   - `specweave sync flush --help`
   - `specweave analytics push --help`

**Test**: Given all prior tasks complete, when the verification checklist runs, then all 7 checks pass.

- **TC-001**: `npx vitest run` exits 0 with no failures.
- **TC-002**: `generateHooksSettings({ projectRoot, port })` with httpMode=true returns object with exactly `{ hooks: { PreToolUse: [...], UserPromptSubmit: [...] } }`.
- **TC-003**: HANDLERS map in hook-router.ts has exactly 2 keys.
- **TC-004**: No `.test.sh` files in `tests/unit/hooks/`.
- **TC-005**: `specweave session start --help` exits 0.
- **TC-006**: `specweave session end --help` exits 0.
- **TC-007**: `specweave sync flush --help` exits 0.
- **TC-008**: `specweave analytics push --help` exits 0.
