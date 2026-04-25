---
increment: 0716-studio-search-api-and-telemetry
title: "Studio search API extension + same-origin proxy + telemetry endpoints"
type: feature
priority: P1
status: planned
created: 2026-04-25
structure: user-stories
test_mode: TDD
coverage_target: 90
parallel: true
siblings:
  - 0717-studio-find-ui
  - 0718-studio-submit-deeplink
brainstorm: .specweave/docs/brainstorms/2026-04-24-local-studio-discovery-submission.md
---

# Feature: Studio search API extension + same-origin proxy + telemetry endpoints

## Overview

Local Studio is gaining a discovery UI ([0717](../0717-studio-find-ui/)) and a submit deep-link CTA ([0718](../0718-studio-submit-deeplink/)). Today Studio is local-only — it never calls `verified-skill.com`. This increment owns the **server contract** that 0717 and 0718 consume:

1. **Search API extension** — additive `publisher` field + `offset/total` pagination on `/api/v1/skills/search` so result cards can render publisher chips and a LoadMore control.
2. **Same-origin Studio search proxy** at `/api/v1/studio/search` with a 60s LRU cache, per-IP rate-limit, and abort-aware forwarding. The browser never calls `verified-skill.com` directly — eliminates CORS, gives us a cache + rate-limit shield for free, and rides on top of [0715](../0715-search-perf-edge-first-and-cache/)'s edge-first cache work.
3. **Telemetry endpoints** — `submit-click` and `install-copy` so we can later measure conversion of the discover→install and discover→submit loops without third-party tools.

This is the critical-path contract increment. 0717 and 0718 develop against mocked contracts in parallel and integrate once these endpoints land.

## Out of scope

- OAuth or auth in Studio (deferred indefinitely — submit deep-links to `verified-skill.com/submit`).
- Category / tier / sort filters on search (defer until users ask).
- Server-side install action (Studio uses clipboard-copy; daemon deferred to V2).
- Porting `/publishers`, `/trust`, `/audits`, `/insights`, `/admin` pages (Studio deep-links instead).
- 90-day telemetry retention sweep (separate follow-up).

## User Stories

### US-001: `publisher` field + `offset/total` pagination on `/api/v1/skills/search` (P1)
**Project**: vskill-platform

**As a** Studio result card
**I want** the search response to include the publisher and a result-set total
**So that** I can render a publisher chip with verified status and a pagination control that knows when to stop.

The current `/api/v1/skills/search` response already returns `name, author, repoUrl, trustTier, certTier, githubStars, vskillInstalls, isBlocked, threatType, severity, alternateRepos, currentVersion`. Two additive fields close the gap for Studio: `publisher` (joined from `Submission.publisherId → Publisher`) and `total` (so LoadMore can disable correctly).

**Acceptance Criteria**:
- [x] **AC-US1-01**: Response payload includes a `publisher` field shaped `{ slug: string, name: string, verified: boolean } | null` per result. Null when no publisher row joined (e.g. legacy submissions).
- [x] **AC-US1-02**: Endpoint accepts `offset` query param (0-based, integer, default 0). When omitted, current behavior is preserved (offset=0).
- [x] **AC-US1-03**: Response envelope includes `total: number` — the total count of results matching the query before pagination. LoadMore in Studio uses this to disable when `offset + limit >= total`.
- [x] **AC-US1-04**: Backward compatibility — clients that ignore `publisher` and `total` continue to work; `vskill find` (CLI) still parses results correctly with no code change. Verified by running existing `vskill find` integration tests against the new response.
- [x] **AC-US1-05**: Performance — adding the publisher join contributes <10ms p95 to search latency, measured via the existing `Server-Timing: enrichment` segment from [0715](../0715-search-perf-edge-first-and-cache/). When the join would cause regression, results return with `publisher: null` and a warning is logged (graceful degradation, never block search).
- [x] **AC-US1-06**: Null-safety — when `Submission.publisherId` is null or the publisher row was deleted, `publisher` is `null` in the response (no 500, no crash).
- [x] **AC-US1-07**: `limit` continues to clamp at 30 (existing constraint). Requests with `limit > 30` are clamped server-side and an `X-Limit-Clamped: 30` response header is set.

---

### US-002: Same-origin `/api/v1/studio/search` proxy (P1)
**Project**: vskill-platform

**As a** Local Studio browser client
**I want** to call a same-origin search endpoint instead of `verified-skill.com` directly
**So that** I avoid CORS, get a shared cache layer, and keep the upstream rate-limit insulated.

The Studio backend is the same Next.js app that hosts the public registry. A thin proxy at `/api/v1/studio/search` wraps the search client with an in-memory LRU and a per-IP token bucket. This is the only network endpoint the Studio Find UI ([0717](../0717-studio-find-ui/)) calls.

**Acceptance Criteria**:
- [x] **AC-US2-01**: New endpoint `GET /api/v1/studio/search?q=&limit=&offset=` exists, returns the same envelope as `/api/v1/skills/search` (with US-001 extensions).
- [x] **AC-US2-02**: In-memory LRU cache keyed by `${q}|${limit}|${offset}` with TTL 60s and max 100 entries. On hit, the upstream call is skipped — verified by mocking the upstream client and asserting zero invocations on the second identical request.
- [x] **AC-US2-03**: Per-IP token-bucket rate-limit, 60 requests / 60 seconds. Bursts return HTTP 429 with `Retry-After` header. Cache hits do **not** count against the limit (only upstream-bound requests do).
- [x] **AC-US2-04**: Abort-aware — when the client disconnects mid-request, the upstream fetch is aborted via `AbortController`. Verified by a unit test that aborts the request and asserts the upstream fetch's signal received an abort event.
- [x] **AC-US2-05**: Upstream errors are sanitized — 5xx from upstream returns a generic 502 envelope `{ error: "search_unavailable" }` to the Studio client; the raw error is logged server-side only. No upstream URL or DB-level details leak.
- [x] **AC-US2-06**: `limit` clamps at 30 (mirrors US-001 AC-07). `offset` clamps at 5000 (defensive — beyond this is almost certainly a scraper).
- [x] **AC-US2-07**: As-you-type performance budget — for cache-hit queries, the proxy responds with p50 <5ms and p95 <15ms measured locally. For cache-miss (cold) queries, p95 ≤ upstream p95 + 10ms overhead.
- [x] **AC-US2-08**: Studio client's `If-None-Match` header (etag of last response hash) returns 304 when the cached response matches — saves bandwidth on repeat queries.

---

### US-003: Studio telemetry endpoints (`submit-click` + `install-copy`) (P2)
**Project**: vskill-platform

**As a** product owner
**I want** to log when users click "Submit your skill" or copy an install command
**So that** we can later measure conversion of the discover→submit and discover→install loops without integrating a third-party analytics SDK.

Telemetry is fire-and-forget — Studio never blocks UI on the telemetry response. Storage is a dedicated `StudioTelemetry` Prisma model so we can query later without depending on a 3rd party.

**Acceptance Criteria**:
- [x] **AC-US3-01**: New endpoint `POST /api/v1/studio/telemetry/submit-click` accepts JSON `{ repoUrl?: string, q?: string, ts: number }`. Returns 204 on success.
- [x] **AC-US3-02**: New endpoint `POST /api/v1/studio/telemetry/install-copy` accepts JSON `{ skillName: string, q?: string, ts: number }`. Returns 204 on success.
- [x] **AC-US3-03**: Schema-validated server-side (Zod). Invalid payloads return 400 with `{ error: "invalid_payload", issues: [...] }`. Verified by unit tests for each invalid shape.
- [x] **AC-US3-04**: Append-only `StudioTelemetry` Prisma model `{ id String @id @default(cuid()), kind String, payload Json, createdAt DateTime @default(now()) }` + Prisma migration. No PII fields (no IP, no UA, no user id) are stored.
- [x] **AC-US3-05**: Per-IP rate-limit 10 req/min. Excess returns 429. Telemetry rate-limit is independent from search rate-limit.
- [x] **AC-US3-06**: Failure mode — if the DB write fails, the endpoint logs and still returns 204 (telemetry must never break the UX). Verified by injecting a DB failure and asserting 204 response.
- [x] **AC-US3-07**: GDPR-defensive — payload is opaque JSON; we explicitly do **not** read request `req.headers['x-forwarded-for']` or `user-agent` into the row. Code-review check enforces this.

## Functional Requirements

### FR-001: Contract document
Publish `.specweave/docs/contracts/studio-search-api-v1.md` summarizing the search response envelope (with new `publisher` + `total` + `offset` fields), the studio proxy contract (cache headers, ETag, error envelope), and the telemetry endpoint payload schemas. Sibling increments 0717 and 0718 mock against this contract.

### FR-002: Server-Timing instrumentation
Extend the existing `Server-Timing` header from [0715](../0715-search-perf-edge-first-and-cache/) with a `enrichment;desc=publisher;dur=<ms>` segment so the publisher join cost is observable in production.

### FR-003: Backward-compat regression suite
Run existing `vskill find` integration tests (in `vskill/`) against the new search response to assert publisher/total/offset additions don't break parsing. This is a CI gate, not a one-time check.

## Performance budgets

| Path | p50 | p95 |
|---|---|---|
| `/api/v1/studio/search` cache hit | <5ms | <15ms |
| `/api/v1/studio/search` cache miss | upstream p50 + 10ms | upstream p95 + 10ms |
| Telemetry POST | <20ms | <50ms |
| Publisher join overhead on `/api/v1/skills/search` | <5ms | <10ms |

## Risk register

| Risk | Mitigation |
|---|---|
| Publisher join slows search | Graceful degrade to `publisher: null` + log; AC-US1-05 |
| LRU memory pressure under load | Cap 100 entries × ~5KB = 500KB max per Worker isolate |
| Token bucket bypass via X-Forwarded-For spoofing | Use Cloudflare's `cf-connecting-ip` (CF-trusted), fallback to socket addr |
| Telemetry table grows unbounded | Follow-up increment will add 90-day retention sweep |
| Backward break for `vskill find` | AC-US1-04 explicit regression test against existing CLI integration tests |
| Cross-isolate cache divergence | Acceptable — per-isolate hit rate is what matters for as-you-type |

## Success Criteria

- All ACs pass with TDD red→green→refactor evidence in tasks.md.
- Integration: 0717 and 0718 can hit `/api/v1/studio/search` and the telemetry endpoints unmocked at the end of their respective implementations.
- No regression in existing `/api/v1/skills/search` callers (CLI `vskill find`, public registry web UI).
- Performance budgets met in deployed Worker (smoke test post-deploy, ≥20 sequential requests for each budget).

## Dependencies

- [0715-search-perf-edge-first-and-cache](../0715-search-perf-edge-first-and-cache/) — Studio proxy rides on top of edge-first cache; performance assumptions assume 0715 has shipped Step 1.
- Existing `Submission` + `Publisher` Prisma tables (no schema change for these).
- Existing Cloudflare KV namespace for any future caching extensions (out of scope here).
