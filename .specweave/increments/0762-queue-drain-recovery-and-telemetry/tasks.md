# 0762 — Tasks

### T-001: scheduler.js registers `stats-compute`
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03 | **Status**: [x]
**Test Plan**: Given the scheduler module is imported, When `SOURCE_TIMEOUTS` and `SOURCE_COOLDOWNS` are read, Then `stats-compute` resolves to 5×60×1000 and 10×60×1000 respectively.

### T-002: ensureFreshStats no-op when KV is fresh
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 | **Status**: [x]
**Test Plan**: Given a KV fixture where `submissions:stats-cache.generatedAt` is now-5min, When `ensureFreshStats(env)` is called, Then no DB query and no KV write happen.

### T-003: ensureFreshStats writes when KV is stale
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02 | **Status**: [x]
**Test Plan**: Given KV `generatedAt` is 30 min old, When `ensureFreshStats(env)` runs against a Prisma mock returning per-state counts, Then a fresh-`generatedAt` payload is `KV.put` to `submissions:stats-cache` with `degraded: true`.

### T-004: cron handler calls ensureFreshStats first
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 | **Status**: [x]
**Test Plan**: Given the scheduled handler in `.open-next/worker-with-queues.js`, When it executes, Then `ensureFreshStats` is invoked before `refreshPlatformStats` / `refreshQueueStats`.

### T-005: releaseStuckScanning resets stuck items
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-03 | **Status**: [x]
**Test Plan**: Given a Prisma fixture with 3 items in `TIER1_SCANNING` updatedAt 31 min ago and 1 item updated 5 min ago, When `releaseStuckScanning(env)` runs, Then `updateMany` is called with `state='TIER1_SCANNING' AND updatedAt < now-30min` and only 3 items are reset to `RECEIVED`. A stateEvent with `trigger='scanner_timeout'` is written for each.

### T-006: releaseStuckScanning rejects after 3 retries
**User Story**: US-002 | **Satisfies ACs**: AC-US2-02 | **Status**: [x]
**Test Plan**: Given KV `recovery:scanning-released:{id}` reads "3", When `releaseStuckScanning` evaluates that item, Then it transitions to `REJECTED` with `trigger='scanner_timeout_max_retries'` instead of resetting.

### T-007: cron handler calls releaseStuckScanning
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01 | **Status**: [x]
**Test Plan**: Given the scheduled handler, When it runs, Then `releaseStuckScanning` is invoked alongside `recoverStuckSubmissions`.

### T-008: stageTimings derived from stateHistory
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01 | **Status**: [x]
**Test Plan**: Given `stateHistory` with RECEIVED→TIER1_SCANNING→AUTO_APPROVED→PUBLISHED entries 1s apart, When `GET /api/v1/submissions/{id}` is called, Then the response includes `stageTimings` with the expected ISO timestamps and msIn* values matching the gaps.

### T-009: stageTimings clamps out-of-order timestamps to 0
**User Story**: US-003 | **Satisfies ACs**: AC-US3-02 | **Status**: [x]
**Test Plan**: Given a stateHistory where PUBLISHED.timestamp < AUTO_APPROVED.timestamp (the live `sub_32a4c001` case), When stageTimings is computed, Then `msInAutoApproved` is 0 (not negative).

### T-010: /api/v1/queue/health response shape
**User Story**: US-003 | **Satisfies ACs**: AC-US3-03 | **Status**: [x]
**Test Plan**: Given fixtures for KV `submissions:stats-cache` and Submission table, When `GET /api/v1/queue/health` is called, Then the JSON includes `statsAge.{generatedAt,ageMs,source}`, `oldestActive.{id,state,ageMs}`, `drainRate.{last1h,last6h}`, `vmHeartbeat.lastPostAt`.

### T-011: /api/v1/queue/health caches 30s
**User Story**: US-003 | **Satisfies ACs**: AC-US3-03 | **Status**: [x]
**Test Plan**: Given the second consecutive call within 30s, When the route runs, Then it serves from KV `queue-health:cache` and skips DB queries.

### T-012: list cache never persists empty submissions
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01 | **Status**: [x]
**Test Plan**: Given a request that produces `submissions=[]` and `total=153`, When the route reaches the cache-write block, Then no `KV.put` is called for either the exact or "latest" cache key.

### T-013: flushDbUpdates failures are logged
**User Story**: US-004 | **Satisfies ACs**: AC-US4-02 | **Status**: [x]
**Test Plan**: Given `db.submission.updateMany` rejects with an Error, When `flushDbUpdates` settles, Then `console.error("[queue/flushDbUpdates] failed:", ...)` is called once per rejection.

### T-014: drain-verify.mjs records movement
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01, AC-US5-02, AC-US5-03 | **Status**: [x]
**Test Plan**: Given the script is invoked with `--count=5 --duration=30m`, When at least one polled `total` differs from baseline, Then it writes a per-id timing matrix to `reports/drain-verification-<ts>.txt`. If no movement is observed, the report begins with `NO_DRAIN_OBSERVED`.

### T-015: Production deploy + live verification
**User Story**: US-005 | **Satisfies ACs**: AC-US5-03 | **Status**: [x]
**Test Plan**: Run drain-verify.mjs against verified-skill.com after deploy, attach the report to the increment, and confirm `statsAge.ageMs < 15min` on `/api/v1/queue/health`.
