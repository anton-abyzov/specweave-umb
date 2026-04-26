# 0773 — Fix View Queue deep-link + slow `/queue?q=` search

## Context

Two regressions on `verified-skill.com`:

1. **View Queue button doesn't deep-link to the just-submitted item.** After submitting a skill on `/submit`, the prominent "View Queue >>" button hard-codes `<a href="/queue">`. The user lands on the generic queue page (default filter, default sort) and has to scan a paginated list to find their submission. The `results` array already has every new submission ID — it's thrown away.

2. **`/queue?q=<term>` search is slow.** The `/api/v1/submissions/search` route runs two parallel Postgres queries (`findMany` + `count`) that both do `ILIKE %term%` over three columns (`skillName`, `repoUrl`, `id`). No `pg_trgm` GIN index exists, so each query is a sequential scan. There is no result cache. When the queue page is opened with `?q=` in the URL, the SSR path in `data.ts` still fetches the full queue list — the client immediately replaces it with search results, so the SSR fetch is wasted. On top, the queue client fires `fetchQueue()` on mount AND a debounce-triggered `doSearch()` AND a redundant filter-effect `doSearch()` — up to 5 Prisma roundtrips on a single cold `/queue?q=foo` page load. The `id` column is in the OR even though no user types UUID substrings. The `reason` filter is also silently dropped from the search query — a correctness bug.

## User Stories

### US-001 — Land on my submission after clicking "View Queue"

**As** a user who just submitted a skill,
**I want** the "View Queue >>" button to take me to my submission row in the queue,
**So that** I don't have to manually search a paginated list.

**Acceptance Criteria**:
- [x] AC-US1-01: The submit page's "View Queue >>" link includes `?filter=active&highlight=<id1>,<id2>,...` listing every submission ID created in the just-completed batch (excludes skipped, already-verified, and errored entries). Force `filter=active` because new submissions always start in the active bucket.
- [x] AC-US1-02: When the queue page loads with `?highlight=<ids>`, the first highlighted row scrolls into view (centered) within 1s of the table rendering.
- [x] AC-US1-03: Each highlighted row plays the existing `queue-row-flash` animation extended to ~4s on first render so it's visible without missing it.
- [x] AC-US1-04: If no highlighted ID is found on the rendered page, the queue auto-refetches with `filter=all` once and re-attempts scroll. No more than one fallback retry.
- [x] AC-US1-05: After the flash starts, the URL is rewritten via `router.replace` to drop `?highlight=` so reload/share doesn't re-flash.
- [x] AC-US1-06: The highlight ID list is capped at 50 server-side parsed IDs (URL-length safety).

### US-002 — Fast `/queue?q=` search

**As** a user searching the queue,
**I want** the search to feel instant (sub-second after debounce),
**So that** I can find my submission without waiting on a slow query.

**Acceptance Criteria**:
- [x] AC-US2-01: The search route caches results in `SUBMISSIONS_KV` keyed by `submissions:search:<lowercase-term>:<state>:<limit>:<offset>` with a 60s TTL. Cache hits return without a `findMany` call.
- [x] AC-US2-02: Cache writes are skipped when `state === "active"` (rows churn) or `term.length > 50` (avoid KV bloat). Cache writes are non-blocking (fire-and-forget on `ctx.waitUntil` or unawaited Promise).
- [x] AC-US2-03: The search route stops doing `contains` on the `id` column. Substring search is limited to `skillName` and `repoUrl`.
- [x] AC-US2-04: The search route accepts the `reason` filter and ANDs it into the `where` clause when `state` resolves to `rejected`. Currently the route ignores `reason` — a correctness bug.
- [x] AC-US2-05: The search route returns 400 when `term.length < 2` (matches client guard, defends against direct API hits).
- [x] AC-US2-06: The over-fetch multiplier for dedup drops from `limit*4` (max 400) to `limit*2` (max 200).

### US-003 — Eliminate redundant fetches on `/queue?q=` cold-load

**As** a user opening a deep-link to a search query,
**I want** the page to fetch only what's needed,
**So that** the search result appears in one DB roundtrip, not five.

**Acceptance Criteria**:
- [x] AC-US3-01: `getQueueInitialDataSSR` skips `getQueueSubmissionsSSR` and `getQueueSubmissionsDirectSSR` when `params.q` is present. Stats may still be fetched (cheap, KV).
- [x] AC-US3-02: `QueuePageClient` skips the mount-time `fetchQueueRef.current()` call when `searchQuery.length >= 2` — search results override the list anyway.
- [x] AC-US3-03: The debounce effect that runs on `searchInput` change is gated by a `didMountRef` so it doesn't fire a redundant search on initial mount when SSR-hydrated `searchInput` already equals the URL `q`.

### US-004 — Verify perf gain via tests

**As** a maintainer,
**I want** vitest assertions covering each optimization,
**So that** future refactors don't silently undo the work.

**Acceptance Criteria**:
- [x] AC-US4-01: Vitest covers cache-hit (no `findMany` call) and cache-miss (one `findMany` + cache write) paths in the search route.
- [x] AC-US4-02: Vitest asserts the `where.OR` length is 2 (no `id` clause) and the `take` is `limit*2` (max 200).
- [x] AC-US4-03: Vitest asserts `getQueueInitialDataSSR({q:"foo"})` returns `submissions: null` without calling the SSR list helpers.
- [x] AC-US4-04: Vitest asserts the submit page's View Queue link href contains `?filter=active&highlight=` with the expected IDs when at least one submission has an `id`.
- [x] AC-US4-05: Vitest asserts the search route ANDs `reason` into the `where` clause when present.

## Out of Scope

- Adding `pg_trgm` extension + GIN index. Recommended in `plan.md` for future work; defer until KV cache hit rate is measured.
- Replacing search with a typesense / meilisearch / vector index.
- Search-result virtualization in the table.
- `COUNT(*) OVER()` window function for single-roundtrip count + rows. Worth measuring after this increment lands; not implemented here.
- Increasing client debounce from 500ms → 750ms. Cache + skip-redundant-fetch should be enough.
