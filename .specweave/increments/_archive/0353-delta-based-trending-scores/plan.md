# Plan — 0353 Delta-Based Trending Scores

## Approach

1. Schema migration first (T-001: MetricsSnapshot model)
2. Data pipeline (T-002: insert snapshots, T-004: replace formula, T-005: pruning)
3. New trending module (T-003: computeTrendingScore function)
4. UI updates (T-006, T-007: update displays)
5. Edge case handling (T-008: non-GitHub skills)

## Key Files

| File | Changes |
|------|---------|
| `prisma/schema.prisma` | New MetricsSnapshot model with relation to Skill |
| `src/lib/cron/enrichment.ts` | Insert snapshots, query historical data, replace formula, add pruning |
| `src/lib/cron/trending-score.ts` | NEW: computeTrendingScore function with delta logic |
| `src/app/components/home/TrendingSkills.tsx` | Spark bar: trendingScore7d instead of githubStars |
| `src/app/skills/[name]/page.tsx` | "7d Trend" label |

## Formula Design

```
score = clamp(0, 100,
  (stars_now - stars_7d_ago) * 2.0
  + (downloads_now - downloads_7d_ago) * 0.001
  + (installs_now - installs_7d_ago) * 1.0
  + recencyBonus(lastCommitAt)  // 10 if <7d, 5 if <30d, 0 otherwise
)
```

Negative deltas contribute 0 per-metric (each term floored at 0).

## Snapshot Query Strategy

```sql
SELECT DISTINCT ON ("skillId") *
FROM "MetricsSnapshot"
WHERE "capturedAt" >= NOW() - INTERVAL '8 days'
  AND "capturedAt" <= NOW() - INTERVAL '6 days'
ORDER BY "skillId", "capturedAt" ASC
```

Gets the snapshot closest to 7 days ago per skill. Similar for 30d window.

## Dependencies

- **Requires 0354 completed**: transaction wrapping, metrics-can-decrease fix

## Verification

1. Unit tests for `computeTrendingScore` with various delta scenarios
2. Integration test: seed snapshots, run enrichment, verify scores
3. Test cold start: no snapshots → score 0
4. Test non-GitHub: star delta = 0, other metrics contribute
5. `npx vitest run` (full suite)
