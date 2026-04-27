---
increment: 0789-submissions-list-filters
title: "Add repoUrl and q filters to submissions list API"
---

# Implementation Plan: 0789 — Submissions list filters

## Architecture

The fix is **strictly contained** in `src/app/api/v1/submissions/route.ts` GET handler. No new infrastructure, no schema changes, no migrations.

Key design choice: **admin filters bypass the KV cache.** The existing cache layer (`LIST_CACHE_PREFIX`, `LIST_LATEST_PREFIX`) is sized and shaped for the queue-page UI's high-traffic state-only filter switching. Sprinkling admin filters across cache keys would either (a) explode key cardinality, or (b) require cache-key normalization with subtle bugs. The simpler path: detect admin filters and route directly to Prisma without touching KV in either direction.

## Files Modified

| File | Change |
|---|---|
| `repositories/anton-abyzov/vskill-platform/src/app/api/v1/submissions/route.ts` | Parse `repoUrl` and `q` from `searchParams`; add to `where` clause; bypass KV cache fast-path AND cache-write when either filter is active |

## Files Created

| File | Purpose |
|---|---|
| `repositories/anton-abyzov/vskill-platform/src/app/api/v1/submissions/__tests__/route.filters.test.ts` | New vitest unit test for `repoUrl`/`q` filtering |

## AC-by-AC implementation

### US-001 — repoUrl filter

**AC-US1-01**: After existing `searchParams.get` block (around line 154):
```ts
const repoUrlParam = searchParams.get("repoUrl");
const repoUrlFilter = repoUrlParam && GITHUB_REPO_VALIDATION_RE.test(repoUrlParam) ? repoUrlParam : null;
```
Then in the where-clause builder (around line 215):
```ts
if (repoUrlFilter) where.repoUrl = repoUrlFilter;
```

**AC-US1-02**: The `GITHUB_REPO_VALIDATION_RE.test` guard rejects non-GitHub URLs. Already imported at line 22.

**AC-US1-03**: Add `hasAdminFilter` boolean early in the handler:
```ts
const hasAdminFilter = !!repoUrlFilter || !!qFilter;
```
Skip the KV cache read fast-path when `hasAdminFilter` is true. Skip the `listEnv.SUBMISSIONS_KV.put(cacheKey, ...)` write at the end when true.

### US-002 — q filter

**AC-US2-01**: Parse:
```ts
const qParam = searchParams.get("q")?.trim() ?? null;
const qFilter = qParam && qParam.length >= 2 && qParam.length <= 100 ? qParam : null;
```
Where clause:
```ts
if (qFilter) {
  where.OR = [
    { skillName: { contains: qFilter, mode: "insensitive" } },
    { repoUrl: { contains: qFilter, mode: "insensitive" } },
  ];
}
```

**AC-US2-02**: The `qParam.length >= 2 && <= 100` guard handles bounds.

**AC-US2-03**: Both filters AND-combine naturally because Prisma merges `where` keys with AND. If `state` is also set, all three apply via the existing `where.state` assignment that's already there.

**AC-US2-04**: Same `hasAdminFilter` gate as AC-US1-03.

### US-003 — Tests

**AC-US3-01 + AC-US3-02 + AC-US3-03**: New file `__tests__/route.filters.test.ts` with mocks of `getDb`, `dbCircuitAllows`, etc. (mirroring the pattern in `__tests__/route.cache-poison.test.ts` which already does this). Three TCs:
- TC-FILT-001: `?repoUrl=...` calls `db.submission.findMany` with `where.repoUrl` set
- TC-FILT-002: `?q=foo` calls `db.submission.findMany` with `where.OR` containing both `skillName` and `repoUrl` contains-filters
- TC-FILT-003: Unfiltered request hits the existing KV cache path (no DB call)

## Risk Assessment

| Risk | Likelihood | Mitigation |
|---|---|---|
| Cache poisoning from admin filters | None — admin filters bypass cache entirely | `hasAdminFilter` gate on both read & write |
| Existing tests break | Low — handler is additive | Run full `src/app/api/v1/submissions/__tests__/` suite |
| `OR` clause confused with `state` filter | Low | Prisma merges top-level `where` keys with AND; nested `OR` is scoped |
| `q` injection (Prisma string interpolation) | None | Prisma parameterizes `contains`; no raw SQL |

## Test Strategy

- **Unit (vitest)**: 3 new TCs for filter wiring
- **Regression**: full `src/app/api/v1/submissions/__tests__/` directory must pass

## Rollout

Single CF Worker deploy via `wrangler deploy`. No DB migration. Roll forward only — no traffic shift required since admin filters were never functional.
