# Tasks: Queue Observability Alerts

## Task Notation

- `[T###]`: Task ID
- `[ ]` not started · `[x]` completed
- Each task lists ACs satisfied + a BDD test scenario.

## Phase 1: Foundation

### T-001: Create alert types module
**AC**: AC-US3-01
**File**: `src/lib/alerts/types.ts`
**Description**: Define `AlertKind`, `Severity`, `Alert`, `AlertEnv` interfaces.
**Test**: Given a TS file imports types → When we type-check → Then no errors.
**Status**: [x] completed

### T-002: Create dedup module + tests
**AC**: AC-US3-02, AC-US3-03, AC-US3-06
**Files**: `src/lib/alerts/dedup.ts`, `src/lib/alerts/__tests__/dedup.test.ts`
**Test plan**:
- TC-001 — Given fresh KV, When `shouldFire(critical, "x")` is called, Then it returns true.
- TC-002 — Given `recordFired(critical, "x")` was just called, When `shouldFire(critical, "x")` is called, Then it returns false (dedup hit).
- TC-003 — Given a critical record, When we read its TTL, Then it equals 3600.
- TC-004 — Given a warning record, When we read its TTL, Then it equals 21600.
- TC-005 — Given the recent ring buffer has 100 entries, When we record a 101st alert, Then the oldest entry is evicted.
- TC-006 — Given a recorded alert, When `clearDedup` runs, Then `shouldFire` returns true again.
**Status**: [x] completed

## Phase 2: Detectors (TDD per detector)

### T-003: Implement detectDrainStalled + tests
**AC**: AC-US2-01
**File**: `src/lib/alerts/detectors.ts`, `src/lib/alerts/__tests__/detectors.test.ts`
**Test plan**:
- TC-007 — Given drainRate.last1h=0 + oldestActive exists, When detector runs, Then returns 1 alert kind=drain-stalled.
- TC-008 — Given drainRate.last1h=5, When detector runs, Then returns [].
- TC-009 — Given drainRate.last1h=0 but no oldestActive, When detector runs, Then returns [] (queue is empty, not stalled).
**Status**: [x] completed

### T-004: Implement detectHeartbeatStale + tests
**AC**: AC-US2-02
**Test plan**:
- TC-010 — Given vmHeartbeat.ageMs=900_000 (15min) + threshold 600_000, When detector runs, Then returns 1 alert kind=heartbeat-stale.
- TC-011 — Given vmHeartbeat.ageMs=300_000, When detector runs, Then returns [].
**Status**: [x] completed

### T-005: Implement detectOrphanGrowing + tests
**AC**: AC-US2-03
**Test plan**:
- TC-012 — Given no baseline in KV, When detector runs with count=200, Then writes baseline and returns [].
- TC-013 — Given baseline=100, When detector runs with count=160 (delta 60), Then returns 1 alert and updates baseline.
- TC-014 — Given baseline=100, When detector runs with count=120 (delta 20 < 50), Then returns [].
- TC-015 — Given baseline=100, When detector runs with count=80 (decreased), Then returns [] and updates baseline.
**Status**: [x] completed

### T-006: Implement detectLlmFallbackSpike + tests
**AC**: AC-US2-04
**Test plan**:
- TC-016 — Given fallback counts {claude: 12, ollama: 10} + threshold 20, When detector runs, Then returns 1 alert kind=llm-fallback-spike.
- TC-017 — Given fallback counts {claude: 5, ollama: 5} + threshold 20, When detector runs, Then returns [].
**Status**: [x] completed

### T-007: Implement detectSubmissionMaxRetries + tests
**AC**: AC-US2-05
**Test plan**:
- TC-018 — Given 2 submissions with processingAttempts >=3, When detector runs, Then returns 2 alerts (one per submission).
- TC-019 — Given submissions with attempts <3, When detector runs, Then returns [].
- TC-020 — Given a submission in PUBLISHED state with attempts >=3, When detector runs, Then returns [] (terminal state).
**Status**: [x] completed

### T-008: Implement runAllDetectors orchestrator + tests
**AC**: AC-US2-06
**Test plan**:
- TC-021 — Given multiple detectors return alerts, When orchestrator runs, Then merged list returned.
- TC-022 — Given one detector throws, When orchestrator runs, Then other detectors still execute and their alerts are returned.
**Status**: [x] completed

## Phase 3: Email + recipients

### T-009: Replace OPS_ALERT_TO with getAlertRecipients() + tests
**AC**: AC-US1-01, AC-US1-02, AC-US1-03
**Files**: `src/lib/email.ts`, `src/lib/__tests__/email.alerts.test.ts`
**Test plan**:
- TC-023 — Given ALERT_RECIPIENTS unset, When getAlertRecipients() runs, Then returns ['admin@easychamp.com'].
- TC-024 — Given ALERT_RECIPIENTS="a@x.com,b@y.com", Then returns ['a@x.com','b@y.com'].
- TC-025 — Given ALERT_RECIPIENTS=" a@x.com ,, a@x.com ", Then returns ['a@x.com'] (trimmed + deduped).
- TC-026 — Given ALERT_RECIPIENTS="", Then returns ['admin@easychamp.com'] (empty string falls back to default).
**Status**: [x] completed

### T-010: Extend QueueHealthAlertParams + sendQueueHealthAlert HTML branches
**AC**: AC-US2-01..05, AC-US3-01
**Test plan**:
- TC-027 — Given a `drain-stalled` alert payload, When sendQueueHealthAlert runs (dry-run env), Then HTML body contains "Queue drain stalled".
- TC-028..030 — same for `heartbeat-stale`, `orphan-growing`, `submission-max-retries`, `llm-fallback-spike`.
**Status**: [x] completed

### T-011: Implement sendAlertDigest + tests
**AC**: AC-US3-05
**Test plan**:
- TC-031 — Given digest with zero events, When sendAlertDigest runs, Then no email sent (returns {sent:false}).
- TC-032 — Given digest with events, Then HTML contains counts table and sample list.
**Status**: [x] completed

## Phase 4: API routes

### T-012: Internal alerts-evaluator route + tests
**AC**: AC-US2-06, AC-US3-02, AC-US3-04
**Files**: `src/app/api/v1/internal/alerts-evaluator/route.ts` + `__tests__/route.test.ts`
**Test plan**:
- TC-033 — Given missing cron-auth header, When POST runs, Then 403.
- TC-034 — Given valid cron-auth, When detector returns 1 critical alert (no dedup), Then SendGrid called once + dedup recorded.
- TC-035 — Given dedup KV has matching key, When POST runs, Then SendGrid NOT called (suppressed).
- TC-036 — Given alerts:debug:fire-once KV key exists, When POST runs, Then synthetic heartbeat-stale alert fired AND key deleted.
- TC-037 — Given an info-severity alert, When POST runs, Then NO email sent (digest only) but counter incremented.
**Status**: [x] completed

### T-013: Internal alerts-digest route + tests
**AC**: AC-US3-05
**Test plan**:
- TC-038 — Given current window already fired (digest:fired:<window> key exists), When POST runs, Then no-op response.
- TC-039 — Given new window + non-empty events, Then sendAlertDigest invoked + window dedup recorded.
**Status**: [x] completed

### T-014: Admin recent alerts GET + tests
**AC**: AC-US4-01
**Files**: `src/app/api/v1/admin/alerts/recent/route.ts` + `__tests__/route.test.ts`
**Test plan**:
- TC-040 — Given non-admin caller, When GET runs, Then 401/403.
- TC-041 — Given admin caller + 3 alerts in ring buffer, Then returns those 3 sorted desc.
**Status**: [x] completed

### T-015: Admin ack POST + tests
**AC**: AC-US4-02
**Files**: `src/app/api/v1/admin/alerts/[id]/ack/route.ts` + `__tests__/route.test.ts`
**Test plan**:
- TC-042 — Given admin POST with valid alert id, When runs, Then alert marked acknowledged in ring buffer + dedup KV cleared.
- TC-043 — Given non-existent id, Then 404.
**Status**: [x] completed

## Phase 5: UI + cron + deploy

### T-016: RecentAlertsPanel component
**AC**: AC-US4-03
**File**: `src/app/admin/queue/RecentAlertsPanel.tsx`
**Test**: Renders list of alerts grouped by severity; Acknowledge button calls API.
**Status**: [x] completed

### T-017: Wire into /admin/queue page
**AC**: AC-US4-03
**File**: `src/app/admin/queue/page.tsx`
**Test**: Page imports + renders panel above existing tabs.
**Status**: [x] completed

### T-018: Cron cohort dispatcher wiring
**AC**: AC-US2-06
**File**: `src/lib/cron/cohort-dispatch.ts`, `wrangler.jsonc`
**Test**: Light cohort handler fires alerts-evaluator; heavy cohort fires alerts-digest.
**Status**: [x] completed

### T-019: ALERTS_KV namespace registered in wrangler.jsonc
**AC**: AC-US3-06
**Test**: wrangler.jsonc has new kv_namespaces entry; binding accessible from Worker env.
**Status**: [x] completed

### T-020: Playwright e2e admin-alerts.spec.ts
**AC**: AC-US4-04
**File**: `tests/e2e/admin-alerts.spec.ts`
**Test plan**:
- TC-044 — Given admin signed in + seeded alert in ring buffer, When navigating to /admin/queue, Then RecentAlertsPanel shows the alert.
- TC-045 — Given the seeded alert, When clicking Acknowledge, Then alert moves to "Acknowledged" section after reload.
**Status**: [x] completed

## Phase 6: Verification + deploy

### T-021: Run vitest, fix failures
**Status**: [x] completed

### T-022: Build + deploy
**Cmd**: `npm run build && npm run build:worker && npm run deploy`
**Status**: [ ] not started

### T-023: Production smoke (synthetic fire)
**Action**: write `alerts:debug:fire-once` KV key, then `curl POST /api/v1/internal/alerts-evaluator` and confirm email at admin@easychamp.com.
**Status**: [ ] not started

### T-024: Commit + push
**Status**: [ ] not started
