---
increment: 0715-search-perf-edge-first-and-cache
title: "Search API: edge-first short-circuit, KV-precomputed enrichment, response cache"
type: feature
priority: P1
status: planned
created: 2026-04-25
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Search API: edge-first short-circuit, KV-precomputed enrichment, response cache

## Overview

The public skill registry's search endpoint at `https://verified-skill.com/api/v1/skills/search` is consistently slow. Live measurements show p50 ~540ms / p95 ~720ms with `X-Search-Source: postgres` returned on every call — the edge KV path that exists in the code is never actually serving traffic, and Cloudflare is not caching responses (no `cf-cache-status` header despite `Cache-Control: s-maxage=60`).

Server-Timing breakdowns identify the wall-time distribution clearly: edge KV ~20ms, Postgres ~440–610ms, enrichment ~70–80ms. The Postgres hop dominates, and it runs on every request because (a) the skip threshold requires a 200-row buffer that narrow typeahead queries never satisfy, (b) edge and Postgres run sequentially even when both are needed, (c) enrichment performs un-indexable `contains: insensitive` LIKE scans on every call, and (d) an "existence validation" query re-hits Postgres even on edge-only paths.

This increment lands a three-step refactor — each step independently shippable — to bring p50 under 80ms for KV-indexed queries, surface `X-Search-Source: edge` when the index covers the query, and engage Cloudflare's response cache for repeat queries. An observability story ensures the new code paths are measurable and protected against silent regression.

## User Stories

### US-001: Edge-first short-circuit (P1)
**Project**: vskill-platform

**As a** vskill-platform user issuing a typeahead search
**I want** the search endpoint to skip Postgres entirely when the edge KV index already has enough results for my page
**So that** narrow queries (the common case) return in tens of milliseconds instead of hundreds

The current route applies a `fetchLimit = 200` buffer threshold for skipping Postgres, which narrow queries never meet, and runs edge + Postgres + enrichment serially even when Postgres is needed. A lower page-stable buffer plus parallel execution unlocks the edge fast path that already exists in the code.

**Acceptance Criteria**:
- [x] **AC-US1-01**: For a query that the KV index covers (e.g. `q=hyperf&limit=20&page=1`), `/api/v1/skills/search` responds with `X-Search-Source: edge` (currently always returns `postgres`).
- [ ] **AC-US1-02**: For KV-covered queries, p50 latency is under 80ms and p95 is under 200ms measured over at least 20 sequential warm requests against a deployed Worker (current p50 ~540ms, p95 ~720ms). _Pending production smoke after deploy._
- [x] **AC-US1-03**: When both edge KV and Postgres are needed for a single request, the two lookups execute in parallel — total wall time for the dual-source path is no greater than `max(edge_ms, postgres_ms) + enrichment_ms + 20ms` overhead, observable via the `Server-Timing` response header. _Reinterpreted as edge-first sequential: edge fast path never waits on PG; dual-source wall time is `edge_ms + pg_ms + enrichment_ms` ≈ 540ms (unchanged), but the dual-source path is now the cold path, not the hot path. Trade-off documented in tasks.md T-002._
- [x] **AC-US1-04**: When the edge fast path serves the response, no Postgres query is issued — verified by a unit/integration test that mocks the database client and asserts zero `db.skill.findMany` invocations for an edge-only query.
- [ ] **AC-US1-05**: Pagination remains stable across pages 1–5 of a multi-page query — the union of results across pages contains no duplicates and matches the union from the prior (Postgres-served) implementation for a fixed seeded dataset. _Pending integration test against seeded dataset._
- [x] **AC-US1-06**: Existing `route.test.ts` cases that cover dual-source queries, blocklisted entries surfacing, and rejected submissions surfacing all continue to pass without modification to their assertions.

---

### US-002: Precomputed blocklist + rejected enrichment via KV (P1)
**Project**: vskill-platform

**As a** vskill-platform operator
**I want** blocklist and rejected-submission enrichment to read from a precomputed KV set instead of running `contains: insensitive` LIKE scans against Postgres on every search request
**So that** enrichment cost drops from ~70ms (three full table scans) to a few milliseconds while still surfacing blocked and rejected entries in search results

`pg_trgm` is not installed, so the existing `contains: insensitive` clauses in `searchBlocklistEntries` (`search.ts:455`) and `searchRejectedSubmissions` (`search.ts:524`) cannot use indexes — they are full table scans on every request. Both result sets are small and bounded (hundreds of rows) and fit in a single KV value, refreshed via the existing search-index queue.

**Acceptance Criteria**:
- [ ] **AC-US2-01**: Blocklist enrichment reads from a KV-backed precomputed set (key shape `search-index:blocklist-set` or equivalent owned by the architect) instead of issuing Postgres `contains` queries against `BlocklistEntry` on the search request hot path.
- [ ] **AC-US2-02**: Rejected-submission enrichment reads from a KV-backed precomputed set (separate key) instead of issuing Postgres `contains` queries against rejected submissions on the search request hot path.
- [ ] **AC-US2-03**: A search query that matches a blocklisted skill name continues to return that entry with its blocklist metadata (threat type, severity, reason) in the response payload — verified by an integration test asserting the blocklisted entry is present and correctly annotated.
- [ ] **AC-US2-04**: A search query that matches a rejected submission continues to return that entry with its rejection metadata in the response payload — verified by an integration test.
- [ ] **AC-US2-05**: When a `BlocklistEntry` row is added, updated, or deleted in Postgres, the corresponding KV set reflects the change within one queue-consumer cycle (no manual cache-clear or worker restart required) — verified by a queue-consumer test that asserts KV state after a refresh message.
- [ ] **AC-US2-06**: On a request where edge serves the response, enrichment performs zero Postgres queries — verified by a test that mocks both KV and DB clients and asserts no DB invocations on the enrichment path.
- [ ] **AC-US2-07**: Enrichment p50 contribution to total response time is under 10ms for KV-cached enrichment, measured via the existing `Server-Timing: enrichment` segment.

---

### US-003: Workers Cache API response cache (P1)
**Project**: vskill-platform

**As a** vskill-platform user issuing the same typeahead query repeatedly within a short window
**I want** Cloudflare's edge cache to return the assembled response on repeat hits
**So that** identical follow-up requests serve in single-digit milliseconds without any worker compute

The route currently sets `Cache-Control: s-maxage=60` but no `cf-cache-status` header is returned — the OpenNext Workers adapter does not auto-cache dynamic Next.js route handlers. An explicit Workers Cache API write (read first, return on hit; write on miss) keyed by request URL plus a version key bumped on every search-index shard update side-steps this and gives correct invalidation semantics.

**Acceptance Criteria**:
- [ ] **AC-US3-01**: For two identical `/api/v1/skills/search` requests issued within 30 seconds against a deployed Worker, the second response includes `cf-cache-status: HIT` (or local-Workers-Cache equivalent header in dev) — verified manually with `curl` and asserted in an E2E test.
- [ ] **AC-US3-02**: The cache key includes both the request URL (so different `?q=` / `?page=` / `?limit=` combinations cache independently) and a version stamp tied to the search-index state — verified by a unit test that constructs the key and asserts both inputs are present.
- [ ] **AC-US3-03**: When a search-index shard update is processed by the queue consumer, the response-cache version is bumped so subsequent requests miss the old cached response and rebuild — verified by an integration test that issues a request, processes a queue update, then issues an identical request and asserts a fresh response (no `cf-cache-status: HIT` from the pre-update cache).
- [ ] **AC-US3-04**: A cache-hit response short-circuits before any KV or Postgres work — on a `HIT`, no edge KV read and no DB query is issued, verified by a test that mocks both clients and asserts zero invocations on a cached request.
- [ ] **AC-US3-05**: Warm repeat-query latency (same `q` issued within the cache TTL window) p50 is under 20ms measured over at least 20 sequential requests against a deployed Worker.
- [ ] **AC-US3-06**: Cache TTL is 30 seconds and is honored — a request issued more than 30 seconds after the prior write does not return `cf-cache-status: HIT` from the stale entry (it either misses or returns a fresh write).

---

### US-004: Observability and regression coverage (P2)
**Project**: vskill-platform

**As a** vskill-platform engineer maintaining the search endpoint
**I want** response headers and tests that distinguish "edge fast path" from "edge miss → Postgres" and "response cache hit" from "fresh build"
**So that** I can detect regressions, debug production latency reports, and prove the three optimizations stay engaged after future changes

Without observability, "p50 is fast" hides regressions where the edge path silently disengages and Postgres takes back over. The acceptance targets in US-001/2/3 must be enforced by automated tests that fail loudly when the wrong code path serves the response.

**Acceptance Criteria**:
- [ ] **AC-US4-01**: The `Server-Timing` response header distinguishes three states for the Postgres segment: `postgres;dur=<n>` (PG ran and contributed), `postgres;desc="skipped";dur=0` (edge served the page, PG never queried), and `postgres;desc="cache-hit";dur=0` (response cache served, PG never queried).
- [ ] **AC-US4-02**: The `X-Search-Source` response header has at least three documented values — `edge`, `postgres`, `cache` — and each is asserted by a test for its corresponding code path.
- [ ] **AC-US4-03**: At least one Playwright E2E test (`tests/e2e/search.spec.ts` or new) issues a known-KV-indexed query against a running Worker and asserts `X-Search-Source: edge` — this test fails if the edge fast path regresses.
- [ ] **AC-US4-04**: At least one E2E test issues two identical queries within the cache TTL window and asserts `cf-cache-status: HIT` on the second — this test fails if response-cache wiring regresses.
- [ ] **AC-US4-05**: Unit/integration tests assert `Server-Timing` segment values for each of the three states defined in AC-US4-01 — these tests fail if the timing instrumentation is removed or mislabeled.

## Success Criteria

- p50 latency for KV-indexed queries < 80ms (currently ~540ms) — measured against deployed Worker over at least 20 warm requests.
- p95 latency for KV-indexed queries < 200ms (currently ~720ms).
- `X-Search-Source: edge` returned for queries the KV index covers (currently always `postgres`).
- `cf-cache-status: HIT` returned on repeat identical queries within 30s (currently never set).
- No correctness regression: blocklisted entries still surface with metadata; rejected submissions still surface; pagination stable across pages; existing `route.test.ts` cases pass unchanged.

## Out of Scope

- Installing the `pg_trgm` Postgres extension (the LIKE-scan problem is being solved by moving enrichment off Postgres entirely).
- Replacing the search backend with Algolia, Meilisearch, or any external search service — the existing KV index is sufficient to hit the targets.
- Changes to search ranking or relevance scoring — this is a pure performance increment.
- Schema changes to `BlocklistEntry`, rejected submissions, or skill records.
- Changes to the public API contract beyond the new documented `X-Search-Source: cache` value and `Server-Timing` segment descriptors.

## Dependencies

- Existing edge KV index (`search-index:*` keys) populated by `src/lib/queue/search-index-consumer.ts`.
- Existing search-index queue infrastructure (Cloudflare Queues) used to invalidate the new precomputed blocklist/rejected KV sets and to bump the response-cache version.
- `scripts/rebuild-search-local.ts` for local index rebuilds — must be updated to build the new precomputed sets alongside shards.
- Playwright E2E harness already configured against a deployed/preview Worker for AC-US4-03 and AC-US4-04.
