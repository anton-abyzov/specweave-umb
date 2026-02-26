# 0377: Architecture Plan

## Overview

Extend the existing `PlatformStats` KV caching pipeline to include trending skills data, then update the homepage component to read from cache instead of making a direct DB call.

## Changes by File

### 1. `src/lib/stats-compute.ts` — Add trendingSkills to PlatformStats

**Interface change:**
```typescript
export interface PlatformStats {
  // ... existing fields ...
  trendingSkills: TrendingSkillEntry[];  // NEW
  updatedAt: string;
}
```

**Type for KV-cached trending entry** (use `SkillData` from types.ts directly — no slim type to avoid mapping overhead and type mismatch bugs):

```typescript
import type { SkillData } from "./types";
// trendingSkills: SkillData[] in PlatformStats
```

**`computeFullStats()` change:**
- Add a 15th query to the `Promise.allSettled` array:
  ```typescript
  db.skill.findMany({
    where: { isDeprecated: false },
    orderBy: { trendingScore7d: "desc" },
    take: 8,
  }),
  ```
- Map result through `mapDbSkillToSkillData` (need to export or extract the mapper)
- Add to returned object: `trendingSkills: mappedResults`

**`computeMinimalStats()` change:**
- Add a try/catch block fetching top 8 trending skills
- Include `trendingSkills` in returned object (defaults to `[]` on failure)

**Mapper access:** `mapDbSkillToSkillData` is currently a private function in `data.ts`. Two options:
- **Option A (preferred):** Move the trending query INTO `stats-compute.ts` using raw Prisma and map manually (avoids circular deps, keeps data.ts unchanged)
- **Option B:** Export `mapDbSkillToSkillData` from `data.ts` and import in `stats-compute.ts`

Go with **Option A** — `stats-compute.ts` already does raw queries and has `getDb()` imported. The trending query is simple enough to map inline. Use the same field mapping as `mapDbSkillToSkillData` but keep it local to avoid coupling.

### 2. `src/lib/cron/stats-refresh.ts` — Update EMPTY_STATS and backfill

- Add `trendingSkills: []` to `EMPTY_STATS` constant
- Add `stats.trendingSkills ??= []` in `getPlatformStats` backfill section (alongside existing `rejectedCount`, `blocklistCount`, `totalScanned` backfills)

### 3. `src/app/components/home/TrendingSkills.tsx` — Read from cache

- Remove `import { getTrendingSkills } from "@/lib/data"`
- Get trending data from `getHomeStats()` (already imported and called)
- Reorder: call `getHomeStats()` first, extract `trendingSkills` from result
- Type the trending entries as `PlatformStats["trendingSkills"]` or use the array element type

### 4. Tests

- Update `src/lib/cron/__tests__/stats-refresh.test.ts`: verify `trendingSkills` is present in computed stats
- Existing `data.test.ts` / `data-db-first.test.ts` / `data-prisma.test.ts` tests for `getTrendingSkills` remain untouched (function still exists and is exported)

## Data Flow (After)

```
Cron (5 min) → computePlatformStats() [includes trendingSkills query]
            → refreshPlatformStats(kv) → KV.put("platform:stats", blob)

Homepage → getHomeStats() → resolveStatsKV() → KV.get("platform:stats")
         → TrendingSkillsSection reads stats.trendingSkills
         → No DB call for trending
```

## Risk Assessment

- **Low risk:** The trending query is identical to what `getTrendingSkills` already does
- **Backward compat:** Old cached blobs without `trendingSkills` will backfill to `[]`, component shows nothing (same as empty state)
- **KV blob size:** Adding 8 skill objects (~2-3 KB) to the stats blob is negligible (current blob is ~5-10 KB)
- **Staleness:** Trending data will be at most 5 minutes stale (cron interval) — acceptable for a ranking display
