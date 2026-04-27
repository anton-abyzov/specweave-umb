---
increment: 0789-submissions-list-filters
title: "Add repoUrl and q filters to submissions list API"
---

# Tasks: 0789 — Submissions list filters

### T-001: Parse repoUrl from searchParams + validate against GITHUB_REPO_VALIDATION_RE
**User Story**: US-001 | **AC**: AC-US1-01, AC-US1-02 | **Status**: [x] completed
**Test Plan**: Given `?repoUrl=https://github.com/foo/bar`, When the handler parses, Then `repoUrlFilter` is the URL. Given `?repoUrl=https://gitlab.com/x/y` (non-GitHub), Then `repoUrlFilter` is null.

### T-002: Parse q from searchParams + bound length [2..100]
**User Story**: US-002 | **AC**: AC-US2-01, AC-US2-02 | **Status**: [x] completed
**Test Plan**: Given `?q=v`, When parsed, Then `qFilter` is null (too short). Given `?q=foo`, Then `qFilter` is "foo". Given a 101-char `q`, Then `qFilter` is null.

### T-003: Add `hasAdminFilter` flag + bypass KV cache read & write
**User Story**: US-001, US-002 | **AC**: AC-US1-03, AC-US2-04 | **Status**: [x] completed
**Test Plan**: Given `?repoUrl=...` matches, When the handler runs, Then `SUBMISSIONS_KV.get(cacheKey)` is NOT called and `SUBMISSIONS_KV.put(cacheKey, ...)` is NOT called. Given no admin filter, Then KV is consulted as today.

### T-004: Add `where.repoUrl` assignment in where-clause builder
**User Story**: US-001 | **AC**: AC-US1-01 | **Status**: [x] completed
**Test Plan**: Given `?repoUrl=https://github.com/foo/bar`, When the handler calls Prisma, Then `where` includes `repoUrl: "https://github.com/foo/bar"`.

### T-005: Add `where.OR` for q filter (skillName + repoUrl ILIKE)
**User Story**: US-002 | **AC**: AC-US2-01 | **Status**: [x] completed
**Test Plan**: Given `?q=foo`, When the handler calls Prisma, Then `where.OR` is `[{ skillName: { contains: "foo", mode: "insensitive" } }, { repoUrl: { contains: "foo", mode: "insensitive" } }]`.

### T-006: Add vitest unit test file with 3 TCs
**User Story**: US-003 | **AC**: AC-US3-01, AC-US3-02, AC-US3-03 | **Status**: [x] completed
**Test Plan**: New file `__tests__/route.filters.test.ts` with TC-FILT-001/002/003 covering repoUrl filter, q filter, and cache-bypass behavior.

### T-007: Run regression — full submissions __tests__ suite + typecheck
**User Story**: US-001..US-003 | **AC**: NFR | **Status**: [x] completed
**Test Plan**: `npx vitest run src/app/api/v1/submissions/__tests__` → all green; `npx tsc --noEmit` → no new errors in `route.ts`.
