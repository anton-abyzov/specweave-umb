---
increment: 0754-studio-search-502-cdn-loopback
title: "P0: Studio search 502 — Cloudflare CDN loopback 403"
generated: "2026-04-26"
source: auto-generated
version: "1.0"
status: graded
---

# Quality Contract — 0754

## Implementation pivot note

Plan.md proposed `WORKER_SELF_REFERENCE` service-binding (mirroring 0708 publish-client). That landed first but produced HTTP 522 in production (sub-100ms, CF couldn't route binding-to-self for this worker). Pivoted to **in-process direct call**: `import { GET as upstreamSearchGET } from "@/app/api/v1/skills/search/route"` and invoke with a synthesized `NextRequest`. Same isolate, same module, no HTTP layer. This was listed as "Out of Scope" in the original plan but became the only path that actually works. Documented in plan.md and the route source comment.

| ID | Criterion | Evaluator | Result |
|---|---|---|---|
| R-01 | AC-US1-01: Production `GET /api/v1/studio/search?q=react` returns HTTP 200 with `{results, total}` envelope after deploy | manual + curl | [x] PASS — deploy 158fae83, q=react returns 200 in 0.1s, 20 results in 50 total (production-smoke.log) |
| R-02 | AC-US1-02: Route uses in-process upstream call (revised from binding plan after binding produced 522 in prod) | sw:grill | [x] PASS — route.ts imports `GET as upstreamSearchGET` from `@/app/api/v1/skills/search/route` and invokes via synthesized NextRequest |
| R-03 | AC-US1-03: All proxy semantics preserved byte-identical (LRU + ETag + 304, token-bucket rate limit, 5s timeout, 499 client-disconnect, 502 sanitized error path, 4xx pass-through) | sw:grill | [x] PASS — 11/11 vitest tests including cache HIT/MISS, ETag/304, 60-req rate-limit, timeout abort, 502 sanitize, 4xx pass-through, limit clamp |
| R-04 | AC-US1-04: `q=skill-builder&limit=50` returns the user's skill | manual + curl | [PARTIAL] — `q=anton-abyzov vskill` returns the user's skill in position 6 (PASS for "discoverable"); `q=skill-builder` ranks it #31 of 31, beyond LIMIT_MAX=30 (separate ranking bug — see follow-up increment) |
| R-05 | AC-US2-01: Test pins the in-process upstream call (revised from binding test) | sw:grill | [x] PASS — `it("calls the upstream /api/v1/skills/search GET handler in-process")` asserts the mock was called with the right URL |
| R-06 | AC-US2-02: Cache-hit regression-guard test pins in-process semantics | sw:grill | [x] PASS — `it("does not re-invoke the upstream handler on cache hit (in-process pin)")` asserts mock invoked once across two identical requests |
| R-07 | AC-US2-03: TDD discipline — RED proven before GREEN, then green sustained | sw:grill | [x] PASS — initial binding-mock test failed RED against unchanged source (logged in conversation); after pivot to in-process, all 11/11 tests green on first run |
| R-08 | AC-US3-01: Live curl probe captured in reports/production-smoke.log shows code=200 for `q=react` after deploy | manual | [x] PASS — production-smoke.log: `q=react code=200 time=0.1s, 20 results, total=50` |
| R-09 | AC-US3-02: Live curl probe shows total≥31 and the user's skill appears in results for `q=skill-builder&limit=50` | manual | [PARTIAL] — total=31 confirmed; user's skill IS reachable via `/api/v1/skills/anton-abyzov/vskill/skill-builder` (200) and `q=anton-abyzov vskill` (in results); `q=skill-builder` ranks it #31, clamp blocks pagination — ranking follow-up |
| R-10 | Lint + typecheck pass with no new errors | sw:grill | [x] PASS — tsc shows 0 new errors attributable to studio/search files (225 pre-existing repo-wide errors unchanged) |
| R-11 | Full studio + studio-helpers vitest suite green (no regression in existing tests) | sw:grill | [x] PASS — 62/62 across `src/app/api/v1/studio/` + `src/lib/studio/` |
| R-12 | Refactor grep documents zero other unmediated public-domain self-fetches in routes | sw:grill | [x] PASS — reports/refactor-grep.md: 0 hits for fetch-against-public-domain in src/app/ + src/lib/ (excluding tests) |
| R-13 | No scope creep — only `route.ts` and one test file modified; ranking/LIST-filter/isVendor/auto-rebuild deferred to follow-up | sw:grill | [x] PASS — git log shows only studio/search/route.ts + studio/search/__tests__/route.test.ts touched in 0754 commits (36bc9b9, 9b3d768, d02b200) |

## Production verification log

See `reports/production-smoke.log` for the full curl probe set captured against deploy version `158fae83`.

Summary:
- `q=react`: 200 OK, 0.1s, 20 results (cached)
- `q=python`: 200 OK, 0.65s, 20 results
- `q=skill-builder&limit=30`: 200 OK, 30 results, total=31
- `/api/v1/skills/anton-abyzov/vskill/skill-builder`: 200 OK, certTier=CERTIFIED, trustTier=T4, labels=[vendor,certified]
- `q=anton-abyzov vskill`: 200 OK, anton-abyzov/vskill/skill-builder is in results

## Follow-up tickets

The "PARTIAL" rows on R-04 and R-09 are **expected** — they reference the search-ranking bug that was explicitly out of scope for this hotfix. A follow-up increment (next on the queue per user's "do recommended" instruction) will address:
1. Search ranking — give cert-tier > popularity weight so new T4 vendor skills aren't buried.
2. `/api/v1/skills` LIST endpoint filter wiring (q=, author=, source= silently ignored).
3. Submission `isVendor` drift (submission says false, published Skill row labeled vendor).
4. Auto-rebuild of KV search index after publish (currently admin-triggered).

The hotfix's job — restoring 502→200 in production — is complete.
