# 0763 — Plan

## Files touched

| File | Change |
|---|---|
| `src/lib/cron/queue-stats-refresh.ts` | Replace ScanResult avg query with Skill.certScore query (lines 99-116). Drop the 5s timeout to ~2s — Skill table is small. |
| `src/app/components/home/HeroSearch.tsx` | Add optional `verifiedCount?: number` prop; render dynamic placeholder. |
| `src/app/page.tsx` | Pass `stats.verifiedCount` from `getHomeStats()` into `<HeroSearch>`. |
| `src/lib/cron/__tests__/queue-stats-refresh.test.ts` | (existing) HEALTHY/ZERO_DEGRADED fixtures already cover avgScore field; no schema change. |
| `src/app/components/home/__tests__/HeroSearch.test.tsx` | Add 3 cases: with count, with 0, with sub-1000 count. |

## Code changes

### 1. queue-stats-refresh.ts (lines 99-116 replacement)

```typescript
// Phase 1b: avg_score from Skill.certScore (small denormalized table).
// Previously queried ScanResult.score which has millions of rows and no index
// on score, causing the 5s timeout to fire on every cron run and leaving
// avgScore at the initialized 0. Skill table is ~115K rows with the
// rebuild-index path keeping certScore current; query returns in <500ms.
try {
  const rows = await withDbTimeout(
    () => db.$queryRaw<Array<{ avg_score: number | null }>>`
      SELECT ROUND(AVG("certScore"))::int AS avg_score
      FROM "Skill"
      WHERE NOT "isDeprecated" AND "certScore" IS NOT NULL AND "certScore" > 0
    `,
    2_000,
  );
  if (rows.length > 0 && rows[0].avg_score != null) {
    avgScore = Number(rows[0].avg_score);
  }
} catch (err) {
  console.warn("[queue-stats] Phase 1b avg_score skipped:", err instanceof Error ? err.message : err);
  // Not setting p1Degraded — counts are the critical part. Prior _memQueueStats
  // value is preserved by the shouldOverwriteStats regression guard downstream.
}
```

### 2. HeroSearch.tsx (signature + placeholder)

```typescript
export default function HeroSearch({ verifiedCount }: { verifiedCount?: number }) {
  // ...
  const placeholder = formatSearchPlaceholder(verifiedCount);
  // ...
}

function formatSearchPlaceholder(count: number | undefined): string {
  if (!count || count <= 0) return "Search verified skills...";
  if (count < 1000) return `Search ${count}+ verified skills...`;
  const floored = Math.floor(count / 1000) * 1000;
  return `Search ${floored.toLocaleString("en-US")}+ verified skills...`;
}
```

Export `formatSearchPlaceholder` for unit tests.

### 3. page.tsx (pass prop)

```typescript
const stats = await getHomeStats();
// ...
<HeroSearch verifiedCount={stats.verifiedCount} />
```

## Risks

- **Skill table avg drift from ScanResult avg**: certScore is set at rebuild-index time. If a skill is rescanned and ScanResult has a newer score, certScore lags until the next rebuild. Acceptable — same lag as `verifiedCount` on the home page; consistent narrative.
- **Cache invalidation**: existing KV cache (`submissions:stats-cache`) holds the bad `avgScore: 0` value. The next cron tick (≤30 min) will overwrite. To accelerate: prod operator can call `/api/v1/admin/refresh-stats` if available, or wait one cron tick. No manual data migration needed.
- **HeroSearch test snapshot churn**: existing tests render with no props — they will continue to pass (placeholder defaults to non-numeric phrase). New tests verify the count branches.

## Validation

- [ ] `npx vitest run src/lib/cron/__tests__/queue-stats-refresh.test.ts`
- [ ] `npx vitest run src/app/components/home/__tests__/HeroSearch.test.tsx`
- [ ] After deploy + 30 min: `curl https://verified-skill.com/api/v1/submissions/stats | jq .avgScore` returns positive integer
- [ ] Home page placeholder shows real count
