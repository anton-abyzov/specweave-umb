---
increment: 0713B-production-rollout
title: "Queue Pipeline Restoration (P0) — Production Rollout"
type: ops
priority: P0
status: backlog
created: 2026-04-25
parent: 0713-queue-pipeline-restoration
structure: user-stories
test_mode: manual
coverage_target: 0
---

# Feature: Queue Pipeline Restoration — Production Rollout

## Overview

Operator-only execution split out from 0713-queue-pipeline-restoration. The code, unit tests, integration tests, and Playwright e2e tests for all four user stories shipped in 0713 (commits up to `bf2af0df`). What remains is **production execution**: deploying to Cloudflare, draining stuck rows from the production database, backfilling state-history against production, and post-deploy smoke verifications.

These tasks were split out because they require Anton's hands on the production console (`wrangler tail`, production DB access, `wrangler deploy`). Agents do not have credentials and must not auto-execute them. The 0713 increment is closed at "implementation complete; production execution deferred to 0713B."

## Context (carried from 0713)

verified-skill.com submission pipeline has stacked bugs:
- Frozen stats cron (CTE timeout)
- List endpoint masking DB failures as empty
- Malformed state-history writes
- Queue page silently auto-flipping filters

Phase 1 fixes (US-001, US-002, US-004) and Phase 2 fixes (US-003, US-005) are merged on `main` with green tests. Production verification is what closes the loop.

## User Stories

### US-101: Phase 1 deploy + production verification (P0)
**Project**: vskill-platform

**As a** platform operator
**I want** the Phase 1 stats/list/drain code shipped to production and verified live
**So that** the P0 outage is actually resolved for end users (not just on `main`)

**Acceptance Criteria**:
- [ ] **AC-US101-01**: `cd repositories/anton-abyzov/vskill-platform && npm run build && npx wrangler deploy` completes without error against the production worker.
- [ ] **AC-US101-02**: Within 11 minutes of deploy, `GET /api/v1/submissions/stats` returns `generatedAt` < 11 min old AND `degraded:false`. (Carries former AC-US1-06.)
- [ ] **AC-US101-03**: `curl -s 'https://verified-skill.com/api/v1/submissions?state=all&sort=createdAt&sortDir=desc&limit=10' | jq '.items | length'` returns ≥ 10. (Carries former AC-US2-05.)
- [ ] **AC-US101-04**: `wrangler tail` shows the stats cron firing on its 10-min schedule with no errors for at least three consecutive ticks.

### US-102: Drain stuck hyperframes rows in production (P0)
**Project**: vskill-platform

**As a** platform operator
**I want** the 6 stuck hyperframes RECEIVED rows drained
**So that** the originally-reported user submission completes the pipeline

**Acceptance Criteria**:
- [ ] **AC-US102-01**: `node scripts/drain-stuck-received.ts --repo-url https://github.com/heygen-com/hyperframes --age-min 5 --dry-run` lists exactly the 6 expected IDs (`sub_4ce1d8a7…`, `sub_e64164f1…`, `sub_1ce97022…`, `sub_79d9e244…`, `sub_b8642378…`, `sub_4a5b43de…`).
- [ ] **AC-US102-02**: Running without `--dry-run` re-enqueues all 6 and within 60 seconds they transition out of RECEIVED. (Carries former AC-US4-02.)

### US-103: Backfill state-history in production (P1)
**Project**: vskill-platform

**As a** platform operator
**I want** the malformed `? -> ?` state-history entries replaced with reconstructed `{from, to, reason}` shape
**So that** debuggers can reconstruct lifecycle from history alone for the affected rows

**Acceptance Criteria**:
- [ ] **AC-US103-01**: `node scripts/backfill-state-history.ts --dry-run` reports the count of malformed rows without writing.
- [ ] **AC-US103-02**: Running without `--dry-run` rewrites malformed entries; `curl /api/v1/submissions/<id> | jq '.submission.stateHistory'` for the 6 hyperframes IDs shows real `from -> to` transitions, not `? -> ?`. (Carries former AC-US3-04.)

### US-104: Phase 2 deploy + UX verification (P1)
**Project**: vskill-platform

**As a** queue page visitor
**I want** the Phase 2 UI (degraded ribbon, per-tab default sort, single time column, no auto-flip) shipped to production
**So that** I see honest counters and don't get silently redirected to `?filter=published`

**Acceptance Criteria**:
- [ ] **AC-US104-01**: `cd repositories/anton-abyzov/vskill-platform && npx wrangler deploy` completes (Phase 2 may piggyback on Phase 1 deploy if shipping together).
- [ ] **AC-US104-02**: After deploy, visiting `https://verified-skill.com/queue` (no filter) does NOT redirect to `?filter=published`. URL remains `/queue`. (Carries former AC-US5-06.)
- [ ] **AC-US104-03**: After deploy, visiting `https://verified-skill.com/queue?filter=all` renders rows sorted by `createdAt` desc (most recent first). (Carries former AC-US5-07.)

## Out of Scope

- Code changes (everything is in 0713; no new code expected here).
- Spec changes (the contracts are settled).
- Adding new tests (the test suite is in 0713 and stays green on `main`).

## Dependencies

- 0713-queue-pipeline-restoration must be merged on `main` (it is — see commit `bf2af0df`).
- Production credentials for `wrangler deploy`, production DB access, production KV access.
- 24h post-deploy monitoring per 0713 rubric "Operational verification" section.

## Notes for the operator

- Phase 1 deploy comes first; verify AC-US101-02 + AC-US101-03 before Phase 2 deploy.
- After Phase 1 verifies green, run the drain script (US-102), then the backfill (US-103).
- Phase 2 deploy ships the UX. Smoke-test against `/queue` and `/queue?filter=all`.
- If any verification fails, do NOT close this increment — open a follow-up hotfix.
