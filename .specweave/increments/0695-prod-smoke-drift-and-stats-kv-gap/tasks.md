---
increment: 0695-prod-smoke-drift-and-stats-kv-gap
title: "Fix prod smoke drift and stats KV write gap"
---

# Tasks — prod-smoke-drift-and-stats-kv-gap

### T-001: RED unit test — watermark must not persist on stats KV put failure
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-03 | **Status**: [ ] pending
**Test Plan**: Given a mock KV whose `put("platform:stats", …)` throws and a stub `computePlatformStats` returning consistent stats → When `refreshPlatformStats(kv)` is awaited → Then the mock's `put` was NOT called with key `platform:lastStatsComputedAt` during this invocation.
Create `src/lib/cron/__tests__/stats-refresh.watermark.test.ts`. Mock `computePlatformStats` (return non-zero stats). Use an in-memory KV double. Include a complementary test that asserts the watermark IS written when the stats put succeeds (covers AC-US2-02).

### T-002: GREEN — gate watermark write on kvWriteOk
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-05 | **Status**: [ ] pending
**Test Plan**: Given the RED tests from T-001 → When the fix is applied → Then both tests pass.
Edit `src/lib/cron/stats-refresh.ts` at the watermark block (~line 183). Wrap the `kv.put(STATS_WATERMARK_KEY, …)` call in `if (kvWriteOk) { … } else { console.error("[stats-refresh] skipping watermark write because stats KV put failed"); }`. Do not touch the DB fallback upsert (step 7 in plan.md). Keep the completion log line as-is; the `kvWriteOk` flag already modifies its message.

### T-003: Verify AC-US2-04 with an explicit test
**User Story**: US-002 | **Satisfies ACs**: AC-US2-04 | **Status**: [ ] pending
**Test Plan**: Given `computePlatformStats` returns all-zero stats (inconsistent) → When `refreshPlatformStats(kv)` is awaited → Then neither `platform:stats` nor `platform:lastStatsComputedAt` was written.
Add a third test case to `stats-refresh.watermark.test.ts`. Confirms the existing early-return at line 141 still holds — no regression.

### T-004: Diagnose /skills rows missing on prod (F2)
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02 | **Status**: [ ] pending
**Test Plan**: Given the current prod deploy → When `E2E_BASE_URL=https://verified-skill.com npx playwright test tests/e2e/smoke.spec.ts:113 --project=chromium --headed` runs → Then browser network + console traces reveal whether `a.skills-list-row` appears at runtime.
Run the headed test, inspect the browser. Fetch `https://verified-skill.com/skills` with `curl` and count `skills-list-row` occurrences. Read `src/lib/skills-query.ts` (or `getSkills`) to understand the default query. Record findings inline here:

- Observations: (fill in during T-004)
- Decision: (a) fix server-side in `skills-query.ts`, or (b) fix test-side by raising timeout + `waitForLoadState("networkidle")`.

### T-005: Apply F2 fix per T-004 decision
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02, AC-US1-05 | **Status**: [ ] pending
**Test Plan**: Given the T-004 decision → When the fix is applied → Then `tests/e2e/smoke.spec.ts:113` passes against prod (after deploy if server-side fix; immediately if test-side).
If (a): edit `src/lib/skills-query.ts` (or equivalent) to repair the default-filter query. If (b): edit `tests/e2e/smoke.spec.ts:113-119` to add `await page.waitForLoadState("networkidle")` and bump the `toBeVisible` timeout to 45_000 ms.

### T-006: Fix smoke F1 — hero count selector
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-05 | **Status**: [ ] pending
**Test Plan**: Given the homepage renders a slogan `.hero-h1` plus a `{count} verified` span → When the smoke test runs → Then it reads the count via `getByText(/(\d[\d,]*)\s+verified/).first()`, captures the number, and asserts > 0.
Rename the test to `homepage shows verified skill count > 0`. Keep a separate `await expect(page.locator("span.hero-h1")).toBeVisible()` to lock the slogan presence. Drop the old regex matcher tied to "security-approved skills".

### T-007: Fix smoke F4 — retarget metric cards to /insights
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03, AC-US1-05 | **Status**: [ ] pending
**Test Plan**: Given the homepage no longer renders `.metric-grid` but `/insights` does → When the smoke test runs → Then it navigates to `/insights` and asserts each aggregate card's value is non-zero. If `/insights` does not expose a `.metric-grid`, retarget to `/api/v1/stats` aggregate non-zero assertion + `/insights` page 200.
Read `src/app/insights/page.tsx` to confirm structure. Rename the test to `insights metrics are non-zero`. Keep the assertion strength (no nullable acceptance).

### T-008: Build + deploy + live cron verification
**User Story**: US-001, US-002 | **Satisfies ACs**: AC-US1-04, AC-US1-05, AC-US2-03 | **Status**: [ ] pending
**Test Plan**: Given all source + test fixes are committed → When `npm run build:worker && npm run deploy` runs in `repositories/anton-abyzov/vskill-platform` → Then the Worker version increments, and the next scheduled `:00 UTC` cron tick writes both `platform:stats` and `platform:lastStatsComputedAt` to KV. Verified via `curl -s https://verified-skill.com/api/v1/stats/health | jq` → `status: "OK", ageMinutes: <60`.

### T-009: Full prod smoke run — all 11 tests green
**User Story**: US-001 | **Satisfies ACs**: AC-US1-05 | **Status**: [ ] pending
**Test Plan**: Given T-008 has completed and the next cron tick has fired → When `E2E_BASE_URL=https://verified-skill.com npx playwright test tests/e2e/smoke.spec.ts --project=chromium --reporter=list` runs → Then 11/11 tests pass. No retries hide failures.

### T-010: Close via /sw:done
**User Story**: US-001, US-002 | **Status**: [ ] pending
**Test Plan**: Given tasks T-001..T-009 are complete and tests green → When `/sw:done 0695` is invoked → Then code-review, simplify, grill, judge-llm, PM validation all pass; external tools sync; increment status flips to `completed`.
