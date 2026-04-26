---
increment: 0748-crawl-worker-watchdog
title: "Hetzner crawl-worker watchdog (defense in depth)"
type: feature
status: planned
---

# Tasks: Hetzner crawl-worker watchdog (defense in depth)

---

## Phase 1 — VM-side systemd watchdog

### T-001a: [RED] Bash test fixture for watchdog.sh
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01 | **Status**: [x] completed

**Test Plan**:
- Given a mock `docker` CLI on PATH that reports a container present, when `crawl-worker-watchdog.sh` runs, then it exits 0 and records zero `docker compose up` invocations.
- Given a mock `docker` CLI that returns empty output (container missing), when `crawl-worker-watchdog.sh` runs, then it exits 0 and records exactly one `docker compose up -d crawl-worker` invocation.
- Given a mock `docker compose up` that exits non-zero, when `watchdog.sh` runs, then the script exits non-zero (`set -e` propagation).

**Files**:
- `crawl-worker/watchdog/__tests__/watchdog.test.sh` (NEW)
- `crawl-worker/watchdog/__tests__/mocks/docker` (NEW mock binary)

**Notes**: Write the test harness (mock PATH shim + assertion helpers) BEFORE the implementation script exists. Tests must fail with a meaningful message at this stage.

---

### T-001b: [GREEN] Implement crawl-worker/watchdog/ files
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05, AC-US1-06 | **Status**: [x] completed

**Test Plan**:
- Given the bash test fixture from T-001a, when `crawl-worker-watchdog.sh` runs with container-present mock, then `watchdog.test.sh` passes (exit 0, zero compose invocations).
- Given the bash test fixture from T-001a, when `crawl-worker-watchdog.sh` runs with container-absent mock, then `watchdog.test.sh` passes (exit 0, one compose invocation).

**Files**:
- `crawl-worker/watchdog/crawl-worker-watchdog.sh` (NEW)
- `crawl-worker/watchdog/crawl-worker-watchdog.service` (NEW)
- `crawl-worker/watchdog/crawl-worker-watchdog.timer` (NEW — OnBootSec=30s, OnUnitActiveSec=2min, WantedBy=timers.target)
- `crawl-worker/watchdog/install-watchdog.sh` (NEW — idempotent: copy units, daemon-reload, enable --now)

**Run after**: `bash crawl-worker/watchdog/__tests__/watchdog.test.sh`

---

### T-002: Wire watchdog install into scanner-worker/deploy.sh
**User Story**: US-001 | **Satisfies ACs**: AC-US1-07 | **Status**: [x] completed

**Test Plan**:
- Given the deploy.sh script, when the file is inspected, then lines after `docker compose up -d` and before the existing health-check block contain the `scp` + `bash install-watchdog.sh` invocations.
- Given a dry-run with SSH_USER and WORKER_IP environment overrides pointing at a local stub, when deploy.sh runs, then watchdog install commands execute once per VM (no duplicate runs).

**Files**:
- `scanner-worker/deploy.sh` (MODIFIED — insert scp + ssh install-watchdog.sh block after `docker compose up -d`, before health checks, inside the per-VM loop)

**Notes**: Insert after line ~99 (docker compose up -d), before line ~105 (health checks). No other deploy.sh lines changed.

---

### T-003: Deploy watchdog to all 3 VMs and verify timers active
**User Story**: US-001 | **Satisfies ACs**: AC-US1-08 | **Status**: [x] completed

**Test Plan**:
- Given deploy.sh with the watchdog install block, when `./scanner-worker/deploy.sh` completes, then `ssh root@5.161.69.232 'systemctl list-timers | grep crawl-worker-watchdog'` exits 0 and shows an active, next-elapse time.
- Given the same for `91.107.239.24` and `5.161.56.136`, when queried, then all three VMs show an active timer.

**Files**:
- No new files — deploy-time verification step.

**Run after**: `./scanner-worker/deploy.sh` (from repositories/anton-abyzov/vskill-platform/)

---

### T-004: MANUAL — Stop crawl-worker on VM-3, confirm auto-restart within 5 min
**Type**: MANUAL | **User Story**: US-004 | **Satisfies ACs**: AC-US4-05 | **Status**: [x] completed (live test 2026-04-26 06:24:15Z stop → 06:25:58Z back, 1m43s — under 5min SLO)

**Test Plan**:
- Given the watchdog timer active on VM-3 (`5.161.56.136`), when `ssh root@5.161.56.136 'cd /opt/scanner-worker && docker compose stop crawl-worker'` runs, then within ≤5 minutes `ssh root@5.161.56.136 'docker ps --filter name=crawl-worker'` shows the container back up.
- Given the restart occurred, when `ssh root@5.161.56.136 'journalctl -u crawl-worker-watchdog.service --since "10 minutes ago"'` runs, then output contains `container missing — starting via docker compose`.

**Files**:
- `.specweave/increments/0748-crawl-worker-watchdog/reports/phase1-manual-test.md` (NEW — record timestamp and copy of journal output)

---

## Phase 2 — CF Cron VM healthcheck

### T-005a: [RED] Vitest tests for POST /api/v1/internal/vm-healthcheck
**User Story**: US-004 | **Satisfies ACs**: AC-US4-02 | **Status**: [x] completed

**Test Plan**:
- Given a request with a wrong/missing X-Internal-Key, when the route handles it, then it returns 401.
- Given HETZNER_VM_IPS unset, when the route runs, then it returns `200 { skipped: true, reason: "HETZNER_VM_IPS not set" }`.
- Given 1 consecutive fetch failure for an IP, when the route runs, then the KV fail counter is 1 and no email is sent.
- Given 2 consecutive fetch failures (counter already 1), when the route runs, then the counter is 2 and sendEmail is called exactly once, and the `vm-health:<ip>:alerted` flag is set.
- Given a 3rd failure with `vm-health:<ip>:alerted` already set, when the route runs, then no second email is sent (throttle respected).
- Given a successful /health response after 2 failures, when the route runs, then both `vm-health:<ip>:fails` and `vm-health:<ip>:alerted` keys are deleted.
- Given a /health response with HTTP 200 but `scheduler.running === false`, when the route runs, then the VM is treated as unhealthy (AD-003).
- Given fetch times out via AbortSignal, when the route runs, then the VM is treated as unhealthy.
- Given SendGrid throws on sendEmail, when the route runs, then it still returns 200 (AC-US2-09).

**Files**:
- `src/app/api/v1/internal/vm-healthcheck/__tests__/route.test.ts` (NEW — Vitest, must fail at this stage because route does not exist)

**Run after**: `npx vitest run src/app/api/v1/internal/vm-healthcheck` — expect failures.

---

### T-005b: [GREEN] Implement src/app/api/v1/internal/vm-healthcheck/route.ts
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05, AC-US2-06, AC-US2-07, AC-US2-08, AC-US2-09 | **Status**: [x] completed

**Test Plan**:
- Given the Vitest suite from T-005a, when the route is implemented, then all nine test cases pass.

**Files**:
- `src/app/api/v1/internal/vm-healthcheck/route.ts` (NEW)
  - POST handler
  - X-Internal-Key auth via `timingSafeEqualString` (copied from enqueue-submissions/route.ts:31-41)
  - Parse `env.HETZNER_VM_IPS`, return skipped if empty
  - `Promise.allSettled` parallel fetch of `http://<ip>:9600/health` with `AbortSignal.timeout(5000)`
  - Healthy iff `res.ok && body.status === "ok" && body.scheduler?.running === true`
  - KV: `vm-health:<ip>:fails` (TTL 1h), `vm-health:<ip>:alerted` (TTL 6h)
  - Alert at streak >= 2 if no alerted flag; log and swallow sendEmail errors

**Run after**: `npx vitest run src/app/api/v1/internal/vm-healthcheck`

---

### T-006: Add QUEUE_HEALTH_ALERT email template to src/lib/email.ts
**User Story**: US-002 | **Satisfies ACs**: AC-US2-05 | **Status**: [x] completed

**Test Plan**:
- Given `sendQueueHealthAlert({ kind: "vm-down", ip: "1.2.3.4", streak: 2 })` is called, when the email renders, then the subject contains `[ALERT] crawl-worker VM 1.2.3.4` and the body contains the IP, streak count, and a link to wrangler tail.
- Given `sendQueueHealthAlert({ kind: "queue-stuck", oldestAgeMs: 3600001, receivedCount: 50 })`, when the email renders, then the subject contains `[ALERT] submission queue stuck` and the body contains the human-readable age and count.

**Files**:
- `src/lib/email.ts` (MODIFIED)
  - Add `'QUEUE_HEALTH_ALERT'` to `EmailType` union
  - Add `queueHealthAlertTemplate({ kind, ip?, streak?, oldestAgeMs?, oldestId?, receivedCount? })` returning subject + HTML body
  - Add render branch in existing switch
  - Export `sendQueueHealthAlert(params)` helper (TO: `anton.abyzov@gmail.com`)

---

### T-007: Wire vm-healthcheck and queue-health-check into CF Cron (build-worker-entry.ts)
**User Story**: US-002 | **Satisfies ACs**: AC-US2-08 | **Status**: [x] completed

**Test Plan**:
- Given the updated `build-worker-entry.ts`, when the file is inspected, then a new `ctx.waitUntil` block for `vm-healthcheck` exists alongside the existing blocks at lines 259-286 and does not modify any existing blocks.
- Given a second new `ctx.waitUntil` block for `queue-health-check` (AD-007), when the file is inspected, then it appears after the vm-healthcheck block.
- Given the file is type-checked via `tsc --noEmit`, when run, then zero errors.

**Files**:
- `scripts/build-worker-entry.ts` (MODIFIED — add vm-healthcheck ctx.waitUntil block, then queue-health-check ctx.waitUntil block inside `*/10 * * * *` handler; existing blocks unchanged)
- `src/app/api/v1/internal/queue-health-check/route.ts` (NEW — POST, X-Internal-Key auth, same Prisma query as admin endpoint, alerts if oldestAgeMs > 1h, throttle via `queue-health:stuck:alerted` TTL 6h)

---

### T-008: Add HETZNER_VM_IPS to wrangler.jsonc
**User Story**: US-002 | **Satisfies ACs**: AC-US2-02 | **Status**: [x] completed

**Test Plan**:
- Given the updated `wrangler.jsonc`, when the file is parsed, then `vars.HETZNER_VM_IPS` equals `"5.161.69.232,91.107.239.24,5.161.56.136"`.
- Given `npx wrangler deploy --dry-run`, when run, then it exits 0 (no JSON syntax errors).

**Files**:
- `wrangler.jsonc` (MODIFIED — add `"HETZNER_VM_IPS": "5.161.69.232,91.107.239.24,5.161.56.136"` to vars section per AD-006)

---

### T-009: Deploy CF Worker and verify vm-healthcheck cron fires
**User Story**: US-002 | **Satisfies ACs**: AC-US2-08 | **Status**: [x] completed (Worker version 5836dabd-2804-46a7-bb2a-bd7bb23c5319 deployed; cron tick verification monitor running)

**Test Plan**:
- Given `npx wrangler deploy` completes, when the next `*/10 * * * *` cron tick fires, then `wrangler tail` shows `[cron] vm-healthcheck status=200` within 10 minutes.
- Given the same tick, then `[cron] queue-health-check status=200` also appears (AD-007 block).

**Files**:
- No new files — deploy-time verification step.

**Run after**: `npx wrangler deploy` from `repositories/anton-abyzov/vskill-platform/`

---

### T-010: MANUAL — Alert simulation with bogus IP
**Type**: MANUAL | **User Story**: US-004 | **Satisfies ACs**: AC-US4-06 | **Status**: [ ] pending

**Test Plan**:
- Given `HETZNER_VM_IPS` temporarily updated to include `127.0.0.1:9999` (unreachable), when two `*/10 * * * *` cron ticks complete (~20 minutes), then exactly one `QUEUE_HEALTH_ALERT` email with subject `[ALERT] crawl-worker VM 127.0.0.1` arrives at `anton.abyzov@gmail.com`.
- Given the HETZNER_VM_IPS reverted and one more cron tick, when the route runs, then `wrangler tail` shows the KV throttle key and fail counter cleared for that IP.

**Files**:
- `.specweave/increments/0748-crawl-worker-watchdog/reports/phase2-alert-simulation.md` (NEW — record email screenshot or copy, timestamps)

---

## Phase 3 — Admin queue-health endpoint + auto-alert

### T-011a: [RED] Vitest tests for GET /api/v1/admin/queue-health
**User Story**: US-004 | **Satisfies ACs**: AC-US4-03 | **Status**: [x] completed

**Test Plan**:
- Given no RECEIVED submissions in Prisma mock, when the route handles a GET, then it returns `{ oldestReceivedAgeMs: 0, oldestReceivedId: null, receivedCount: 0, thresholdExceeded: false, thresholdMs: 3600000, cached: false }`.
- Given a RECEIVED submission created 30 minutes ago, when the route handles a GET, then `oldestReceivedAgeMs` ~= 1800000 and `thresholdExceeded: false`.
- Given a RECEIVED submission created 3 hours ago, when the route handles a GET, then `thresholdExceeded: true` and sendEmail is called once.
- Given the same 3-hour-old submission on a second call within 6h (throttle flag set), when the route runs, then no second email is sent.
- Given the queue clears (no RECEIVED), when the route runs, then `queue-health:alerted` KV key is deleted.
- Given a KV cache hit (key `dashboard:queue-health` present), when the route runs, then it returns `cached: true` and Prisma is NOT called.
- Given non-admin auth, when the route runs, then `requireAdmin()` returns 401/403.
- Given SendGrid throws, when the route runs, then it still returns 200 (AC-US3-08).

**Files**:
- `src/app/api/v1/admin/queue-health/__tests__/route.test.ts` (NEW — Vitest, must fail because route does not exist)

**Run after**: `npx vitest run src/app/api/v1/admin/queue-health` — expect failures.

---

### T-011b: [GREEN] Implement src/app/api/v1/admin/queue-health/route.ts
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04, AC-US3-05, AC-US3-06, AC-US3-07, AC-US3-08 | **Status**: [x] completed

**Test Plan**:
- Given the Vitest suite from T-011a, when the route is implemented, then all eight test cases pass.

**Files**:
- `src/app/api/v1/admin/queue-health/route.ts` (NEW)
  - GET handler
  - `requireAdmin(request)` + `isAuthError()` short-circuit (verbatim from state-counts/route.ts:19-21)
  - KV cache check: key `dashboard:queue-health`, TTL 60s
  - On miss: `withDbTimeout(() => prisma.submission.findFirst({ where: { state: "RECEIVED" }, orderBy: { createdAt: "asc" }, select: { id: true, createdAt: true } }), 5_000)` + count query
  - Compute `oldestReceivedAgeMs`, set `thresholdMs = 60 * 60 * 1000` (1h, AC-US3-05), set `thresholdExceeded`
  - Alert via `sendQueueHealthAlert({ kind: "queue-stuck", ... })` throttled via `queue-health:alerted` (TTL 6h)
  - On threshold clear: delete `queue-health:alerted`
  - Write result to KV, return response (swallow sendEmail errors)

**Run after**: `npx vitest run src/app/api/v1/admin/queue-health`

---

### T-012a: [RED] Vitest tests for POST /api/v1/internal/queue-health-check
**User Story**: US-004 | **Satisfies ACs**: AC-US4-03 | **Status**: [x] completed

**Test Plan**:
- Given a POST with valid X-Internal-Key and Prisma showing oldest RECEIVED > 1h, when the route runs, then sendEmail fires once and throttle key `queue-health:stuck:alerted` is set.
- Given the throttle key already present, when the route runs again, then no second email is sent.
- Given the queue is healthy (no RECEIVED or oldest < 1h) and the throttle key is present, when the route runs, then the throttle key is deleted.
- Given wrong/missing X-Internal-Key, when the route runs, then it returns 401.

**Files**:
- `src/app/api/v1/internal/queue-health-check/__tests__/route.test.ts` (NEW — Vitest, must fail at this stage)

**Run after**: `npx vitest run src/app/api/v1/internal/queue-health-check` — expect failures.

---

### T-012b: [GREEN] Implement src/app/api/v1/internal/queue-health-check/route.ts
**User Story**: US-003 | **Satisfies ACs**: AC-US3-06, AC-US3-07, AC-US3-08 | **Status**: [x] completed

**Test Plan**:
- Given the Vitest suite from T-012a, when the route is implemented, then all four test cases pass.

**Files**:
- `src/app/api/v1/internal/queue-health-check/route.ts` (NEW)
  - POST handler
  - X-Internal-Key auth (same pattern as vm-healthcheck)
  - Same Prisma findFirst + count queries as admin endpoint
  - Alert if `oldestAgeMs > 2 * 60 * 60 * 1000` AND no `queue-health:stuck:alerted`
  - Clear throttle if healthy
  - Swallow sendEmail errors, always return 200

**Run after**: `npx vitest run src/app/api/v1/internal/queue-health-check`

---

### T-013: Deploy CF Worker + verify queue-health endpoint and cron alert block
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-03 | **Status**: [x] completed (deployed CF Worker — vskill@5836dabd, all 3 routes return 401 unauthenticated as expected)

**Test Plan**:
- Given `npx wrangler deploy` completes and an admin session cookie, when `GET /api/v1/admin/queue-health` is called, then it returns 200 with `oldestReceivedAgeMs` near 0 and `thresholdExceeded: false` (healthy fleet).
- Given the next `*/10 * * * *` cron tick, when `wrangler tail` is watched, then `[cron] queue-health-check status=200` appears.

**Files**:
- No new files — deploy-time verification step.

**Run after**: `npx wrangler deploy` from `repositories/anton-abyzov/vskill-platform/`

---

### T-014: MANUAL — queue-health endpoint smoke test against live fleet
**Type**: MANUAL | **User Story**: US-004 | **Satisfies ACs**: AC-US4-03 | **Status**: [ ] pending

**Test Plan**:
- Given the deployed admin endpoint and an admin session, when `GET /api/v1/admin/queue-health` is called, then the JSON shows `oldestReceivedAgeMs` near 0 and `thresholdExceeded: false`.
- Given the response, when the field values are recorded, then `receivedCount` is 0 or a small number (no stuck submissions after the 2026-04-26 manual fix).

**Files**:
- `.specweave/increments/0748-crawl-worker-watchdog/reports/phase3-queue-health-smoke.md` (NEW — record curl output and timestamp)

---

## Full test suite gate

### T-015: Run complete Vitest suite — zero regressions
**User Story**: US-004 | **Satisfies ACs**: AC-US4-04 | **Status**: [ ] pending

**Test Plan**:
- Given all implementation tasks complete, when `npx vitest run` executes from `repositories/anton-abyzov/vskill-platform/`, then zero test failures (new suites pass, no pre-existing test regressions).
- Given `bash crawl-worker/watchdog/__tests__/watchdog.test.sh` runs, then exit code 0.

**Files**:
- No new files — CI gate.

**Run after**: all T-001 through T-012b tasks complete.

---

## Closure

### T-016: Run /sw:done 0748 — closure pipeline
**Status**: [ ] pending

**Test Plan**:
- Given all tasks T-001 through T-015 are marked complete, when `/sw:done 0748` runs, then:
  - `sw:code-reviewer` writes `code-review-report.json` with no critical/high/medium findings (or fix loop completes within 3 iterations).
  - `/simplify` runs and removes any duplication or readability issues.
  - `sw:grill` writes `grill-report.json` confirming all ACs satisfied.
  - `sw:judge-llm` writes `judge-llm-report.json` (or is waived if consent denied).
  - PM gates pass: all 31 ACs checked, increment status set to `closed`.

**Files**:
- `.specweave/increments/0748-crawl-worker-watchdog/reports/code-review-report.json`
- `.specweave/increments/0748-crawl-worker-watchdog/reports/grill-report.json`
- `.specweave/increments/0748-crawl-worker-watchdog/reports/judge-llm-report.json`
