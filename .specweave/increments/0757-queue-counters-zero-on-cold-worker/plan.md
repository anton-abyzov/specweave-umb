# Implementation Plan: Queue counters render 0/0/0/0/0 on cold Cloudflare workers

## Overview

Four-layer fix in `repositories/anton-abyzov/vskill-platform`. Each layer is independently small and has a tight, mockable test. No new modules, no new dependencies, no schema changes, no new env vars.

## Architecture

### Affected files (existing — modify only)

| File | Lines | Change | Layer |
|---|---|---|---|
| `src/lib/queue/queue-stats-cache.ts` | 12 | Bump `DB_STATS_FALLBACK_TIMEOUT_MS` from `150` → `800` | A (timeout) |
| `src/app/api/v1/submissions/stats/route.ts` | ~40-60 | Branch on `snapshot.source === "empty"` → return `NextResponse.json(body, { status: 503, headers: { "Retry-After": "5", ... } })` | B (503) |
| `src/app/queue/data.ts` | 27, 280, 293 | Type `QueueInitialData.stats` as `QueueStats \| null`. When `statsUnavailable`, return `stats: null` instead of zero stats. Same change in the no-data fallback branch. | C (SSR null) |
| `src/app/queue/QueuePageClient.tsx` | 38-52, 129, 225-246, 322-366, 663-687 | (1) `stats` state typed as `QueueStats \| null`, init from `initialData.stats ?? null`. (2) `EMPTY_STATS` constant kept for SSE optimistic deltas (where prev exists). (3) `StatCard` rendering: pass `null` value when `stats === null`; component renders `—`. (4) `fetchStats` — on 503 OR `{total:0, degraded:true}` body, schedule retry via `setTimeout` with attempt counter (max 3) at delays 1000/3000/7000ms. Reset counter on success or on `submission_created` SSE event. (5) Cleanup pending timer in `useEffect` cleanup. | D (client) |
| `src/app/queue/QueuePageComponents.tsx` | StatCard def | Accept `value: number \| null`; render `—` when `null` | D (client) |

### New test files

| File | Specs | Layer |
|---|---|---|
| `src/app/api/v1/submissions/stats/__tests__/route.test.ts` | (new or extend existing if present) — mocks `readQueueStatsSnapshot`; asserts 503+Retry-After when source=empty; 200 otherwise | B |
| `src/app/queue/__tests__/data.initial-data.test.ts` | extend — assert `stats: null` when degraded+zero; real stats pass through | C |
| `src/app/queue/__tests__/QueuePageClient.test.tsx` | extend — `initialData.stats=null` → 6 StatCards with `—`; retry chain on 503; cap at 3 attempts; reset on success | D |
| `src/app/queue/__tests__/QueuePageClient.sse.test.tsx` | extend — `submission_created` event resets retry counter | D |
| `src/lib/queue/__tests__/queue-stats-cache.test.ts` | extend (or add) — assert `DB_STATS_FALLBACK_TIMEOUT_MS === 800` (sanity pin) | A |

## Data flow (after fix)

```
Browser GET /queue
   ↓
Next.js SSR (Cloudflare Worker)
   ↓
getQueueInitialDataSSR()
   ├── readQueueStatsSnapshot()        — 4-tier fallback
   │     ├── KV    .get(submissions:stats-cache)   ~5-20ms
   │     ├── memory cache                          ~0ms (warm isolate)
   │     ├── DB    cachedStats.findUnique          ≤ 800ms (was 150ms) ★
   │     └── empty {total:0,degraded:true}
   └── Branch on source:
         ├── source ∈ {kv,memory,db}  → stats: real
         └── source = "empty"          → stats: null  ★
   ↓
QueuePageClient receives initialData
   ├── stats === null → render 6 StatCards with "—"  ★
   └── stats !== null → render real numbers
   ↓
useEffect → fetchStats() on mount
   ├── HTTP 503 (source=empty)        → schedule retry [1s/3s/7s]  ★
   ├── HTTP 200 + degraded + total=0  → schedule retry [1s/3s/7s]  ★
   ├── HTTP 200 + total>0             → setStats; reset retry counter
   └── HTTP 200 + degraded + total>0  → setStats (existing behavior)
   ↓
SSE submission_created event
   └── reset retry counter; trigger fetchStats  ★

★ = changed in this increment
```

## API contract

`GET /api/v1/submissions/stats`

| Snapshot source | HTTP | Body | Headers |
|---|---|---|---|
| `kv` | 200 | `{total, active, ..., degraded?, generatedAt}` | `X-Queue-Stats-Source: kv`, `X-Queue-Stats-Freshness: fresh|stale` |
| `memory` | 200 | same | `X-Queue-Stats-Source: memory` |
| `db` | 200 | same | `X-Queue-Stats-Source: db` |
| `empty` | **503** | `{total:0, ..., degraded:true, generatedAt}` | `X-Queue-Stats-Source: empty`, **`Retry-After: 5`** |

Body for `source: "empty"` is intentionally identical to current 200 body — only status code changes. This means a careless client that ignores status codes still sees the same JSON shape.

## Type changes

`src/app/queue/data.ts`:

```diff
 export interface QueueInitialData {
-  stats: QueueStats;
+  stats: QueueStats | null;   // null = source=empty; client renders placeholders
   submissions: SubmissionRow[] | null;
   total: number | null;
   queuePositions: Record<string, number> | null;
   defaultFilter: FilterCategory;
   mode: QueueBootMode;
   message?: string;
 }
```

`src/app/queue/QueuePageComponents.tsx` (StatCard):

```diff
 interface StatCardProps {
   label: string;
-  value: number;
+  value: number | null;
   ...
 }
```

`src/app/queue/QueuePageClient.tsx`:

```diff
-const [stats, setStats] = useState<QueueStats>(initialData.stats ?? EMPTY_STATS);
+const [stats, setStats] = useState<QueueStats | null>(initialData.stats);
```

## Retry chain — implementation sketch

```ts
const RETRY_DELAYS_MS = [1000, 3000, 7000] as const;
const retryAttemptRef = useRef(0);
const retryTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

const clearPendingRetry = useCallback(() => {
  if (retryTimerRef.current) {
    clearTimeout(retryTimerRef.current);
    retryTimerRef.current = null;
  }
}, []);

const scheduleRetry = useCallback(() => {
  const attempt = retryAttemptRef.current;
  if (attempt >= RETRY_DELAYS_MS.length) return;          // cap
  const delay = RETRY_DELAYS_MS[attempt];
  retryAttemptRef.current = attempt + 1;
  clearPendingRetry();
  retryTimerRef.current = setTimeout(() => {
    fetchStatsRef.current?.();
  }, delay);
}, [clearPendingRetry]);

const fetchStats = useCallback(async () => {
  try {
    const res = await fetch("/api/v1/submissions/stats");
    if (res.status === 503) {
      scheduleRetry();
      return;
    }
    if (res.ok) {
      const json = await res.json();
      if (json.total > 0 || !json.degraded) {
        const sum = (json.active||0) + (json.published||0) + (json.rejected||0) + (json.blocked||0) + (json.onHold||0);
        if (sum > json.total) json.total = sum;
        setStats(json);
        setStatsAreCached(false);
        retryAttemptRef.current = 0;     // reset on success
        clearPendingRetry();
      } else {
        scheduleRetry();                  // empty-degraded body → retry
      }
    }
  } catch { /* keep prev stats */ }
}, [scheduleRetry, clearPendingRetry]);

// Reset retry chain on submission_created SSE event
} else if (eventType === "submission_created") {
  retryAttemptRef.current = 0;
  clearPendingRetry();
  fetchQueueRef.current();
  fetchStatsRef.current();
}

// Cleanup on unmount
useEffect(() => () => clearPendingRetry(), [clearPendingRetry]);
```

## Architecture decisions

- **Why bump 150ms→800ms specifically?** Empirical observation: a cold Neon connection from a fresh Cloudflare isolate routinely takes 300-500ms for the first query (TLS handshake + connection auth + query). 150ms reliably misses; 800ms reliably catches. The bound stays well under Cloudflare's per-request CPU envelope (60s for scheduled events, 30s for fetch handlers per `wrangler.jsonc:12`).
- **Why 503 instead of 200 with a flag?** Status codes are the cheap, universal signal that intermediaries (CDNs, browsers, log analytics) understand. Existing client code can be updated trivially; new clients can branch on status without parsing bodies. Cache-Control `s-maxage=10, stale-while-revalidate=15` continues to apply to 200 responses; the 5xx response Bypass Cache by default in Cloudflare's CDN behavior.
- **Why em-dash specifically?** It's the existing convention in vskill-platform for "unknown / N/A" displayed values, semantically distinct from `0`. No new design tokens.
- **Why retry caps at 3 attempts (not infinite)?** Bounds total retry window to ~11 seconds. After that, the page surface remains in placeholder state until an SSE event or user navigation triggers fresh fetches. Avoids self-amplifying loops on persistent failures.
- **Why reset retry counter on `submission_created`?** SSE event implies the worker pool now has fresh activity; assume cold-worker condition has resolved.

## ADR refs

No new ADRs. Inherits the existing 4-tier fallback architecture (introduced in 0713). This increment tightens its boundaries.

## Rollback plan

Pure client + edge changes; revert by reverting the commit. Cache-Control `s-maxage=10` means clients pick up the reverted version within ~10 seconds at the CDN edge. No data migrations to undo.
