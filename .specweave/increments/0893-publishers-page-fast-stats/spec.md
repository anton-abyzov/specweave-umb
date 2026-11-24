# Publishers page fast stats

## Problem

verified-skill.com/publishers (and `/api/v1/authors`) returned HTTP 500 on uncached requests. Every cache miss runs one live aggregation over all public `Skill` rows (1.34M rows, 3.2 GB heap) inside a 10 s database budget. The default first page is cached in KV for 5 minutes and pre-warmed by cron, but every other sort, every search, every later page (which Google crawls) and every cache expiry runs the full aggregation. The 2026-10-07 covering index (`Skill_public_author_metrics_idx`) made the plan an index-only scan, yet the scan still touches ~350k buffers: production EXPLAIN ANALYZE on 2026-10-10 measured 7.3 s with a cold buffer cache (49.6k blocks read) and 0.8 s warm, after a manual VACUUM ANALYZE. Earlier production timings were 3-27 s. This is the remaining part of AC-03 in 0885-search-console-seo-recovery.

## Scope

In: a precomputed public publisher statistics snapshot (materialized view) with per-sort indexes, a snapshot reader used by the publisher list and count, a live taint guard, a fallback to the existing live aggregation while the snapshot is unavailable, refresh from the heavy cron cohort, per-table autovacuum tuning for `Skill`, tests, and the production apply/deploy steps for Anton. Out: changing eligibility rules, search semantics, the publisher detail page, KV cache keys/TTL, or applying anything to production from this session.

## Acceptance Criteria

- [ ] AC-01: With the `PublisherStats` snapshot present, every publisher list sort, search, later page and out-of-range total is served from the snapshot in one statement that reads an index range (no scan of `Skill` beyond the taint skip scan), with the same eligibility, ordering tie-break and totals as the live aggregation.
- [ ] AC-02: A publisher that gains a public, non-deprecated tainted skill is excluded from the list and totals immediately, without waiting for a snapshot refresh.
- [ ] AC-03: While the snapshot is missing or unpopulated, list and count fall back to the existing live aggregation without an error and retry the snapshot after one minute; timeouts and connectivity errors still propagate.
- [ ] AC-04: The heavy cron cohort refreshes the snapshot with `REFRESH MATERIALIZED VIEW CONCURRENTLY` (readers never blocked), logs the outcome and never throws.
- [ ] AC-05: `Skill` gets per-table autovacuum thresholds (2% vacuum and insert-vacuum, 1% analyze) through a migration, so the visibility map stays fresh for index-only scans without manual VACUUM.
- [ ] AC-06: In production the two migrations are applied and recorded, the worker is deployed, the snapshot refreshes on cron, and uncached `/publishers` requests (all sorts, page 2+, search) return 200 well under the 10 s budget.

## Approach

vskill-platform branch `fix/publishers-fast-stats` (worktree `repositories/anton-abyzov/0885-coverage`):

1. `prisma/migrations/20261010200000_publisher_stats_snapshot`: `CREATE MATERIALIZED VIEW "PublisherStats"` with the exact `author_stats` aggregation used today (public, non-deprecated, stars deduplicated per repository, tainted publishers excluded), a unique index on `author` (required for CONCURRENTLY) and one index per DESC sort order. ~110k rows, ~23 MB.
2. `src/lib/publishers/stats-snapshot.ts`: reader (`readPublisherSnapshotPage`, `countPublisherSnapshot`) with whitelisted ORDER BY fragments, bound search, total via a scalar count over the same `visible` CTE, and a live taint guard: a recursive skip scan over the existing `(isTainted, author)` index then an EXISTS check for public, non-deprecated rows (2 ms in production for 116k tainted rows / 5 authors; the naive DISTINCT took 4.3 s). Missing/unpopulated view (42P01/55000) returns null and is remembered for 60 s.
3. `src/lib/data.ts`: `getPublisherPage` and `getPublisherCount` try the snapshot first, then the unchanged live SQL.
4. `scripts/build-worker-entry.ts`: heavy cohort runs `refreshPublisherStats()` in its own `ctx.waitUntil` (cron wall time, not the 30 s fetch waitUntil of cache-warm); not wrapped in `withDbTimeout` so a slow refresh cannot trip the request circuit breaker.
5. `prisma/migrations/20261010200100_skill_autovacuum_tuning`: `ALTER TABLE "Skill" SET (...)`; justified by 1.39M updates with one autovacuum at the 20% default.

Freshness trade-off: counts, stars, newly published, newly private or deprecated publishers lag by at most one heavy tick (10 min); taint is live. Rejected: KV-only stale-while-revalidate (still runs the full aggregation for every later page and search), a plain stats table rewritten by DELETE+INSERT (about 110k row writes and WAL every refresh, versus CONCURRENTLY writing only changed rows), keeping a `refreshedAt` column in the view (changes every row, defeating CONCURRENTLY's diff). Production apply goes through psql with `--single-transaction` plus `prisma migrate resolve --applied`, never `prisma migrate deploy` (other migrations are pending there). The code is safe to deploy before the migration (fallback path).

Measured locally (PostgreSQL 14, synthetic 1.34M-row `Skill`, 110,766 publishers): view build 0.45 s, indexes 0.2 s, refresh CONCURRENTLY 0.68 s; snapshot reads 6-25 ms for every sort, 20 ms for page 500, 19 ms for search, count 6 ms; live aggregation fallback 0.46 s warm on the same data (7.3 s cold in production).

## Open questions

- none

## Tasks

### T-01 Publisher stats snapshot, reader, taint guard and fallback
- AC: AC-01, AC-02, AC-03 | Files: repositories/anton-abyzov/vskill-platform/prisma/migrations/20261010200000_publisher_stats_snapshot/migration.sql, repositories/anton-abyzov/vskill-platform/src/lib/publishers/stats-snapshot.ts, repositories/anton-abyzov/vskill-platform/src/lib/data.ts, repositories/anton-abyzov/vskill-platform/src/lib/__tests__/publisher-stats-snapshot.test.ts, repositories/anton-abyzov/vskill-platform/src/lib/__tests__/publisher-public-scope.test.ts | Test: cd /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/0885-coverage && npx vitest run src/lib/__tests__/publisher-stats-snapshot.test.ts src/lib/__tests__/publisher-public-scope.test.ts src/lib/__tests__/publisher-list-page.test.ts

### T-02 Refresh the snapshot from the heavy cron cohort
- AC: AC-04 | Files: repositories/anton-abyzov/vskill-platform/scripts/build-worker-entry.ts, repositories/anton-abyzov/vskill-platform/scripts/__tests__/build-worker-entry.test.ts | Test: cd /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/0885-coverage && npx vitest run scripts/__tests__/build-worker-entry.test.ts src/lib/__tests__/publisher-stats-snapshot.test.ts

### T-03 Skill autovacuum tuning migration
- AC: AC-05 | Files: repositories/anton-abyzov/vskill-platform/prisma/migrations/20261010200100_skill_autovacuum_tuning/migration.sql | Test: grep -q "autovacuum_vacuum_scale_factor = 0.02" /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/0885-coverage/prisma/migrations/20261010200100_skill_autovacuum_tuning/migration.sql && grep -q "autovacuum_analyze_scale_factor = 0.01" /Users/antonabyzov/Projects/github/specweave-umb/repositories/anton-abyzov/0885-coverage/prisma/migrations/20261010200100_skill_autovacuum_tuning/migration.sql

### T-04 Production apply, deploy and uncached proof (Anton)
- AC: AC-06 | Files: none (production operation; steps in the vskill-platform PR body) | Test: for p in "/publishers?sort=skillCount" "/publishers?page=2" "/publishers?search=anton" "/api/v1/authors?sort=trust&limit=21&offset=40"; do curl -s -o /dev/null -w "%{http_code} %{time_total}\n" "https://verified-skill.com$p" | awk '$1!=200 || $2>3 {exit 1}'; done
