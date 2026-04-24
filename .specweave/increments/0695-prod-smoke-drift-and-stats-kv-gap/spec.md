---
increment: 0695-prod-smoke-drift-and-stats-kv-gap
title: "Fix prod smoke drift and stats KV write gap"
type: bug
priority: P1
status: planned
created: 2026-04-24
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Fix prod smoke drift and stats KV write gap

## Context

Four Playwright smoke tests in `tests/e2e/smoke.spec.ts` fail against `https://verified-skill.com`:

1. `homepage shows skill count > 0` — hero `<h1 className="hero-h1">` now renders slogan text, not the `"N security-approved skills"` string the test matches against. ([HeroStats.tsx:15-16](repositories/anton-abyzov/vskill-platform/src/app/components/home/HeroStats.tsx))
2. `skills page loads with skill rows` — `a.skills-list-row` is missing from the SSR HTML even though 110k+ skills exist in DB. ([skills/page.tsx:242-257](repositories/anton-abyzov/vskill-platform/src/app/skills/page.tsx))
3. `stats health endpoint is not stale or missing` — `GET /api/v1/stats/health` returns `{"status":"MISSING"}` because the hourly cron writes its 6h recompute watermark *even when the KV `put("platform:stats", …)` fails*, trapping the system in a permanent short-circuit on the next tick. ([stats-refresh.ts:150-188](repositories/anton-abyzov/vskill-platform/src/lib/cron/stats-refresh.ts))
4. `dashboard metric cards show non-zero values` — the `.metric-grid` the test queries has been removed from the homepage; only CSS + component remain. Zombie test.

None of these are caused by the just-closed 0685 increment — they are pre-existing drift revealed by smoke-testing prod after 0685's deploy.

## Goal

Every failing smoke test passes against prod, without lowering any assertion. The stats KV write pipeline recovers on the first successful cron tick after deploy.

## User Stories

### US-001 — Prod smoke suite is green against verified-skill.com

**Project**: vskill-platform

**As** an operator running `E2E_BASE_URL=https://verified-skill.com npm run test:e2e:smoke`,
**I want** all 11 smoke tests to pass in one run,
**so that** prod regressions surface immediately and smoke-test drift stops masking real problems.

**Acceptance Criteria**

- [ ] **AC-US1-01** (Hero count test passes on current UI): Given the homepage hero renders slogan `"Install AI skills you can trust"` in `.hero-h1` and a separate `{count} verified` span at [HeroStats.tsx:24](repositories/anton-abyzov/vskill-platform/src/app/components/home/HeroStats.tsx), when the smoke test runs, then it asserts the count span text matches `/(\d[\d,]*)\s+verified/` with captured number > 0.
- [ ] **AC-US1-02** (Skills page rows visible): Given `/skills` with default filters, when the page is loaded, then `a.skills-list-row` is present and visible within 45 s. Root cause (server-side empty array OR test-side race) is identified and fixed at the real source — not by weakening the assertion.
- [ ] **AC-US1-03** (Metric cards test retargeted to live UI): Given the homepage no longer renders `.metric-grid`, when the smoke test runs, then the test targets a page that does render aggregate cards (e.g. `/insights`) OR switches to the equivalent `/api/v1/stats` invariant, with all assertions still requiring non-zero values. Test is renamed to reflect the new target.
- [ ] **AC-US1-04** (Stats health goes OK after next cron tick): Given the deploy ships the watermark-gating fix, when the next cron tick at `:00 UTC` fires successfully, then `GET /api/v1/stats/health` returns `{"status":"OK", "ageMinutes": <60, ...}` and remains OK through at least the following tick.
- [ ] **AC-US1-05** (Full smoke run is green): Given all four test fixes + the stats cron fix are deployed, when `E2E_BASE_URL=https://verified-skill.com npx playwright test tests/e2e/smoke.spec.ts --project=chromium` is run once, then 11/11 tests pass (was 7/11).

### US-002 — Stats cron is resilient to transient KV write failures

**Project**: vskill-platform

**As** an operator of the stats refresh cron,
**I want** the 6-hour recompute watermark to persist only when the corresponding stats KV write succeeded,
**so that** a single transient `kv.put` failure does not lock the system into a stale state until an isolate recycles.

**Acceptance Criteria**

- [ ] **AC-US2-01** (No watermark without stats): Given `refreshPlatformStats(kv)` runs and the `kv.put("platform:stats", …)` call throws, when the function returns, then the watermark key `platform:lastStatsComputedAt` MUST NOT have been written on this invocation.
- [ ] **AC-US2-02** (Happy path unchanged): Given `refreshPlatformStats(kv)` runs and both the stats KV put and the DB fallback write succeed, when the function returns, then the watermark is persisted with the current timestamp (same behavior as before the fix).
- [ ] **AC-US2-03** (Next tick recomputes after failure): Given the previous cron tick had a KV put failure and therefore did not write the watermark, when the next cron tick fires, then `refreshPlatformStats` executes the full recompute path (no watermark short-circuit) and attempts a new KV write.
- [ ] **AC-US2-04** (Inconsistent-stats early-return preserved): Given `computePlatformStats` returns partial-zero stats and `statsAreConsistent()` returns false, when the function early-returns at [stats-refresh.ts:141](repositories/anton-abyzov/vskill-platform/src/lib/cron/stats-refresh.ts), then neither the stats nor the watermark are written (unchanged from current behavior — this path is already correct).
- [ ] **AC-US2-05** (Observability): Given a KV put failure occurs, when the function returns, then a structured `console.error` is emitted noting both the stats-put failure and the explicit skip of the watermark write, so ops can correlate the gap.

## Non-Goals

- Replacing/removing the `MetricCard` component or `.metric-grid` CSS.
- Rearchitecting the stats refresh pipeline (delta-skipping, watermark key scheme, etc.). Only fix the ordering bug.
- Fixing unrelated smoke flakiness (cold-start timing on CF, rate-limit interference).

## Risks & Mitigations

- **Risk**: `/skills` empty-result root cause may require deeper investigation (missing index, filter default change). **Mitigation**: start with a headed Playwright run + prod-log review; only touch `getSkills()` if we confirm a server-side bug.
- **Risk**: `/insights` page may not have the exact dashboard structure the old test expected. **Mitigation**: verify structure before writing the assertion; fall back to API-level invariant.
- **Risk**: Watermark fix could unintentionally re-trigger expensive recompute on every tick if tests reveal an existing silent-failure stream. **Mitigation**: fix is narrow — only omits the watermark when the stats put failed; happy path unchanged. Verify via prod monitoring after deploy.
