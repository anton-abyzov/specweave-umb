---
increment: 0658-fix-submission-pipeline-reliability
type: bug
priority: P1
---

# Architecture Plan: Fix Submission Pipeline Reliability

## Overview

Three surgical fixes to break the submission deadlock chain. All changes are additive (new code paths) or constant-value changes — no state machine modifications, no new DB tables, no new APIs.

**Risk**: Low. Each fix is independent and backward-compatible. Existing behavior preserved for all non-stuck submissions.

## Architecture Decision: Inline Fix vs. Separate Recovery Service

**Decision**: Inline fix in existing files.

**Rationale**: All three bugs are off-by-one/missing-check issues in existing code paths. Introducing new modules would increase surface area without benefit. The existing `isStale()`, `waitUntil()`, and threshold constant patterns are proven and reusable.

**Rejected alternative**: Adding a new "submission watchdog" worker. Overkill for 3 constant/logic fixes. Would require new Cloudflare Worker binding, deployment config, and monitoring — violates minimal-change principle.

## Component Changes

### Component 1: Dedup Pending Staleness (Bug A)
**Project**: vskill-platform
**Files**: `src/lib/submission-dedup.ts`
**Satisfies**: US-001 (AC-US1-01 through AC-US1-05)

#### Current Behavior
```
checkSubmissionDedup():
  if PENDING_STATES.includes(state) → return { kind: "pending" }  // NO staleness check
```

#### Target Behavior
```
checkSubmissionDedup():
  if PENDING_STATES.includes(state):
    if isStale(updatedAt, state, config) → return { kind: "new" }   // ← NEW
    else → return { kind: "pending" }
```

#### Changes

1. **Add `DEFAULT_STALE_PENDING_HOURS = 4`** constant (line ~29 area)

2. **Add `stalePendingHours` to `DedupConfig` interface** (line ~15 area)
   ```typescript
   stalePendingHours?: number;
   ```

3. **Add `stalePendingHours` to `buildDedupConfig()`** (line ~45 area)
   ```typescript
   stalePendingHours: parseEnvNumber(e.DEDUP_STALE_PENDING_HOURS as string),
   ```

4. **Add PENDING case to `getStalenessHours()`** (line ~51-58)
   - Add check: if `state` is in `PENDING_STATES`, return `config?.stalePendingHours ?? DEFAULT_STALE_PENDING_HOURS`
   - Insert before the `return defaultH` fallback line

5. **Add staleness gate in `checkSubmissionDedup()`** (line ~82-85)
   - Before returning `{ kind: "pending" }`, check `isStale(existing.updatedAt, existing.state, config)`
   - If stale, return `{ kind: "new" }` instead

6. **Add staleness gate in `checkSubmissionDedupBatch()`** (line ~182-184)
   - Same pattern: before `results.set(name, { kind: "pending" })`, check `isStale()`
   - If stale, fall through to `needsSkillCheck` instead of setting "pending"

#### Design Notes
- Reuses the existing `isStale()` function (line 61-65) — it's already generic and parameterized by state
- `getStalenessHours()` is the single source of truth for all staleness windows — adding PENDING here propagates everywhere
- 4-hour default is a balance: long enough for legitimate Tier2 LLM scans (which can take 30-60 min), short enough to unblock genuinely stuck submissions before the next cron cycle

### Component 2: Queue Send Failure Fallback (Bug B)
**Project**: vskill-platform
**Files**: `src/app/api/v1/submissions/route.ts`
**Satisfies**: US-002 (AC-US2-01 through AC-US2-04)

#### Current Behavior
```
Single send (line 811-826):
  try { await SUBMISSION_QUEUE.send(...) }
  catch { console.error(...) }  // submission silently dropped

Batch send (line 724-749):
  try { await SUBMISSION_QUEUE.sendBatch(...) }
  catch { console.error(...) }  // entire chunk silently dropped
```

#### Target Behavior
```
Single send:
  try { await SUBMISSION_QUEUE.send(...) }
  catch {
    console.warn(...)  // downgrade to warn, add fallback note
    pendingProcessing.push(...)  // ← reuse existing inline path
  }

Batch send:
  try { await SUBMISSION_QUEUE.sendBatch(...) }
  catch {
    console.warn(...)
    pendingProcessing.push(...chunk)  // ← add failed chunk to inline path
  }
```

#### Changes

1. **Lift `pendingProcessing` declaration** to outer scope (before the `if (isBatch)` branch at line ~666) so both batch and sequential paths can append fallback items.

2. **Single send fallback** (line ~821-826): Replace `console.error` with `console.warn` and push to `pendingProcessing` array.
   - Push `{ submissionId: submission.id, skillName: skill.name, skillPath: skill.path }` into it on queue failure.

3. **Batch send fallback** (line ~743-748): On `sendBatch()` failure, push the failed chunk's items into `pendingProcessing`.
   - Iterate `chunk` and push each item's `{ submissionId, skillName, skillPath }`.

4. **Shared `waitUntil()` processing**: Move the existing `waitUntil()` block (lines 844-876) to after both code paths converge, so it handles fallback items from either batch or single mode. Guard with `if (pendingProcessing.length > 0)`.

#### Design Notes
- Zero new APIs or abstractions — reuses the existing `pendingProcessing` + `waitUntil(processSubmission(...))` pattern
- The inline path already has staggered batching (BATCH_SIZE=5, BATCH_DELAY_MS=500) to respect GitHub rate limits
- If inline processing ALSO fails, the submission stays in RECEIVED state — the recovery cron (with the reduced threshold from Bug C) will pick it up within 15 minutes

### Component 3: RECEIVED Recovery Threshold Reduction (Bug C)
**Project**: vskill-platform
**Files**: `src/lib/submission-store.ts`
**Satisfies**: US-003 (AC-US3-01 through AC-US3-05)

#### Current Behavior
```
STALE_RECEIVED_THRESHOLD_MS = 2 * 60 * 60 * 1000  // 2 hours
```

#### Target Behavior
```
STALE_RECEIVED_THRESHOLD_MS = 15 * 60 * 1000  // 15 minutes — aligned with STUCK_THRESHOLD_MS
```

#### Changes

1. **Change constant value** (line 1618): `2 * 60 * 60 * 1000` → `15 * 60 * 1000`

2. **Update comment** to reflect alignment with `STUCK_THRESHOLD_MS`

#### Design Notes
- One-line change. The entire `recoverStaleReceived()` function logic remains identical
- The `updatedAt` touch after re-enqueue (line 505-508) prevents re-enqueue loops: after touch, the submission's `updatedAt` is "now", so the next 15-min threshold check won't re-enqueue it until it's stuck again for another 15 minutes
- The 24-hour `VERY_OLD_RECEIVED_MS` threshold (line 440) is unchanged — very old items still get auto-rejected
- The `MAX_STALE_RETRIES = 3` budget (line 442) is unchanged — items still get 3 retry attempts before rejection

## Interaction Between Fixes

```
Submission arrives → POST /submissions creates DB record (RECEIVED)
                  → Queue send attempted
                      ├─ SUCCESS: normal queue processing
                      └─ FAILURE (Bug B fix): inline waitUntil() fallback
                           ├─ SUCCESS: normal processing continues
                           └─ FAILURE: stays in RECEIVED
                                └─ Recovery cron (every 30 min):
                                    └─ recoverStaleReceived() detects at 15 min (Bug C fix)
                                        └─ Re-enqueues (max 3 retries)
                                            └─ If all retries exhausted: auto-reject

Meanwhile, if user re-submits same skill:
  → checkSubmissionDedup() finds stuck RECEIVED submission
      ├─ < 4 hours old: returns "pending" (legitimate in-flight)
      └─ > 4 hours old (Bug A fix): returns "new" (allows resubmission)
```

## Testing Strategy

All tests use Vitest with ESM mocking (`vi.hoisted()` + `vi.mock()`), matching existing test patterns in `src/lib/__tests__/submission-store.test.ts` and `src/lib/queue/__tests__/recovery.test.ts`.

### Bug A Tests (submission-dedup.test.ts — new file or extend existing)
- Pending submission within staleness window → returns `kind:"pending"`
- Pending submission past staleness window → returns `kind:"new"`
- Custom `stalePendingHours` config overrides default
- Batch mode applies same staleness logic
- All existing PUBLISHED/REJECTED/BLOCKED staleness behavior unchanged

### Bug B Tests (route.test.ts — extend existing)
- Queue send failure triggers `pendingProcessing` fallback
- Batch queue send failure triggers fallback for failed chunk
- API response unchanged on queue failure
- Double failure (queue + inline) logs both errors, submission stays RECEIVED

### Bug C Tests (submission-store.test.ts — extend existing)
- RECEIVED submission at 20 minutes → detected as stale
- RECEIVED submission at 10 minutes → not yet stale
- 24-hour auto-rejection unchanged
- Retry budget unchanged

## Deployment Notes

- All changes are in the vskill-platform Cloudflare Worker
- No new environment variables required (DEDUP_STALE_PENDING_HOURS is optional)
- No database migrations
- No new Cloudflare bindings
- Safe to deploy atomically — each fix is independent and backward-compatible
- Rollback: revert the commit; all changes are constant/logic modifications in existing functions

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| 4h pending staleness too aggressive | Low | Low | Configurable via env; 4h is 8x the max expected scan time |
| Inline fallback overloads Worker | Low | Medium | Staggered batching (5 concurrent, 500ms delay) already in place |
| 15min threshold causes re-enqueue storms | Low | Low | `updatedAt` touch + 30min cron interval = max 1 re-enqueue per cron |
| Existing tests break | Very Low | Medium | Changes are additive; no behavior change for non-stuck paths |
