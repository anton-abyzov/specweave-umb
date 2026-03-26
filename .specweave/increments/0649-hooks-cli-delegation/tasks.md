# Tasks: Hooks Architecture Redesign — CLI Delegation

## Phase 1: Infrastructure

### T-001: Create handler types module
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02, AC-US1-03 | **Status**: [ ] pending
**AC**: AC-US1-02, AC-US1-03

Create `src/core/hooks/handlers/types.ts` with `HookInput`, `HookResult`, `HookContext`, and `HandlerFn` interfaces as specified in plan.md §2.3. These types are the shared contract for all handlers.

**Test Plan**:
- **File**: `tests/unit/core/hooks/handlers/types.test.ts`
- Given the types module is imported → When a handler function matches `HandlerFn` signature → Then TypeScript compilation succeeds with no type errors (type-level compile check only)

---

### T-002: Create shared handler utilities
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02, AC-US1-03 | **Status**: [ ] pending
**AC**: AC-US1-02, AC-US1-03

Create `src/core/hooks/handlers/utils.ts` with: `findProjectRoot()` (walk up from cwd to find `.specweave/config.json`), `readStdin(timeoutMs)` (read stdin as JSON with 5s timeout), `writeResult(result)` (JSON.stringify to stdout), `createContext(projectRoot)` (build `HookContext`), `logHook(context, handler, message)` (append to `.specweave/logs/hooks.log`).

**Test Plan**:
- **File**: `tests/unit/core/hooks/handlers/utils.test.ts`
- Given `findProjectRoot()` called from inside a `.specweave` project → When walking up → Then returns the correct project root
- Given `findProjectRoot()` called from path with no `.specweave/config.json` → When reaching fs root → Then returns null
- Given `readStdin()` receives valid JSON via stdin mock → When parsed → Then returns correct object
- Given `readStdin()` with 100ms timeout and no stdin data → When timeout expires → Then rejects/throws
- Given `createContext('/some/root')` → When called → Then returns `HookContext` with correct `stateDir`, `logsDir`, `configPath`, and ISO `timestamp`

---

### T-003: Create hook router
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04 | **Status**: [ ] pending
**AC**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04

Create `src/core/hooks/handlers/hook-router.ts`. The router reads stdin JSON, resolves project root, checks `SPECWEAVE_DISABLE_HOOKS=1`, dynamically imports the matching handler, executes it, and writes the JSON result. Wraps everything in a top-level try/catch — always outputs valid JSON. Unknown event-type returns `{"continue":true}`. Implements the dynamic import map from plan.md §2.2.

**Test Plan**:
- **File**: `tests/unit/core/hooks/handlers/hook-router.test.ts`
- Given `SPECWEAVE_DISABLE_HOOKS=1` env var is set → When `hookRouter('pre-compact', stdin)` is called → Then returns `{"continue":true}` without loading any handler
- Given `hookRouter('pre-compact', validJson)` called with no `.specweave/` in path → When handler returns → Then returns `{"continue":true}` (pass-through)
- Given `hookRouter('pre-tool-use', validJson)` → When called → Then dynamically imports only `pre-tool-use.ts` (not all handlers)
- Given `hookRouter('unknown-event', validJson)` → When called → Then returns `{"continue":true}` without throwing
- Given handler throws unexpected error → When caught by router → Then outputs safe default JSON for the event type (not a raw stack trace)

---

### T-004: Register `specweave hook` CLI command
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-05 | **Status**: [ ] pending
**AC**: AC-US1-01, AC-US1-05

Create `src/cli/commands/hook.ts` with exported `handleHook(eventType: string)`. Register `program.command('hook <event-type>')` in `bin/specweave.js` following the `detect-intent` pattern (async dynamic import of `dist/src/cli/commands/hook.js`). Hide from `--help`. Install `process.on('unhandledRejection')` and always exit 0.

**Test Plan**:
- **File**: `tests/unit/cli/commands/hook.test.ts`
- Given `handleHook('pre-compact')` called with valid stdin → When complete → Then exits with code 0
- Given `handleHook('nonexistent-event')` called → When router returns safe JSON → Then exits with code 0 (no crash)
- Given `specweave --help` output → When inspected → Then `hook` command is not listed

---

### T-005: Create handlers barrel export
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 | **Status**: [ ] pending
**AC**: AC-US1-01

Create `src/core/hooks/handlers/index.ts` barrel exporting `HandlerFn`, `HookContext`, `HookInput`, `HookResult` from `types.ts` and `hookRouter` from `hook-router.ts`.

**Test Plan**:
- **File**: (compile check only — no separate test file needed)
- Given barrel imported in TypeScript → When compiled → Then no re-export conflicts or missing exports

---

## Phase 2a: Simple Handlers

### T-006: Implement pre-compact handler
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04 | **Status**: [ ] pending
**AC**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04

Create `src/core/hooks/handlers/pre-compact.ts`. Port logic from `pre-compact.sh`: read/increment compaction counter in `context-pressure.json`, determine escalation level (elevated/critical/emergency), write `context-pressure.json` and `prompt-health-alert.json`. ~60 lines TS.

**Test Plan**:
- **File**: `tests/unit/core/hooks/handlers/pre-compact.test.ts`
- Given `.specweave/config.json` does not exist → When `handle()` called → Then returns `{"continue":true}` (non-SpecWeave pass-through) per AC-US2-03
- Given `SPECWEAVE_DISABLE_HOOKS=1` → When `handle()` called → Then returns `{"continue":true}` immediately per AC-US2-04
- Given first compaction (counter 0 → 1) → When `handle()` called → Then writes `context-pressure.json` with `level:"elevated"` per AC-US2-01
- Given fourth compaction (counter 3 → 4) → When `handle()` called → Then writes `context-pressure.json` with `level:"critical"` per AC-US2-01
- Given `handle()` runs → When complete → Then `prompt-health-alert.json` exists with `remediation` field per AC-US2-02
- Given any execution → When complete → Then returns `{"continue":true}` per AC-US2-03

---

### T-007: Implement session-start handler
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01, AC-US5-02, AC-US5-03, AC-US5-04 | **Status**: [ ] pending
**AC**: AC-US5-01, AC-US5-02, AC-US5-03, AC-US5-04

Create `src/core/hooks/handlers/session-start.ts`. Port logic from `v2/dispatchers/session-start.sh` and `startup-health-check.sh`: clear stale auto-session files (>24h old), reset `context-pressure.json`, perform baseline health check (CLAUDE.md exists, MEMORY.md size warning). Returns `{"continue":true}` always.

**Test Plan**:
- **File**: `tests/unit/core/hooks/handlers/session-start.test.ts`
- Given no `.specweave/` directory in project → When `handle()` called → Then returns `{"continue":true}` immediately per AC-US5-04
- Given `auto-session-abc.json` with mtime >24h ago → When `handle()` called → Then file is deleted per AC-US5-01
- Given `auto-session-xyz.json` with mtime <1h ago → When `handle()` called → Then file is preserved per AC-US5-01
- Given `context-pressure.json` with `level:"critical"` → When `handle()` called → Then file is cleared/reset per AC-US5-02
- Given CLAUDE.md missing in project → When `handle()` called → Then health check logs a warning per AC-US5-03
- Given any path → When `handle()` returns → Then result is `{"continue":true}` per AC-US5-04

---

## Phase 2b: Complex Handlers

### T-008: Implement pre-tool-use handler
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04, AC-US3-05 | **Status**: [ ] pending
**AC**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04, AC-US3-05

Create `src/core/hooks/handlers/pre-tool-use.ts`. Guard logic inlined (no external guard scripts): (1) fast path — if `file_path` not in `.specweave/increments/` and tool is not `TeamCreate`, return `{"decision":"allow"}`; (2) status-completion-guard: block Edit/Write on `metadata.json` that sets status to `"completed"`; (3) interview-enforcement-guard: block Write to `spec.md` when interview incomplete; (4) TeamCreate guard: block if no active/in-progress increment exists.

**Test Plan**:
- **File**: `tests/unit/core/hooks/handlers/pre-tool-use.test.ts`
- Given `file_path` outside `.specweave/increments/` and tool is `Edit` → When `handle()` called → Then returns `{"decision":"allow"}` per AC-US3-04
- Given Edit on `metadata.json` changing `status` to `"completed"` → When `handle()` called → Then returns `{"decision":"block","reason":"..."}` containing "specweave complete" per AC-US3-01
- Given Edit on `metadata.json` changing `status` to `"in-progress"` → When `handle()` called → Then returns `{"decision":"allow"}` per AC-US3-01
- Given Write to `spec.md` and `metadata.json` shows interview `state:"incomplete"` → When `handle()` called → Then returns `{"decision":"block","reason":"..."}` per AC-US3-02
- Given `TeamCreate` tool and no active increment → When `handle()` called → Then returns `{"decision":"block","reason":"..."}` per AC-US3-03
- Given `TeamCreate` tool and an active increment exists → When `handle()` called → Then returns `{"decision":"allow"}` per AC-US3-03
- Given any path → When result returned → Then JSON has only `decision` field plus optional `reason` per AC-US3-05

---

### T-009: Implement post-tool-use handler
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04, AC-US4-06 | **Status**: [ ] pending
**AC**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04, AC-US4-06

Create `src/core/hooks/handlers/post-tool-use.ts`. Port lifecycle detection from `v2/dispatchers/post-tool-use.sh`: parse tool result from stdin, detect `metadata.json` status changes → queue lifecycle events, detect `spec.md` AC checkbox changes, queue to `pending.jsonl` via `queueSyncEvent`, trigger immediate `LivingDocsSync` for `increment.done` and `increment.reopened`. Load GitHub/JIRA/ADO integrations lazily from config.

**Test Plan**:
- **File**: `tests/unit/core/hooks/handlers/post-tool-use.test.ts`
- Given Edit result for `metadata.json` changing status `"in-progress"` → `"paused"` → When `handle()` called → Then `increment.paused` event written to `pending.jsonl` per AC-US4-01, AC-US4-03
- Given Edit result for `metadata.json` changing status to `"done"` → When `handle()` called → Then `LivingDocsSync.sync()` called immediately (not just queued) per AC-US4-04
- Given Edit result for `spec.md` with AC checkbox `[ ]` → `[x]` → When `handle()` called → Then AC-checked event queued to `pending.jsonl` per AC-US4-02, AC-US4-03
- Given config has no `sync` key → When `handle()` called → Then no integration handler is loaded per AC-US4-06
- Given config has `sync.github` configured → When status changes → Then GitHub integration handler is dynamically imported per AC-US4-06

---

### T-010: Implement post-tool-use-analytics handler
**User Story**: US-004 | **Satisfies ACs**: AC-US4-05 | **Status**: [ ] pending
**AC**: AC-US4-05

Create `src/core/hooks/handlers/post-tool-use-analytics.ts`. Port from `v2/dispatchers/post-tool-use-analytics.sh`: extract skill/agent name from stdin, append analytics event to `.specweave/state/analytics/events.jsonl`. Fire-and-forget — no stdout output.

**Test Plan**:
- **File**: `tests/unit/core/hooks/handlers/post-tool-use-analytics.test.ts`
- Given `Skill` tool invocation with `tool_name:"sw:pm"` → When `handle()` called → Then one JSONL line appended with `tool:"Skill"` and `name:"sw:pm"` per AC-US4-05
- Given `Task` tool invocation → When `handle()` called → Then analytics event appended with `tool:"Task"` per AC-US4-05
- Given `events.jsonl` does not exist → When first event written → Then file is created without error per AC-US4-05
- Given any execution → When complete → Then handler returns without writing to stdout per AC-US4-05

---

### T-011: Implement user-prompt-submit handler
**User Story**: US-006 | **Satisfies ACs**: AC-US6-01, AC-US6-02, AC-US6-03, AC-US6-04, AC-US6-05, AC-US6-06, AC-US6-07 | **Status**: [ ] pending
**AC**: AC-US6-01, AC-US6-02, AC-US6-03, AC-US6-04, AC-US6-05, AC-US6-06, AC-US6-07

Create `src/core/hooks/handlers/user-prompt-submit.ts`. Port 2,550-line bash into ~800 lines TS section by section: (1) built-in command fast exit (`/help`, `/clear`, `/config`, `/status`); (2) `/sw:` fast-path routing; (3) project scope guard (reuse `evaluateProjectScopeGuard` from `project-scope-guard.ts`); (4) intent detection (call `detectIntentCommand()` directly — no subprocess); (5) context injection via `hookSpecificOutput.additionalContext`; (6) turn deduplication via content hash.

**Test Plan**:
- **File**: `tests/unit/core/hooks/handlers/user-prompt-submit.test.ts`
- Given prompt `/help` → When `handle()` called → Then returns `{"decision":"approve"}` with no `hookSpecificOutput` per AC-US6-01
- Given prompt `/clear` → When `handle()` called → Then returns `{"decision":"approve"}` immediately, skipping all SpecWeave processing per AC-US6-01
- Given prompt `/sw:pm create story` → When `handle()` called → Then returns `{"decision":"approve"}` via fast-path without invoking `detectIntentCommand` per AC-US6-02
- Given no `.specweave/` directory and prompt is a SpecWeave skill → When scope guard evaluates → Then returns `{"decision":"block","reason":"..."}` per AC-US6-03
- Given normal prompt in a SpecWeave project → When `detectIntentCommand` returns plugins → Then result includes `hookSpecificOutput.additionalContext` per AC-US6-04, AC-US6-05
- Given same content hash submitted twice in one session → When second invocation runs → Then returns `{"decision":"approve"}` without reprocessing per AC-US6-06
- Given any execution path → When `handle()` returns → Then shape is `{"decision":"approve"|"block"}` with optional `user_prompt`/`reason` per AC-US6-07

---

### T-012: Implement stop hooks (reflect, auto, sync)
**User Story**: US-007 | **Satisfies ACs**: AC-US7-01, AC-US7-02, AC-US7-03, AC-US7-04, AC-US7-05 | **Status**: [ ] pending
**AC**: AC-US7-01, AC-US7-02, AC-US7-03, AC-US7-04, AC-US7-05

Create three stop handler files:

**`stop-reflect.ts`**: Check `reflect.enabled` in config. If disabled or no `.specweave/`, return `{"decision":"approve"}` immediately. Otherwise call `reflectStopCommand()` from `reflect-stop.ts`. Always approve.

**`stop-auto.ts`**: Read `auto-session.json` marker. Check staleness, turn counter, dedup. Scan active increments for pending tasks/open ACs. If work remains, block with context. If session age exceeded or no work remains, approve.

**`stop-sync.ts`**: Read `pending.jsonl`. Deduplicate by increment ID. Call `LivingDocsSync` + `SyncCoordinator` per increment. Route lifecycle vs user-story events. Clean up processed entries. Always approve.

**Test Plan**:
- **Files**: `tests/unit/core/hooks/handlers/stop-reflect.test.ts`, `stop-auto.test.ts`, `stop-sync.test.ts`
- Given `reflect.enabled: false` in config → When `stop-reflect` `handle()` called → Then returns `{"decision":"approve"}` immediately per AC-US7-02
- Given no `.specweave/` directory → When `stop-reflect` `handle()` called → Then returns `{"decision":"approve"}` without reading config per AC-US7-02
- Given `reflect.enabled: true` and transcript exists → When `stop-reflect` runs → Then calls `reflectStopCommand()` and returns `{"decision":"approve"}` per AC-US7-01
- Given `auto-session.json` with open tasks remaining → When `stop-auto` `handle()` called → Then result contains remaining work context per AC-US7-03
- Given `auto-session.json` with all tasks completed → When `stop-auto` `handle()` called → Then returns `{"decision":"approve"}` per AC-US7-03
- Given `pending.jsonl` with 3 events (2 for same increment ID) → When `stop-sync` `handle()` called → Then deduplicates to 2 sync calls per AC-US7-04
- Given any stop handler throws internally → When error caught → Then still returns `{"decision":"approve"}` per AC-US7-05

---

## Phase 3: Wire Up

### T-013: Rewrite hooks.json to CLI delegation
**User Story**: US-008 | **Satisfies ACs**: AC-US8-01 | **Status**: [ ] pending
**AC**: AC-US8-01

Replace contents of `plugins/specweave/hooks/hooks.json` with the new CLI delegation format from plan.md §3. All events route to `specweave hook <event-type>` commands.

**Test Plan**:
- Given the new `hooks.json` → When parsed as JSON → Then valid JSON with no syntax errors
- Given the new `hooks.json` → When inspected → Then no `command` entries contain `bash` or `run-hook.sh`; all use `specweave hook <event>` pattern per AC-US8-01

---

### T-014: Register `hook` command in bin/specweave.js
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-05 | **Status**: [ ] pending
**AC**: AC-US1-01, AC-US1-05

Add `hook <event-type>` command registration to `bin/specweave.js` following the `detect-intent` pattern. Use `.helpOption(false)` to hide from `--help`. Add to the internal hidden-commands list alongside `detect-intent`, `evaluate-completion`, `reflect-stop`, `detect-project`.

**Test Plan**:
- Given `specweave hook pre-compact` invoked with valid stdin → When executed → Then exits 0 and outputs valid JSON per AC-US1-01
- Given `specweave --help` output → When inspected → Then `hook` is not listed per AC-US1-05

---

## Phase 4: Cleanup

### T-015: Remove bash script copy from plugin-copier
**User Story**: US-009 | **Satisfies ACs**: AC-US9-01, AC-US9-02, AC-US9-03 | **Status**: [ ] pending
**AC**: AC-US9-01, AC-US9-02, AC-US9-03

In `src/utils/plugin-copier.ts`, remove lines 907-933 that copy bash scripts from `plugins/*/hooks/` to `.claude/hooks/`. Skills must still copy to `.claude/skills/` correctly. Lockfile entries in `vskill.lock` must still compute hash, version, and timestamp.

**Test Plan**:
- **File**: `tests/unit/utils/plugin-copier.test.ts` (update existing)
- Given `copyPluginSkillsToProject()` called on plugin with hooks → When complete → Then `.claude/hooks/` directory is NOT created per AC-US9-01
- Given `copyPluginSkillsToProject()` called → When complete → Then `.claude/skills/` still contains plugin skills per AC-US9-02
- Given `copyPluginSkillsToProject()` called → When complete → Then `vskill.lock` entries have correct hash, version, and timestamp per AC-US9-03

---

### T-016: Delete all bash scripts from hooks directory
**User Story**: US-008 | **Satisfies ACs**: AC-US8-02, AC-US8-03, AC-US8-04, AC-US8-05 | **Status**: [ ] pending
**AC**: AC-US8-02, AC-US8-03, AC-US8-04, AC-US8-05

Delete all non-JSON files from `plugins/specweave/hooks/`: root `.sh`/`.md` scripts, `universal/` (all files), `v2/` (all subdirs and files), `lib/`, `tests/`, `_archive/`. Only `hooks.json` must remain.

**Test Plan**:
- Given `plugins/specweave/hooks/` → When listing files recursively → Then only `hooks.json` exists; no `.sh`, `.mjs`, `.cmd`, `.ps1`, or `.md` files per AC-US8-02 through AC-US8-05
- Given `plugins/specweave/hooks/` → When subdirectories listed → Then `universal/`, `v2/`, `lib/`, `tests/`, `_archive/` do not exist per AC-US8-03

---

## Phase 5: Verification

### T-017: Build, test, and end-to-end verify
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03 | **Status**: [ ] pending
**AC**: AC-US1-01, AC-US1-02, AC-US1-03

Run full verification pipeline: `npm run build` must pass with no TypeScript errors. `npx vitest run` must pass with 90%+ coverage per handler. Measure cold-start latency: `echo '{}' | specweave hook pre-compact` must complete in <200ms. Pipe sample stdin through each event type and verify stdout is valid JSON.

**Test Plan**:
- Given `npm run build` → When complete → Then exits 0 with no TypeScript errors
- Given `npx vitest run` → When complete → Then all handler tests pass at 90%+ coverage per handler
- Given `echo '{"tool_name":"Edit"}' | time specweave hook pre-compact` → When measured → Then wall time <200ms per NFR
- Given `echo '{}' | specweave hook user-prompt-submit` → When stdout captured → Then valid JSON with `decision` field
- Given `echo '{}' | specweave hook pre-tool-use` → When stdout captured → Then valid JSON with `decision:"allow"`
- Given `echo '{}' | specweave hook session-start` → When stdout captured → Then valid JSON with `continue:true`
