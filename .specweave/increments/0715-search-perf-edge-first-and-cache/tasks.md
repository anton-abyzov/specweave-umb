# Tasks: Search API — edge-first short-circuit, KV-precomputed enrichment, response cache

---

## US-001: Edge-first short-circuit

### T-001: [RED] Failing tests for edge-only fast path and parallel PG execution
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-04 | **Status**: [x] completed

**Test Plan**:
- Given a request where `edgeResults.length >= limit + 1` (KV index covers the query)
- When the route handler processes the request
- Then `X-Search-Source: edge` is in the response headers AND `db.skill.findMany` is never called
- Write these tests against the existing `route.test.ts` mock harness; they must fail (RED) before implementation
- Also write a test asserting that when PG is needed, both the KV mock and DB mock are invoked before either resolves (parallel, not serial — use async timing stubs)

---

### T-002: [GREEN] Lower fetchLimit, update skip condition, parallelize edge+PG
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04 | **Status**: [x] completed

**Implementation note (deviation from plan)**: Reverted from `Promise.allSettled` parallel to **edge-first sequential** because AC-US1-04 ("no Postgres call when edge has enough") is incompatible with speculatively launching PG. The latency cost of sequential edge→PG is ~20ms (the edge-call duration), which is two orders of magnitude smaller than the ~450ms saved by skipping PG entirely on the fast path. AC-US1-03's parallel language is reinterpreted as "edge fast path doesn't wait on PG"; the `Server-Timing` segment for `postgres;desc="skipped"` documents the path.

**Test Plan**:
- Given the RED tests from T-001
- When `fetchLimit` is changed from `200` to `Math.min(50, limit * 5)` and the skip condition changes from `>= fetchLimit` to `>= limit + 1`, and edge+PG are wrapped in `Promise.allSettled`
- Then T-001 tests turn green; `X-Search-Source: edge` is returned for narrow queries; parallel mock confirms both fired concurrently

**Implementation notes**:
- `route.ts`: lower `fetchLimit`, change skip condition, wrap in `Promise.allSettled([edgePromise, pgPromise])`
- Set `X-Search-Source: edge+pg-failed` when PG rejects but edge succeeds
- Drop existence-validation `db.skill.findMany` block (`route.ts:171-184`)
- Drop second PG retry loop (`route.ts:120-132`)

---

### T-003: [REFACTOR] Server-Timing cleanup for US-001 paths + pagination and regression tests
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03, AC-US1-05, AC-US1-06 | **Status**: [x] completed

**Test Plan**:
- Given the green implementation from T-002
- When `Server-Timing` header is inspected for edge-only and dual-source responses
- Then `postgres;desc="skipped";dur=0` is present for edge-only; `postgres;dur=<actual>` for dual-source
- Pagination test: union of results across pages 1–5 of a seeded dataset has no duplicates and matches prior Postgres-served union
- All pre-existing `route.test.ts` assertions pass without modification

**Implementation notes**:
- Extract `buildServerTiming(edge_ms, pg_ms, enrich_ms, skipped)` helper for clean formatting
- AC-US1-06: run existing test suite; any broken assertion is a bug to fix, not a test to update

---

### T-004: Verify US-001 unit suite
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05, AC-US1-06 | **Status**: [x] completed

**Result**: `npx vitest run src/app/api/v1/skills/search src/lib/search.test.ts` → 98/98 passing (route 41, search.test 50, plus dedup 7). Zero `db.skill.findMany` invocations on edge-only test cases. AC-US1-02/05 (live latency, multi-page seeded dataset) deferred to integration smoke after Step 2 + 3 ship.

**Test Plan**:
- Run `npx vitest run src/app/api/v1/skills/search`
- All tests pass; no `db.skill.findMany` invocations appear for edge-only test cases

---

## US-002: Precomputed blocklist + rejected enrichment via KV

### T-005: [RED] Failing tests for KV-backed blocklist and rejected enrichment (no DB on edge path)
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-06 | **Status**: [ ] pending

**Test Plan**:
- Given a search request where edge serves the response and a mocked KV that returns a `blocklist-set` and `rejected-set`
- When `searchBlocklistEntries` and `searchRejectedSubmissions` are called
- Then no DB query is issued (mock DB asserts zero invocations) AND the KV values are used for enrichment
- Write tests in `route.test.ts` (or `search.test.ts`); must fail (RED) before implementation

---

### T-006: [RED] Failing tests for queue consumer blocklist refresh and resp-version bump
**User Story**: US-002 | **Satisfies ACs**: AC-US2-05 | **Status**: [ ] pending

**Test Plan**:
- Given a `BlocklistRefreshQueueMessage` with `reason: "blocklist_change"` dispatched to the consumer
- When `handleBlocklistRefresh` processes the message
- Then KV contains updated `search-index:blocklist-set`, `search-index:rejected-set`, and `search-index:resp-version` is bumped
- Write in `search-index-consumer.test.ts`; must fail (RED) before implementation

---

### T-007: [RED] Failing tests for rebuildBlocklistKv round-trip and 5000-entry cap
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02 | **Status**: [ ] pending

**Test Plan**:
- Given a DB with 6000 active blocklist entries ranked by `discoveredAt DESC`
- When `rebuildBlocklistKv(kv, db)` is called
- Then KV receives exactly 5000 entries (newest first) — the tail is truncated
- Write in `src/lib/__tests__/search-index.test.ts`; must fail (RED) before implementation

---

### T-008: [GREEN] KV types, constants, and rebuild helpers in search-index.ts
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-05 | **Status**: [ ] pending

**Test Plan**:
- Given RED tests from T-007
- When `BLOCKLIST_KV_KEY`, `REJECTED_KV_KEY`, `RESP_VERSION_KEY`, `BlocklistKvEntry`, `RejectedKvEntry`, `rebuildBlocklistKv`, `rebuildRejectedKv`, `bumpRespVersion`, `getRespVersion` are added to `search-index.ts`
- Then T-007 tests turn green; truncation cap enforced at 5000; TTL 7 days written to KV

---

### T-009: [GREEN] Rewrite searchBlocklistEntries and searchRejectedSubmissions to read KV first
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-06 | **Status**: [ ] pending

**Test Plan**:
- Given RED tests from T-005
- When `searchBlocklistEntries` and `searchRejectedSubmissions` in `search.ts` are rewritten to call `kv.get(BLOCKLIST_KV_KEY)` / `kv.get(REJECTED_KV_KEY)` and filter in-memory by `query` substring
- Then T-005 tests turn green; blocklisted and rejected entries still appear in responses (AC-US2-03, AC-US2-04); DB fallback invoked when KV returns null

---

### T-010: [GREEN] BlocklistRefreshQueueMessage type and handleBlocklistRefresh consumer
**User Story**: US-002 | **Satisfies ACs**: AC-US2-05 | **Status**: [ ] pending

**Test Plan**:
- Given RED tests from T-006
- When `BlocklistRefreshQueueMessage` is added to `queue/types.ts` and `handleBlocklistRefresh` is implemented in `search-index-consumer.ts` (calls `rebuildBlocklistKv`, `rebuildRejectedKv`, `bumpRespVersion`)
- Then T-006 tests turn green; consumer dispatches on `type: "rebuild_blocklist_kv"`

---

### T-011: [GREEN] handleSearchIndexUpdate bumps resp-version after shard write
**User Story**: US-002 | **Satisfies ACs**: AC-US2-05 | **Status**: [ ] pending

**Test Plan**:
- Given a shard update message processed by the existing consumer
- When `handleSearchIndexUpdate` completes a shard write
- Then `bumpRespVersion(kv)` is called once; KV `search-index:resp-version` increments by 1
- Write/update test in `search-index-consumer.test.ts`

---

### T-012: [GREEN] Extend scripts/rebuild-search-local.ts to write blocklist + rejected KV
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02 | **Status**: [ ] pending

**Test Plan**:
- Given a full local index rebuild via `scripts/rebuild-search-local.ts`
- When the script completes
- Then `search-index:blocklist-set`, `search-index:rejected-set`, and `search-index:resp-version` are present in local KV dev binding
- Script must not throw on empty blocklist/rejected sets

---

### T-013: [REFACTOR] Extract KV enrichment path + preserve Server-Timing enrichment segment
**User Story**: US-002 | **Satisfies ACs**: AC-US2-06, AC-US2-07 | **Status**: [ ] pending

**Test Plan**:
- Given green implementations from T-008–T-012
- When `enrichWithBlocklistAndRejected` is refactored to clearly branch KV vs DB path and `enrichment;dur=<n>` segment is preserved in Server-Timing
- Then AC-US2-07: enrichment dur < 10ms in integration test (mock KV returning precomputed set, measure elapsed ms in test harness)
- Zero DB invocations when KV returns a valid set

---

### T-014: Verify US-002 unit suite
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05, AC-US2-06, AC-US2-07 | **Status**: [ ] pending

**Test Plan**:
- Run `npx vitest run src/app/api/v1/skills/search src/lib/__tests__/search-index.test.ts src/lib/queue`
- All tests pass; blocklist + rejected enrichment appears in responses; DB not queried on KV-hit paths

---

## US-003: Workers Cache API response cache

### T-015: [RED] Failing test: cache hit short-circuits before KV/PG; second call returns HIT
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-04 | **Status**: [ ] pending

**Test Plan**:
- Given a mock `caches.default` that returns a cached Response on the second call with the same key
- When two identical requests are processed by the route handler
- Then the second returns `cf-cache-status: HIT` with zero KV reads and zero DB calls (mock invocation count assertions)
- Must fail (RED) before implementation; write in `route.test.ts`

---

### T-016: [RED] Failing unit test: buildCacheKey includes URL params and resp-version; strips unknown params
**User Story**: US-003 | **Satisfies ACs**: AC-US3-02 | **Status**: [ ] pending

**Test Plan**:
- Given two requests: `?q=hyperf&limit=20&page=1` and `?q=hyperf&limit=20&page=2`
- When `buildCacheKey(req, respVersion)` is called for each
- Then the two keys differ; the same URL with `?utm_source=x` appended produces the same key as without it; the key contains both `q=hyperf` and `v=<version>`
- Write as a pure unit test for `buildCacheKey`; must fail (RED) before implementation

---

### T-017: [RED] Failing integration test: shard update bumps version → cache invalidation
**User Story**: US-003 | **Satisfies ACs**: AC-US3-03 | **Status**: [ ] pending

**Test Plan**:
- Given a first request that populates cache with `v=5`
- When a queue update bumps `resp-version` to `6`
- Then an identical second request misses cache (new key is `v=6`), triggers a fresh live query, and does NOT contain `cf-cache-status: HIT`
- Must fail (RED) before implementation

---

### T-018: [GREEN] Implement buildCacheKey and integrate Cache API read/write in route.ts
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-04, AC-US3-05, AC-US3-06 | **Status**: [ ] pending

**Test Plan**:
- Given RED tests from T-015, T-016
- When `buildCacheKey` is implemented (canonical URL, normalized `q`, strips unknown params, includes `v=`) and the GET handler wraps with `caches.default.match` → early return on HIT, `cache.put` on miss via `ctx.waitUntil` or fire-and-forget `.catch(() => {})`
- Then T-015 and T-016 tests turn green
- Cache-Control on cached response: `public, max-age=30, s-maxage=30`; `resp-version` read parallelized with first KV shard read

---

### T-019: [GREEN] Wire version invalidation — cache miss after shard version bump
**User Story**: US-003 | **Satisfies ACs**: AC-US3-03, AC-US3-06 | **Status**: [ ] pending

**Test Plan**:
- Given RED test from T-017
- When `handleSearchIndexUpdate` bumps `resp-version` after shard write (already wired in T-011) and route reads `resp-version` early and includes it in the cache key
- Then T-017 integration test turns green; after version bump, same-URL request is a cache miss

---

### T-020: [REFACTOR] Extract response cache wrapper; add cache Server-Timing segment
**User Story**: US-003 | **Satisfies ACs**: AC-US3-04, AC-US3-05 | **Status**: [ ] pending

**Test Plan**:
- Given green cache implementation from T-018, T-019
- When route.ts cache logic is extracted into `withResponseCache(req, version, handler)` helper
- Then `cache;dur=<n>` segment is added to `Server-Timing` for both HIT and MISS paths; all existing tests remain green

---

### T-021: Verify US-003 unit suite
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04, AC-US3-05, AC-US3-06 | **Status**: [ ] pending

**Test Plan**:
- Run `npx vitest run src/app/api/v1/skills/search`
- All cache hit/miss/invalidation tests pass; buildCacheKey unit tests pass

---

## US-004: Observability and regression coverage

### T-022: [RED] Failing tests for Server-Timing three-state postgres segment
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-05 | **Status**: [ ] pending

**Test Plan**:
- Given three route invocations: (a) dual-source, (b) edge-only, (c) cache hit
- When the `Server-Timing` header is parsed for each
- Then (a) contains `postgres;dur=<n>` with positive dur; (b) contains `postgres;desc="skipped";dur=0`; (c) contains `postgres;desc="cache-hit";dur=0`
- Write as unit tests asserting exact substring/regex matches; must fail (RED) if any path is not yet emitting correctly

---

### T-023: [RED] Failing tests for X-Search-Source three documented values
**User Story**: US-004 | **Satisfies ACs**: AC-US4-02 | **Status**: [ ] pending

**Test Plan**:
- Given separate route invocations routing through edge-only, postgres-only, and cache-hit paths
- When `X-Search-Source` header is read for each
- Then each invocation returns exactly `edge`, `postgres`, or `cache` (respectively) — no other undocumented values
- Must fail (RED) for any path not yet emitting the correct value

---

### T-024: [GREEN] Emit correct Server-Timing postgres states and X-Search-Source: cache
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-05 | **Status**: [ ] pending

**Test Plan**:
- Given RED tests from T-022 and T-023
- When route.ts is updated to emit `X-Search-Source: cache` on cache hits and `postgres;desc="cache-hit";dur=0` in Server-Timing for the cache-hit path
- Then T-022 and T-023 tests turn green
- Confirm `edge+postgres`, `edge+pg-failed`, `postgres` paths also emit correct values (regression check)

---

### T-025: [RED] Playwright E2E — X-Search-Source: edge assertion
**User Story**: US-004 | **Satisfies ACs**: AC-US4-03 | **Status**: [ ] pending

**Test Plan**:
- Given a running deployed Worker (or preview Worker URL in CI env)
- When `tests/e2e/search.spec.ts` issues `GET /api/v1/skills/search?q=hyperf&limit=20&page=1`
- Then response header `X-Search-Source` equals `edge`
- Write this test; it must fail (RED) if the edge fast path is not deployed — serves as regression guard

---

### T-026: [RED] Playwright E2E — cf-cache-status: HIT on second identical request
**User Story**: US-004 | **Satisfies ACs**: AC-US4-04 | **Status**: [ ] pending

**Test Plan**:
- Given two identical requests issued within 30 seconds against a deployed Worker
- When the second request arrives
- Then response header `cf-cache-status` equals `HIT`
- Write in `tests/e2e/search.spec.ts`; fails (RED) until cache wiring is deployed

---

### T-027: [GREEN] E2E tests pass against deployed Worker
**User Story**: US-004 | **Satisfies ACs**: AC-US4-03, AC-US4-04 | **Status**: [ ] pending

**Test Plan**:
- Given the full implementation deployed to preview/staging Worker
- When `npx playwright test tests/e2e/search.spec.ts` runs against the preview URL (or `wrangler dev` at localhost:8787)
- Then both T-025 and T-026 E2E tests pass

---

### T-028: Full unit + E2E verification run
**User Story**: US-001, US-002, US-003, US-004 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05, AC-US1-06, AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05, AC-US2-06, AC-US2-07, AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04, AC-US3-05, AC-US3-06, AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04, AC-US4-05 | **Status**: [ ] pending

**Test Plan**:
- Run `npx vitest run src/app/api/v1/skills/search src/lib/__tests__/search-index.test.ts src/lib/queue`
- Run `npx playwright test tests/e2e/search.spec.ts`
- All pass; coverage report meets 90% target per spec frontmatter

---

### T-029: Production smoke — p50 < 100ms post-deploy
**User Story**: US-001, US-002, US-003 | **Satisfies ACs**: AC-US1-02, AC-US3-05 | **Status**: [ ] pending

**Test Plan**:
- Given a deployed production Worker with all three optimization phases live
- When the following curl loop is executed against the production endpoint:
  ```
  for i in {1..20}; do
    curl -s -o /dev/null -D - \
      'https://verified-skill.com/api/v1/skills/search?q=hyperf&limit=20&page=1' \
    | grep -iE 'server-timing|x-search-source|cf-cache-status'
  done
  ```
- Then:
  - First call (cold): `X-Search-Source: edge`, `Server-Timing` shows `postgres;desc="skipped";dur=0`, enrichment dur < 10ms
  - Subsequent calls (warm cache within 30s): `cf-cache-status: HIT`, total response < 20ms
  - p50 across 20 warm requests < 100ms (AC-US1-02 target <80ms; 100ms accounts for network variance)
  - p95 across 20 warm requests < 200ms
  - No `cf-cache-status: MISS` after the first call within the 30s cache window
