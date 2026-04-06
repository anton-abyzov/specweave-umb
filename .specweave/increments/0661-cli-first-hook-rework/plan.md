# Implementation Plan: CLI-First Hook Architecture Rework

## Overview

Migrate 6 of 8 Claude Code hook event types to explicit CLI commands. Retain only PreToolUse (guard) and UserPromptSubmit (context injection) as real-time hooks. The six migrated handlers become CLI subcommands invokable by skill prompts or the user directly, removing hook overhead and making SpecWeave 80% tool-agnostic.

## Architecture

### Current State: 9 Handlers, 8 Hook Event Types

```
hooks.json registers 8 event types → Claude Code spawns bash process → specweave hook <event> → hookRouter → handler
```

| Event Type           | Handler File               | Mechanism | Purpose                              |
|----------------------|----------------------------|-----------|--------------------------------------|
| PreToolUse           | pre-tool-use.ts            | Guard     | Block illegal edits (completion/interview/team) |
| UserPromptSubmit     | user-prompt-submit.ts      | Injection | Context injection + scope guard      |
| PostToolUse (edits)  | post-tool-use.ts           | Queue     | Queue sync events on increment file writes |
| PostToolUse (analytics) | post-tool-use-analytics.ts | Track  | Track Skill/Task usage analytics     |
| SessionStart         | session-start.ts           | Lifecycle | Clean stale auto, reset pressure, health check |
| PreCompact           | pre-compact.ts             | Signal    | Track compaction count, escalate pressure |
| Stop (reflect)       | stop-reflect.ts            | Lifecycle | Check reflect config, log intent     |
| Stop (auto)          | stop-auto.ts               | Lifecycle | Scan pending tasks, log auto state   |
| Stop (sync)          | stop-sync.ts               | Lifecycle | Flush pending event queue            |

### Target State: 2 Hooks + 4 CLI Commands

**KEEP as hooks** (require real-time interception):
- `PreToolUse` -- blocks illegal tool calls BEFORE execution. Cannot be post-hoc.
- `UserPromptSubmit` -- injects context BEFORE prompt processing. Cannot be post-hoc.

**MIGRATE to CLI commands** (do not require real-time interception):

| New CLI Command          | Replaces Hook(s)                    | Rationale                              |
|--------------------------|--------------------------------------|----------------------------------------|
| `specweave sync flush`   | stop-sync + post-tool-use (queue)    | Event queue is file-based; flush on demand |
| `specweave session start`| session-start                        | Session init is a one-time action      |
| `specweave session end`  | stop-reflect + stop-auto             | End-of-session cleanup is one-time     |
| `specweave analytics push` | post-tool-use-analytics            | Analytics append is non-blocking, can batch |

**REMOVE entirely** (absorb into session/compact signal):
- `pre-compact` -- pressure tracking moves to `specweave session compact` (new, lightweight)

### Components

#### C1: `src/cli/commands/session.ts` (NEW)
**Project**: specweave

Session lifecycle CLI. Three subcommands:

```
specweave session start     -- init session (replaces session-start hook)
specweave session end       -- cleanup session (replaces stop-reflect + stop-auto)
specweave session compact   -- record compaction event (replaces pre-compact hook)
```

**`start`**: Clears stale auto-mode files, resets context pressure, runs baseline prompt health check. Reuses existing logic from `session-start.ts` handler.

**`end`**: Runs reflect check (from `stop-reflect.ts`) then auto-mode scan (from `stop-auto.ts`). Sequential, not parallel. Exits 0 always.

**`compact`**: Increments compaction counter, escalates pressure level, writes health alert. Reuses logic from `pre-compact.ts`.

**Interface**:
```typescript
export interface SessionCommandResult {
  success: boolean;
  action: 'start' | 'end' | 'compact';
  details: Record<string, unknown>;
}

export async function sessionCommand(
  action: 'start' | 'end' | 'compact',
  options?: { projectRoot?: string; silent?: boolean; json?: boolean }
): Promise<SessionCommandResult>;
```

#### C2: `src/cli/commands/sync-flush.ts` (NEW)
**Project**: specweave

Replaces stop-sync handler + post-tool-use event queuing handler. Two modes:

1. **Queue mode** (`specweave sync flush --queue <event-json>`): Appends an event to the pending queue. Replaces post-tool-use.ts handler logic for writing to `event-queue/pending.jsonl`.

2. **Flush mode** (`specweave sync flush` with no args): Reads pending.jsonl, deduplicates by increment ID, logs sync intent, clears queue. Replaces stop-sync.ts handler.

**Interface**:
```typescript
export interface SyncFlushResult {
  success: boolean;
  mode: 'queue' | 'flush';
  eventsQueued?: number;
  eventsFlushed?: number;
  incrementIds?: string[];
}

export async function syncFlushCommand(
  options?: { queue?: string; projectRoot?: string; silent?: boolean; json?: boolean; dryRun?: boolean }
): Promise<SyncFlushResult>;
```

#### C3: `src/cli/commands/analytics-push.ts` (NEW)
**Project**: specweave

Replaces post-tool-use-analytics handler. Accepts analytics event data via CLI args or stdin.

```
specweave analytics push --type skill --name "sw:do" --plugin specweave
specweave analytics push --type agent --name "explorer"
```

**Interface**:
```typescript
export interface AnalyticsPushResult {
  success: boolean;
  eventsWritten: number;
}

export async function analyticsPushCommand(
  options: { type: 'skill' | 'agent'; name: string; plugin?: string; projectRoot?: string; json?: boolean }
): Promise<AnalyticsPushResult>;
```

#### C4: Trimmed `hooks.json` (MODIFY)
**Project**: specweave

Reduce from 8 event types to 2 (PreToolUse + UserPromptSubmit). Remove SessionStart, PreCompact, PostToolUse, and Stop sections entirely.

#### C5: Trimmed hook-router.ts and types.ts (MODIFY)
**Project**: specweave

Remove the 7 handler entries from the HANDLERS map and SAFE_DEFAULTS. Keep only `pre-tool-use` and `user-prompt-submit`. The removed handler files become dead code (delete them) since their logic now lives in the CLI commands.

#### C6: Core logic extraction modules (REFACTOR)
**Project**: specweave

Extract shared business logic from handlers into reusable core modules, so both the new CLI commands and (if needed) the remaining hooks can share code without duplication:

- `src/core/session/session-lifecycle.ts` -- stale cleanup, health check, pressure tracking
- `src/core/sync/event-queue.ts` -- queue append, flush, dedup (extracted from post-tool-use.ts + stop-sync.ts)
- `src/core/analytics/event-writer.ts` -- append to events.jsonl (extracted from post-tool-use-analytics.ts)
- `src/core/session/reflect-checker.ts` -- reflect config check (extracted from stop-reflect.ts)
- `src/core/session/auto-scanner.ts` -- pending task scan (extracted from stop-auto.ts)

### Data Model

No schema changes. All state files remain the same:

| State File                            | Owner (Before)       | Owner (After)                |
|---------------------------------------|----------------------|------------------------------|
| `.specweave/state/auto-mode.json`     | session-start hook   | `specweave session start`    |
| `.specweave/state/context-pressure.json` | pre-compact hook  | `specweave session compact`  |
| `.specweave/state/prompt-health.json` | session-start hook   | `specweave session start`    |
| `.specweave/state/prompt-health-alert.json` | pre-compact hook | `specweave session compact` |
| `.specweave/state/event-queue/pending.jsonl` | post-tool-use hook | `specweave sync flush` |
| `.specweave/state/analytics/events.jsonl` | post-tool-use-analytics hook | `specweave analytics push` |

### API Contracts

No HTTP APIs. All interfaces are CLI stdin/stdout:

**CLI contract** (all commands):
- Input: CLI flags + optional stdin JSON
- Output: Human-readable by default, `--json` for machine output
- Exit code: 0 on success, 1 on error
- Never crash -- catch all errors, log, return gracefully

### Invocation Pattern (Post-Migration)

Skills and CLAUDE.md instructions replace hook-based invocations:

```
# Before (hooks.json drives this automatically):
SessionStart → specweave hook session-start
PostToolUse (Edit on .specweave/) → specweave hook post-tool-use
Stop → specweave hook stop-reflect && stop-auto && stop-sync

# After (skills invoke CLI directly):
Session start skill prompt → specweave session start
/sw:done or /sw:do → specweave sync flush (on increment file changes)
Session end skill prompt → specweave session end
```

The `specweave sync flush --queue` call replaces the PostToolUse event queuing. Skills that modify increment files (sw:do, sw:done, sw:pm) call `specweave sync flush --queue '{"event":"task.updated","incrementId":"0661-cli-first-hook-rework"}'` after writing.

## Technology Stack

- **Language**: TypeScript (ESM, `.js` import extensions)
- **CLI Framework**: Commander.js (existing pattern)
- **Testing**: Vitest (unit + integration)
- **Build**: tsc (existing)
- **No new dependencies**

**Architecture Decisions**:

### AD-1: Subcommand Grouping vs. Flat Commands

**Decision**: Use subcommand grouping (`specweave session start`, `specweave sync flush`, `specweave analytics push`).

**Rationale**: Groups related operations under a single namespace. Follows the existing pattern where `sync-*` commands are related. `session` is a new top-level group. `analytics push` extends the existing `analytics` command.

**Alternative rejected**: Flat commands (`specweave session-start`, `specweave sync-flush`). Rejected because it pollutes the top-level namespace and doesn't communicate grouping.

### AD-2: Extract-and-Reuse vs. Copy-and-Delete

**Decision**: Extract business logic into core modules first, then have CLI commands import from core. Delete old handler files after CLI commands pass tests.

**Rationale**: Avoids duplication during migration. Core modules can be tested independently. If a future tool (not Claude Code) needs the same logic, it imports from core.

**Alternative rejected**: Copy handler logic directly into CLI commands. Rejected because it creates duplication between handlers (during transition) and between CLI commands that share logic (session start/end both need auto-mode scanning).

### AD-3: Hook Removal Strategy -- Atomic vs. Incremental

**Decision**: Atomic removal in a single increment. All 6 hooks removed from hooks.json at once, replaced by CLI commands.

**Rationale**: Incremental removal creates a confusing hybrid state where some functions are hooks and some are CLI commands. The hooks are independent (no handler depends on another handler's output), so removing them simultaneously is safe. Tests verify the CLI commands produce identical outputs to the old handlers.

**Alternative rejected**: Remove one hook at a time across multiple PRs. Rejected because the hooks are simple, low-risk, and independent. The overhead of 6 separate PRs outweighs the marginal safety benefit.

### AD-4: Handling pre-compact Migration

**Decision**: Absorb pre-compact into `specweave session compact` rather than removing pressure tracking.

**Rationale**: Pressure tracking is valuable for context-window management. Making it a CLI command means the skill prompt (or CLAUDE.md instructions for the PreCompact event) can call `specweave session compact` when compaction is detected. Claude Code still fires the PreCompact event to skills -- we just don't need a hook process for it.

## Implementation Phases

### Phase 1: Core Logic Extraction (Foundation)

1. Create `src/core/session/session-lifecycle.ts` -- extract from session-start.ts
2. Create `src/core/session/reflect-checker.ts` -- extract from stop-reflect.ts
3. Create `src/core/session/auto-scanner.ts` -- extract from stop-auto.ts
4. Create `src/core/sync/event-queue.ts` -- extract from post-tool-use.ts + stop-sync.ts
5. Create `src/core/analytics/event-writer.ts` -- extract from post-tool-use-analytics.ts
6. Unit tests for all extracted modules (100% coverage of existing logic)

### Phase 2: New CLI Commands

7. Create `src/cli/commands/session.ts` -- import from core modules
8. Create `src/cli/commands/sync-flush.ts` -- import from core modules
9. Create `src/cli/commands/analytics-push.ts` -- import from core modules
10. Register all commands in `bin/specweave.js`
11. Integration tests: CLI output matches old handler output for identical inputs

### Phase 3: Hook Cleanup

12. Trim `hooks.json` to PreToolUse + UserPromptSubmit only
13. Remove handler entries from hook-router.ts HANDLERS map
14. Remove SAFE_DEFAULTS for deleted event types
15. Remove HookEventType entries for deleted types
16. Delete handler files: session-start.ts, pre-compact.ts, stop-reflect.ts, stop-auto.ts, stop-sync.ts, post-tool-use.ts, post-tool-use-analytics.ts
17. Delete corresponding test files for removed handlers
18. Update handler index.ts barrel exports

### Phase 4: Verification

19. Full test suite passes (`npx vitest run`)
20. Manual smoke test: `specweave session start`, `specweave session end`, `specweave sync flush`, `specweave analytics push`
21. Verify hooks.json only registers PreToolUse + UserPromptSubmit
22. Verify `specweave hook pre-tool-use` and `specweave hook user-prompt-submit` still work

## Testing Strategy

**Unit tests** (per extracted core module):
- `session-lifecycle.test.ts` -- stale cleanup, health check, pressure tracking
- `reflect-checker.test.ts` -- config parsing, enabled/disabled logic
- `auto-scanner.test.ts` -- task counting, session staleness
- `event-queue.test.ts` -- append, flush, dedup, empty queue
- `event-writer.test.ts` -- analytics event writing

**Integration tests** (per CLI command):
- `session.test.ts` -- start/end/compact subcommands with real fs
- `sync-flush.test.ts` -- queue and flush modes with real pending.jsonl
- `analytics-push.test.ts` -- event writing with real events.jsonl

**Equivalence tests** (migration correctness):
- For each removed handler, compare its output to the equivalent CLI command output for the same input. Ensures behavioral parity.

**Regression tests** (kept hooks):
- Existing tests for pre-tool-use.ts and user-prompt-submit.ts remain unchanged.
- Verify hook-router.ts rejects unknown event types gracefully after handler removal.

## Technical Challenges

### Challenge 1: PostToolUse Event Queuing Without a Hook

**Problem**: Currently, `post-tool-use.ts` fires automatically after every Edit/Write to `.specweave/increments/`. Without this hook, increment file changes won't queue sync events.

**Solution**: Skills that modify increment files (sw:do, sw:done, sw:pm, sw:plan) already know which increment they're modifying. They call `specweave sync flush --queue '{"event":"task.updated","incrementId":"XXXX"}'` directly. This is more precise than the hook (which had to parse file paths to detect the increment ID) and eliminates false positives.

**Risk**: If a user edits increment files manually without using skills, events won't be queued. **Mitigation**: The `specweave sync flush` (without --queue) can be called by the session end flow to catch any missed changes via mtime scanning as a safety net.

### Challenge 2: PreCompact Event Without a Hook

**Problem**: Claude Code fires PreCompact before compaction. Without a hook, we lose the signal.

**Solution**: Claude Code still sends the PreCompact event even without a hook registered. Skills can respond to compaction pressure via CLAUDE.md instructions that advise calling `specweave session compact` when context is getting large. Additionally, the skill system can detect compaction events and call the CLI command.

**Risk**: Pressure tracking becomes opt-in rather than automatic. **Mitigation**: Accept this trade-off. Pressure tracking was informational, not blocking. The session start command resets pressure anyway.

### Challenge 3: Backward Compatibility During Rollout

**Problem**: Users running older SpecWeave versions will have the old hooks.json. Users updating will get the new trimmed hooks.json. If a skill calls `specweave session start` but the CLI hasn't been updated, it fails.

**Solution**: Version-gated release. CLI commands land first (additive, no breaking change). hooks.json trimming lands in a subsequent release. The CLI commands work even with old hooks.json (hooks just do nothing useful -- the CLI command does the real work).

**Risk**: Minimal. The hooks were best-effort anyway (never blocking). Adding CLI commands is purely additive.
