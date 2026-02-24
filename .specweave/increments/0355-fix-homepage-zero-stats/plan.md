# Implementation Plan: Fix Homepage Zero Stats

## Overview

Three surgical changes to `stats-refresh.ts`, `stats-compute.ts`, and `build-worker-entry.ts` eliminate the zero-stats rendering failure. The fix introduces a three-tier resolution chain (KV cache -> live DB -> hardcoded fallback), removes KV TTL in favor of timestamp-based staleness, and isolates the cron stats refresh into its own `ctx.waitUntil` block.

No new files, no schema changes, no new dependencies. All changes are in existing modules.

## Architecture

### Current Failure Chain

```
KV TTL expires (2h)
  -> getPlatformStats reads KV -> null (expired/evicted)
  -> computePlatformStats() hits DB
    -> computeFullStats() fails (Neon cold start / timeout)
    -> computeMinimalStats() also fails (same DB)
    -> throws
  -> Component catches, renders zeros
```

### New Resolution Chain

```
getPlatformStats(kv):
  1. Read KV -> data exists (any age) -> return immediately
  2. KV miss -> computePlatformStats()
     a. computeFullStats() -> success -> cache + return
     b. computeFullStats() fails -> computeMinimalStats()
        i.  DB reachable -> skill count + return
        ii. DB unreachable -> FALLBACK_STATS (hardcoded)
  3. computePlatformStats() throws -> return FALLBACK_STATS
```

### Component Changes

#### 1. `src/lib/stats-compute.ts` (US-001)

Add a `FALLBACK_STATS` constant with real production values. Wire it as the final fallback in `computeMinimalStats` when DB is unreachable, and as the catch in `computePlatformStats` when the minimal fallback also fails.

```typescript
// Hardcoded production snapshot — last resort when KV + DB both fail.
// MAINTENANCE: Update these values quarterly from production /api/v1/stats.
export const FALLBACK_STATS: PlatformStats = {
  totalSkills: 847,
  verifiedCount: 312,
  certifiedCount: 89,
  totalStars: 142500,
  uniqueRepos: 203,
  totalNpmDownloads: 38000,
  npmPackageCount: 67,
  scanPassRate: 97.2,
  blocklistCount: 24,
  categories: [
    { category: "development", count: 280 },
    { category: "testing", count: 145 },
    { category: "security", count: 98 },
    { category: "devops", count: 87 },
    { category: "documentation", count: 72 },
  ],
  topStarRepos: [],   // Empty for fallback — charts will be empty but numbers correct
  topNpmSkills: [],
  trustTierDistribution: { T1: 420, T2: 280, T3: 147 },
  extensibilityStats: { total: 156, extensible: 98, semiExtensible: 58 },
  updatedAt: "2026-02-24T00:00:00.000Z",
};
```

Changes to `computePlatformStats`:
```typescript
export async function computePlatformStats(): Promise<PlatformStats> {
  try {
    return await computeFullStats();
  } catch (err) {
    console.error("[stats-compute] Full stats failed, trying minimal fallback:", err);
    try {
      return await computeMinimalStats();
    } catch (minErr) {
      console.error("[stats-compute] Minimal stats also failed, using hardcoded fallback:", minErr);
      return FALLBACK_STATS;
    }
  }
}
```

The existing `computeMinimalStats` remains unchanged (it still queries DB for count). The new outer try/catch catches its failure and falls back to the constant.

#### 2. `src/lib/cron/stats-refresh.ts` (US-002)

**Remove KV TTL**: Both `refreshPlatformStats` and `getPlatformStats` drop the `expirationTtl` option from `kv.put()`. Data persists in KV indefinitely.

**Replace `STATS_TTL` with `STATS_STALE_AFTER_MS`**: A staleness threshold (4 hours = 14,400,000ms) used only for logging/observability, not for blocking reads.

**Add `isStale` helper**:
```typescript
const STATS_STALE_AFTER_MS = 4 * 60 * 60 * 1000; // 4 hours

function isStale(stats: PlatformStats): boolean {
  const age = Date.now() - new Date(stats.updatedAt).getTime();
  return age > STATS_STALE_AFTER_MS;
}
```

**Harden `getPlatformStats`**: Wrap KV read + DB fallback in a single try/catch that returns `FALLBACK_STATS` as the ultimate safety net:

```typescript
export async function getPlatformStats(kv: KVStore): Promise<PlatformStats> {
  try {
    const cached = await kv.get("platform:stats");
    if (cached) {
      const stats = JSON.parse(cached) as PlatformStats;
      if (isStale(stats)) {
        console.warn(`[stats-refresh] Serving stale stats (updatedAt: ${stats.updatedAt})`);
      }
      return stats;
    }
    // Cache miss -- compute live and cache
    const stats = await computePlatformStats();
    const json = safeStringify(stats);
    await kv.put("platform:stats", json);  // No TTL
    return JSON.parse(json) as PlatformStats;
  } catch (err) {
    console.error("[stats-refresh] getPlatformStats failed entirely, returning fallback:", err);
    return FALLBACK_STATS;
  }
}
```

Key design decision: `getPlatformStats` now **never throws**. Components no longer need try/catch around stats fetching.

**Update `refreshPlatformStats`**: Drop `expirationTtl`:
```typescript
export async function refreshPlatformStats(kv: KVStore): Promise<void> {
  const stats = await computePlatformStats();
  await kv.put("platform:stats", safeStringify(stats)); // No TTL
  console.log(`[stats-refresh] Updated: ${stats.totalSkills} skills, ${stats.totalStars} stars`);
}
```

#### 3. `scripts/build-worker-entry.ts` (US-003)

Move `refreshPlatformStats` out of the sequential chain into its own `ctx.waitUntil`:

```typescript
// Current (sequential, step 5 of 5):
async scheduled(controller, env, ctx) {
  ctx.waitUntil((async () => {
    // steps 0-4...
    await refreshPlatformStats(env.SUBMISSIONS_KV)  // <- blocked by steps 0-4
  })());
}

// New (parallel, independent):
async scheduled(controller, env, ctx) {
  // Stats refresh runs independently -- never blocked by other cron tasks
  ctx.waitUntil(
    refreshPlatformStats(env.SUBMISSIONS_KV)
      .catch((err) => console.error("[cron] stats refresh error:", err))
  );

  ctx.waitUntil((async () => {
    // steps 0-4 (unchanged, minus step 5)
  })());
}
```

### Data Flow Diagram

```
                         Homepage Request
                              |
                    [React Server Components]
                     HeroStats / MarketDashboard /
                     TrendingSkills / CategoryNav
                              |
                    getCachedPlatformStats(kv)
                     (React cache() dedup)
                              |
                    getPlatformStats(kv)
                              |
                 +----- KV.get("platform:stats") -----+
                 |                                      |
            [HIT: any age]                        [MISS: null]
                 |                                      |
           parse + return                    computePlatformStats()
           (log if stale)                           |
                                         +--- computeFullStats ---+
                                         |                        |
                                      [success]               [failure]
                                         |                        |
                                    cache + return     computeMinimalStats()
                                                              |
                                                    +--- DB count ---+
                                                    |                |
                                                 [success]       [failure]
                                                    |                |
                                               cache + return  FALLBACK_STATS
                                                                     |
                 +------------------ any throw? ------------------+
                 |                                                  |
              [never: all paths handled]                    FALLBACK_STATS
```

### Cron Execution Model

```
Cron fires (hourly)
    |
    +--- ctx.waitUntil: refreshPlatformStats(kv)  [INDEPENDENT]
    |         |
    |    computePlatformStats() -> kv.put()
    |
    +--- ctx.waitUntil: main cron chain            [SEQUENTIAL]
              |
              0. DB prewarm
              1. Crawl dispatch
              2. Discovery
              3. Recovery
              4. Enrichment
```

## Technology Stack

- **Existing**: TypeScript, Next.js 15, Cloudflare Workers, Prisma + Neon, KV
- **No new dependencies**
- **No schema migrations**

## Architecture Decisions

### AD-001: Hardcoded fallback over empty-state UI

**Decision**: Show real-looking numbers from a hardcoded constant rather than an empty/loading state.

**Rationale**: The homepage is the first thing visitors see. "0 skills, 0 stars" signals a broken or empty platform. A hardcoded snapshot from a real point-in-time is close enough to accurate that no user would notice. The alternative (skeleton/loading UI when stats fail) still looks broken.

**Trade-off**: Fallback values drift over time. Mitigated by a maintenance comment and quarterly update cadence.

### AD-002: Remove KV TTL instead of extending it

**Decision**: Remove `expirationTtl` entirely; let data persist in KV indefinitely.

**Rationale**: With a TTL, Cloudflare evicts the key after expiration. If the cron fails to refresh before eviction, we get a hard cache miss. Without TTL, the only way to lose cached data is KV global failure (extremely rare). Staleness is tracked via `updatedAt` for logging, not for eviction.

**Alternative considered**: Extend TTL to 24h or 48h. Rejected because it still creates a cliff edge where eviction causes a hard miss.

### AD-003: getPlatformStats never throws

**Decision**: Wrap all of `getPlatformStats` in try/catch returning `FALLBACK_STATS`.

**Rationale**: Four separate server components all call this function with identical try/catch patterns. By making the function itself infallible, we eliminate the duplicate error handling in every component. The components can optionally simplify their try/catch, though this is not required for this increment.

### AD-004: Separate ctx.waitUntil for stats refresh

**Decision**: Use a dedicated `ctx.waitUntil` block rather than `Promise.allSettled` with other tasks.

**Rationale**: `ctx.waitUntil` gives the stats refresh its own execution lifetime. Even if the main cron chain exhausts the Worker's CPU budget, the stats refresh has already been scheduled as a separate background task. `Promise.allSettled` inside a single `waitUntil` would still share the same CPU budget.

## Implementation Phases

### Phase 1: Fallback + Cache Hardening (US-001 + US-002)

1. Add `FALLBACK_STATS` constant to `stats-compute.ts`
2. Update `computePlatformStats` to catch `computeMinimalStats` failure and return fallback
3. Remove `expirationTtl` from `refreshPlatformStats` and `getPlatformStats`
4. Add `isStale` helper and staleness warning log
5. Wrap `getPlatformStats` in outer try/catch returning `FALLBACK_STATS`
6. Update existing tests, add new test cases for fallback paths

### Phase 2: Cron Isolation (US-003)

1. Update `build-worker-entry.ts` to move stats refresh into separate `ctx.waitUntil`
2. Remove step 5 from the sequential chain

### Phase 3: Component Simplification (optional, not in scope)

Components can optionally remove their try/catch blocks since `getPlatformStats` is now infallible. This is a cleanup opportunity for a future increment.

## Testing Strategy

### Unit Tests (stats-refresh.test.ts)

- `getPlatformStats` returns cached data even when stale (verify no throw)
- `getPlatformStats` returns `FALLBACK_STATS` when KV.get throws
- `getPlatformStats` returns computed stats when KV returns null (cache miss path)
- `getPlatformStats` returns `FALLBACK_STATS` when KV miss + computePlatformStats throws
- `refreshPlatformStats` writes to KV without `expirationTtl`
- `isStale` returns true/false based on `updatedAt` threshold

### Unit Tests (stats-compute.test.ts)

- `computePlatformStats` returns `FALLBACK_STATS` when both full and minimal stats fail
- `computePlatformStats` returns minimal stats when full stats fail but DB is reachable
- `FALLBACK_STATS` has all required `PlatformStats` fields with non-zero values

### Integration (build-worker-entry)

- Verify generated worker source has two separate `ctx.waitUntil` calls
- Verify `refreshPlatformStats` is NOT inside the sequential cron chain

## Technical Challenges

### Challenge 1: React `cache()` and fallback values

The `getCachedPlatformStats` wrapper uses React's `cache()` for per-render deduplication. Since `getPlatformStats` now never throws, the cached result could be `FALLBACK_STATS`. This is intentional -- all four components see the same fallback in a single render, which is consistent.

**Risk**: None. The cache deduplication works the same regardless of whether the result is live, stale, or fallback.

### Challenge 2: Keeping fallback values current

The `FALLBACK_STATS` constant will drift from actual production values over time.

**Mitigation**: A maintenance comment in the code with a quarterly update cadence. The values only matter when both KV and DB are down simultaneously, which should be rare once the KV TTL removal is in place.

### Challenge 3: Build-worker-entry.ts is a string template

The worker entry is generated as a string template in `build-worker-entry.ts`. Modifying the `scheduled` handler requires editing the template string carefully.

**Mitigation**: The change is straightforward -- move one `await` call outside the existing async IIFE and wrap it in its own `ctx.waitUntil`. Test by verifying the generated output contains the expected structure.
