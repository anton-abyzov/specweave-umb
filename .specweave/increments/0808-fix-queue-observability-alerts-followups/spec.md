---
increment: 0808-fix-queue-observability-alerts-followups
title: Fix queue observability alerts follow-ups (0807 judge-llm)
type: bug
priority: P1
status: completed
created: 2026-04-29T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Fix queue observability alerts follow-ups (0807 judge-llm)

## Overview

Close five judge-llm findings carried forward from increment 0807-queue-observability-alerts (`reports/judge-llm-report.json`, score 87/100). The biggest is a real production bug: the digest counter for info-severity alerts (currently only `llm-fallback-spike`) inflates ~36× over a 6h window because the cron loop calls `recordFired()` without a `shouldFire()` gate. The remaining four are quality cleanups: a trivially-skipped e2e ack test, a code/spec drift on digest window timing, zero unit tests for `RecentAlertsPanel`, and a dead single-iteration loop in the drain detector.

A submission-processing guarantee gate is bundled in: a fresh end-to-end submission against verified-skill.com must reach PUBLISHED quickly, measured during the deploy smoke pass.

## Problem

Five concrete findings:
- **J-001** (HIGH, real bug): `src/app/api/v1/internal/alerts-evaluator/route.ts:222-229` — info branch records every cron tick. Sustained `llm-fallback-spike` over 6h emits ~36 digest events instead of 1, polluting the digest email.
- **J-002** (HIGH, CI gap): `tests/e2e/admin-alerts.spec.ts:84-106` — TC-044/TC-045 use `test.skip` when ring buffer empty (the default in CI), so the panel-renders → ack → "Acknowledged" assertion never actually runs.
- **J-003** (MEDIUM, spec drift): 0807 `spec.md:71` AC-US3-05 says "09:00 / 13:00 / 17:00 / 21:00 UTC" but the implementation aligns to 00/06/12/18 UTC (`alerts-digest/route.ts:24-34`).
- **J-004** (MEDIUM, missing tests): `src/app/admin/queue/RecentAlertsPanel.tsx` (258 lines) has zero unit tests.
- **J-005** (LOW, dead code): `alerts-evaluator/route.ts:43` has `for (let i = 0; i < 1; i++)` — refactor leftover.

User follow-up requirement: prove submission processing is working AND fast end-to-end.

## User Stories

### US-001: Info-severity dedup gate (J-001) (P1)
**Project**: vskill-platform

**As an** ops operator
**I want** info-severity alerts to record into the digest at most once per (kind, key) per day
**So that** routine `llm-fallback-spike` noise does not inflate the digest counter ~36×

**Acceptance Criteria**:
- [x] **AC-US1-01**: `alerts-evaluator/route.ts` info branch checks `shouldFire(alertsKV, alert.kind, alert.key)` before `recordFired()` — same pattern as warning/critical. Suppressed runs increment the existing `suppressed` counter.
- [x] **AC-US1-02**: Existing `SEVERITY_TTL_S.info = 86400` is reused unchanged — info dedup keys live for 1 day per `(kind, key)`.
- [x] **AC-US1-03**: TC-046 in `alerts-evaluator/__tests__/route.test.ts`: two consecutive POSTs with the same sustained `llm-fallback-spike` condition → first call returns `counts.info===1` AND writes the dedup key; second call returns `counts.info===0`, `counts.suppressed>=1`, and the `alerts:digest:count:llm-fallback-spike` counter stays at `"1"`.

---

### US-002: AC-US4-04 e2e auto-seed (J-002) (P1)
**Project**: vskill-platform

**As an** ops operator
**I want** the `/admin/queue` ack-flow e2e test to run end-to-end on a clean ring buffer
**So that** I get real CI signal on the panel-renders → click Acknowledge → reload → "Acknowledged" assertion instead of `test.skip` noise

**Acceptance Criteria**:
- [x] **AC-US2-01**: New POST `/api/v1/admin/alerts/_test-seed` route. Double-gated: requires `requireAdmin` AND `env.ALLOW_ALERT_SEED === "1"`. Returns 403 if either gate fails.
- [x] **AC-US2-02**: Body `{ kind: AlertKind, severity?, key?, title?, payload? }` with sensible defaults: `severity = KIND_SEVERITY[kind]`, `key="e2e-seed"`, `title="[E2E SEED] {kind}"`, `payload={}`. Builds an `Alert` and calls `recordFired(alertsKV, alert)` — landing in `alerts:recent` AND in dedup KV.
- [x] **AC-US2-03**: Three vitest cases for `_test-seed`: 403 without flag, 401/403 without admin, 200 + ring-buffer entry on happy path.
- [x] **AC-US2-04**: Updated `tests/e2e/admin-alerts.spec.ts` ack-flow seeds via `_test-seed` before navigating, then runs the full assert chain (panel visible → ack click → reload → seeded id under `[data-testid="alerts-acknowledged-section"]`). When `ALLOW_ALERT_SEED` is unset (local dev), test falls back to `test.skip` once with a clear reason.
- [x] **AC-US2-05**: `ALLOW_ALERT_SEED` flag default-OFF in prod (Cloudflare secret set to "0").

---

### US-003: Spec/code alignment for digest window (J-003) (P2)
**Project**: vskill-platform

**As a** future maintainer
**I want** 0807 `spec.md:71` AC-US3-05 wording to match the implemented digest window
**So that** spec ↔ code do not drift

**Acceptance Criteria**:
- [x] **AC-US3-01**: 0807 spec line "09:00 / 13:00 / 17:00 / 21:00 UTC" updated to "00:00 / 06:00 / 12:00 / 18:00 UTC" with a brief inline note referencing this 0808 increment for auditability. Code stays unchanged.

---

### US-004: RecentAlertsPanel unit tests (J-004) (P2)
**Project**: vskill-platform

**As a** future maintainer
**I want** RTL unit tests covering the five interesting states of `RecentAlertsPanel`
**So that** UI regressions surface in vitest, not on `/admin/queue` after a release

**Acceptance Criteria**:
- [x] **AC-US4-01**: New `src/app/admin/queue/__tests__/RecentAlertsPanel.test.tsx` with 5 test cases (TC-051..TC-055): empty buffer, loading, fetch error, severity grouping, ack flow.
- [x] **AC-US4-02**: Tests use the existing `@testing-library/react` + `@testing-library/jest-dom` stack with vitest jsdom env (already auto-applied to `src/app/**/__tests__/*.test.tsx`).
- [x] **AC-US4-03**: Tests assert against the existing data-testid hooks: `recent-alerts-panel`, `alerts-empty`, `alerts-error`, `alerts-{critical|warning|info}`, `ack-btn-{id}`, `alerts-acknowledged-section`. No DOM markup change.

---

### US-005: Drain-window cleanup (J-005) (P3)
**Project**: vskill-platform

**As a** future maintainer
**I want** the dead `for (let i = 0; i < 1; i++)` loop in `readDrainLast1h` replaced with a clear, env-configurable window
**So that** a confused reader does not assume a bug, and a future operator can widen the look-back window without redeploying code

**Acceptance Criteria**:
- [x] **AC-US5-01**: Replace dead loop with `for (let i = 0; i < envInt("ALERT_DRAIN_WINDOW_HOURS", 1); i++)`. Default behavior unchanged at `windowHours=1`.
- [x] **AC-US5-02**: One inline code comment names `ALERT_DRAIN_WINDOW_HOURS` so the operator knob is discoverable in code (not just env).
- [x] **AC-US5-03**: New test asserts `ALERT_DRAIN_WINDOW_HOURS=3` reads three hourly buckets and sums them.

---

### US-006: Submission-processing guarantee (P1)
**Project**: vskill-platform

**As an** ops operator
**I want** proof during 0808 deploy that a brand-new submission to verified-skill.com reaches PUBLISHED quickly
**So that** I can guarantee the submission pipeline is healthy after the alert system + key rotation work in 0807

**Acceptance Criteria**:
- [x] **AC-US6-01**: During production smoke (T-012), POST a fresh test submission via `/api/v1/submissions` against a public skill in a vendor repo (or re-use an existing stale RECEIVED if appropriate).
- [x] **AC-US6-02**: Time the round-trip from POST to `state=PUBLISHED` (poll DB at 5s cadence). Record elapsed seconds in the increment closure notes.
- [x] **AC-US6-03**: Elapsed time must be ≤ 300 seconds (5 minutes). If it exceeds, the increment fails closure and a follow-up incident note is created.

## Success Criteria

- 65/65 vitest tests pass across `src/lib/alerts/**`, `src/app/api/v1/admin/alerts/**`, `src/app/api/v1/internal/alerts-{evaluator,digest}/**`, `src/app/admin/queue/__tests__/RecentAlertsPanel.test.tsx`.
- `npx tsc --noEmit` produces zero errors on 0808 paths.
- Production smoke confirms TWO consecutive `*/10` cron ticks with the same `llm-fallback-spike` condition leave `alerts:digest:count:llm-fallback-spike` at `"1"` and the dedup key set.
- A fresh submission processed during deploy reaches PUBLISHED within 5 minutes.
- Worker version recorded in increment closure notes.

## Out of Scope

- Slack / Discord / PagerDuty channels (still email-only — punted in 0807).
- Per-user alert subscription preferences.
- Replacing the broken VM heartbeat producer (separate bug, separate increment).
- Refactoring the queue consumer / scanner pipeline. The 2,882 stuck RECEIVED submissions discovered during 0807 closure are out of scope here; 0808 only verifies that NEW submissions flow through quickly.
- Cleaning up the seeded test alert from the ring buffer post-test (it ages out via the 100-entry cap).

## Dependencies

- 0807 shipped — alerts pipeline + admin UI live in production (worker `a0d3cae1-5af4-451c-bc01-169f4186cd43`).
- `@testing-library/react@^16.3.2`, `@testing-library/jest-dom@^6.9.1`, vitest 3 jsdom env (already in repo).
- SendGrid + ALERTS_KV bindings already wired.
