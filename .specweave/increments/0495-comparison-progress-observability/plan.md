# Architecture Plan: Comparison Progress Observability

## Overview

Replace the opaque `withHeartbeat()` wrapper in the compare endpoint with a new imperative `startDynamicHeartbeat()` helper that allows mid-flight phase updates, and thread an `onProgress` callback through the comparator functions so the endpoint can report which LLM call is running (skill gen, baseline gen, scoring).

## Architecture Decisions

### AD-1: Imperative heartbeat vs. wrapping each LLM call in its own `withHeartbeat()`

**Option A (chosen): Imperative `startDynamicHeartbeat()` with `update()`/`stop()`**
- Single timer for the entire comparison, phase changed imperatively
- Simpler wiring: one `start` at top, `update` at each boundary, `stop` in finally
- Heartbeat ticks continue between phase transitions with the latest phase/message
- No nesting of timers or race conditions

**Option B (rejected): Three sequential `withHeartbeat()` calls**
- Would require splitting `runComparison()` apart at the call site
- Timer restarts at each phase, resetting elapsed counters
- Requires the endpoint to know the internal decomposition of comparator steps

Decision: Option A. It keeps the comparator's internal structure opaque to the endpoint while allowing phase updates via a callback. The elapsed timer runs continuously across all phases, giving users a consistent sense of total duration.

### AD-2: Callback threading vs. EventEmitter

**Option A (chosen): `onProgress?: (phase: string, message: string) => void` callback parameter**
- Zero dependencies, matches existing patterns (e.g., assertion iteration already uses inline callbacks)
- Optional parameter preserves backward compat -- callers that don't pass it see no change
- Direct, synchronous, no subscription/unsubscription lifecycle

**Option B (rejected): EventEmitter on `LlmClient` or comparator**
- Adds pub/sub complexity for 3 events
- Requires emitter lifecycle management (on/off)
- Overkill for sequential calls

Decision: Option A. A plain callback is the minimal viable surface for 3 phase transitions.

### AD-3: ProgressLog phase registration -- extend existing Sets vs. config object

Extend the existing `spinnerPhases` and `accentPhases` Sets in `ProgressLog.tsx` with the 3 new phase strings. No config object or phase registry needed -- 3 string additions to 2 Sets is trivial and consistent with how all existing phases are registered.

## Component Design

### Layer 1: SSE Helper (`src/eval-server/sse-helpers.ts`)

```
startDynamicHeartbeat(res, intervalMs?)
  -> returns { update(data), stop() }
```

- `update(data: { phase: string; message: string; eval_id?: number })` -- replaces the current payload for subsequent ticks
- `stop()` -- clears the interval timer (idempotent, safe to call multiple times)
- First tick fires immediately on `start` with the initial data
- Subsequent ticks fire every `intervalMs` (default 3000ms) with whatever `update()` last set
- Each tick appends `elapsed_ms` to the payload automatically
- `withHeartbeat()` remains untouched

Type signature:
```typescript
interface DynamicHeartbeat {
  update(data: { phase: string; message: string; eval_id?: number }): void;
  stop(): void;
}

export function startDynamicHeartbeat(
  res: http.ServerResponse,
  intervalMs?: number,
): DynamicHeartbeat;
```

### Layer 2: Comparator Callback (`src/eval/comparator.ts`)

Add optional `onProgress` to `generateComparisonOutputs()` and `runComparison()`:

```typescript
type ProgressCallback = (phase: string, message: string) => void;

// generateComparisonOutputs gains optional 4th param
export async function generateComparisonOutputs(
  prompt: string,
  skillContent: string,
  client: LlmClient,
  onProgress?: ProgressCallback,
): Promise<ComparisonOutput>;

// runComparison gains optional 4th param
export async function runComparison(
  prompt: string,
  skillContent: string,
  client: LlmClient,
  onProgress?: ProgressCallback,
): Promise<ComparisonResult>;
```

Phase transition points inside the functions:

| Call site | Phase string | Message |
|---|---|---|
| Before `client.generate(skillSystemPrompt, ...)` | `generating_skill` | `Generating skill output...` |
| Before `client.generate(baselineSystemPrompt, ...)` | `generating_baseline` | `Generating baseline output...` |
| Before `scoreComparison(...)` | `scoring` | `Scoring responses...` |

Each fires `onProgress?.(phase, message)` -- the `?.` optional chain means no-op when undefined.

### Layer 3: Endpoint Wiring (`src/eval-server/api-routes.ts`)

In the compare endpoint loop (per eval case):

1. Call `startDynamicHeartbeat(res)` before `runComparison()`
2. Pass an `onProgress` callback that calls `heartbeat.update({ phase, message, eval_id })`
3. Call `heartbeat.stop()` in a `finally` block after `runComparison()` returns
4. Remove the existing `withHeartbeat()` wrapper from the compare endpoint
5. Remove the initial manual `sendSSE(res, "progress", { phase: "comparing", ... })` since the dynamic heartbeat's first tick replaces it

### Layer 4: Frontend Phase Support (`src/eval-ui/src/components/ProgressLog.tsx`)

Add to `spinnerPhases`: `generating_skill`, `generating_baseline`, `scoring`
Add to `accentPhases`: `generating_skill`, `generating_baseline`, `scoring`

These phases show a spinner when they are the latest active entry, and the accent-color dot when completed.

### Layer 5: ComparisonPage Integration (`src/eval-ui/src/pages/ComparisonPage.tsx`)

Adopt the same pattern as `BenchmarkPage.tsx`:

1. Import `ProgressLog` and `ProgressEntry`
2. In the event processing loop, extract `progress` events into a `progressEntries` array
3. Render `<ProgressLog entries={progressEntries} isRunning={running} />` below the start button / above the results

The existing `useSSE` hook already captures all SSE events including `progress` -- no hook changes needed.

## Data Flow

```
ComparisonPage
  |
  | POST /api/skills/:plugin/:skill/compare
  v
api-routes.ts (compare endpoint)
  |
  | startDynamicHeartbeat(res) -> heartbeat
  | runComparison(prompt, skill, client, onProgress)
  |   |
  |   | onProgress("generating_skill", msg)
  |   |   -> heartbeat.update({phase, message, eval_id})
  |   |   -> next tick: sendSSE(res, "progress", {phase, message, eval_id, elapsed_ms})
  |   |
  |   | client.generate(skillSystemPrompt, prompt)  [LLM call 1]
  |   |
  |   | onProgress("generating_baseline", msg)
  |   |   -> heartbeat.update(...)
  |   |
  |   | client.generate(baselineSystemPrompt, prompt)  [LLM call 2]
  |   |
  |   | onProgress("scoring", msg)
  |   |   -> heartbeat.update(...)
  |   |
  |   | scoreComparison(...)  [LLM call 3]
  |   |
  |   v returns ComparisonResult
  |
  | heartbeat.stop()
  v
SSE stream -> useSSE hook -> progress events -> ProgressLog
```

## Backward Compatibility

- `withHeartbeat()` is NOT modified or removed -- other endpoints (benchmark, improve) continue using it
- `generateComparisonOutputs()` and `runComparison()` accept the new param as optional -- existing callers (if any outside the endpoint) are unaffected
- The SSE event name remains `"progress"` -- the only change is the `phase` field value within the data payload
- `ProgressLog` already renders unknown phases with a green dot (the default branch in `phaseIcon`) so even if a consumer sees new phases before updating, it degrades gracefully

## Risk Mitigation

| Risk | Mitigation |
|---|---|
| Timer leak if `stop()` not called | `finally` block in endpoint guarantees cleanup; `stop()` is idempotent |
| `res.write()` after response closed | Existing `aborted` flag + `res.on("close")` pattern in the endpoint; `sendSSE` is fire-and-forget (Node swallows write errors on closed streams) |
| Multiple rapid `update()` calls before a tick | Last-write-wins semantics on the mutable payload ref -- safe, consistent |
| `onProgress` throws | Wrap callback invocations in try/catch inside comparator to prevent progress errors from killing the comparison |

## Files Changed

| File | Change |
|---|---|
| `src/eval-server/sse-helpers.ts` | Add `startDynamicHeartbeat()` export (~25 lines) |
| `src/eval/comparator.ts` | Add optional `onProgress` param to `generateComparisonOutputs()` and `runComparison()`, fire at 3 boundaries (~10 lines) |
| `src/eval-server/api-routes.ts` | Replace `withHeartbeat()` with `startDynamicHeartbeat()` + `onProgress` wiring in compare endpoint (~15 lines changed) |
| `src/eval-ui/src/components/ProgressLog.tsx` | Add 3 phases to `spinnerPhases` and `accentPhases` Sets (~2 lines) |
| `src/eval-ui/src/pages/ComparisonPage.tsx` | Import ProgressLog, extract progress entries from events, render component (~20 lines) |
| Tests (new) | Unit tests for `startDynamicHeartbeat`, `onProgress` callback in comparator, ProgressLog phase rendering |

## Test Strategy

- **`startDynamicHeartbeat`**: Unit test with a mock `ServerResponse` -- verify initial tick fires, `update()` changes payload, `stop()` clears timer, elapsed_ms increments
- **`onProgress` in comparator**: Unit test with a mock `LlmClient` -- verify callback fires 3 times with correct phase strings in correct order; verify no call when callback is undefined
- **ProgressLog phases**: Component test -- render with `generating_skill`/`generating_baseline`/`scoring` entries, assert spinner on latest, accent dot on completed
- **Integration**: E2E-style test of the compare endpoint with a mock client, verifying the SSE stream contains 3 distinct phase values before `done`
