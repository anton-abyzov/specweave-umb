---
increment: 0789-submissions-list-filters
title: Add repoUrl and q filters to submissions list API
type: bug
priority: P1
status: completed
---

# 0789: Add repoUrl and q filters to submissions list API

## Problem

`GET /api/v1/submissions` parses `state`, `reason`, `limit`, `offset`, `sort`, `sortDir` from `searchParams` — but **never reads `repoUrl` or `q`**. Calls like:

```
GET /api/v1/submissions?repoUrl=https://github.com/vercel-labs/skills&limit=5
GET /api/v1/submissions?q=vercel-labs&limit=5
```

silently drop both filters. The handler returns the global default-state listing, served from the cache key `submissions:list:all::processingOrder:asc:50:0`. From the caller's perspective this looks like "the filter returned the wrong rows" — the rows are unrelated to the requested repo. Discovered 2026-04-27 during a crawler-coverage audit when three different `repoUrl` queries returned the same 200 anton-abyzov rows.

## Goal

Wire `repoUrl` (exact match) and `q` (case-insensitive substring on `skillName` OR `repoUrl`) into the GET handler's Prisma `where` clause, with cache-bypass when these admin filters are active so they don't poison the high-traffic queue-page caches.

## User Stories

### US-001: Filter by exact repoUrl
**Project**: vskill-platform

**As a** platform operator debugging a specific repo's submission history
**I want** to filter the submissions list by `repoUrl=<url>`
**So that** I see only that repo's submissions instead of the global newest list

**Acceptance Criteria**:
- [x] **AC-US1-01**: `GET /api/v1/submissions?repoUrl=https://github.com/foo/bar` filters Prisma `where` to `{ repoUrl: "https://github.com/foo/bar" }`
- [x] **AC-US1-02**: When `repoUrl` is present and contains a non-GitHub URL, the filter is silently dropped (no error, behaves like no filter — defense against accidental misuse)
- [x] **AC-US1-03**: When `repoUrl` is present, the KV cache fast-path is skipped on read AND the response is not written to the standard cache keys (avoids cache poisoning of the queue page)

### US-002: Search by free-text `q`
**Project**: vskill-platform

**As a** platform operator
**I want** to fuzzy-search submissions by `q=<text>` matching `skillName` OR `repoUrl`
**So that** I can find submissions by partial name without knowing the exact repo URL

**Acceptance Criteria**:
- [x] **AC-US2-01**: `GET /api/v1/submissions?q=vercel` filters where `skillName` ILIKE `%vercel%` OR `repoUrl` ILIKE `%vercel%`
- [x] **AC-US2-02**: `q` is bounded — strings shorter than 2 chars or longer than 100 chars are silently dropped (defense against pathological queries)
- [x] **AC-US2-03**: `q` works in combination with `state` and `repoUrl` (all filters AND-combined)
- [x] **AC-US2-04**: When `q` is present, the KV cache is bypassed (same rationale as US-001)

### US-003: Regression coverage
**Project**: vskill-platform

**As a** platform maintainer
**I want** unit tests that assert the filter changes results
**So that** silent-drop regressions are caught before reaching prod

**Acceptance Criteria**:
- [x] **AC-US3-01**: New vitest TC asserts `repoUrl` is read and added to the Prisma `where` clause
- [x] **AC-US3-02**: New vitest TC asserts `q` is read and added as `OR: [{ skillName: contains }, { repoUrl: contains }]`
- [x] **AC-US3-03**: Test asserts an unfiltered query (no `repoUrl`, no `q`) behaves identically to today (cache fast-path still wins)

## Out of Scope

- Pagination/limit changes
- Filter UI in the queue page (this is an API-level fix; UI is a separate concern)
- Authentication for these filters — they're read-only and the existing rate limit applies

## Non-Functional Requirements

- **Cache integrity**: Existing `submissions:list:*` cache keys must not be polluted by admin-filter results
- **Backwards compatibility**: All existing tests in `__tests__/route.cache-poison.test.ts`, `__tests__/parse-usable-list-cache.test.ts`, etc. must still pass
- **Defensive parsing**: Malformed `repoUrl` and out-of-bounds `q` are silently dropped, not 400-errored — keeps the endpoint forgiving
