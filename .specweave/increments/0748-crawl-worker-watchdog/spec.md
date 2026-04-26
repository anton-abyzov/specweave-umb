---
increment: 0748-crawl-worker-watchdog
title: "Hetzner crawl-worker watchdog (defense in depth)"
type: feature
priority: P1
status: planned
created: 2026-04-26
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Hetzner crawl-worker watchdog (defense in depth)

## Overview

On 2026-03-09 a half-finished `scanner-worker/deploy.sh` aborted while VM-2 (`91.107.239.24`) port 9500 was held by a legacy bare `node server.js`. As a side effect, the `crawl-worker` containers stopped on **all three** Hetzner VMs (`5.161.69.232`, `91.107.239.24`, `5.161.56.136`) and stayed stopped. Docker's `restart: unless-stopped` does not recover from a manual stop, none of the VMs rebooted, and **no alert ever fired**. The submission queue silently piled up `RECEIVED` items for **6+ weeks** until 162 stuck submissions were noticed on 2026-04-26. Operator (Anton) restarted them by hand with `docker compose up -d crawl-worker` per VM.

This increment makes that failure mode impossible to miss again. Three independent layers, each catching a different failure mode, each cheap to build and reusing existing infrastructure (no new services, no new credentials beyond a comma-separated VM-IP list):

| Layer | Catches | Misses |
|---|---|---|
| 1 — VM-side systemd timer (every 2 min) | Container stopped (manual or crash) — restarts within 2 min | Host offline, network partition |
| 2 — CF Cron VM healthcheck (every 10 min) | Host offline, systemd broken, container running but `/health` failing | CF cron itself broken |
| 3 — Admin queue-health endpoint + auto-alert | "Containers running but submission-scanner stuck" (orthogonal to `/health`) | Nothing — eyeball + auto-email |

Existing infrastructure being reused: Cloudflare Worker cron dispatcher in `scripts/build-worker-entry.ts` (lines 103-287), `selfRef.fetch` + `X-Internal-Key` pattern (lines 272-278), `requireAdmin()` from `src/lib/auth.ts`, `getDb()` + `withDbTimeout()` from `src/lib/db.ts`, SendGrid via `src/lib/email.ts`, `SUBMISSIONS_KV` for caching/throttling, indexed Prisma `Submission` model, per-VM dispatch loop in `scanner-worker/deploy.sh`.

## User Stories

### US-001: VM-side systemd watchdog auto-restarts crawl-worker (P1)
**Project**: vskill-platform

**As an** operator
**I want** a systemd timer on each Hetzner VM that auto-restarts the `crawl-worker` container within ~2 minutes whenever it isn't running
**So that** manual stops, half-finished deploys, and container crashes can never cause silent multi-week outages again

**Acceptance Criteria**:
- [x] **AC-US1-01**: A new directory `crawl-worker/watchdog/` contains four files installed on every VM: `crawl-worker-watchdog.sh` (bash script), `crawl-worker-watchdog.service` (systemd one-shot unit), `crawl-worker-watchdog.timer` (systemd timer), and `install-watchdog.sh` (idempotent installer).
- [x] **AC-US1-02**: The timer runs every 2 minutes (`OnUnitActiveSec=2min`) and starts ~30 seconds after boot (`OnBootSec=30s`).
- [x] **AC-US1-03**: The timer survives VM reboots — installed with `WantedBy=timers.target` and enabled via `systemctl enable --now crawl-worker-watchdog.timer`.
- [x] **AC-US1-04**: The watchdog script ONLY restarts the container when `docker ps --filter name=crawl-worker --format '{{.Names}}'` returns no match. When the container is present (any state recognized by `docker ps`), the script is a strict no-op. Restart is performed via `cd /opt/scanner-worker && docker compose up -d crawl-worker` (compose itself is a no-op if already running, so the action is double-idempotent).
- [x] **AC-US1-05**: Every restart event is logged via `logger -t crawl-worker-watchdog`, so `journalctl -u crawl-worker-watchdog.service` shows when and why a restart happened.
- [x] **AC-US1-06**: `install-watchdog.sh` is fully idempotent: re-running it copies units to `/etc/systemd/system/`, runs `systemctl daemon-reload`, and `systemctl enable --now crawl-worker-watchdog.timer` without errors whether the watchdog is already installed or not.
- [x] **AC-US1-07**: `scanner-worker/deploy.sh` is updated so that, immediately after `docker compose up -d` (current line ~99) and before the existing post-deploy health checks (~105), it `scp`'s the `crawl-worker/watchdog/` directory to the VM and runs `bash <remote>/watchdog/install-watchdog.sh`. The change runs inside the existing per-VM loop and therefore deploys to all three VMs (`5.161.69.232`, `91.107.239.24`, `5.161.56.136`).
- [x] **AC-US1-08**: After `./scanner-worker/deploy.sh`, `ssh root@<vm> 'systemctl list-timers | grep crawl-worker-watchdog'` shows an active, scheduled timer on every one of the three VMs.

**Required for Validation**:
- Bash unit tests for the watchdog script (mocked `docker` CLI) — see US-004.
- Manual integration test: stop crawl-worker on VM-3, confirm auto-restart within 5 minutes via `docker ps`, and confirm the restart event in `journalctl -u crawl-worker-watchdog.service`.

---

### US-002: CF Cron VM healthcheck alerts when systemd can't help (P1)
**Project**: vskill-platform

**As** Anton
**I want** an email alert within ~20 minutes whenever any VM's crawl-worker is unreachable (host down, network partition, container running but `/health` failing)
**So that** I'm immediately aware of failure modes the on-VM systemd watchdog cannot fix

**Acceptance Criteria**:
- [x] **AC-US2-01**: A new internal route `POST /api/v1/internal/vm-healthcheck` lives at `src/app/api/v1/internal/vm-healthcheck/route.ts` and authenticates via the `X-Internal-Key` header using the same timing-safe-equal helper used by `src/app/api/v1/internal/enqueue-submissions/route.ts`. Requests without the header (or with a wrong key) return `401`.
- [x] **AC-US2-02**: The route reads VM IPs from a new env binding `HETZNER_VM_IPS` (comma-separated, e.g. `5.161.69.232,91.107.239.24,5.161.56.136`). When the env var is unset or empty, the route logs a warning and returns `200 { skipped: true, reason: "HETZNER_VM_IPS not set" }` — never crashes.
- [x] **AC-US2-03**: For each VM, the route fetches `http://<ip>:9600/health` with a **5-second** timeout (`AbortSignal.timeout(5000)`). The three fetches run in parallel via `Promise.allSettled`.
- [x] **AC-US2-04**: A consecutive-failure counter is tracked per VM in `SUBMISSIONS_KV` under key `vm-health:<ip>:fails` with TTL 1 hour. Each failed fetch (non-2xx, timeout, network error) increments the counter; each success resets it to 0 (delete the key).
- [x] **AC-US2-05**: When the counter reaches **2 or more**, an alert email is sent via `src/lib/email.ts` (new template `QUEUE_HEALTH_ALERT`, FROM `noreply@verified-skill.com`, TO `anton.abyzov@gmail.com`) containing the VM IP, failing endpoint, last error message, and consecutive-failure count.
- [x] **AC-US2-06**: Alerts are throttled per VM via a separate KV key `vm-health:<ip>:alerted` (TTL 6 hours). While that flag is present, the route still increments the failure counter but does NOT re-send the email.
- [x] **AC-US2-07**: On a successful fetch for a VM, BOTH KV keys (`vm-health:<ip>:fails` and `vm-health:<ip>:alerted`) are deleted, so the next failure streak can re-alert.
- [x] **AC-US2-08**: `scripts/build-worker-entry.ts` is updated to add a new `ctx.waitUntil(runWithWorkerEnv(env, async () => { await selfRef.fetch("/api/v1/internal/vm-healthcheck", { method: "POST", headers: { "X-Internal-Key": internalKey } }) }))` block inside the existing `*/10 * * * *` cron `scheduled()` handler, mirroring the shape of the reconciler-ensure block at lines 272-278. The other cron blocks (reconciler-ensure, etc.) are unchanged.
- [x] **AC-US2-09**: A failed alert email send (SendGrid 429/5xx) does NOT cause the route to return non-2xx — it logs the error and returns `200` with the per-VM result so the cron block's `ctx.waitUntil` cannot fail noisily.

**Required for Validation**:
- Vitest tests for `src/app/api/v1/internal/vm-healthcheck/route.ts` covering: 1-fail no alert, 2-fail alert fires once, 3+-fail no second alert (throttled), success clears both keys, env var unset returns `{ skipped: true }`. See US-004.
- Manual integration test: temporarily set `HETZNER_VM_IPS` to include a bogus IP (e.g. `127.0.0.1:9999`), wait two `*/10 * * * *` ticks, confirm an alert email arrives.

---

### US-003: Admin queue-health endpoint + auto-alert catches the orthogonal failure mode (P1)
**Project**: vskill-platform

**As** Anton
**I want** `GET /api/v1/admin/queue-health` to return the oldest `RECEIVED` submission's age, AND I want it to auto-email me when that age exceeds 1 hour
**So that** the case "containers running, `/health` returns 200, but submission-scanner is stuck" — the actual 2026-03-09 root failure mode that no `/health` check can detect — is also caught

**Acceptance Criteria**:
- [x] **AC-US3-01**: A new route `GET /api/v1/admin/queue-health` lives at `src/app/api/v1/admin/queue-health/route.ts` and authenticates via `requireAdmin()` from `src/lib/auth.ts`, modeled on `src/app/api/v1/admin/submissions/state-counts/route.ts`. Requests without admin auth return `401`/`403` per `requireAdmin()` semantics.
- [x] **AC-US3-02**: The route runs `prisma.submission.findFirst({ where: { state: 'RECEIVED' }, orderBy: { createdAt: 'asc' }, select: { id: true, createdAt: true } })` wrapped in `withDbTimeout(..., 5_000)`. The existing `Submission` indexes (`@@index([state])`, `@@index([createdAt])` in `prisma/schema.prisma`) make this O(1).
- [x] **AC-US3-03**: The response shape is exactly:
  ```json
  {
    "oldestReceivedAgeMs": 3600000,
    "oldestReceivedId": "sub_...",
    "receivedCount": 162,
    "thresholdExceeded": true,
    "thresholdMs": 3600000
  }
  ```
  When no `RECEIVED` submissions exist, `oldestReceivedAgeMs` is `0`, `oldestReceivedId` is `null`, `thresholdExceeded` is `false`.
- [x] **AC-US3-04**: Results are cached in `SUBMISSIONS_KV` under key `queue-health:snapshot` with TTL 60 seconds. A cache hit short-circuits the Prisma query.
- [x] **AC-US3-05**: `thresholdMs` is set to `3600000` (1 hour). `thresholdExceeded` is `true` iff `oldestReceivedAgeMs > thresholdMs`.
- [x] **AC-US3-06**: When `thresholdExceeded` is `true`, the route auto-sends the `QUEUE_HEALTH_ALERT` email (same template as US-002) including `oldestReceivedAgeMs`, `oldestReceivedId`, and `receivedCount`. The alert is throttled via a separate KV key `queue-health:alerted` (TTL 6 hours) — independent from the per-VM throttle in US-002 so a queue-stuck condition can still alert while a VM-down alert is in-flight.
- [x] **AC-US3-07**: When `thresholdExceeded` returns to `false` (oldest age back under 1 hour, or no `RECEIVED` rows), the route deletes the `queue-health:alerted` key so the next breach re-alerts.
- [x] **AC-US3-08**: A failed alert email send does not cause a non-2xx response — the route logs the error and still returns the JSON envelope.

**Required for Validation**:
- Vitest tests for `src/app/api/v1/admin/queue-health/route.ts` covering: empty queue, oldest age within threshold (no alert), oldest age over threshold (alert fires), repeat call within 6h (throttled — no second email), KV cache hit short-circuits Prisma. See US-004.
- Manual integration test: hit the endpoint with admin cookie against the current healthy fleet; expect `oldestReceivedAgeMs` near zero and `thresholdExceeded: false`.

---

### US-004: Test coverage and end-to-end verification gate the rollout (P1)
**Project**: vskill-platform

**As a** maintainer
**I want** every layer of this watchdog to be covered by automated tests AND verified by a manual integration run
**So that** the watchdog itself can't have a silent regression — defending against silent failures by means of tests that themselves can fail silently is an obvious anti-pattern

**Acceptance Criteria**:
- [x] **AC-US4-01**: Bash unit tests at `crawl-worker/watchdog/__tests__/watchdog.test.sh` use a fixture `PATH` that shadows `docker` with a mock. Two cases: (a) container present → script exits 0 and the mock recorded zero `compose up` invocations; (b) container missing → script exits 0 and the mock recorded exactly one `docker compose up -d crawl-worker` invocation.
- [x] **AC-US4-02**: Vitest tests at `src/app/api/v1/internal/vm-healthcheck/__tests__/route.test.ts` cover all six branches in AC-US2-04 through AC-US2-09: 1-fail no alert, 2-fail alert fires, 3+-fail throttled (only 1 email total), success clears both KV keys, `HETZNER_VM_IPS` unset returns `{ skipped: true }`, SendGrid failure does not 5xx the route. Mocks: `fetch` for VM `/health`, `SUBMISSIONS_KV` (in-memory map), `sendEmail` from `src/lib/email.ts`.
- [x] **AC-US4-03**: Vitest tests at `src/app/api/v1/admin/queue-health/__tests__/route.test.ts` cover all eight ACs in US-003: empty queue, under-threshold no alert, over-threshold alert fires once, throttle prevents second alert within 6h, threshold-clear deletes throttle key, KV cache hit, KV cache miss + Prisma path, SendGrid failure does not 5xx the route. Mocks: Prisma client with seeded `Submission` rows, `SUBMISSIONS_KV`, `requireAdmin()`.
- [x] **AC-US4-04**: All new tests are wired into the existing Vitest config and pass via `npx vitest run` from the `vskill-platform` repo root.
- [x] **AC-US4-05**: Live integration test (manual, post-deploy) — recorded in the increment's `reports/` folder:
  1. `ssh root@5.161.56.136 'cd /opt/scanner-worker && docker compose stop crawl-worker'`.
  2. Wait ≤ 5 minutes; `ssh root@5.161.56.136 'docker ps --filter name=crawl-worker'` shows the container back up.
  3. `ssh root@5.161.56.136 'journalctl -u crawl-worker-watchdog.service --since "10 minutes ago"'` shows the `container missing — restarting via docker compose` log line.
- [ ] **AC-US4-06**: Live alert-simulation test (manual, post-deploy) — recorded in the increment's `reports/` folder: temporarily set `HETZNER_VM_IPS` to a list including an unreachable IP, wait two `*/10 * * * *` cron ticks, confirm exactly one `QUEUE_HEALTH_ALERT` email arrives at `anton.abyzov@gmail.com`, then revert `HETZNER_VM_IPS` and confirm the next tick clears the throttle and KV failure counter.

**Required for Validation**:
- `npx vitest run` — all new tests pass; no regressions in existing tests.
- `bash crawl-worker/watchdog/__tests__/watchdog.test.sh` — passes locally and in any future CI bash matrix.

## Functional Requirements

### FR-001: Defense in depth across three layers
The system MUST NOT rely on any single layer to detect or recover from a stopped crawl-worker. Each layer MUST be installed and verified independently. Removing any one layer MUST NOT silently disable the others.

### FR-002: All failure paths are observable
Every restart, every alert, every throttle decision MUST be observable via at least one of: `journalctl -u crawl-worker-watchdog.service` (Layer 1), `wrangler tail` log lines from the cron block (Layer 2), the `queue-health` JSON response shape (Layer 3), or the alert email itself.

### FR-003: Idempotent installation
Re-running `scanner-worker/deploy.sh` MUST be safe at every layer: the systemd installer is a strict idempotent operation, the CF Worker deploy uses standard `wrangler deploy`, and the new env binding `HETZNER_VM_IPS` is read at request time (no rebuild required to update VM list).

### FR-004: Alert throttling prevents pager fatigue
Each alert source (per-VM healthcheck, queue-health) MUST throttle to at most one email per 6 hours per failure source while the failure persists, and MUST self-clear on first success.

### FR-005: No new infrastructure
The implementation MUST reuse existing primitives only: SendGrid + `src/lib/email.ts`, `SUBMISSIONS_KV`, `requireAdmin()`, `withDbTimeout()`, `selfRef.fetch` + `X-Internal-Key`, the existing `*/10 * * * *` cron in `scripts/build-worker-entry.ts`, the existing `scanner-worker/deploy.sh` per-VM loop. No new database tables, no new queues, no new auth providers, no new external services.

## Success Criteria

- **Mean time to recovery for a stopped crawl-worker container drops from 6+ weeks (current observed) to ≤ 5 minutes** (Layer 1 systemd timer cadence + restart latency).
- **Mean time to alert for a host-level outage drops from "never" to ≤ 20 minutes** (Layer 2: 2 failed `*/10 * * * *` ticks).
- **Mean time to alert for a "containers up but queue stuck" condition drops from "never" to ≤ 1 hour** (Layer 3: `thresholdMs = 3600000`).
- **Zero silent multi-day outages** of the submission pipeline going forward — verified by absence of any new `RECEIVED`-pile-up incidents over a 90-day post-deploy window.
- **All three layers observable** via journalctl / `wrangler tail` / queue-health JSON within 10 minutes of any failure event.

## Out of Scope

The following are explicitly NOT part of this increment (each is tracked separately if needed):

- **Redeploying VM crawl-worker code itself.** The currently running VM image is 6+ weeks stale (the live submission-scanner cooldown is 5 seconds vs. current code's 5 minutes — Neon DB is being hammered). A separate increment will address that; this increment only protects against silent process death, not stale code.
- **The Tier-2 LLM `text.trim is not a function` bug.** Surfaced during the same incident triage but unrelated to watchdog mechanics.
- **The legacy bare `node server.js` on VM-2 holding port 9500.** Cleanup is a separate operational task; the watchdog will tolerate its presence.
- **Surfacing `oldestReceivedAgeMs` on the admin dashboard UI.** The endpoint exists in this increment; rendering it in `vskill-platform`'s admin UI is a follow-up increment.
- **Automatic failover or VM provisioning.** Three-VM topology stays the same; the watchdog only restarts existing containers.

## Dependencies

- **Existing CF Worker cron** in `scripts/build-worker-entry.ts` (lines 103-287) — Layer 2 grafts onto it.
- **Existing `requireAdmin()`** in `src/lib/auth.ts` — Layer 3 reuses it verbatim.
- **Existing `getDb()` + `withDbTimeout()`** in `src/lib/db.ts` — Layer 3 query path.
- **Existing `SUBMISSIONS_KV` binding** — used by all alert throttles and the queue-health 60s cache.
- **Existing `src/lib/email.ts`** SendGrid wrapper — Layers 2 and 3 add a single new template (`QUEUE_HEALTH_ALERT`).
- **Existing `Submission` model** in `prisma/schema.prisma` (lines 150-210) with `@@index([state])` and `@@index([createdAt])` — both indexes already exist; no migration required.
- **Existing `scanner-worker/deploy.sh`** per-VM loop — Layer 1 install hooks into it after `docker compose up -d`.
- **New env binding `HETZNER_VM_IPS`** — added to `wrangler.jsonc` (or pushed via `wrangler secret put` if Anton prefers secret-grade handling, though the IPs are public infra).
- **Three Hetzner VMs** at `5.161.69.232`, `91.107.239.24`, `5.161.56.136` running Ubuntu with `systemd` enabled (verified during the 2026-04-26 manual recovery).
