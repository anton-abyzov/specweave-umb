# Verify — 0748-crawl-worker-watchdog

FAIL · 2026-10-27T21:14:20.895Z · commands from explicit

## Commands

### `cd /Users/antonabyzov/.specwithcode/m4/worktrees/vskill-platform/0854-isolated-runtime && PWDEBUG=0 PLAYWRIGHT_HTML_OPEN=never node_modules/.bin/vitest run src/lib/watchdog/__tests__ --maxWorkers=4` → exit 0 (2s)

```
 DEPRECATED  "environmentMatchGlobs" is deprecated. Use `test.projects` to define different configurations instead.

 RUN  v3.2.7 /Users/antonabyzov/.specwithcode/m4/worktrees/vskill-platform/0854-isolated-runtime

 ✓ src/lib/watchdog/__tests__/acceptance-email.test.ts (21 tests) 8ms
 ✓ src/lib/watchdog/__tests__/email-regression.test.ts (31 tests) 33ms
 ✓ src/lib/watchdog/__tests__/acceptance.test.ts (75 tests) 41ms
 ✓ src/lib/watchdog/__tests__/acceptance.workerd.test.ts (1 test) 1762ms

 Test Files  4 passed (4)
      Tests  128 passed (128)
   Start at  17:14:18
   Duration  2.20s (transform 190ms, setup 27ms, collect 527ms, tests 1.84s, environment 0ms, prepare 124ms)
```

## Acceptance criteria

30/31 met

| AC | Met | Acceptance | Text |
|---|---|---|---|
| AC-US1-01 | x | met | A new directory `crawl-worker/watchdog/` contains four files installed on every VM: `crawl-worker-watchdog.sh` (bash script), `crawl-worker-watchdog.service` (systemd one-shot unit), `crawl-worker-watchdog.timer` (systemd timer), and `install-watchdog.sh` (idempotent installer). |
| AC-US1-02 | x | met | The timer runs every 2 minutes (`OnUnitActiveSec=2min`) and starts ~30 seconds after boot (`OnBootSec=30s`). |
| AC-US1-03 | x | met | The timer survives VM reboots — installed with `WantedBy=timers.target` and enabled via `systemctl enable --now crawl-worker-watchdog.timer`. |
| AC-US1-04 | x | met | The watchdog script ONLY restarts the container when `docker ps --filter name=crawl-worker --format '{{.Names}}'` returns no match. When the container is present (any state recognized by `docker ps`), the script is a strict no-op. Restart is performed via `cd /opt/scanner-worker && docker compose up -d crawl-worker` (compose itself is a no-op if already running, so the action is double-idempotent). |
| AC-US1-05 | x | met | Every restart event is logged via `logger -t crawl-worker-watchdog`, so `journalctl -u crawl-worker-watchdog.service` shows when and why a restart happened. |
| AC-US1-06 | x | met | `install-watchdog.sh` is fully idempotent: re-running it copies units to `/etc/systemd/system/`, runs `systemctl daemon-reload`, and `systemctl enable --now crawl-worker-watchdog.timer` without errors whether the watchdog is already installed or not. |
| AC-US1-07 | x | met | `scanner-worker/deploy.sh` is updated so that, immediately after `docker compose up -d` (current line ~99) and before the existing post-deploy health checks (~105), it `scp`'s the `crawl-worker/watchdog/` directory to the VM and runs `bash <remote>/watchdog/install-watchdog.sh`. The change runs inside the existing per-VM loop and therefore deploys to all three VMs (`5.161.69.232`, `91.107.239.24`, `5.161.56.136`). |
| AC-US1-08 | x | met | After `./scanner-worker/deploy.sh`, `ssh root@<vm> 'systemctl list-timers \| grep crawl-worker-watchdog'` shows an active, scheduled timer on every one of the three VMs. |
| AC-US2-01 | x | met | A new internal route `POST /api/v1/internal/vm-healthcheck` lives at `src/app/api/v1/internal/vm-healthcheck/route.ts` and authenticates via the `X-Internal-Key` header using the same timing-safe-equal helper used by `src/app/api/v1/internal/enqueue-submissions/route.ts`. Requests without the header (or with a wrong key) return `401`. |
| AC-US2-02 | x | met | The route reads VM IPs from a new env binding `HETZNER_VM_IPS` (comma-separated, e.g. `5.161.69.232,91.107.239.24,5.161.56.136`). When the env var is unset or empty, the route logs a warning and returns `200 { skipped: true, reason: "HETZNER_VM_IPS not set" }` — never crashes. |
| AC-US2-03 | x | met | For each VM, the route fetches `http://<ip>:9600/health` with a **5-second** timeout (`AbortSignal.timeout(5000)`). The three fetches run in parallel via `Promise.allSettled`. |
| AC-US2-04 | x | met | A consecutive-failure counter is tracked per VM in `SUBMISSIONS_KV` under key `vm-health:<ip>:fails` with TTL 1 hour. Each failed fetch (non-2xx, timeout, network error) increments the counter; each success resets it to 0 (delete the key). |
| AC-US2-05 | x | met | When the counter reaches **2 or more**, an alert email is sent via `src/lib/email.ts` (new template `QUEUE_HEALTH_ALERT`, FROM `noreply@verified-skill.com`, TO `anton.abyzov@gmail.com`) containing the VM IP, failing endpoint, last error message, and consecutive-failure count. |
| AC-US2-06 | x | met | Alerts are throttled per VM via a separate KV key `vm-health:<ip>:alerted` (TTL 6 hours). While that flag is present, the route still increments the failure counter but does NOT re-send the email. |
| AC-US2-07 | x | met | On a successful fetch for a VM, BOTH KV keys (`vm-health:<ip>:fails` and `vm-health:<ip>:alerted`) are deleted, so the next failure streak can re-alert. |
| AC-US2-08 | x | met | `scripts/build-worker-entry.ts` is updated to add a new `ctx.waitUntil(runWithWorkerEnv(env, async () => { await selfRef.fetch("/api/v1/internal/vm-healthcheck", { method: "POST", headers: { "X-Internal-Key": internalKey } }) }))` block inside the existing `*/10 * * * *` cron `scheduled()` handler, mirroring the shape of the reconciler-ensure block at lines 272-278. The other cron blocks (reconciler-ensure, etc.) are unchanged. |
| AC-US2-09 | x | met | A failed alert email send (SendGrid 429/5xx) does NOT cause the route to return non-2xx — it logs the error and returns `200` with the per-VM result so the cron block's `ctx.waitUntil` cannot fail noisily. |
| AC-US3-01 | x | met | A new route `GET /api/v1/admin/queue-health` lives at `src/app/api/v1/admin/queue-health/route.ts` and authenticates via `requireAdmin()` from `src/lib/auth.ts`, modeled on `src/app/api/v1/admin/submissions/state-counts/route.ts`. Requests without admin auth return `401`/`403` per `requireAdmin()` semantics. |
| AC-US3-02 | x | met | The route runs `prisma.submission.findFirst({ where: { state: 'RECEIVED' }, orderBy: { createdAt: 'asc' }, select: { id: true, createdAt: true } })` wrapped in `withDbTimeout(..., 5_000)`. The existing `Submission` indexes (`@@index([state])`, `@@index([createdAt])` in `prisma/schema.prisma`) make this O(1). |
| AC-US3-03 | x | met | The response shape is exactly: |
| AC-US3-04 | x | met | Results are cached in `SUBMISSIONS_KV` under key `queue-health:snapshot` with TTL 60 seconds. A cache hit short-circuits the Prisma query. |
| AC-US3-05 | x | met | `thresholdMs` is set to `3600000` (1 hour). `thresholdExceeded` is `true` iff `oldestReceivedAgeMs > thresholdMs`. |
| AC-US3-06 | x | met | When `thresholdExceeded` is `true`, the route auto-sends the `QUEUE_HEALTH_ALERT` email (same template as US-002) including `oldestReceivedAgeMs`, `oldestReceivedId`, and `receivedCount`. The alert is throttled via a separate KV key `queue-health:alerted` (TTL 6 hours) — independent from the per-VM throttle in US-002 so a queue-stuck condition can still alert while a VM-down alert is in-flight. |
| AC-US3-07 | x | met | When `thresholdExceeded` returns to `false` (oldest age back under 1 hour, or no `RECEIVED` rows), the route deletes the `queue-health:alerted` key so the next breach re-alerts. |
| AC-US3-08 | x | met | A failed alert email send does not cause a non-2xx response — the route logs the error and still returns the JSON envelope. |
| AC-US4-01 | x | met | Bash unit tests at `crawl-worker/watchdog/__tests__/watchdog.test.sh` use a fixture `PATH` that shadows `docker` with a mock. Two cases: (a) container present → script exits 0 and the mock recorded zero `compose up` invocations; (b) container missing → script exits 0 and the mock recorded exactly one `docker compose up -d crawl-worker` invocation. |
| AC-US4-02 | x | met | Vitest tests at `src/app/api/v1/internal/vm-healthcheck/__tests__/route.test.ts` cover all six branches in AC-US2-04 through AC-US2-09: 1-fail no alert, 2-fail alert fires, 3+-fail throttled (only 1 email total), success clears both KV keys, `HETZNER_VM_IPS` unset returns `{ skipped: true }`, SendGrid failure does not 5xx the route. Mocks: `fetch` for VM `/health`, `SUBMISSIONS_KV` (in-memory map), `sendEmail` from `src/lib/email.ts`. |
| AC-US4-03 | x | met | Vitest tests at `src/app/api/v1/admin/queue-health/__tests__/route.test.ts` cover all eight ACs in US-003: empty queue, under-threshold no alert, over-threshold alert fires once, throttle prevents second alert within 6h, threshold-clear deletes throttle key, KV cache hit, KV cache miss + Prisma path, SendGrid failure does not 5xx the route. Mocks: Prisma client with seeded `Submission` rows, `SUBMISSIONS_KV`, `requireAdmin()`. |
| AC-US4-04 | x | met | All new tests are wired into the existing Vitest config and pass via `npx vitest run` from the `vskill-platform` repo root. |
| AC-US4-05 | x | met | Live integration test (manual, post-deploy) — recorded in the increment's `reports/` folder: |
| AC-US4-06 |   | open | Live alert-simulation test (manual, post-deploy, separately approved) — record four distinct real `*/10 * * * *` cron ticks in an isolated run: failure; second failure and exactly one SendGrid attempt to one explicitly authorized recipient; throttled failure; healthy recovery clearing only the run failure/throttle state. Confirm one received email separately from provider acceptance. The disabled-by-default immutable manifest expires after 40 minutes; missing/late/reordered ticks fail closed. Atomic per-run claim persists before transport and is never released for retry. Do not change real `HETZNER_VM_IPS`, heartbeat/source keys, real alert recipients, queues or VM state. Source correction authorized October 21; this does not claim live completion. |

## Tasks (ledger)

| Task | State | By | Evidence | Note |
|---|---|---|---|---|
| T-001a | done | tasks.md | checkbox in tasks.md |  |
| T-001b | done | tasks.md | checkbox in tasks.md |  |
| T-002 | done | tasks.md | checkbox in tasks.md |  |
| T-003 | done | tasks.md | checkbox in tasks.md |  |
| T-004 | done | tasks.md | checkbox in tasks.md |  |
| T-005a | done | tasks.md | checkbox in tasks.md |  |
| T-005b | done | tasks.md | checkbox in tasks.md |  |
| T-006 | done | tasks.md | checkbox in tasks.md |  |
| T-007 | done | tasks.md | checkbox in tasks.md |  |
| T-008 | done | tasks.md | checkbox in tasks.md |  |
| T-009 | done | tasks.md | checkbox in tasks.md |  |
| T-010 | blocked | disk-completion-0748 |  | Sole successor explicitly assigned after October21 ownershi… |
| T-011a | done | tasks.md | checkbox in tasks.md |  |
| T-011b | done | tasks.md | checkbox in tasks.md |  |
| T-012a | done | tasks.md | checkbox in tasks.md |  |
| T-012b | done | tasks.md | checkbox in tasks.md |  |
| T-013 | done | tasks.md | checkbox in tasks.md |  |
| T-014 | done | claude@antons-macbook-m4max | 2026-10-21T06:08:35Z, live worker 8a62538e (RELEASE_GIT_SHA… |  |
| T-015 | done | claude@antons-macbook-m4max | cd /Users/antonabyzov/Projects/github/specweave-umb/reposit… |  |
| T-016 | blocked | disk-completion-0748 |  | Sole successor assigned after ownership audit; correcting o… |
| T-017 | done | codex@antons-macbook-m4max | 0fd065a802cdcfcacc8a30a38606b102bef752ee; PR184; 166 focuse… |  |
| T-018 | stale | disk-completion-0748 |  |  |
| T-019 | done | disk-completion-0748 | Product source head 65e72a190b8b6bd582a6439f244d1c788969ccf… |  |
| T-020 | open |  |  |  |
| T-021 | done | codex@antons-macbook-m4max | PR187 reviewed235tests/826assertions,98.75%lines; historica… |  |

21/25 done · 0 skipped · 0 claimed · 2 blocked · 1 stale · 1 open
