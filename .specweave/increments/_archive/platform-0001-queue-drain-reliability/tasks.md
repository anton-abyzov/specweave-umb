---
increment: 0001-queue-drain-reliability
title: "Submission Queue Drain Reliability — Tasks"
status: active
created: 2026-05-14
---

# Tasks

### T-001: Map production queue drain architecture
**User Story**: US-001
**Satisfies ACs**: AC-US1-01, AC-US1-03
**Status**: [x] completed

**Test Plan** (BDD):
- Given the repository source and env files exist → When queue, admin, internal, and worker files are inspected → Then the claim/process/callback path and required secrets are known.

**Notes**: Production drain path is Cloudflare Worker APIs plus three Hetzner crawl-worker containers running `submission-scanner`; production data remains in Neon Postgres. No EasyChamp Postgres migration is needed.

### T-002: Query production queue and user freshness
**User Story**: US-001, US-002
**Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US2-01, AC-US2-02, AC-US2-03
**Status**: [x] completed

**Test Plan** (BDD):
- Given production API/database access → When queue/user/submission queries run → Then current backlog, oldest item, and recent real usage are reported.

**Notes**: The original old `RECEIVED` item `sub_c0667f5e-244a-49dc-8fb6-dd147cab843e` is now `PUBLISHED`. Registered users remain 15; recent human submissions are effectively Anton-only, while discovery/backfill submissions and CLI installs are active.

### T-003: Inspect worker hosts and logs
**User Story**: US-001
**Satisfies ACs**: AC-US1-03, AC-US1-04
**Status**: [x] completed

**Test Plan** (BDD):
- Given host credentials are available → When services/containers/logs are inspected → Then worker liveness and failure mode are identified.

**Notes**: Root cause was stale VM `INTERNAL_KEY` values. VMs were healthy but internal calls returned 401; `submission-scanner` converted pending-fetch failures into empty batches, hiding the outage.

### T-004: Restore or migrate production queue draining
**User Story**: US-003
**Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04
**Status**: [x] completed

**Test Plan** (BDD):
- Given the root cause is known → When remediation or migration is applied → Then at least one stuck `RECEIVED` submission moves forward and queue health drops below alert thresholds.

**Notes**: Updated local and remote worker env, rebuilt/recreated crawl-worker containers on all three VMs, and redeployed Cloudflare Worker version `7835935a-26e7-495e-9ea7-7abf36be3a5b`. Queue health is below threshold; current `RECEIVED` rows are fresh.

### T-005: Add prevention and operational proof
**User Story**: US-004
**Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04
**Status**: [x] completed

**Test Plan** (BDD):
- Given the queue is repaired → When tests/build and production health checks run → Then prevention changes are verified and operator commands are documented without secrets.

**Notes**: Added fatal scanner auth/error handling, switched queue health/stuck recovery age calculations to `updatedAt`, fixed republish requeue races, and verified targeted Vitest plus `build:worker` and production health checks.

### T-006: Make queue-health fixes deploy-proof
**User Story**: US-005
**Satisfies ACs**: AC-US5-01, AC-US5-02, AC-US5-03, AC-US5-04
**Status**: [x] completed

**Test Plan** (BDD):
- Given local route code has changed → When `npm run deploy` is executed → Then the Next.js and OpenNext worker bundles are rebuilt before Cloudflare deploy.
- Given production still serves an old queue-health bundle → When the post-deploy smoke runs → Then deployment exits non-zero instead of silently shipping stale monitoring code.

**Notes**: Recurrence root cause was stale generated `.open-next/worker-with-queues.js` despite source changes. `npm run deploy` now rebuilds before `wrangler deploy`, rejects stale KV health-cache shapes, publishes schema v2 health contracts, and post-deploy smoke verified production Worker version `2ddb298a-5b32-470f-ac0e-fb5f72fb94b8`.

### T-007: Harden deploy smoke against stale bundles and propagation
**User Story**: US-005
**Satisfies ACs**: AC-US5-01, AC-US5-02, AC-US5-03, AC-US5-04, AC-US5-05
**Status**: [x] completed

**Test Plan** (BDD):
- Given a deployment starts from local source → When `npm run deploy` runs → Then it cleans generated artifacts, rebuilds the OpenNext worker bundle, and checks the compiled route contract before upload.
- Given Cloudflare still serves the old worker immediately after deploy → When postdeploy smoke runs → Then it retries until schema v2 is live or fails with the stale contract body.
- Given postdeploy needs to verify the alerting route → When it calls internal queue-health → Then it uses `dryRun=1` so no alert email or throttle mutation occurs.

**Notes**: Added `scripts/verify-queue-health-build.mjs`, changed `predeploy` to clean/build/contract-check, added `dryRun` support to `/api/v1/internal/queue-health-check`, and made `scripts/verify-queue-health-deploy.mjs` poll through propagation. Final production deploy succeeded on Worker version `35fc95ce-0480-4d38-85db-2fed2debf37d`; production reports schema v2 with `updatedAt` age basis and internal dry-run health `exceeded:false`.

### T-008: Make queue alerting self-heal before paging
**User Story**: US-006
**Satisfies ACs**: AC-US6-01, AC-US6-02, AC-US6-03, AC-US6-04, AC-US6-05
**Status**: [x] completed

**Test Plan** (BDD):
- Given a stale `RECEIVED` row breaches the alert threshold → When `/api/v1/internal/queue-health-check` runs outside dry-run → Then it runs stale-received recovery, re-queries, and emails only if the breach still exists.
- Given the Cloudflare scheduled light cohort runs → When recovery and queue-health alerting execute → Then queue-health runs after stale-received recovery in the same `waitUntil`.
- Given an active row is fresh and no queue items drained in the last hour → When smart alert detectors run → Then `drain-stalled` does not fire.
- Given the worker bundle is generated → When `scripts/verify-queue-health-build.mjs` runs → Then it fails if queue-health alerting is not sequenced after stale-received recovery.

**Notes**: Root recurrence was a race: recovery and queue-health were parallel scheduled tasks. The alert could see a stale row milliseconds before recovery touched/requeued it. The alert route now self-heals first, cron sequencing is deterministic, and smart drain-stalled alerts ignore fresh active work.
