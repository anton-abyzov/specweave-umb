# Architecture Plan: Parallel Per-Case Benchmark Execution

## Overview

Transform the vskill eval-ui benchmark system from sequential single-stream execution to independent per-case SSE streams with parallel bulk execution. The core insight: each test case becomes an independently controllable execution unit with its own HTTP connection, AbortController, and lifecycle state.

## Architecture Diagram

```
BEFORE (sequential, single stream):

  UI ──POST /benchmark──► Server ──for-loop──► Case1 → Case2 → Case3
       single SSE stream                       (sequential)
       global isRunning

AFTER (parallel, per-case streams):

  UI ──POST /benchmark/case/1──► Server ──► Case1  ─┐
     ──POST /benchmark/case/2──► Server ──► Case2  ─┤ Semaphore(3)
     ──POST /benchmark/case/3──► Server ──► Case3  ─┤
     ──POST /benchmark/case/4──► Server ──►(queued)─┘
       independent SSE streams
       per-case CaseRunState map
```

## Component Design

### C1: Semaphore (NEW — `src/eval-server/concurrency.ts`)

Zero-dependency cooperative concurrency primitive. Controls how many LLM calls execute simultaneously during bulk runs.

```typescript
export class Semaphore {
  private current: number;
  private readonly max: number;
  private waitQueue: Array<() => void>;

  constructor(max: number);
  async acquire(): Promise<void>;   // blocks until slot available
  release(): void;                  // frees a slot, unblocks next waiter
  get available(): number;
  get pending(): number;
}
```

**Design decisions:**
- Promise-based queue (no polling). `acquire()` returns a Promise that resolves when a slot opens.
- `release()` is idempotent — calling it when no slots are held is a no-op (prevents underflow).
- No timeout on acquire — the client-side AbortController handles cancellation. If a waiting acquire's caller is aborted, the server `res.on('close')` handler must call `release()` to prevent slot leaks.

**Why not p-limit/p-queue:** The semaphore pattern is ~30 lines. Adding a dependency for this is not justified. p-limit also does not expose `release()` for external cleanup, which is needed for the cancel/disconnect flow.

### C2: Per-Case SSE Endpoint (MODIFY — `src/eval-server/api-routes.ts`)

New route: `POST /api/skills/:plugin/:skill/benchmark/case/:evalId`
New route: `POST /api/skills/:plugin/:skill/baseline/case/:evalId`

Each per-case endpoint:
1. Loads evals, finds the single case by evalId
2. Acquires a slot from the per-skill Semaphore
3. Calls `runSingleCaseSSE()` (extracted from benchmark-runner)
4. On complete: writes history entry with `scope: "single"` (unless `bulk: true` in body)
5. Releases Semaphore slot in `finally` block
6. Sends SSE `done` event with the single-case BenchmarkResult

New route: `POST /api/skills/:plugin/:skill/benchmark/bulk-save`
- Accepts an assembled BenchmarkResult from the client after all parallel cases complete
- Writes to history with `scope: "bulk"`
- Used only for bulk aggregate history entries

The existing bulk endpoint (`POST .../benchmark`) is preserved unchanged for CLI backward compatibility.

**Route parameter:** `:evalId` is the numeric eval case ID (e.g., `1`, `2`, `3`).

### C3: Refactored Benchmark Runner (MODIFY — `src/eval-server/benchmark-runner.ts`)

Extract from `runBenchmarkSSE`:

```typescript
// Runs exactly one case on its own SSE response stream
export async function runSingleCaseSSE(opts: SingleCaseRunOptions): Promise<BenchmarkCase>;

// Assembles a BenchmarkResult from individual case results
export function assembleBulkResult(
  cases: BenchmarkCase[],
  meta: { model: string; skillName: string; runType: string; provider: string }
): BenchmarkResult;
```

**`runSingleCaseSSE`** is the core unit extracted from the existing for-loop body. It processes one EvalCase: generate LLM response, judge assertions, emit SSE events, return BenchmarkCase. The existing `runBenchmarkSSE` is preserved for the CLI/legacy bulk endpoint but internally delegates to `runSingleCaseSSE` in a sequential loop.

**`assembleBulkResult`** computes aggregate metrics (overall_pass_rate, totalDurationMs, totalTokens) from an array of BenchmarkCase results. Used by both server-side (legacy bulk) and client-side (bulk-save endpoint).

**Concurrency default:** `const DEFAULT_CONCURRENCY = 3` — hardcoded constant exported from `concurrency.ts`.

### C4: BenchmarkResult Scope Field (MODIFY — `src/eval/benchmark.ts`)

```typescript
export interface BenchmarkResult {
  // ...existing fields...
  scope?: "single" | "bulk";  // NEW — backward compatible (optional)
}
```

- `scope: "single"` — written by single-case runs (contains exactly one case in `cases[]`)
- `scope: "bulk"` — written by bulk runs
- `undefined` — legacy entries, treated as bulk

### C5: Per-Case History Saving (MODIFY — `src/eval/benchmark-history.ts`)

`writeHistoryEntry` already accepts any BenchmarkResult. No signature changes needed.

Single-case runs now call `writeHistoryEntry` (previously only bulk runs did — existing code on line 172 of benchmark-runner.ts guards with `if (!filterIds)`). The `scope` field propagates into the JSON file automatically.

`getCaseHistory` already finds cases by evalId across all history entries. Single-case entries naturally appear in per-case history queries. No changes needed.

The history panel needs minor UI differentiation: entries with `scope: "single"` display as "Single: {case-name}" vs "Full Run" for bulk.

### C6: useMultiSSE Hook (NEW — `src/eval-ui/src/sse.ts`)

Manages a Map of independent SSE connections, one per running case.

```typescript
interface CaseStream {
  controller: AbortController;
  events: SSEEvent[];
  status: "connecting" | "streaming" | "done" | "error";
}

export function useMultiSSE<T = unknown>() {
  // Reactive state: Map<evalId, CaseStream>
  streams: Map<number, CaseStream>;

  startCase(evalId: number, url: string, body?: unknown): void;
  stopCase(evalId: number): void;
  stopAll(): void;
}
```

**Event flow:** Each `startCase` call creates a new `AbortController`, opens a `fetch()` POST with SSE parsing (same logic as existing `useSSE.start()`), and appends events to the per-case entry. `stopCase` aborts only that case's controller.

**Memory cleanup:** When a stream reaches `done` or `error` status, its AbortController reference is cleared. The Map entry persists (for result display) until a new run starts for that case.

**Re-render strategy:** Uses `useState` with a new Map instance on each update (shallow copy triggers React re-render). The hook exposes the `streams` Map as reactive state.

The existing `useSSE` hook is preserved (used by comparison mode and activation testing).

### C7: Per-Case Run State (MODIFY — `src/eval-ui/src/pages/workspace/workspaceTypes.ts`)

```typescript
export type CaseRunStatus = "idle" | "queued" | "running" | "complete" | "error" | "cancelled";

export interface CaseRunState {
  status: CaseRunStatus;
  startedAt?: number;
}

export interface WorkspaceState {
  // REMOVE: isRunning: boolean;
  // REMOVE: runScope: RunScope | null;

  // ADD:
  caseRunStates: Map<number, CaseRunState>;
  bulkRunActive: boolean;  // true when a "Run All" is in progress
  // KEEP: runMode: RunMode | null;  (still needed for panel display)
  // ...rest unchanged
}
```

**New actions:**

```typescript
| { type: "CASE_RUN_START"; evalId: number; mode: RunMode }
| { type: "CASE_RUN_COMPLETE"; evalId: number; result: InlineResult }
| { type: "CASE_RUN_ERROR"; evalId: number; error: string }
| { type: "CASE_RUN_CANCEL"; evalId: number }
| { type: "BULK_RUN_START"; mode: RunMode; evalIds: number[] }
| { type: "BULK_RUN_COMPLETE"; benchmark: BenchmarkResult }
| { type: "CANCEL_ALL" }
```

**Derived helpers (not in state, computed):**
- `isAnyRunning(state)`: `Array.from(state.caseRunStates.values()).some(s => s.status === "running" || s.status === "queued")`
- `isCaseRunning(state, evalId)`: `state.caseRunStates.get(evalId)?.status === "running"`

### C8: Workspace Reducer (MODIFY — `src/eval-ui/src/pages/workspace/workspaceReducer.ts`)

New action handlers:

- **CASE_RUN_START:** Sets `caseRunStates.get(evalId).status = "running"`. Only affects the target case. Clears any previous inline result for that case.
- **CASE_RUN_COMPLETE:** Sets status to `"complete"`, merges InlineResult into `inlineResults` map.
- **CASE_RUN_ERROR:** Sets status to `"error"`, stores error in InlineResult.
- **CASE_RUN_CANCEL:** Sets status to `"cancelled"`.
- **BULK_RUN_START:** Sets `bulkRunActive = true`, all specified evalIds to `"queued"`, switches panel to "run".
- **BULK_RUN_COMPLETE:** Sets `bulkRunActive = false`, stores benchmark, increments iterationCount.
- **CANCEL_ALL:** Sets all running/queued cases to `"cancelled"`, sets `bulkRunActive = false`.

Old `RUN_START` and `RUN_COMPLETE` are replaced. `UPDATE_INLINE_RESULT` is kept for streaming SSE event updates.

Initial state: `caseRunStates: new Map()`, `bulkRunActive: false`.

### C9: WorkspaceContext Wiring (MODIFY — `WorkspaceContext.tsx`)

Replace `useSSE` with `useMultiSSE` for benchmark runs. Keep `useSSE` for comparison/activation.

New API surface:

```typescript
export interface WorkspaceContextValue {
  // REMOVE: runBenchmark(mode, scope)
  // REMOVE: cancelRun()

  // ADD:
  runCase: (evalId: number, mode?: RunMode) => void;
  runAll: (mode?: RunMode) => void;
  cancelCase: (evalId: number) => void;
  cancelAll: () => void;
  // ...rest unchanged
}
```

**`runCase` implementation:**
1. Dispatch `CASE_RUN_START` for the target case
2. Call `multiSSE.startCase(evalId, url)`
3. Process SSE events via useEffect watching `multiSSE.streams`
4. On stream done: dispatch `CASE_RUN_COMPLETE`

**`runAll` implementation:**
1. Dispatch `BULK_RUN_START` with all evalIds
2. For each evalId, call `multiSSE.startCase(evalId, url, { bulk: true })`
3. The server-side Semaphore limits concurrent execution to DEFAULT_CONCURRENCY
4. Client-side: all fetch requests fire immediately; server holds queued requests until a Semaphore slot opens
5. Track completion: when all streams are done/error, assemble aggregate result and POST to `/benchmark/bulk-save`, then dispatch `BULK_RUN_COMPLETE`

**`cancelCase`:** Calls `multiSSE.stopCase(evalId)`, dispatches `CASE_RUN_CANCEL`.

**`cancelAll`:** Calls `multiSSE.stopAll()`, dispatches `CANCEL_ALL`.

**SSE event processing:** A useEffect watches `multiSSE.streams`. For each stream with new events, it maps SSE event types to `UPDATE_INLINE_RESULT` dispatches (same logic as current implementation but keyed per-case).

### C10: RunPanel UI (MODIFY — `src/eval-ui/src/pages/workspace/RunPanel.tsx`)

Key changes:
- Replace `isRunning` checks with per-case state lookups from `caseRunStates`
- Controls bar: "Run All" triggers `runAll()`, "Cancel All" appears when `bulkRunActive || isAnyRunning`
- Remove scope selector (all/selected) — replaced by per-case Run buttons and Run All
- Each `RunCaseCard` shows its own status: spinner (running), clock icon (queued), checkmark/X (complete/error), dash (cancelled)
- Per-case Run buttons enabled when that case is idle/complete/error/cancelled
- Per-case Cancel button visible when that case is running
- Progress bar during bulk: shows `(running + complete) / total`

### C11: TestsPanel UI (MODIFY — `src/eval-ui/src/pages/workspace/TestsPanel.tsx`)

Key changes:
- `CaseDetail`: Per-case cancel button (visible only when THAT case is running)
- Run/A/B buttons disabled only when THAT case is running (not global blocking)
- Status pills update independently as per-case SSE events arrive

## Server-Side Semaphore Lifecycle

Per-skill Semaphore registry:

```typescript
const skillSemaphores = new Map<string, Semaphore>();

function getSkillSemaphore(plugin: string, skill: string): Semaphore {
  const key = `${plugin}/${skill}`;
  if (!skillSemaphores.has(key)) {
    skillSemaphores.set(key, new Semaphore(DEFAULT_CONCURRENCY));
  }
  return skillSemaphores.get(key)!;
}
```

Each per-case endpoint handler:
1. `const sem = getSkillSemaphore(plugin, skill)`
2. Register `res.on('close')` handler that calls release (safety net for disconnects during acquire wait)
3. `await sem.acquire()`
4. Execute `runSingleCaseSSE()` in a try/finally
5. `sem.release()` in finally (guaranteed even on error)

The `res.on('close')` handler needs a flag to avoid double-release (once via finally, once via close). Pattern: `let released = false; const doRelease = () => { if (!released) { released = true; sem.release(); } };`

## Data Flow: History Writes

### Single-case run
1. Per-case endpoint completes (no `bulk` flag in body)
2. Server calls `writeHistoryEntry(skillDir, singleCaseResult)` where result has `scope: "single"`
3. Also updates `benchmark.json` (latest) via existing mechanism

### Bulk run
1. Per-case endpoints run with `bulk: true` in body — no individual history writes
2. When all per-case streams complete, client POSTs to `/benchmark/bulk-save` with assembled BenchmarkResult
3. Server writes single aggregate history entry with `scope: "bulk"`
4. Also updates `benchmark.json` (latest)

## Backward Compatibility

| Concern | Resolution |
|---------|-----------|
| Existing `/benchmark` POST endpoint | Preserved, unchanged sequential behavior. Used by CLI. |
| History entries without `scope` field | Treated as bulk (legacy behavior). |
| `BenchmarkResult.scope` optional | Existing code handles undefined gracefully. |
| `isRunning` consumers | Replaced with derived `isAnyRunning` computed from `caseRunStates`. |
| Comparison mode | Unchanged — keeps existing single-stream flow (out of scope). |
| `applyImproveAndRerun` | Updated to call `runCase(evalId)` instead of `runBenchmark("benchmark", { caseId })`. |

## File Change Summary

| File | Change | Lines (est.) |
|------|--------|-------------|
| `src/eval-server/concurrency.ts` | NEW — Semaphore class + DEFAULT_CONCURRENCY | ~45 |
| `src/eval-server/benchmark-runner.ts` | Extract `runSingleCaseSSE`, add `assembleBulkResult` helper | ~60 modified |
| `src/eval-server/api-routes.ts` | Add per-case routes, bulk-save route, semaphore registry | ~90 added |
| `src/eval/benchmark.ts` | Add `scope` field to BenchmarkResult | ~3 |
| `src/eval-ui/src/sse.ts` | Add `useMultiSSE` hook (keep existing `useSSE`) | ~100 added |
| `src/eval-ui/src/pages/workspace/workspaceTypes.ts` | CaseRunState type, new actions, update state shape | ~45 modified |
| `src/eval-ui/src/pages/workspace/workspaceReducer.ts` | New action handlers, replace RUN_START/RUN_COMPLETE | ~80 modified |
| `src/eval-ui/src/pages/workspace/WorkspaceContext.tsx` | Wire useMultiSSE, new API (runCase, cancelCase, etc.) | ~110 modified |
| `src/eval-ui/src/pages/workspace/RunPanel.tsx` | Per-case controls, Cancel All, per-case status | ~70 modified |
| `src/eval-ui/src/pages/workspace/TestsPanel.tsx` | Per-case run/cancel in CaseDetail | ~30 modified |

## Testing Strategy

- **Semaphore unit tests** (`concurrency.test.ts`): Verify max concurrency enforcement, queuing behavior, release-on-error, no underflow on extra release calls.
- **runSingleCaseSSE unit tests**: Mock LlmClient, verify SSE event sequence for success, error, and abort paths.
- **Per-case endpoint integration tests**: Verify route responds with SSE, scope field in history, concurrent case isolation via semaphore.
- **useMultiSSE unit tests**: Verify independent stream lifecycle, stopCase only stops target, stopAll stops all, memory cleanup on done.
- **Reducer unit tests**: Each new action type produces correct state transitions; no cross-case state contamination.
- **assembleBulkResult unit tests**: Correct aggregate metric calculation from individual cases.

## Risks and Mitigations

| Risk | Mitigation |
|------|-----------|
| Semaphore slot leak on crash | try/finally in endpoint handler + res.on('close') safety net with double-release guard |
| Browser HTTP/2 connection limits | Modern browsers multiplex over single HTTP/2 connection. HTTP/1.1 has 6-connection limit per origin, but even 10 cases work fine with queuing. |
| Memory from N SSE parse buffers | Each buffer is < 1KB. With typical 5-20 cases, negligible. |
| Race between cancelCase and stream completion | AbortController.abort() is synchronous. If stream is already done, abort is a no-op. AbortError is caught and ignored (existing pattern). |
| Stale inline results from previous runs | CASE_RUN_START clears the previous inline result for that case before starting. |

## Non-Goals (Confirmed Out of Scope)

- Configurable concurrency via UI slider
- Parallel A/B comparison runs
- WebSocket migration
- Queue priority/reordering
- Automatic retry on failure
