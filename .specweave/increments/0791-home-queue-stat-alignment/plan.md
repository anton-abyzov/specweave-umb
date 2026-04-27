---
increment: 0791-home-queue-stat-alignment
---

# 0791: Plan

## Architecture

Single source of truth: `submissions:stats-cache` (KV) becomes the canonical home for both *submission lifecycle counts* and *registry verified-skill count*. The platform-stats cache (`platform:stats`) keeps its own `verifiedCount` for `/api/v1/stats` and the dashboard, but the homepage hero and `/queue` page both read the queue cache for the visible counters.

```
                ┌─────────────────────────────┐
   /queue ─────►│  submissions:stats-cache    │◄───── /  (HeroHeading)
                │  (KV)                       │
                │   total                     │
                │   active / published /      │
                │   rejected / blocked        │
                │   avgScore                  │
                │ + verifiedSkills  ◄─NEW     │
                └──────────▲──────────────────┘
                           │
                           │ refreshQueueStats() — cron + on-demand
                           │
                ┌──────────┴──────────────────┐
                │  computeQueueStats()        │
                │   Phase 1: Submission counts│
                │   Phase 1b: Skill table     │
                │     • AVG(certScore)        │
                │     • COUNT verified ◄─NEW  │
                │   Phase 2: rejection break  │
                │   Phase 3: KV metrics       │
                └─────────────────────────────┘
```

## Components touched

| File | Change |
|------|--------|
| `src/lib/cron/queue-stats-refresh.ts` | Add `verifiedSkills` to `QueueStats`; extend Phase 1b SQL to project `COUNT(*) FILTER (WHERE status IN (...))`; preserve regression baseline. |
| `src/lib/queue/queue-stats-cache.ts` | Backfill `verifiedSkills ??= 0` on cache reads; include in `EMPTY_QUEUE_STATS`. |
| `src/lib/queue/queue-stats-freshness.ts` | No change — freshness scoring unaffected. |
| `src/app/components/home/HeroStats.tsx` | Prefer `queueSnap.stats.verifiedSkills` over `stats.verifiedCount`; keep platform-stats fallback. |
| `src/app/components/home/HeroSearch.tsx` | No change — placeholder math floors whatever count it receives. |
| Tests (`*.test.ts`, `*.test.tsx`) | Add coverage per US-001/US-002/US-003. |

## SQL change (Phase 1b)

Before:
```sql
SELECT ROUND(AVG("certScore"))::int AS avg_score
FROM "Skill"
WHERE NOT "isDeprecated" AND "certScore" IS NOT NULL AND "certScore" > 0
```

After:
```sql
SELECT
  ROUND(AVG("certScore") FILTER (WHERE "certScore" IS NOT NULL AND "certScore" > 0))::int AS avg_score,
  COUNT(*) FILTER (WHERE "status" IN ('VERIFIED', 'CERTIFIED'))::int AS verified
FROM "Skill"
WHERE NOT "isDeprecated"
```

Both columns project from the same scan over the partial index on `isDeprecated`. The `FILTER` clauses keep the AVG and COUNT independent so a row with `certScore IS NULL` still counts toward `verified` if its status qualifies.

## Regression guard

`shouldOverwriteStats` already guards against `total` dropping to 0 from a non-zero baseline. Add a parallel guard: if `prev.verifiedSkills > 1000` and new `verifiedSkills === 0`, skip the write — same pattern.

## Rollout

1. Land the cron + cache change.
2. First cron tick after deploy populates `verifiedSkills` in KV.
3. Until that tick lands, homepage's fallback (platform-stats `verifiedCount`) renders — no visible regression.
4. After the tick, both pages show identical numbers.

## Observability

- `console.log` in cron after Phase 1b: `verifiedSkills computed: ${verifiedSkills}`.
- No new metrics or alerts needed.
