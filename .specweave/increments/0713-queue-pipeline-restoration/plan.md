---
increment: 0713-queue-pipeline-restoration
title: "Queue Pipeline Restoration (P0) — Architecture & Plan"
---

# Architecture & Implementation Plan

## Design

### Layer 1 — Stats cron (US-001)

The cron at `src/lib/cron/queue-stats-refresh.ts` runs every 10 min via the `scheduled()` handler in `.open-next/worker-with-queues.js`. The current `_refreshQueueStatsImpl` does:

```
WITH deduped AS (
  SELECT DISTINCT ON ("repoUrl","skillName") id, state
  FROM "Submission"
  ORDER BY "repoUrl","skillName","updatedAt" DESC
)
SELECT COUNT(*) AS total,
       COUNT(*) FILTER (WHERE state IN ('RECEIVED','TIER1_SCANNING','TIER2_SCANNING')) AS active,
       ...
FROM deduped;
```

This times out at 15s on the 107k-row table. The CTE is now redundant: `(repoUrl, skillName)` was made a unique index in 0672, so duplicates are impossible. Replace with:

```
SELECT COUNT(*) AS total,
       COUNT(*) FILTER (WHERE state IN ('RECEIVED','TIER1_SCANNING','TIER2_SCANNING')) AS active,
       ...
FROM "Submission";
```

**Sentinel pattern**: When the query throws (timeout, WASM OOM, connection error), instead of writing `{total:0, degraded:true}` (which the regression guard then locks in), write a sentinel `{total:-1, active:-1, ..., degraded:true, error:"<reason>"}`. Update the regression guard at lines 208-218:

```typescript
function shouldOverwriteStats(prev: QueueStats | null, next: QueueStats): boolean {
  if (!prev) return true;                              // no prior — always write
  if (isFailureSentinel(next)) return true;            // failure write — always overwrite (records the outage)
  if (isFailureSentinel(prev)) return true;            // recovering from sentinel — always overwrite
  if (prev.total > 0 && next.total === 0) return false; // legitimate regression guard
  return true;
}
```

Add `isFailureSentinel(stats)` to `src/lib/queue/queue-stats-freshness.ts`:
```typescript
export function isFailureSentinel(s: QueueStats | null | undefined): boolean {
  return !!s && s.total === -1;
}
```

The /api/v1/submissions/stats route (`src/app/api/v1/submissions/stats/route.ts`) clamps sentinel values to 0 when serving to clients but preserves `degraded:true` so the UI can render "Counters refreshing…".

### Layer 2 — List endpoint (US-002)

`src/app/api/v1/submissions/route.ts` GET handler:

1. **`parseUsableListCache` (lines 78-94)**: today returns null when `submissions: []` and `total: 0`. Change to:
   - Return null when JSON parse fails OR the cached object is missing required fields
   - Return the cached payload when it's well-formed, even if `total === 0` (legitimate empty)
   - The "force DB recheck on suspicious zero" decision moves to the caller, where it can compare against current stats.

2. **Non-category branch (lines 401-412)**: wrap the `fetchSubmissionList` invocation in try/catch. On error, fall through to the existing 503 path at lines 472-491.

3. **Stats-vs-list mismatch check**: after a successful DB query that returned 0 rows, read `_memQueueStats` (or the same KV `submissions:stats-cache`). If stats indicate the requested category should have rows, log `list_empty_total_mismatch` and add `warning: "list_empty_total_mismatch"` to the response body. Status remains 200 (the DB IS the source of truth — but we want monitoring).

### Layer 3 — State-history shape (US-003)

`src/lib/submission/db-persist.ts:190` casts `fromState` as a string when null:
```typescript
fromState: prevState as string,  // null becomes "null" or empty
```

Replace with explicit Prisma JSON shape:
```typescript
const historyEntry: StateHistoryEntry = {
  timestamp: new Date().toISOString(),
  from: prevState ?? null,
  to: nextState,
  reason: reason ?? "unknown",
};
```

Validate at write-time: `to` MUST be a `SubmissionState` enum value; `from` MUST be either null (initial RECEIVED only) or a `SubmissionState` value. Throw on violation. The KV mirror (`hist:<id>`) uses the same shape — declare a shared `StateHistoryEntry` type if not already in `src/lib/submission/types.ts`.

**Backfill**: `scripts/backfill-state-history.ts` walks `Submission` table in batches of 500. For each row whose latest history entry is malformed (missing `to`, both `from` and `to` null, or empty/missing `reason`):
- If history is empty → create one entry with `{from: null, to: row.state, reason: "backfill:reconstructed", timestamp: row.updatedAt.toISOString()}`
- If history exists but is malformed → replace the malformed entry with reconstructed shape
- Write a `backfilled: true` marker on the entry to detect on re-runs (idempotent)
- `--dry-run` flag prints intended writes without committing

### Layer 4 — Drain script + recovery cron (US-004)

`scripts/drain-stuck-received.ts` (NEW) — runs locally with wrangler-authenticated credentials. CLI:
```
node scripts/drain-stuck-received.ts \
  [--repo-url https://github.com/heygen-com/hyperframes] \
  [--age-min 5] \
  [--limit 50] \
  [--dry-run]
```

Logic:
1. Connect via Prisma (same datasource as the worker).
2. Query: `SELECT id, state, "repoUrl", "skillName", "createdAt" FROM "Submission" WHERE state = 'RECEIVED' AND "createdAt" < NOW() - INTERVAL '<ageMin> minutes' [AND "repoUrl" = $1] ORDER BY "createdAt" ASC LIMIT $2;`
3. For each row, check the inflight set (KV `inflight:<id>` or `_memInflight`); skip if currently being processed.
4. `SUBMISSION_QUEUE.send({ type: "process_submission", submissionId: row.id })` — same payload as the original POST handler.
5. Log per-row outcome.

`recoverStaleReceived` cron — verify presence in `.open-next/worker-with-queues.js`'s `scheduled()` handler. If missing, add an entry that calls the drain logic with `--age-min 30 --limit 50` every 30 min. If present but broken (state-researcher's report says it exists), repair.

**Code reuse**: extract the queue-send logic from `drain-stuck-received.ts` into `src/lib/queue/recovery.ts` and import it from both the script and the cron.

### Layer 5 — Queue page UX (US-005)

`src/app/queue/data.ts` `chooseBootCandidates` (lines 59-66):

```typescript
function chooseBootCandidates(stats: QueueStats, requestedFilter?: FilterCategory): FilterCategory[] {
  if (requestedFilter) return [requestedFilter];                     // URL filter takes precedence
  if (stats.degraded) return ["all"];                                // honest fallback when stats are stale
  const ranked: FilterCategory[] = ["active", "published", "rejected", "blocked", "all"];
  const preferred = ranked.filter((f) => getFilterCount(stats, f) > 0);
  return preferred.length > 0 ? preferred : ["all"];                  // 'all' instead of empty array
}
```

`src/app/queue/QueuePageClient.tsx`:
- Add a per-tab config object:
  ```typescript
  const TAB_CONFIG: Record<FilterCategory, { defaultSort: { field: string; dir: "asc" | "desc" }; timeColumn: { label: string; field: "createdAt" | "updatedAt" } }> = {
    active: { defaultSort: { field: "processingOrder", dir: "asc" }, timeColumn: { label: "Submitted", field: "createdAt" } },
    published: { defaultSort: { field: "updatedAt", dir: "desc" }, timeColumn: { label: "Updated", field: "updatedAt" } },
    rejected: { defaultSort: { field: "updatedAt", dir: "desc" }, timeColumn: { label: "Updated", field: "updatedAt" } },
    all: { defaultSort: { field: "createdAt", dir: "desc" }, timeColumn: { label: "Last activity", field: "updatedAt" } },
    blocked: { defaultSort: { field: "updatedAt", dir: "desc" }, timeColumn: { label: "Updated", field: "updatedAt" } },
  };
  ```
- When URL `?sort=` and `?dir=` are absent, use `TAB_CONFIG[filter].defaultSort` for the API call.
- Replace dual time columns with a single column whose label and value come from `TAB_CONFIG[filter].timeColumn`.

`src/app/queue/components/StatsBar.tsx` (or wherever the stat cards live):
- When `stats.degraded === true`, render an inline ribbon: "Counters refreshing…" with `aria-live="polite"`.
- Stats numbers themselves still render but the ribbon makes their unreliability visible.

## Rationale

### Why drop the CTE rather than tune the timeout
The CTE was added for defense-in-depth against duplicate (repoUrl, skillName) rows from a pre-0672 era. 0672 made that impossible at the schema level. The CTE is now dead weight — extra cost, zero value. Tuning the 15s timeout would only delay recurrence under load.

### Why a -1 sentinel rather than a separate `lastFailureAt` field
A scalar sentinel means the existing comparison logic in the regression guard doesn't need to know about a new field. It distinguishes three cases (success/regression/failure) with one numeric inspection. The downside is that consumers must clamp -1 to 0 for display — but every consumer already passes through `clampToZero` or similar for safety, so the change surface is small.

### Why honor URL filter unconditionally rather than overriding under degradation
"URL is the user's intent" is a stronger contract than "the system knows best." If the user navigated to `?filter=active`, they want active even if the system thinks active=0. The current behavior (auto-flip on stats=0) was a misguided "smart default" that became a footgun the moment stats became unreliable.

### Why "all" as the degraded default rather than "active"
"Active" requires healthy stats to be meaningful (queue position, ETA). "All" sorted by createdAt desc is always answerable from the DB without any stats dependency. It's the safest fallback when we don't trust the counters.

### Why a separate drain script rather than a one-shot DB UPDATE
The submission lifecycle is queue-driven — re-enqueueing through `SUBMISSION_QUEUE.send` triggers the existing consumer with proper Tier 1 / Tier 2 scoring. A direct UPDATE (e.g., setting state=TIER1_SCANNING) would skip scoring and inevitably violate invariants. The script gives us an emergency lever and the recovery cron makes the same lever automatic for the next time.

### Why `updatedAt desc` for published/rejected as proxies for publishedAt/rejectedAt
The schema doesn't currently have first-class `publishedAt` / `rejectedAt` columns; adding them requires migration tooling and backfill, which is too heavy for this hotfix. `updatedAt` is correct most of the time (state transitions update it) and acceptable under "documented gap" until 0714 ships proper columns.

### Why surface `list_empty_total_mismatch` as a 200 warning rather than 5xx
The DB IS the source of truth for the list. If it returns zero rows, that's the truthful answer at the moment. The mismatch with stats is an observability signal, not an error condition. Returning 200 with a warning preserves caller compatibility (the UI doesn't need a new error path) while giving monitoring something to alert on.

## Files to modify

| File | Change | AC |
|------|--------|---|
| `src/lib/cron/queue-stats-refresh.ts` | Drop CTE, add sentinel write path, update regression guard | US-001 |
| `src/lib/queue/queue-stats-freshness.ts` | Add `isFailureSentinel` helper | US-001 |
| `src/app/api/v1/submissions/stats/route.ts` | Clamp -1 to 0 in response, preserve `degraded:true` | US-001 |
| `src/app/api/v1/submissions/route.ts` | Update `parseUsableListCache`, wrap non-category branch in try/catch, add stats-mismatch warning | US-002 |
| `src/lib/submission/db-persist.ts` | Type-safe state-history writer; reject null `to`; allow null `from` only on initial | US-003 |
| `src/lib/submission/types.ts` (if not present) | Export `StateHistoryEntry` type | US-003 |
| `scripts/drain-stuck-received.ts` (NEW) | Admin re-enqueue script | US-004 |
| `scripts/backfill-state-history.ts` (NEW) | Idempotent history backfill | US-003 |
| `src/lib/queue/recovery.ts` (NEW) | Shared queue-send logic for drain script + recovery cron | US-004 |
| `src/lib/cron/recover-stale-received.ts` | Wire/repair the 30-min cron entry | US-004 |
| `src/app/queue/data.ts` | Refactor `chooseBootCandidates` per design above | US-005 |
| `src/app/queue/QueuePageClient.tsx` | Per-tab config + per-tab default sort + single contextual time column | US-005 |
| `src/app/queue/components/StatsBar.tsx` | Inline "Counters refreshing…" when degraded | US-005 |

## Test files (NEW or extended)

| File | Tests | AC |
|------|-------|---|
| `tests/unit/cron/queue-stats-refresh.test.ts` | regression guard accepts sentinel; rejects 0-after-positive; sentinel→success unfreezes | US-001 |
| `tests/integration/api-submissions-list-failure.test.ts` | KV stale-empty falls through to DB; DB error → 503; mismatch → warning | US-002 |
| `tests/unit/submission/state-history.test.ts` | rejects null `to`; allows null `from` only on initial; KV+DB shapes match | US-003 |
| `tests/unit/scripts/drain-stuck-received.test.ts` | enqueues each row exactly once; skips inflight; respects --dry-run | US-004 |
| `tests/unit/queue/choose-boot-candidates.test.ts` | URL filter wins; degraded → "all"; healthy → ranked by counts | US-005 |
| `tests/integration/cron/recover-stale-received.test.ts` | picks up stale RECEIVED, emits queue.send | US-004 |
| `tests/e2e/queue-default-sort.spec.ts` | `?filter=all` → top row is most recent createdAt | US-005 |
| `tests/e2e/queue-degraded-no-flip.spec.ts` | mocked degraded stats → URL stays `/queue`, no redirect | US-005 |

## Sequencing & deploy strategy

**Phase 1 (P0 — must ship first, sequential within phase)**:
1. T-001 → T-006: Stats cron fix (US-001)
2. T-007 → T-012: List endpoint fix (US-002)
3. T-013 → T-016: Drain script + recovery cron (US-004)
4. **DEPLOY** vskill-platform → CF Workers
5. **VERIFY** stats unfreeze, list returns data
6. **RUN** drain script against `https://github.com/heygen-com/hyperframes`
7. **VERIFY** the 6 stuck rows transition out of RECEIVED within 60s

**Phase 2 (P1 — ship after Phase 1 verified)**:
8. T-017 → T-021: State-history shape + backfill (US-003)
9. T-022 → T-029: Queue page UX (US-005)
10. **DEPLOY** vskill-platform → CF Workers
11. **VERIFY** /queue does not redirect, per-tab columns/sort behave per spec

## Verification

```bash
# After Phase 1 deploy
curl -i 'https://verified-skill.com/api/v1/submissions/stats' | grep -i 'degraded\|generatedAt'
# expect: degraded:false, generatedAt < 11 min old

curl -s 'https://verified-skill.com/api/v1/submissions?state=all&sort=createdAt&sortDir=desc&limit=10' | jq '.items | length'
# expect: > 0

# Run drain
node scripts/drain-stuck-received.ts --repo-url https://github.com/heygen-com/hyperframes --age-min 5 --dry-run
node scripts/drain-stuck-received.ts --repo-url https://github.com/heygen-com/hyperframes --age-min 5

# Verify drained
for id in sub_4ce1d8a7-5819-4c65-8a8d-97182c79969a sub_e64164f1-e2b1-478b-a762-68bd15648ae8 sub_1ce97022-0c2a-432b-8158-978874d65a37 sub_79d9e244-1495-4014-a050-2be36f10adc4 sub_b8642378-69fd-4712-af24-06523917a057 sub_4a5b43de-10b4-4707-88ee-d0ecf6fb3e6f; do
  curl -s "https://verified-skill.com/api/v1/submissions/$id" | jq -r '.submission.state // .state'
done
# expect: TIER1_SCANNING / AUTO_APPROVED / PUBLISHED / TIER1_FAILED — anything but RECEIVED

# After Phase 2 deploy
# Visit https://verified-skill.com/queue → URL stays /queue, no redirect
# Visit https://verified-skill.com/queue?filter=all → top rows sorted by createdAt desc
# Each tab shows ONE time column

# Tests
cd repositories/anton-abyzov/vskill-platform
npx vitest run
npx playwright test tests/e2e/queue*.spec.ts
```

## ADR references

This increment does not introduce new architectural patterns warranting a fresh ADR. It restores the contracts established by:

- 0672 — `(repoUrl, skillName)` unique index that obsoletes the dedup CTE
- 0708 — `-1` sentinel pattern in platform-stats-refresh, replicated here for queue stats
- 0687 — original queue-stats-refresh implementation that this hotfix corrects

A follow-up ADR for "Per-tab default sort and contextual time column" can be authored alongside 0714 when first-class `publishedAt`/`rejectedAt` columns ship and the per-tab semantic becomes more pronounced.
