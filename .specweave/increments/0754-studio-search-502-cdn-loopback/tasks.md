# Tasks: P0 hotfix — Studio search 502 (CDN loopback)

## Task Notation

- `T-NNN`: Task ID
- `[ ]` not started · `[x]` completed
- Model: haiku (mechanical) · opus (judgment)
- TDD discipline: RED → GREEN → REFACTOR → VERIFY

---

## Phase 1: RED — pin binding-first dispatch with failing tests

### T-001: Locate or create the studio-search route test file
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01..03 setup | **Status**: [x] completed | **Model**: haiku

**Description**: Find an existing test file for `src/app/api/v1/studio/search/route.ts`. If none exists, create `src/app/api/v1/studio/search/__tests__/route.test.ts` with the standard vitest scaffolding mirroring the structure of `src/lib/skill-update/__tests__/publish-client.test.ts`. The new file must have a top-level `vi.mock("@opennextjs/cloudflare", () => ({ getCloudflareContext: vi.fn() }))` so each test can stub the CF context.

**Test Plan** (Given/When/Then):
- **Given** the studio-search route is part of the app
- **When** I run `find vskill-platform/src -path '*studio/search*test*'`
- **Then** I either confirm an existing test file (extend it) or know I need to create one

**Verify**: The test file exists with `vi.mock` for `@opennextjs/cloudflare` and at least one passing baseline test (sanity render).

---

### T-002: Add binding-present test (RED)
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-03 | **Status**: [x] completed | **Model**: opus

**Description**: Add a vitest test that:
1. Stubs `getCloudflareContext` to resolve `{ env: { WORKER_SELF_REFERENCE: { fetch: bindingFetchSpy } } }`.
2. Stubs `globalThis.fetch` with a separate spy.
3. Calls the route's `GET` handler with a mock `NextRequest` for `?q=react`.
4. The bindingFetchSpy returns a valid `{ results: [], total: 0 }` envelope as `Response`.
5. Asserts `bindingFetchSpy` was called exactly once with the upstream URL.
6. Asserts `globalThis.fetch` (the module-level spy) was NOT called.

The test description matches `publish-client.test.ts` style: `"uses the WORKER_SELF_REFERENCE service binding when present (avoids public-CDN loopback that returns 403)"`.

**Test Plan** (Given/When/Then):
- **Given** the test stub provides a WORKER_SELF_REFERENCE binding via getCloudflareContext, and the route source still uses globalThis.fetch unconditionally
- **When** I run `npx vitest run src/app/api/v1/studio/search/`
- **Then** the new test FAILS because globalThis.fetch was called instead of the binding (RED achieved)

**Verify**: vitest reports the new test as failing with an assertion on call counts.

---

### T-003: Add binding-absent fallback test (RED)
**User Story**: US-002 | **Satisfies ACs**: AC-US2-02, AC-US2-03 | **Status**: [x] completed | **Model**: opus

**Description**: Add a second vitest test that:
1. Stubs `getCloudflareContext` to resolve `{ env: {} }` (no WORKER_SELF_REFERENCE) OR throw — both branches must produce the fallback.
2. Stubs `globalThis.fetch` with a spy returning a valid envelope.
3. Calls `GET` on the same query.
4. Asserts `globalThis.fetch` was called once with the upstream URL.

Description: `"falls back to globalThis.fetch when no service binding is provided"`.

**Test Plan** (Given/When/Then):
- **Given** no binding is provided and the route source still imports/uses globalThis.fetch
- **When** I run vitest
- **Then** this test should PASS even pre-fix (because fallback IS the current behavior). Confirm so.

**Verify**: This test passes both pre- and post-fix — it's the regression guard for the fallback path. T-002 alone proves RED→GREEN; T-003 ensures the binding-first refactor doesn't break dev/test fallback.

---

## Phase 2: GREEN — apply the service-binding dispatch

### T-004: Add `getSelfBinding()` helper to the route module
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02 | **Status**: [x] completed | **Model**: haiku

**Description**: Inside `src/app/api/v1/studio/search/route.ts`, add a private async helper `getSelfBinding()` near the top (just under the module-level `cache` and `rateLimit` declarations). It dynamically imports `@opennextjs/cloudflare`, awaits `getCloudflareContext({ async: true })`, returns `env.WORKER_SELF_REFERENCE` if present, returns `null` otherwise. Wrap in try/catch so any throw (e.g., dev runtime without CF) returns `null`.

**Test Plan** (Given/When/Then):
- **Given** the helper is added
- **When** the test from T-003 runs and getCloudflareContext throws
- **Then** the helper returns null and the route falls back to globalThis.fetch (test still passes)

**Verify**: route.ts compiles cleanly; the helper is a pure addition (no behavior change yet — that's T-005).

---

### T-005: Swap dispatch at line 153 to binding-first ternary
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03 | **Status**: [x] completed | **Model**: haiku

**Description**: Inside the GET handler, immediately before the existing `upstreamRes = await fetch(url.toString(), { signal: upstreamCtrl.signal });` at line 153, call `const binding = await getSelfBinding();`. Replace the fetch call with `upstreamRes = binding ? await binding.fetch(url.toString(), { signal: upstreamCtrl.signal }) : await fetch(url.toString(), { signal: upstreamCtrl.signal });`.

Do not change the AbortController setup (lines 133-144), the timeout (line 28), the catch block (lines 160-179), the finally block (lines 180-183), the response handling (lines 185-211), or anything else in the file. This is a 2-line transport swap.

**Test Plan** (Given/When/Then):
- **Given** T-002 was failing (binding spy not called)
- **When** I apply this dispatch swap and re-run `npx vitest run src/app/api/v1/studio/search/`
- **Then** T-002 PASSES (binding spy called); T-003 still PASSES (fallback works)

**Verify**: All studio-search route tests pass — both new ones and pre-existing ones (cache, ETag, rate-limit, timeout, malformed envelope, etc.).

---

## Phase 3: REFACTOR — confirm no twin defects elsewhere

### T-006: Grep for other unmediated public-domain self-fetches in routes
**User Story**: US-001 | **Satisfies ACs**: regression guard | **Status**: [x] completed | **Model**: haiku

**Description**: Run two greps to confirm no other Next.js route makes a same-origin loopback fetch without going through the service binding:

```
grep -rn "fetch(.*verified-skill\.com" src/app/ src/lib/ 2>/dev/null
grep -rn "originFromRequest\|new URL.*req\.url.*api/v1" src/app/api/ 2>/dev/null
```

Inspect any hits. If a hit calls `globalThis.fetch` against the same origin without a binding fallback, capture it as a follow-up issue (do not fix here — out of scope for the hotfix). Document the findings in `reports/refactor-grep.md` under the increment folder.

**Test Plan** (Given/When/Then):
- **Given** the two greps run from the vskill-platform repo root
- **When** I review hits
- **Then** I confirm whether the studio-search route was the only offender (likely yes — publish-client was already fixed in 0708) and document any new defects without fixing them

**Verify**: `reports/refactor-grep.md` captures the grep output and a one-line conclusion (clean / follow-up needed).

---

## Phase 4: VERIFY — typecheck, full local tests, deploy, production smoke

### T-007: Run lint + typecheck
**User Story**: US-001 | **Satisfies ACs**: code quality gate | **Status**: [x] completed | **Model**: haiku

**Description**: From `vskill-platform/`, run `npm run lint && npm run typecheck` (or whatever the project scripts expose). Fix any new errors introduced by the change.

**Verify**: both commands exit 0 with no new warnings or errors attributable to the hotfix.

---

### T-008: Run full studio-search route vitest suite + smoke other affected routes
**User Story**: US-001, US-002 | **Satisfies ACs**: regression guard | **Status**: [x] completed | **Model**: haiku

**Description**: `npx vitest run src/app/api/v1/studio/` from vskill-platform — full studio API test surface. Also run `npx vitest run src/lib/studio/` to confirm the LRU/rate-limit/etag helpers still pass. If any pre-existing tests fail, investigate whether they're related to the change before declaring success.

**Verify**: full output shows 0 failures attributable to this increment.

---

### T-009: Deploy to Cloudflare
**User Story**: US-001, US-003 | **Satisfies ACs**: AC-US3-01..02 | **Status**: [x] completed | **Model**: opus

**Description**: From `vskill-platform/`, run `npm run deploy` (= `npx @opennextjs/cloudflare deploy`). This rebuilds the OpenNext bundle and pushes it to the `verified-skill-com` worker. Watch for any deploy errors. Capture deploy output in `reports/deploy-output.txt` under the increment folder.

**IMPORTANT**: Per project memory, deploys after git push are mandatory for vskill-platform. This is a P0 fix — deploy is part of the closure, not optional.

**Test Plan** (Given/When/Then):
- **Given** the source is committed and the deploy command is invoked
- **When** I wait for the deploy to complete
- **Then** OpenNext reports a successful deploy with a worker version ID; the worker URL is the same `verified-skill-com`

**Verify**: deploy output ends with a success message + version ID.

---

### T-010: Production smoke — confirm 502 → 200
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US1-04 | **Status**: [x] completed | **Model**: opus

**Description**: After T-009 deploy completes, run live probes:

```
curl -sS -o /tmp/probe-react.json -w "react: code=%{http_code} size=%{size_download}\n" \
  "https://verified-skill.com/api/v1/studio/search?q=react"
curl -sS -o /tmp/probe-sb.json -w "skill-builder: code=%{http_code} size=%{size_download}\n" \
  "https://verified-skill.com/api/v1/studio/search?q=skill-builder&limit=50"
python3 -c "
import json
sb = json.load(open('/tmp/probe-sb.json'))
print(f'total={sb.get(\"total\")}')
hits = [r for r in sb.get('results', []) if r.get('name','') == 'anton-abyzov/vskill/skill-builder']
print(f'anton-abyzov/vskill/skill-builder present: {len(hits) == 1}')
"
```

Both curls must return code=200. The skill-builder probe must report `total >= 31` and `anton-abyzov/vskill/skill-builder present: True`. Capture all probe output in `reports/production-smoke.log`.

**Test Plan** (Given/When/Then):
- **Given** the deploy is live and CF has propagated
- **When** I run the curl probes
- **Then** both return HTTP 200 with valid JSON envelopes; the user's specific skill is in the result list

**Verify**: `reports/production-smoke.log` shows code=200 for both probes + the skill present check passes. If either fails, the increment stays OPEN — investigate before closing.

**Rollback**: if production smoke fails, revert the source commit and re-deploy. The fix is so small (~10 lines) that a fast revert is the right move; we'd then re-investigate root cause.

---

## Summary

- **Tasks**: 10 (3 RED, 2 GREEN, 1 REFACTOR, 4 VERIFY)
- **Source files changed**: 1 (`route.ts`)
- **Test files changed/added**: 1 (`route.test.ts`)
- **Lines of source delta**: ~15 (new helper + ternary + types)
- **Risk**: low — proven 0708 pattern, 2-line dispatch swap, fallback preserves dev/test
- **Customer-impact criticality**: P0 — every Studio search currently 502s
