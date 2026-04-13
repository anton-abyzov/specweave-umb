---
increment: 0662-hook-transparency-observability
title: Hook Transparency & Observability
status: completed
priority: P1
type: feature
created: 2026-04-06T00:00:00.000Z
---

# Hook Transparency & Observability

## Problem Statement

The hook system blocks tool calls silently with generic "reason" strings. Users cannot distinguish an intentional guard (e.g., "use /sw:done instead") from a broken hook. Rich observability infrastructure (HookLogger, HookHealthTracker, HealthReporter) exists in `src/core/hooks/` but is completely disconnected from the actual execution path in `hook-router.ts` and `pre-tool-use.ts`. The plaintext `logHook()` in `utils.ts` writes unstructured single-line entries, making diagnostics impossible. Additionally, four stale references point to a non-existent `check-hooks` command, and the CLAUDE.md docs URL references `verified-skill.com` instead of `spec-weave.com`.

## Goals

- Make hook blocks self-explanatory: users instantly know "guard working" vs "hook broken"
- Connect existing observability classes to the real execution path (plumbing, not architecture)
- Provide CLI commands (`hooks log`, `hooks health`, `hooks ls`) for hook inspection
- Remove stale references and fix documentation URL

## User Stories

### US-001: Semantic Hook Block Output
**Project**: specweave
**As a** CLI user
**I want** hook block messages to carry semantic prefixes ([GUARD] vs [ERROR])
**So that** I can instantly tell whether a block is an intentional policy enforcement or a hook failure

**Acceptance Criteria**:
- [x] **AC-US1-01**: Given a hook guard blocks a tool call intentionally, when the block reason is displayed to the user, then the message is prefixed with `[GUARD]`
- [x] **AC-US1-02**: Given a hook throws an unhandled exception during execution, when the error is displayed, then the message is prefixed with `[ERROR]`
- [x] **AC-US1-03**: Given the hook router catches an exception in a handler, when it builds the block response JSON, then the `reason` field contains the `[ERROR]` prefix and the original error message
- [x] **AC-US1-04**: Given existing guard logic in `pre-tool-use.ts` (status-completion, interview-enforcement, increment-existence), when any guard blocks, then all three use the `[GUARD]` prefix consistently

### US-002: Structured Hook Logging
**Project**: specweave
**As a** developer debugging hook behavior
**I want** hook executions logged as structured JSON via the existing HookLogger class
**So that** I can filter, search, and analyze hook activity programmatically

**Acceptance Criteria**:
- [x] **AC-US2-01**: Given a hook executes (block or allow), when logging occurs, then `HookLogger.log()` is called with hook name, decision, duration, and context
- [x] **AC-US2-02**: Given the existing `logHook()` in `utils.ts` is called, when it writes the log entry, then it dual-writes: plaintext line to `hooks.log` (backwards compat) AND structured JSON via `HookLogger`
- [x] **AC-US2-03**: Given a hook execution completes, when the structured log entry is written, then it contains fields: `timestamp`, `hookName`, `handler`, `decision` (allow|block), `durationMs`, `reason` (if blocked), and `toolName`
- [x] **AC-US2-04**: Given the HookLogger import is added to `hook-router.ts`, when the module loads, then no new dependencies are introduced beyond existing project modules

### US-003: Hook Log Viewer CLI
**Project**: specweave
**As a** developer investigating hook activity
**I want** a `specweave hooks log` command with filtering options
**So that** I can quickly find relevant hook events without manually parsing log files

**Acceptance Criteria**:
- [x] **AC-US3-01**: Given the user runs `specweave hooks log`, when logs exist, then the last 20 entries are displayed in a human-readable table format
- [x] **AC-US3-02**: Given the user runs `specweave hooks log --blocks-only`, when filtering is applied, then only entries with `decision: "block"` are shown
- [x] **AC-US3-03**: Given the user runs `specweave hooks log --errors-only`, when filtering is applied, then only entries with `[ERROR]` prefix in reason are shown
- [x] **AC-US3-04**: Given the user runs `specweave hooks log --last 5`, when the count flag is provided, then exactly the 5 most recent entries are displayed
- [x] **AC-US3-05**: Given the user runs `specweave hooks log --hook pre-tool-use`, when the hook name filter is provided, then only entries for that hook name are shown

### US-004: Hook Health Dashboard CLI
**Project**: specweave
**As a** developer ensuring hooks are reliable
**I want** a `specweave hooks health` command that reports hook health status
**So that** I can proactively detect degraded or failing hooks

**Acceptance Criteria**:
- [x] **AC-US4-01**: Given the user runs `specweave hooks health`, when structured logs exist, then a health report is displayed using `HookHealthTracker` analysis and `HealthReporter` formatting
- [x] **AC-US4-02**: Given a hook has >90% success rate in the last 24 hours, when health is computed, then its status shows as OK
- [x] **AC-US4-03**: Given a hook has 50-90% success rate in the last 24 hours, when health is computed, then its status shows as DEGRADED with recommendations
- [x] **AC-US4-04**: Given no structured logs exist yet, when `specweave hooks health` is run, then it displays a message indicating no data is available and suggests running hooks first

### US-005: Hook Registry and Listing CLI
**Project**: specweave
**As a** developer exploring available hooks
**I want** a `specweave hooks ls` command backed by a lightweight hook registry
**So that** I can see all registered hooks, their types, and trigger points without reading source code

**Acceptance Criteria**:
- [x] **AC-US5-01**: Given plugin hooks exist in `plugins/*/hooks/` directories, when the user runs `specweave hooks ls`, then a table lists each hook with columns: name, plugin, trigger type, and critical flag
- [x] **AC-US5-02**: Given the HookScanner already discovers hooks at runtime, when `hooks ls` executes, then it uses `HookScanner` to enumerate hooks (no duplicate discovery logic)
- [x] **AC-US5-03**: Given a static manifest file `hooks-manifest.json` does not yet exist in a plugin, when `hooks ls` runs, then it falls back to live scanning via HookScanner without error
- [x] **AC-US5-04**: Given hooks are discovered, when output is rendered, then hooks are grouped by trigger type (pre-tool-use, post-tool-use, session-start, user-prompt-submit)

### US-006: Cleanup Stale References and Docs URL
**Project**: specweave
**As a** contributor reading docs or CLI help
**I want** stale `check-hooks` references removed and the docs URL corrected
**So that** documentation and CLI suggestions point to commands that actually exist

**Acceptance Criteria**:
- [x] **AC-US6-01**: Given stale references to `check-hooks` exist in `hook-health-tracker.ts` and `hooks-checker.ts`, when they are updated, then they point to `specweave hooks health` instead
- [x] **AC-US6-02**: Given the CLAUDE.md docs section references `verified-skill.com`, when corrected, then it references `spec-weave.com`
- [x] **AC-US6-03**: Given all 4 stale `check-hooks` references are identified, when cleanup is complete, then zero references to the non-existent `check-hooks` command remain in the codebase
- [x] **AC-US6-04**: Given the `specweave doctor` hooks checker suggests a command, when it renders suggestions, then it suggests `specweave hooks health` (not `check-hooks`)

## Out of Scope

- Real-time hook streaming / watch mode
- Dashboard UI (web-based hook monitoring)
- Hook performance profiling or flame graphs
- New hook types or guard logic changes
- Persisted manifest generation CLI (`hooks manifest build`)
- Changes to the hook execution order or priority system

## Technical Notes

### Dependencies
- `HookLogger` at `src/core/hooks/hook-logger.ts` — structured JSONL writer
- `HookHealthTracker` at `src/core/hooks/hook-health-tracker.ts` — 24h window health analysis
- `HealthReporter` at `src/core/hooks/HealthReporter.ts` — multi-format report renderer
- `HookScanner` at `src/core/hooks/HookScanner.ts` — plugin hook discovery
- Commander.js CLI framework (existing `src/cli/commands/`)

### Constraints
- Must preserve backwards compatibility with plaintext `hooks.log` (dual-write)
- All new CLI commands register under `specweave hooks <subcommand>` namespace
- No new npm dependencies — use only existing project modules
- ESM module system throughout

### Architecture Decisions
- Wire existing classes into execution path — no new observability architecture
- `hooks` subcommand group consolidates all hook CLI operations
- Semantic prefix is injected at the response-building layer, not in individual guards

## Non-Functional Requirements

- **Performance**: Hook logging overhead must not exceed 5ms per hook execution
- **Compatibility**: Works on macOS, Linux, and Windows path formats
- **Security**: Log files must not contain sensitive tool call parameters (file contents, secrets)
- **Reliability**: Logging failures must be silent — never crash a hook execution due to log I/O

## Edge Cases

- No log files exist yet: `hooks log` and `hooks health` display informative empty-state messages
- Corrupted JSONL line in log file: `hooks log` skips malformed lines with a warning count
- Hook throws non-Error object: `[ERROR]` prefix still applied, message coerced via `String()`
- HookScanner finds zero plugins: `hooks ls` displays "No hooks registered" message
- Concurrent hook executions writing to same log: JSONL append-only format is safe for concurrent writes

## Risks

| Risk | Probability | Impact | Severity | Mitigation |
|------|-------------|--------|----------|------------|
| Dual-write increases log file size rapidly | 0.3 | 3 | 0.9 | JSONL files auto-rotate via existing HookLogger config |
| Semantic prefix breaks existing hook output parsers | 0.2 | 5 | 1.0 | Prefix only in `reason` field, not in `decision` enum |
| HookScanner slow on large plugin sets | 0.2 | 4 | 0.8 | Scanner already caches; `hooks ls` is on-demand only |

## Success Metrics

- Zero user confusion reports about "is this hook working or broken?" after prefix rollout
- `specweave hooks log --blocks-only` returns results within 200ms for 10k log entries
- All 4 stale `check-hooks` references eliminated (verified by grep)
- HookLogger receives structured entries for 100% of hook executions
