# Tasks: Hotfix: studio/search 502 — replace CF Worker self-fetch with direct call

## Summary

13 implementation tasks + 2 manual verification gates. TDD red-green-refactor throughout. Single domain (vskill-platform routes + lib). All file paths relative to `repositories/anton-abyzov/vskill-platform/`.

## Tasks

### T-001: RED — write run-skills-search unit tests
**User Story**: US-002 | **Satisfies ACs**: AC-US2-03 | **Status**: [ ] pending | **Phase**: red

Create `src/lib/studio/__tests__/run-skills-search.test.ts` with failing tests covering the contract of the not-yet-extracted `runSkillsSearch` function. Mock `@/lib/search` (searchSkills, searchSkillsEdge, getBlockedSkillNames, searchBlocklistEntries, searchRejectedSubmissions) and `@/lib/publisher` (enrichWithPublishers, countSkillsMatchingQuery).

**Test Plan**:
- Given `searchSkillsEdge` returns 5 results AND `searchSkills` (postgres) returns 3 overlapping → When `runSkillsSearch({q, limit, offset})` runs → Then results merged + deduped by `(ownerSlug, skillSlug)` keep edge-first, telemetry.source = "edge+postgres".
- Given edge returns empty AND postgres returns 8 → When run → Then 8 results, telemetry.source = "postgres".
- Given a blocklisted skill in the merged set → When run → Then it's filtered out before pagination.
- Given `enrichWithPublishers` rejects after 60ms (>50ms timeout) → When run → Then results return without publisher data, telemetry.publisherDegraded = true.
- Given `limit=10, offset=20` and 50 merged results → When run → Then `pagination.hasMore = true` and `results.length = 10`.

### T-002: GREEN — extract runSkillsSearch
**User Story**: US-001 + US-002 | **Satisfies ACs**: AC-US1-01, AC-US2-01 | **Status**: [ ] pending | **Phase**: green

Create `src/lib/studio/run-skills-search.ts`. Move logic from `src/app/api/v1/skills/search/route.ts:206-304` (edge+postgres parallel, merge, blocklist enrichment, dedup, publisher join with 50ms `Promise.race` timeout, pagination slice). Export `runSkillsSearch` + `RunSkillsSearchInput` + `RunSkillsSearchOutput` interfaces. No `req`/`env`/Workers access — all input via the params object.

**Test Plan**: T-001 tests pass.

### T-003: GREEN — wire skills/search route to use runSkillsSearch
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02 | **Status**: [ ] pending | **Phase**: green

Edit `src/app/api/v1/skills/search/route.ts`. Replace lines 206–304 with `const out = await runSkillsSearch({q, limit, offset, category, respVersion})`. Read `out.telemetry` to populate `Server-Timing` and `X-Search-Source` headers. Keep param parsing, KV `respVersion` lookup via `getKvForVersion`, Workers Cache read/write, `X-Limit-Clamped` header, `Cache-Control` header construction.

**Test Plan**: All existing `src/app/api/v1/skills/search/__tests__/*.test.ts` pass unchanged (`route.test.ts`, `route-publisher.test.ts`, `route-publisher-degrade.test.ts`, `route-bwc-vskill-find.test.ts`, `dedup.test.ts`).

### T-004: RED — migrate studio/search route.test.ts mocks
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03 | **Status**: [ ] pending | **Phase**: red

Edit `src/app/api/v1/studio/search/__tests__/route.test.ts`. Replace `vi.stubGlobal("fetch", mockFetch)` with `vi.mock("@/lib/studio/run-skills-search", () => ({ runSkillsSearch: vi.fn() }))`. Replace `mockFetch.mock.calls[0][0]` URL inspection with `runSkillsSearch.mock.calls[0][0]` payload checks. Rewrite the timeout test as "runSkillsSearch rejects → 502 sanitized". Every existing `it()` block survives — only mock setup + call-site assertions change.

**Test Plan**: Tests fail because the studio route still calls `fetch()`, not `runSkillsSearch`.

### T-005: GREEN — refactor studio/search route to direct call
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02, AC-US1-03 | **Status**: [ ] pending | **Phase**: green

Edit `src/app/api/v1/studio/search/route.ts`:
1. Delete `originFromRequest()` function.
2. Delete `UPSTREAM_TIMEOUT_MS` constant.
3. Delete `upstreamCtrl`, `upstreamTimedOut`, the `req.signal` self-abort wiring, and the surrounding try/catch that wraps the fetch.
4. Replace the fetch+timeout block with: `const out = await runSkillsSearch({q, limit, offset})` inside a try/catch. Catch block returns sanitized `502 search_unavailable`.
5. Keep rate-limit, LRU cache lookup/write, ETag computation, X-Cache header, Cache-Control header, Server-Timing (proxy timing only), and the malformed-envelope guard.
6. Add `console.info("studio_search_direct:", { q_len: q.length, limit, offset, source: out.telemetry?.source })` on the happy path before returning 200.

**Test Plan**: T-004 tests pass.

### T-006: RED — happy-path 200 test
**User Story**: US-001 | **Satisfies ACs**: AC-US1-04 | **Status**: [ ] pending | **Phase**: red

Add a test in `src/app/api/v1/studio/search/__tests__/route.test.ts`:
- Given `runSkillsSearch.mockResolvedValue({results: [skill1, skill2], total: 2, offset: 0, pagination: {page: 1, limit: 20, hasMore: false}})` → When GET → Then status 200, response body matches `{results, total, pagination}` shape, headers include `ETag`, `X-Cache: MISS`, `Cache-Control: private, max-age=60`.

**Test Plan**: Confirm test fails initially if happy path is broken (verifies test is genuine).

### T-007: GREEN — happy-path 200 confirmed
**User Story**: US-001 | **Satisfies ACs**: AC-US1-04 | **Status**: [ ] pending | **Phase**: green

Make T-006 pass. Likely passes after T-005 since the studio route already constructed those headers. If broken, fix the route.

### T-008: RED — runSkillsSearch throws → 502 sanitized
**User Story**: US-001 | **Satisfies ACs**: AC-US1-05 | **Status**: [ ] pending | **Phase**: red

Add a test:
- Given `runSkillsSearch.mockRejectedValue(new Error("DB unreachable: <internal trace>"))` → When GET → Then status 502, body = `{"error":"search_unavailable"}`, no internals leak (`<internal trace>` not in body), `console.error` called with structured log.

**Test Plan**: Verify the catch block sanitizes errors per FR-001/AC-US1-05.

### T-009: GREEN — confirm sanitized 502
**User Story**: US-001 | **Satisfies ACs**: AC-US1-05 | **Status**: [ ] pending | **Phase**: green

Confirm T-008 passes given the catch block in T-005. Adjust if any internal detail leaks.

### T-010: REFACTOR — drop unused imports + lint
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02 | **Status**: [ ] pending | **Phase**: refactor

In `src/app/api/v1/studio/search/route.ts`, remove any imports that are now dead (e.g. unused types from `next/server`). Run `npx eslint src/app/api/v1/studio/search/route.ts` — clean.

### T-011: Migrate route-perf.test.ts
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03 | **Status**: [ ] pending | **Phase**: green

Apply the same fetch-mock → function-mock migration to `src/app/api/v1/studio/search/__tests__/route-perf.test.ts`. The perf assertion (route overhead in ms) remains valid — direct function call is faster than the mocked fetch was.

### T-012: Run full vitest suite for changed modules
**User Story**: US-001 + US-002 | **Satisfies ACs**: AC-US1-03, AC-US1-04, AC-US1-05, AC-US2-02, AC-US2-03 | **Status**: [ ] pending

Run `npx vitest run src/lib/studio src/app/api/v1/studio/search src/app/api/v1/skills/search`. All green. Capture coverage; ensure `run-skills-search.ts` ≥ 90%.

### T-013: Build + worker build clean
**User Story**: US-001 | **Satisfies ACs**: NFR-003 | **Status**: [ ] pending

Run `npm run build` (Next.js) and `npm run build:worker` (OpenNext + wrangler). Both clean — no edge-runtime errors, no type errors, no module resolution failures.

### T-MANUAL-1: Push + deploy (USER-TRIGGERED)
**User Story**: US-001 | **Satisfies ACs**: precondition for AC-US1-06 | **Status**: [ ] pending

After T-013, summarize the change and stop. The user explicitly triggers:
```
git add -A && git commit -m "0753: hotfix studio/search 502 — direct call to runSkillsSearch"
git push origin main
cd repositories/anton-abyzov/vskill-platform && npm run deploy
```
Deploy is a destructive shared-system action — never automated. Wait for user approval.

### T-MANUAL-2: Post-deploy verification
**User Story**: US-001 | **Satisfies ACs**: AC-US1-06 | **Status**: [ ] pending

After the user reports deploy success:
1. `curl -i 'https://verified-skill.com/api/v1/studio/search?q=greet&limit=20'` → expect HTTP/2 200 with `results` array.
2. Open vskill studio locally, ⌘⇧K, type "greet" — expect real results, no "Live search is offline" banner.
3. Check Cloudflare Workers logs for `studio_search_direct:` log line confirming new code path is exercised.
4. Mark AC-US1-06 complete.
