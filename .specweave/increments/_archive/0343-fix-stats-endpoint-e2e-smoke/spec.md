# 0343 — Fix Stats Endpoint 500 + Production E2E Smoke Tests

## Problem
After deploying the DB-first skill architecture (0342), the homepage shows "0 security-scanned skills". The `/api/v1/stats` endpoint returns 500 because `computePlatformStats()` uses sequential `$queryRaw` calls with `::bigint` casts that fail on Cloudflare Workers with the PrismaNeon adapter.

The `/skills` page works fine (127 skills) — the issue is isolated to the stats computation.

## User Stories

### US-001: As a visitor, I see accurate skill counts on the homepage
**ACs:**
- [x] AC-US1-01: Homepage shows correct `totalSkills > 0` (not fallback zeros)
- [x] AC-US1-02: Stats API `/api/v1/stats` returns 200 with valid data
- [x] AC-US1-03: Trending skills section shows skills on homepage
- [x] AC-US1-04: Homepage loads within 10 seconds on production

### US-002: As a developer, stats computation is resilient and fast
**ACs:**
- [x] AC-US2-01: All raw SQL replaced with Prisma Client queries (except DISTINCT ON)
- [x] AC-US2-02: All queries run in parallel via single Promise.all
- [x] AC-US2-03: DISTINCT ON query has safe fallback on failure
- [x] AC-US2-04: Full computation failure falls back to minimal stats (at least totalSkills)
- [x] AC-US2-05: BigInt values safely serialized before KV storage

### US-003: As a developer, E2E smoke tests catch zero-data regressions
**ACs:**
- [x] AC-US3-01: Smoke test verifies homepage skill count > 0
- [x] AC-US3-02: Smoke test verifies stats API returns 200 with totalSkills > 0
- [x] AC-US3-03: Smoke test verifies skills API returns skills array with length > 0
- [x] AC-US3-04: Smoke test verifies trending skills visible on homepage
- [x] AC-US3-05: Smoke test runnable via `npm run test:e2e:smoke`
