---
increment: 0753-studio-search-direct-call
title: 'Hotfix: studio/search 502 — replace CF Worker self-fetch with direct call'
type: hotfix
priority: P1
status: abandoned
created: 2026-04-26T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Hotfix: studio/search 502 — replace CF Worker self-fetch with direct call

## Overview

The Skill Studio find-palette at `verified-skill.com/studio` returns `502 search_unavailable` for every typed query. Verified directly:

```bash
curl 'https://verified-skill.com/api/v1/studio/search?q=greet&limit=20&offset=0'
# → HTTP 502 {"error":"search_unavailable"}

curl 'https://verified-skill.com/api/v1/skills/search?q=greet&limit=20&offset=0'
# → HTTP 200 with real results
```

The underlying `/api/v1/skills/search` route is healthy. The wrapper at `vskill-platform/src/app/api/v1/studio/search/route.ts:149-153` builds a same-origin URL via `originFromRequest(req)` and calls `fetch(...)` — a worker-to-self subrequest inside a Cloudflare Worker. CF throttles those under load; the 5-second `UPSTREAM_TIMEOUT_MS` (line 28) fires, the catch on lines 169-173 flags `upstreamTimedOut`, and the route returns the sanitized `502 search_unavailable` from line 172.

**Fix**: extract the data-search core of `skills/search/route.ts` into `src/lib/studio/run-skills-search.ts` and have BOTH routes call it directly. No HTTP roundtrip, no subrequest, no 5-second timeout. Same Worker, same V8 isolate.

The local `vskill studio` CLI already ships graceful 502 degradation (filtered trending, soft banner — shipped in increment 0741 redesign), so users aren't blocked — but they only see ~10 trending skills instead of the full 112,552-skill catalogue. This hotfix restores the full catalogue.

## Out of Scope

- Generalizing the `originFromRequest` self-fetch pattern to other studio/* routes (`telemetry` and `workspace-info` don't use it — verified)
- Changing the public response envelope (would break the vskill CLI BWC test `route-bwc-vskill-find.test.ts`)
- Client-side palette work (graceful degradation already shipped in 0741)
- Rate-limit / cache / ETag / sanitization contract changes (`/contracts/studio-search-api-v1.md` invariants preserved exactly)

## User Stories

### US-001: Studio search returns real results from production (P1)
**Project**: vskill-platform

**As a** Skill Studio user typing a query in the find-palette
**I want** the search endpoint to return real results from the 112k-skill catalogue
**So that** I can discover and install skills that match my needs (instead of seeing only ~10 client-filtered trending matches)

**Acceptance Criteria**:
- [ ] **AC-US1-01**: `runSkillsSearch({ q, limit, offset, category? })` is exported from `src/lib/studio/run-skills-search.ts`. The function contains the edge+Postgres merge, blocklist enrichment, dedup, publisher join (with 50ms soft-timeout), and pagination slice currently embedded in `skills/search/route.ts:206-304`. It does NOT take `req` — pure data ops only.
- [ ] **AC-US1-02**: `src/app/api/v1/studio/search/route.ts` no longer calls `fetch(...)` on `originFromRequest(req)`. The route imports `runSkillsSearch` and invokes it directly. `originFromRequest`, `UPSTREAM_TIMEOUT_MS`, `upstreamCtrl`, and the `req.signal` self-abort wiring are deleted.
- [ ] **AC-US1-03**: All existing studio/search tests in `src/app/api/v1/studio/search/__tests__/route.test.ts` and `route-perf.test.ts` continue to pass after migrating from `vi.stubGlobal("fetch", ...)` to `vi.mock("@/lib/studio/run-skills-search", ...)`. Every `it()` block survives the migration; only mock setup changes.
- [ ] **AC-US1-04**: A new test asserts that studio/search returns `200 { results, total, pagination: { hasMore } }` when `runSkillsSearch` resolves with a populated envelope. The response carries the same `Cache-Control`, `ETag`, `X-Cache`, and `Server-Timing` headers as before.
- [ ] **AC-US1-05**: When `runSkillsSearch` throws (DB unreachable, KV miss, or any internal exception), the route returns sanitized `502 { error: "search_unavailable" }`. No internals leak to the client. A new test covers this path.
- [ ] **AC-US1-06**: After deploy to Cloudflare via `npm run deploy`, `curl -i 'https://verified-skill.com/api/v1/studio/search?q=greet&limit=20'` returns `HTTP/2 200` with a `results` array. (Manually verified by user post-deploy.)

---

### US-002: Skills/search route shares the same logic (DRY) (P2)
**Project**: vskill-platform

**As a** maintainer
**I want** `skills/search/route.ts` to call the same `runSkillsSearch` function as `studio/search/route.ts`
**So that** the merge/dedupe/enrichment logic lives in one place and can't drift between the two routes

**Acceptance Criteria**:
- [ ] **AC-US2-01**: `skills/search/route.ts` calls `runSkillsSearch` for the data-fetch portion (lines 206–304 today). Header construction (`X-Search-Source`, `Server-Timing`, `Cache-Control`, `X-Limit-Clamped`), Workers Cache read/write, KV `respVersion` lookup, and request param parsing remain in the route layer.
- [ ] **AC-US2-02**: All existing `skills/search` tests (`route.test.ts`, `route-publisher.test.ts`, `route-publisher-degrade.test.ts`, `route-bwc-vskill-find.test.ts`, `dedup.test.ts`) pass unchanged — public response envelope is invariant.
- [ ] **AC-US2-03**: A new unit test file `src/lib/studio/__tests__/run-skills-search.test.ts` covers the extracted function: merge fallback (edge-only, postgres-only, both), dedup-by-(ownerSlug, skillSlug), blocklist filtering, publisher-join 50ms soft-timeout degradation. Coverage ≥ 90% for the new module.

## Functional Requirements

### FR-001: Pure-function extraction
`runSkillsSearch` MUST be a pure function — no `req` access, no `cookies`, no Workers `env` reads. Cache key generation, ETag computation, and rate-limit checks remain in the route layer.

### FR-002: Defense-in-depth envelope check
After `runSkillsSearch` resolves, the studio route validates the envelope shape (`results: array`, `total: number`, `pagination: { hasMore: boolean }`). If validation fails, return sanitized `502` and `console.error` a structured log line. Mirrors the existing malformed-envelope guard at `studio/search/route.ts:203-211`.

### FR-003: Observability for rollout
Add a `console.info("studio_search_direct:", { q_len, limit, offset, source })` log in the studio route happy path so we can confirm the new code path is exercised in CF logs post-deploy. Remove the log line in a follow-up cleanup increment.

## Non-Functional Requirements

### NFR-001: Contract invariants preserved
Per `/.specweave/docs/contracts/studio-search-api-v1.md`:
- Rate limit: 60 req / 60s / IP (cache hits don't consume tokens) ✓
- Cache: `private, max-age=60` + ETag-based 304 ✓
- ETag: base64url SHA-256 truncated to 16 chars, RFC 7232 multi-value matching ✓
- Sanitized 502 on internal error ✓
- vskill CLI BWC envelope `{ results, pagination: { hasMore } }` ✓

### NFR-002: Performance — strictly improves
The refactor REMOVES one full HTTP roundtrip (worker-to-self subrequest), the 5-second timeout budget, and the `AbortController` wiring. CPU usage decreases per request. No regression possible — direct in-process call is a strict improvement over a self-fetch.

### NFR-003: Worker bundle size
The refactor consolidates duplicated code into a shared lib module. Net bundle size decreases or stays neutral. `npm run build:worker` MUST complete cleanly with no edge-runtime breakage.

## Risks

| Risk | Mitigation |
|---|---|
| Test scaffolding migration could miss a behavior assertion | Diff full test file before/after; ensure every `it()` block survives — only the mock setup line changes |
| Extracted function carries env/KV access deeper than expected | Keep `getKvForVersion()` + `respVersion` lookup at the route layer; `runSkillsSearch` takes `respVersion?` as an optional input arg |
| Publisher-join 50ms timeout uses `AbortController` tied to NextResponse | Per Explore agent #1 verification, the timeout uses `Promise.race` + `setTimeout`, independent of NextResponse — ports cleanly |
| Wrangler deploy fails due to Worker CPU budget | Refactor REDUCES CPU (no subrequest fan-out) — only improves the budget |
| Cloudflare cache holds the old 502 response | `Cache-Control: private` means no shared cache; user reload after deploy should fetch the new path |

## Success Criteria

- **Primary**: `curl 'https://verified-skill.com/api/v1/studio/search?q=greet&limit=20'` returns HTTP 200 within 1 hour of deploy.
- **Secondary**: Studio find-palette `studio_search_direct` log line appears in Cloudflare Workers logs post-deploy, confirming the new code path is exercised.
- **Tertiary**: vskill studio palette stops showing the "Live search is offline" graceful-degradation banner for typed queries.

## Dependencies

- **Depends on**: nothing — surgical change to existing files. No new env vars, no new bindings, no migration.
- **Unblocks**: nothing critical — local studio already ships graceful degradation for this 502 (increment 0741). This hotfix simply restores the full catalogue.
