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

- [x] **AC-US1-01** (Hero count test passes on current UI): Retargeted test `homepage shows verified skill count > 0` asserts `.hero-h1` visibility + `getByText(/\d[\d,]*\s+verified/)` > 0. Passes against prod.
- [ ] **AC-US1-02** (Skills page rows visible): BLOCKED on unapplied 0680 Prisma migration (`getSkills` throws `column "(not available)" does not exist`). Defense-in-depth in place: `export const dynamic = "force-dynamic"` + cron-warmed KV fallback on /skills. Test will pass automatically once the 0680 migration lands. Spawn task queued.
- [x] **AC-US1-03** (Metric cards test retargeted to live UI): `.metric-grid` removed from homepage. Retargeted to `homepage hero shows agent-platform count and trust/intent pills`: asserts "Security-verified skills for N AI agent platforms" (N > 0) + "N trust tiers" pill + "AI intent analysis" pill. Passes against prod.
- [ ] **AC-US1-04** (Stats health goes OK after next cron tick): BLOCKED on 0680 migration — `computePlatformStats` fails with the same column error, preventing the stats KV write. Watermark-gate fix (US-002) will take effect immediately once the migration is applied.
- [ ] **AC-US1-05** (Full smoke run is green): 9/11 pass (was 7/11). Remaining 2 failures (`skills API returns 200 with skills array`, `skills page loads with skill rows`) both gated on the 0680 migration.

### US-002 — Stats cron is resilient to transient KV write failures

**Project**: vskill-platform

**As** an operator of the stats refresh cron,
**I want** the 6-hour recompute watermark to persist only when the corresponding stats KV write succeeded,
**so that** a single transient `kv.put` failure does not lock the system into a stale state until an isolate recycles.

**Acceptance Criteria**

- [x] **AC-US2-01** (No watermark without stats): Covered by `stats-refresh.watermark.test.ts` case 1. `kv.put("platform:stats", …)` throws → watermark key `platform:lastStatsComputedAt` never written. Passing.
- [x] **AC-US2-02** (Happy path unchanged): Covered by test case 2. Both stats KV put and watermark put observed on the happy path. Passing.
- [x] **AC-US2-03** (Next tick recomputes after failure): Covered by the ordering guarantee in `stats-refresh.ts:183` — `if (kvWriteOk)` gate means a failure leaves the watermark unset, and the next cron tick takes the "watermark missing" branch into a full recompute.
- [x] **AC-US2-04** (Inconsistent-stats early-return preserved): Covered by test case 3. `statsAreConsistent === false` → no writes to either key. Passing.
- [x] **AC-US2-05** (Observability): Covered by test case 4. On KV put failure, `[stats-refresh] skipping watermark write because stats KV put failed — next cron tick will retry full recompute` is emitted via `console.error`. Passing.

## Non-Goals

- Replacing/removing the `MetricCard` component or `.metric-grid` CSS.
- Rearchitecting the stats refresh pipeline (delta-skipping, watermark key scheme, etc.). Only fix the ordering bug.
- Fixing unrelated smoke flakiness (cold-start timing on CF, rate-limit interference).

## Risks & Mitigations

- **Risk**: `/skills` empty-result root cause may require deeper investigation (missing index, filter default change). **Mitigation**: start with a headed Playwright run + prod-log review; only touch `getSkills()` if we confirm a server-side bug.
- **Risk**: `/insights` page may not have the exact dashboard structure the old test expected. **Mitigation**: verify structure before writing the assertion; fall back to API-level invariant.
- **Risk**: Watermark fix could unintentionally re-trigger expensive recompute on every tick if tests reveal an existing silent-failure stream. **Mitigation**: fix is narrow — only omits the watermark when the stats put failed; happy path unchanged. Verify via prod monitoring after deploy.
