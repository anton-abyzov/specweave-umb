---
increment: 0727-0708-followup-security-and-dos-hardening
title: "0708 Follow-up: Security & DoS Hardening (F-CR2/3/4 + 6 mediums + live E2E)"
type: feature
priority: P1
status: planned
created: 2026-04-25
structure: user-stories
test_mode: TDD
coverage_target: 95
---

# Feature: 0708 Follow-up: Security & DoS Hardening (F-CR2/3/4 + 6 mediums + live E2E)

## Overview

This increment closes 3 HIGH and 6 MEDIUM code-review findings deferred from increment `0708-skill-update-push-pipeline` when it was closed with `--skip-validation`. The deferred findings are catalogued in `0708/reports/code-review-report.json` (F-CR2, F-CR3, F-CR4, F-CR6 through F-CR11) and remain non-blocking for the v1 production deploy of 0708, but must land before public/mainstream traffic hits the SSE and webhook endpoints.

A separate gap surfaced by the e2e-agent during the verify-fix pass is also addressed here: the existing Playwright tests for the skill-update push pipeline stub `/api/v1/skills/stream` with `page.route` rather than exercising a live worker. A new live-wire E2E (against `npx wrangler dev`) closes that observability gap.

Scope is purely hardening — no new product features. All 297 existing tests across `vskill-platform` and `vskill` MUST continue to pass.

## Personas (inherited from 0708)

This increment introduces no new personas. All 4 are inherited from the parent increment:

1. **Studio developer** — consumes SSE update streams via `/api/v1/skills/stream`; affected by US-001 (DoS cap) and US-005 (live E2E).
2. **Skill publisher** — pushes updates to first-party repos via signed GitHub webhooks; affected by US-002 (timing-safe HMAC) and US-003 (atomic anti-replay).
3. **First-party repo maintainer** — operates a repository under webhook anti-replay protection; affected by US-003.
4. **Platform operator** — responsible for Cloudflare Worker availability and security posture; affected by all five user stories.

## User Stories

### US-001: SSE DoS Hardening — Cap Subscription Filter at 500 IDs (P1)
**Project**: vskill-platform
**Source finding**: F-CR2 (HIGH) — `0708/reports/code-review-report.json`

**As a** platform operator
**I want** the SSE endpoint to reject query-string subscription filters that exceed 500 skill IDs
**So that** a malicious or buggy client cannot degrade fan-out across all subscribers and breach NFR-002 / NFR-007 from 0708

**Background**: `src/app/api/v1/skills/stream/route.ts` currently accepts arbitrarily long `?skills=<csv>` filters. A connection with 100k IDs degrades the entire fan-out path. The architect's documented scaling threshold for query-string filtering is 500 IDs; anything larger is supposed to route through the existing `POST /api/v1/skills/stream/subscribe` endpoint. This story enforces that boundary.

**Acceptance Criteria**:
- [x] **AC-US1-01**: SSE endpoint rejects `GET /api/v1/skills/stream?skills=<csv>` requests with more than 500 IDs by returning HTTP 400 with body `{ "code": "subscription_filter_too_large", "maxIds": 500 }`. Verified by Vitest in `__tests__/route.test.ts` for the SSE route.
- [x] **AC-US1-02**: SSE endpoint accepts a request with exactly 500 IDs and returns a normal SSE stream (HTTP 200, `Content-Type: text/event-stream`). Verified by Vitest in the same suite.
- [x] **AC-US1-03**: Inline documentation in the route handler (and the OpenAPI/spec entry if one exists) cites `POST /api/v1/skills/stream/subscribe` as the path for filters > 500 IDs. Behavior of the POST endpoint is unchanged.

---

### US-002: Timing-Safe HMAC Comparison Across All Auth Paths (P1)
**Project**: vskill-platform
**Source finding**: F-CR3 (HIGH) — `0708/reports/code-review-report.json`

**As a** platform operator
**I want** every HMAC digest comparison in the codebase to be constant-time
**So that** an attacker cannot mount a timing side-channel attack to recover or guess HMAC signatures, and so the implementation matches the contract documented in 0708 spec AC-US3-03

**Background**: `src/lib/internal-auth.ts` currently uses `===` to compare HMAC digests. Spec AC-US3-03 of 0708 explicitly mandates timing-safe comparison via `crypto.timingSafeEqual`. The fix must also audit `webhook-auth.ts` and any other file that compares HMACs.

**Acceptance Criteria**:
- [x] **AC-US2-01**: `src/lib/internal-auth.ts` compares HMAC digests using `crypto.timingSafeEqual` over equal-length `Uint8Array` (or `Buffer`) operands. The `===` operator is no longer used for digest comparison anywhere in this file. Verified by structural test that asserts `crypto.timingSafeEqual` is invoked and behavioral test that valid signatures pass and invalid signatures (including length-mismatched) reject.
- [x] **AC-US2-02**: `src/lib/webhook-auth.ts` and every other file in `src/lib/**` and `src/app/api/**` performing HMAC comparison is audited and either already timing-safe or hardened identically in this increment. The audit is recorded as a checklist in `tasks.md`.
- [x] **AC-US2-03**: A unit test for each hardened path asserts (a) `crypto.timingSafeEqual` is invoked on the digest compare hot path, and (b) an unequal-length input returns `false` early without throwing.

---

### US-003: Atomic Webhook Anti-Replay via Durable Object State (P1)
**Project**: vskill-platform
**Source finding**: F-CR4 (HIGH) — `0708/reports/code-review-report.json`
**Decision**: Atomic anti-replay primitive = **(a) Durable Object state with conditional put** (selected during interview; rationale: matches existing UpdateHub / OutboxReconcilerDO patterns; D1 is not currently used in `vskill-platform`; option (b) would introduce net-new infrastructure for a hardening-only increment).

**As a** first-party repo maintainer
**I want** the webhook anti-replay check to be atomic (single-shot put-if-absent)
**So that** two concurrent deliveries of the same `X-GitHub-Delivery` cannot both pass the dedupe check and double-enqueue scans

**Background**: `src/app/api/v1/webhooks/github/route.ts:103-110` currently performs a non-atomic GET-then-PUT to record the delivery-ID nonce. Two concurrent webhook deliveries with the same delivery ID can both observe GET-not-found before either's PUT completes, both passing the dedupe check. Downstream scan-lock mitigates the user-visible damage, but the layer remains incorrect. The fix is to replace the GET-then-PUT pair with a Durable Object `state.storage.put`-with-conditional-check pattern (or equivalent atomic primitive in the existing DO infrastructure).

**Acceptance Criteria**:
- [ ] **AC-US3-01**: Webhook anti-replay in `src/app/api/v1/webhooks/github/route.ts` uses Durable Object state with conditional put-if-absent semantics. The non-atomic GET-then-PUT sequence is removed. Implementation reuses an existing DO (UpdateHub, OutboxReconcilerDO) or adds a small purpose-built `WebhookNonceDO`, whichever the architect's plan.md designates.
- [ ] **AC-US3-02**: Concurrency test: 100 concurrent calls to the webhook handler with the same `X-GitHub-Delivery` header result in **exactly one** `enqueueScanHigh` invocation and **99 dedup-hit** responses. No race window exists between the check and the write. Verified by Vitest using `Promise.all` with mocked DO state.
- [ ] **AC-US3-03**: TTL behavior is preserved at 300 seconds. After TTL expiry, a re-delivery of the same `X-GitHub-Delivery` is accepted (replay-after-TTL still permitted, matching current behavior). Verified by a Vitest test using fake timers.

---

### US-004: Six Medium-Severity Quality Fixes (P2)
**Project**: vskill-platform
**Source findings**: F-CR6, F-CR7, F-CR8, F-CR9, F-CR10, F-CR11 (all MEDIUM) — `0708/reports/code-review-report.json`

**As a** platform operator
**I want** the six MEDIUM-severity quality and observability findings deferred from 0708 to be cleared
**So that** the codebase is consistent, regressions in scanner / outbox / publish paths are detected by tests, and operators have correlation IDs in logs and metrics

**Background**: None of these warrants its own user story; they are grouped here for atomic delivery. Each AC corresponds to one specific finding in `0708/reports/code-review-report.json`.

**Acceptance Criteria**:
- [ ] **AC-US4-01** (F-CR6): Add a regression test for the scanner's deterministic placeholder `contentHash` format. The test asserts unresolved skills produce `sha256:pending:<sha12>` (a deterministic 12-char prefix) and will be replaced by a real content hash once 0680's SKILL.md reader lands. Test lives in `src/lib/skill-update/__tests__/scanner.test.ts`.
- [ ] **AC-US4-02** (F-CR7): Remove the two `any` casts in `src/lib/skill-update/__tests__/queue-consumer.test.ts`. Replace with proper Vitest typing using `vi.hoisted()` and the appropriate `Mock<>` generic. `tsc --noEmit` passes with no `@ts-expect-error`.
- [ ] **AC-US4-03** (F-CR8): The outbox reconciler logs and AE metric tags include `UpdateEvent.id` for correlation between failed dispatches and downstream traces. Verified by a unit test asserting `logger.error` is called with an object containing `updateEventId` and `metric.tag` includes `update_event_id:<id>`.
- [ ] **AC-US4-04** (F-CR9): The broad `try/catch` around fingerprint computation in `src/lib/submission/publish.ts` is narrowed to the specific error class (likely `RangeError` or `TypeError`). Other error types propagate. Unit test asserts a synthetic `Error` (non-targeted) is *not* swallowed by the narrowed catch.
- [ ] **AC-US4-05** (F-CR10): The `as never` Prisma type cast in `src/lib/skill-update/__tests__/outbox-writer.test.ts` is replaced with proper Prisma type narrowing (`Prisma.InputJsonValue` or the field-specific generated type). `tsc --noEmit` passes with strict mode.
- [ ] **AC-US4-06** (F-CR11): On Worker cold start, `scripts/build-worker-entry.ts` (or the entry it generates) emits `[cron] handler attached` to the log stream so operators can verify cron registration in production. Verified by a smoke test that the generated entry includes the log line and by a manual `wrangler tail` runbook step in `tasks.md`.

---

### US-005: Live-Wire E2E Spec for Skill-Update Pipeline (P2)
**Project**: vskill-platform (test spec lives in shared E2E surface; can be physically located in either `vskill-platform/__tests__/e2e/` or `vskill/e2e/` per architect's plan.md)
**Source flag**: e2e-agent during 0708 verify-fix pass

**As a** platform operator
**I want** at least one Playwright E2E that exercises the full skill-update push pipeline end-to-end against a live `wrangler dev` instance — no `page.route` stubs
**So that** regressions in the integration seam (signed webhook → DB write → DO broadcast → EventSource → Studio UI) are caught before reaching production

**Background**: All current Playwright tests touching `/api/v1/skills/stream` use `page.route` to inject canned events. This means the integration seam between the API route, the DO broadcast pump, and the client EventSource is never exercised under test. Any regression there ships unnoticed.

**Acceptance Criteria**:
- [ ] **AC-US5-01**: A new Playwright spec exists at the path designated in plan.md (`repositories/anton-abyzov/vskill/e2e/skill-update-pipeline-live.spec.ts` or `repositories/anton-abyzov/vskill-platform/__tests__/e2e/skill-update-live.spec.ts`). The spec runs against a local `npx wrangler dev` instance and contains zero `page.route(...)` calls for the skill-update endpoints.
- [ ] **AC-US5-02**: Test flow exercises the entire wire path: (1) POST a signed `skill.updated` webhook to the local Worker; (2) wait for matching `SkillVersion` and `UpdateEvent` rows in the DB via direct Prisma read; (3) assert the Studio page's EventSource receives a `skill.updated` server-sent event within 2 seconds; (4) assert the UpdateBell badge increments in the rendered DOM.
- [ ] **AC-US5-03**: The spec is tagged `@live` and gated out of the default test run. Operators run it on demand with `npx playwright test --grep @live`. CI integration is optional and tracked as a follow-up if needed; a runbook entry in `tasks.md` documents how to start `wrangler dev` and execute the live tests.

## Functional Requirements

### FR-001: SSE subscription filter cap is enforced server-side
The SSE endpoint MUST reject filters exceeding 500 IDs at the route handler level before any DO or DB call. Cap value `500` is fixed (architect's documented scaling threshold; matches the boundary at which 0708's plan routes traffic through `POST /subscribe`).

### FR-002: All HMAC digest comparisons are constant-time
Every HMAC digest comparison in `src/lib/**` and `src/app/api/**` MUST use `crypto.timingSafeEqual` over equal-length operands. Direct `===` / `==` comparison of HMAC digests is forbidden by codebase convention going forward.

### FR-003: Webhook anti-replay is atomic
The webhook anti-replay check MUST be atomic (put-if-absent semantics) implemented via Durable Object state. The existing 300-second TTL is preserved.

### FR-004: Quality and observability fixes are persisted
The six MEDIUM findings (F-CR6 through F-CR11) are cleared with regression tests where applicable so they cannot silently regress in future increments.

### FR-005: A live-wire E2E spec exists and is opt-in
A `@live`-tagged Playwright spec exercises the full skill-update push pipeline end-to-end against a local `wrangler dev` instance.

## Non-Functional Requirements

### NFR-NR-01: No test regression
All 297 existing tests across `vskill-platform` and `vskill` MUST continue to pass after these changes. Verification:

```bash
cd repositories/anton-abyzov/vskill-platform && npx vitest run && npx tsc --noEmit
cd repositories/anton-abyzov/vskill && npx vitest run && npx playwright test
```

Both repos must remain green at HEAD of this increment's branch.

### NFR-NR-02: SSE endpoint p99 latency unchanged
The cap check is O(1) on `csv.split(',').length`. Observed SSE accept-path p99 latency MUST not regress. Spot-checked via local benchmark before and after; documented as a checklist item under US-001's tasks.

### NFR-NR-03: Webhook P50 latency unchanged
The atomic primitive (DO conditional put) MUST match or beat the current GET-then-PUT in observed P50 latency. If P50 regresses by more than 5%, the implementation reverts to the current pattern guarded by an external lock (architect's call). Documented as a checklist item under US-003's tasks.

### NFR-NR-04: HMAC comparison is constant-time regardless of payload length
Verified structurally (assertion that `crypto.timingSafeEqual` is on the hot path) rather than by timing measurement, because timing measurements in CI runners are noisy.

### NFR-NR-05: Anti-replay state is strongly consistent (atomic)
Guaranteed by Durable Object semantics (single-writer per object key).

## Success Criteria

- All 18 acceptance criteria across the 5 user stories pass
- All 297 pre-existing tests in `vskill-platform` and `vskill` remain green
- `tsc --noEmit` passes in `vskill-platform` with no new `@ts-expect-error` or `as never` casts
- `code-review-report.json` for this increment shows zero remaining findings traceable to F-CR2, F-CR3, F-CR4, F-CR6, F-CR7, F-CR8, F-CR9, F-CR10, or F-CR11
- The live-wire E2E spec passes locally against `npx wrangler dev`
- Production deploy of 0708 is unblocked by this increment (this increment is non-blocking but cleanup-completing)

## Out of Scope

The following are explicitly NOT addressed in this increment:

- **Any new functional features for the skill-update push pipeline** — 0708 is closed. Net-new behavior belongs in a separate increment.
- **Production schema migration** — the `vskill-platform` operator's manual Prisma migrate-deploy step. Runbook lives in `0708/reports/`. Out of scope here.
- **Re-implementing or redesigning anything from 0708** — only the identified 9 findings + 1 e2e gap are touched.
- **0712 follow-ups** — increment `0712-0708-followups-scanner-outbox-do-alarm-and-e2e` owns those (DO alarm timer, outbox reconciler enhancements, additional E2E coverage). No overlap.
- **D1 unique-constraint anti-replay** — option (b) from interview was rejected. D1 is not currently used in `vskill-platform` and would constitute net-new infrastructure for a hardening-only increment.
- **Adding the live-wire E2E to CI default runs** — the `@live` tag keeps it opt-in. CI integration is a follow-up if/when desired.
- **Updating client-side code to enforce the 500-ID cap before sending** — server-side enforcement is the contract. Client-side hardening is a separate UX concern.

## Dependencies

### Upstream
- **Increment 0708 (`0708-skill-update-push-pipeline`)**: closed. This increment exists because 0708 was closed with `--skip-validation` deferring the 9 findings catalogued at `.specweave/increments/0708-skill-update-push-pipeline/reports/code-review-report.json`. All file paths, schemas, and contracts referenced here are defined by 0708's spec, plan, and code.
- **Increment 0680 (SKILL.md reader)** — informational only. AC-US4-01's regression test asserts the `sha256:pending:<sha12>` placeholder format, which 0680 will eventually replace with a real content hash. No work in 0680 is required for this increment to land.

### Sibling (no overlap, do not coordinate)
- **Increment 0712 (`0712-0708-followups-scanner-outbox-do-alarm-and-e2e`)**: owns separate 0708 follow-ups (DO alarm timer, additional outbox enhancements, broader E2E coverage). This increment (0727) is scoped to the 9 specific findings + the 1 e2e-gap above and does not touch 0712's deliverables.

### Cross-references in 0708 review report
This spec references the following finding IDs verbatim from `.specweave/increments/0708-skill-update-push-pipeline/reports/code-review-report.json`:
- **F-CR2** (HIGH) → US-001
- **F-CR3** (HIGH) → US-002
- **F-CR4** (HIGH) → US-003
- **F-CR6** (MEDIUM) → AC-US4-01
- **F-CR7** (MEDIUM) → AC-US4-02
- **F-CR8** (MEDIUM) → AC-US4-03
- **F-CR9** (MEDIUM) → AC-US4-04
- **F-CR10** (MEDIUM) → AC-US4-05
- **F-CR11** (MEDIUM) → AC-US4-06

## Critical Files (no new modules expected — pure edits)

**vskill-platform**:
- `src/app/api/v1/skills/stream/route.ts` — US-001 cap
- `src/lib/internal-auth.ts` — US-002 timing-safe
- `src/lib/webhook-auth.ts` — US-002 audit
- `src/app/api/v1/webhooks/github/route.ts` — US-003 atomic
- `src/lib/skill-update/scanner.ts` — US-004 (F-CR6)
- `src/lib/skill-update/outbox-reconciler.ts` — US-004 (F-CR8)
- `src/lib/submission/publish.ts` — US-004 (F-CR9)
- `src/lib/skill-update/__tests__/scanner.test.ts` — US-004 (F-CR6)
- `src/lib/skill-update/__tests__/queue-consumer.test.ts` — US-004 (F-CR7)
- `src/lib/skill-update/__tests__/outbox-writer.test.ts` — US-004 (F-CR10)
- `scripts/build-worker-entry.ts` — US-004 (F-CR11)
- `__tests__/route.test.ts` files for US-001, US-002, US-003 ACs
- New (US-003): `src/lib/durable-objects/webhook-nonce-do.ts` *or* extension to an existing DO (architect's call in plan.md)

**vskill** (only if E2E lives here — architect's call):
- New: `e2e/skill-update-pipeline-live.spec.ts`
- Possibly modified: `playwright.config.ts` (for `@live` tag config)

## Test Strategy

- **TDD strict mode** for every AC. Red → Green → Refactor per `/sw:tdd-cycle`.
- **Structural test** for HMAC timing-safety: assert `crypto.timingSafeEqual` is invoked on the hot path; reject `===` for digest compare in the codebase via lint or grep gate (architect to decide).
- **Concurrency test** for webhook anti-replay: parallel duplicate-event delivery test (`Promise.all` of 100 deliveries with same `X-GitHub-Delivery`).
- **Live-wire E2E** tagged `@live`, opt-in only (`npx playwright test --grep @live`). Default CI runs are unaffected.
- Coverage targets: unit 95%, integration 90%, e2e 100% of AC scenarios.

## Verification Plan (per US)

1. **US-001**: Vitest covers the 501-IDs → 400 and 500-IDs → 200 cases. Manual: `curl 'http://localhost:3000/api/v1/skills/stream?skills=$(seq 1 501 | paste -sd, -)'` returns 400 with the documented body.
2. **US-002**: Vitest verifies `crypto.timingSafeEqual` is invoked on each hardened path; structural assertion that `===` is no longer used for digest compare; integration test confirms HMAC verify still passes valid signatures and rejects invalid (and length-mismatched) signatures.
3. **US-003**: Vitest concurrency test (`Promise.all` of 100 webhook deliveries with same `X-GitHub-Delivery`) → assert exactly one `enqueueScanHigh` mock call. Fake-timer test for TTL expiry behavior.
4. **US-004**: Each fix has a targeted unit test or assertion; no broader behavior change introduced.
5. **US-005**: `npx playwright test --grep @live` in `vskill` (or wherever the spec lands) passes against a locally-running `wrangler dev`. Runbook in `tasks.md` documents the boot sequence.

**Full sweep at end of increment**:
```bash
cd repositories/anton-abyzov/vskill-platform && npx vitest run && npx tsc --noEmit
cd repositories/anton-abyzov/vskill && npx vitest run && npx playwright test
```
Both must remain green.

## Coordination & Sequencing

- 0708 is closed; this increment is purely additive and non-blocking.
- The production deploy of 0708 may proceed independently — these fixes do NOT block the cron re-enable, the migrate-deploy step, or the worker rollout.
- Recommended order if both happen this week: ship 0708 production deploy first (validates the cron + outbox in the wild), then merge this hardening pass after observing one clean cycle of `[cron] skill-update scan completed`.

## Estimated Complexity

| Story | Tasks | Complexity |
|---|---|---|
| US-001 | 2 (red/green) | Low |
| US-002 | 4 (audit + 2 fixes + tests) | Low |
| US-003 | 4 (red/green for atomic + concurrency test + TTL test) | Medium (atomic primitive choice) |
| US-004 | 12 (6 fixes × red/green) | Low |
| US-005 | 4 (new E2E spec + CI config + runbook) | Medium (live wrangler dev integration) |

Total: ~26 tasks, mostly Low complexity. Fits cleanly in `/sw:auto` or single-domain `/sw:do` execution. No multi-agent team required.

## Recommended Execution Path

After increment creation: `/sw:do 0727` (single-engineer focused work, ~half-day) or `/sw:auto 0727` (autonomous loop). Skip `sw:team-lead` — domain footprint is uniform (vskill-platform, mostly `src/lib` + `src/app/api`), no contracts to negotiate, no Phase 1/2 split needed.
