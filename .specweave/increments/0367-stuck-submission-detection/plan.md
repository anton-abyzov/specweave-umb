# Implementation Plan: Stuck Submission Detection

## Overview

This increment extends the existing submission pipeline in vskill-platform to detect and recover stuck submissions within minutes instead of hours. The architecture builds on top of existing modules (recovery.ts, consumer.ts, metrics-store.ts) with six focused changes: cron frequency, retry budget, inflight KV tracking, staleness warning API, error classification, and pre-aggregated timeout metrics.

All changes are confined to the `src/lib/queue/` and `src/app/api/` directories, with one UI enhancement to the submission status page. No schema migrations needed -- all new state uses KV with auto-expiring TTLs.

## Architecture

### Component Map

```
wrangler.jsonc                    -- Cron: */5 * * * *
  |
  v
build-worker-entry.ts             -- scheduled() handler (unchanged logic, faster cadence)
  |
  v
recovery.ts                       -- MODIFIED: 3-retry budget with backoff
  |-- reads recovery:budget:{id}  -- KV JSON: {count, lastRetryAt, nextRetryAfter}
  |-- reads inflight:{id}         -- KV JSON: {stage, startedAt, submissionId, error?}
  |-- writes timeout metrics      -- via recordTimeout()
  v
consumer.ts                       -- MODIFIED: inflight tracking + error classification
  |-- writes inflight:{id}        -- On processing start
  |-- deletes inflight:{id}       -- On success
  |-- classifies error            -- On failure
  |-- writes inflight:{id}.error  -- On failure (augments existing record)
  |-- calls recordTimeout()       -- On classified failure
  v
classify-error.ts                 -- NEW: classifyError() utility
  |
  v
metrics-store.ts                  -- MODIFIED: new recordTimeout() + getTimeoutMetrics()
  |-- writes tm:{hour}:{class}    -- Pre-aggregated hourly buckets
  v
GET /api/v1/submissions/[id]      -- MODIFIED: staleness field from inflight KV
GET /api/v1/admin/queue/metrics   -- MODIFIED: timeouts section in response
GET /api/v1/admin/queue/status    -- MODIFIED: timeout classification in stuck entries
```

### New KV Key Schemas

| Key Pattern | Value Schema | TTL | Written By | Read By |
|---|---|---|---|---|
| `recovery:budget:{id}` | `{"count":N,"lastRetryAt":"ISO","nextRetryAfter":"ISO"}` | 24h | recovery.ts | recovery.ts |
| `inflight:{id}` | `{"stage":"TIER1_SCANNING","startedAt":"ISO","submissionId":"sub_xxx"}` | 1h | consumer.ts | submissions/[id] API, recovery.ts |
| `tm:{ISO-hour}:{classification}` | `{"hour":"...","classification":"...","count":N,"totalDurationMs":N}` | 48h | metrics-store.ts | admin/queue/metrics API |

### Files Modified

| File | Change Type | US Coverage |
|---|---|---|
| `wrangler.jsonc` | Config: cron `*/5 * * * *` | US-001 |
| `src/lib/queue/recovery.ts` | Major rewrite: 3-retry budget, backoff | US-002 |
| `src/lib/queue/consumer.ts` | Add inflight KV writes, error classification | US-003, US-005 |
| `src/lib/queue/classify-error.ts` | New file: `classifyError()` utility | US-005 |
| `src/lib/queue/metrics-store.ts` | Add `recordTimeout()`, `getTimeoutMetrics()` | US-006 |
| `src/lib/queue/types.ts` | Add `TimeoutClassification`, `TimeoutMetricsBucket` types | US-005, US-006 |
| `src/app/api/v1/submissions/[id]/route.ts` | Add staleness field from inflight KV | US-004 |
| `src/app/api/v1/admin/queue/metrics/route.ts` | Add timeouts section to response | US-006 |
| `src/app/api/v1/admin/queue/status/route.ts` | Add classification to stuck entries | US-006 |
| `src/app/submit/[id]/page.tsx` | Render staleness warning banner | US-004 |

### Data Flow: Submission Processing (Modified)

```
1. Queue consumer receives message
2. consumer.ts writes inflight:{id} = {stage: "RECEIVED", startedAt: now}  [NEW]
3. processSubmission() runs pipeline
   a. updateState("TIER1_SCANNING") -> also updates inflight:{id}.stage   [NEW]
   b. Tier 1 scan runs
   c. updateState("TIER2_SCANNING") -> also updates inflight:{id}.stage   [NEW]
   d. Tier 2 scan runs
4a. SUCCESS: delete inflight:{id}, ack message                            [NEW]
4b. FAILURE: classify error, augment inflight:{id} with error,            [NEW]
    call recordTimeout(), retry message                                   [NEW]
5. Terminal state reached: delete inflight:{id}                           [NEW]
```

### Data Flow: Recovery (Modified)

```
1. Cron fires every 5 minutes (was hourly)                               [CHANGED]
2. getStuckSubmissions() finds entries stuck > 5 min (unchanged threshold)
3. For each stuck submission:
   a. Read recovery:budget:{id} from KV                                  [NEW]
   b. If budget not found: create with count=0, proceed to retry         [NEW]
   c. If now < nextRetryAfter: SKIP (backoff window not elapsed)         [NEW]
   d. If count >= 3: mark REJECTED with STUCK_EXHAUSTED                  [NEW]
   e. Otherwise: increment count, compute nextRetryAfter, re-enqueue     [CHANGED]
   f. Read inflight:{id} for classification context                      [NEW]
   g. recordTimeout(kv, classification, stuckForMs)                      [NEW]
```

### Data Flow: Staleness Warning

```
1. User visits /submit/{id}, frontend fetches GET /api/v1/submissions/{id}
2. API reads sub:{id} from KV (existing)
3. API reads inflight:{id} from KV                                       [NEW]
4. If inflight exists AND startedAt > 3 min ago:                         [NEW]
   - Add staleness field to response:
     {stale: true, staleSince: startedAt, staleStage: "TIER1_SCANNING",
      message: "Your submission appears stuck during Tier 1 scanning"}
5. Frontend renders yellow warning banner if staleness.stale === true     [NEW]
6. On next poll/SSE event, if submission progresses, staleness disappears [NEW]
```

## Architecture Decisions

### AD-001: Extend Recovery KV vs Add Prisma Column

**Decision**: Use KV (`recovery:budget:{id}`) instead of a Prisma column.

**Rationale**: The retry budget is ephemeral state (24h TTL, auto-cleans). Adding a Prisma column would require a schema migration, index on the retry count, and manual cleanup. KV with TTL is self-managing and matches the existing `recovery:retried:` pattern. The budget JSON replaces the boolean marker.

**Trade-off**: KV is eventually consistent (rare edge case: double-retry if two cron runs overlap). Mitigated by the 5-minute cron interval being much larger than KV propagation delay (~1s).

### AD-002: Inflight KV in Consumer vs updateState Hook

**Decision**: Write inflight KV directly in consumer.ts, not as a hook inside `updateState()`.

**Rationale**: The inflight tracking has different lifecycle semantics than submission state. It should be written at the start of processing (before any state transition) and deleted on completion. Coupling it to `updateState()` would create a tight dependency and add KV writes to every state transition (including non-scanning states like PUBLISHED). The consumer is the natural owner of "this submission is currently being processed."

**Trade-off**: Stage updates within `processSubmission()` (TIER1_SCANNING -> TIER2_SCANNING) need a mechanism to update the inflight KV. Solution: pass a lightweight callback or read-modify-write in the consumer's catch/finally block based on the current DB state.

**Refinement**: The consumer writes the initial inflight record. For stage updates (TIER1 -> TIER2), `updateState()` will check if the new state is a scanning state and update the inflight KV accordingly. This is a targeted hook (only for scanning states), not a blanket hook for all transitions.

### AD-003: Separate UX vs Recovery Thresholds

**Decision**: 3-minute UX warning, 5-minute recovery trigger.

**Rationale**: Users benefit from early notification that something may be wrong. But triggering recovery too early would create unnecessary re-enqueues for submissions that are legitimately processing (some Tier 2 LLM scans take 30-50s, and the withTimeout is 55s). The 5-minute recovery threshold ensures the original processing attempt has definitively timed out before intervening.

### AD-004: Pre-Aggregated Timeout Metrics

**Decision**: Write timeout counts to KV hourly buckets (same pattern as existing throughput metrics).

**Rationale**: The admin metrics API currently reads 24 hourly bucket keys. Adding 5 more keys per hour (one per classification) is negligible. On-the-fly computation would require scanning all inflight/recovery KV keys, which is expensive and subject to KV rate limits. The existing `getHourKey()` utility from metrics-store.ts is reused.

### AD-005: Error Classification in Consumer vs Process-Submission

**Decision**: Classify in consumer.ts catch block, not inside processSubmission().

**Rationale**: The consumer already catches all errors from processSubmission and has access to QUEUE_METRICS_KV for recording. Classifying at this level captures ALL failure modes (including the withTimeout wrapper itself). Process-submission throws; the consumer classifies, records, and retries.

## Technology Stack

- **Runtime**: Cloudflare Workers (existing)
- **KV**: Cloudflare KV for all new ephemeral state (existing bindings, no new namespaces)
- **DB**: Prisma/Neon (existing, no schema changes)
- **Frontend**: React client components (existing submission status page)
- **Testing**: Vitest with mock KV (existing test infrastructure)

## Implementation Phases

### Phase 1: Foundation (US-005, US-003)
1. New `classify-error.ts` utility with pattern matching
2. New types in `types.ts` (TimeoutClassification, TimeoutMetricsBucket)
3. Inflight KV write/delete in consumer.ts
4. Inflight KV stage update hook in updateState()

### Phase 2: Recovery Enhancement (US-001, US-002)
1. Change cron schedule in wrangler.jsonc
2. Rewrite recovery.ts with 3-retry budget and backoff logic
3. Migration: old `recovery:retried:` keys are compatible (budget-not-found = first attempt)

### Phase 3: User Experience (US-004)
1. Modify submission detail API to read inflight KV and compute staleness
2. Add staleness warning banner to submission status page

### Phase 4: Admin Observability (US-006)
1. Add `recordTimeout()` and `getTimeoutMetrics()` to metrics-store.ts
2. Wire recordTimeout into consumer.ts and recovery.ts
3. Extend admin metrics API response
4. Extend admin queue status API with classification context

## Testing Strategy

- **Unit tests**: `classify-error.test.ts` (pattern matching), `recovery.test.ts` (budget logic, backoff), `metrics-store.test.ts` (timeout aggregation)
- **Integration tests**: consumer.test.ts (inflight lifecycle), submissions/[id] route (staleness field)
- **Mock KV**: All tests use mock KV objects (existing pattern in test suite)
- **Edge cases**: concurrent recovery runs, KV TTL expiry during processing, classification of chained errors, budget overflow at exactly 3 retries

## Technical Challenges

### Challenge 1: Inflight KV Consistency During Crashes
**Problem**: If a Worker crashes mid-processing, the inflight KV key may contain stale data until TTL expires.
**Solution**: 1-hour TTL auto-cleans orphaned records. Recovery reads inflight KV for context but relies on DB `updatedAt` for the authoritative stuck check. The inflight KV is informational, not authoritative.

### Challenge 2: Race Between Consumer and Recovery
**Problem**: The consumer may be actively processing a submission when the recovery cron picks it up as "stuck" (the DB updatedAt hasn't been refreshed within 5 minutes).
**Solution**: The existing `getSubmission()` re-read in recovery.ts guards against this. Additionally, the inflight KV key serves as a signal that processing is active. Recovery can check `inflight:{id}` existence and skip if `startedAt` is recent (< 5 min). This provides double-checking beyond the DB query.

### Challenge 3: Backward Compatibility with Old Recovery Keys
**Problem**: Existing `recovery:retried:{id}` boolean keys from the old 1-retry system may still exist in KV.
**Solution**: Recovery.ts reads `recovery:budget:{id}` first. If not found, checks `recovery:retried:{id}` for backward compatibility -- if that exists, treat as count=1 and proceed to budget tracking. Old keys auto-expire via their existing 24h TTL.
