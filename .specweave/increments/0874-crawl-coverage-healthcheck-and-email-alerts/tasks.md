# Tasks: Crawl coverage: health-check, email alerts, verification + GitHub breadth

**TDD**: every task RED→GREEN→REFACTOR. Unit: Vitest (platform) / node:test (crawl-worker). `npx vitest run` green before `[x]`.

Domains: **A** = platform alerts/heartbeat, **B** = platform intake, **C** = crawl-worker discovery. Tracks are largely independent → parallelizable.

> **Reconciliation (2026-06-24, audit-verified):** the per-task checkboxes below are STALE. A 3-agent evaluation (psql against prod + `git diff` + full `vitest`/`node:test` runs) found **~12 of 21 tasks implemented and green**, not 1. Verified done+tested: **T-001–T-005** (Track A coverage health), **T-011/012/013/015/016** (Track C size-bisection), **T-020** (coverage-gap bridge), **T-021**. **Not implemented:** Track B intake false-negatives **T-007/008/009/010** (scanner gained a tri-state probe but `submissions/bulk/route.ts` still calls the boolean path, still poisons `headCache`, still pushes `status:"error"` on a transient); plus **T-006/017/018/019**. **Was NOT shippable:** **T-014** referenced an undefined `parseSizeShards` in `crawl-worker/server.js` → would ReferenceError and crash all 3 VMs at scheduler boot — **FIXED 2026-06-24** (see **T-022**). Pipeline confirmed healthy; the prod "Alert evaluator is BLIND" page was a **false positive** (transient Hyperdrive cold-connect), fixed in **T-022**.

---

## Track A — Silent-failure health check + email alerting

### T-001: Transmit per-source coverageTotal off the VM
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 | **Status**: [ ] pending
**AC**: AC-US1-01
**Test**: Given a skills-sh `lastResult` with `totalSkillsSh=9590` → When `getHeartbeatSources()` builds the payload and `vm-heartbeat` persists it → Then `SOURCE_OBS_KEY` for `skills-sh` contains `coverageTotal=9590` and `SourceObservation` exposes it.
**Files**: `crawl-worker/scheduler.js`, `src/app/api/v1/internal/vm-heartbeat/route.ts`, `src/lib/alerts/detectors.ts`

### T-002: detectCoverageRegression (upward-only HWM baseline)
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02 | **Status**: [ ] pending
**AC**: AC-US1-02
**Test**: Given a stored baseline HWM of 73,148 and `coverageTotal=9590` → When `detectCoverageRegression` runs → Then it returns a `critical` finding (both <floor 20000 and <70% of HWM); and given a later 80,000 reading → Then the baseline rises to 80,000 but a subsequent 9,590 still fires (baseline never lowered).
**Files**: `src/lib/alerts/detectors.ts`

### T-003: detectCoverageStale + detectCoverageRatioCollapse
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03 | **Status**: [ ] pending
**AC**: AC-US1-03
**Test**: Given `lastSuccessAt` older than cooldown×1.5 → When `detectCoverageStale` runs → Then it warns; Given 3 heartbeats with `submittedΔ/discoveredΔ=0.02` while `discovered>0` → When `detectCoverageRatioCollapse` runs → Then it warns.
**Files**: `src/lib/alerts/detectors.ts`

### T-004: Wire 3 new AlertKinds through to SendGrid email
**User Story**: US-001 | **Satisfies ACs**: AC-US1-04 | **Status**: [ ] pending
**AC**: AC-US1-04
**Test**: Given a `coverage-regression` finding → When `alerts-evaluator` dispatches → Then `sendQueueHealthAlert` renders a `[ALERT] skills-sh coverage regressed: 9,590 vs baseline 73,148 (-87%)` body and is deduped by `shouldFire/recordFired` (second run within the window does not re-send).
**Files**: `src/lib/alerts/types.ts`, `src/lib/email.ts`, `src/app/api/v1/internal/alerts-evaluator/route.ts`

### T-005: queue-health exposes coverageTotal + baseline + lastSuccessfulPublishAt
**User Story**: US-001 | **Satisfies ACs**: AC-US1-05 | **Status**: [ ] pending
**AC**: AC-US1-05
**Test**: Given persisted observations → When `GET /api/v1/admin/queue-health` → Then each source shows `coverageTotal`, `baseline`, `lastSuccessfulPublishAt`.
**Files**: `src/app/api/v1/admin/queue-health/route.ts`

### T-006: Relabel skills-sh metric (skills vs installs)
**User Story**: US-001 | **Satisfies ACs**: AC-US1-06 | **Status**: [ ] pending
**AC**: AC-US1-06
**Test**: Given a skills-sh run → When `/coverage` is read → Then it exposes `skillsShUpstreamReportedTotal`, `skillsShAllTimeInstalls`, `skillsShDiscoveredThisRun` (no bare `skillsShTotal`); README documents 9,589 skills ≠ 748,368 installs.
**Files**: `crawl-worker/sources/skills-sh.js`, `crawl-worker/server.js`, `crawl-worker/README.md`, `crawl-worker/lib/coverage-metrics.js`, `crawl-worker/__tests__/coverage-metrics.test.js`, `crawl-worker/__tests__/skills-sh.test.js`, `crawl-worker/__tests__/server.test.js`

---

## Track B — Intake verification false-negatives

### T-007: Authenticate the intake SKILL.md probe
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01 | **Status**: [ ] pending
**AC**: AC-US2-01
**Test**: Given `cfEnv.GITHUB_TOKEN` set → When `cachedCheck → checkSkillMdExists → detectBranch` runs → Then requests carry `Authorization: Bearer` (asserted via mock fetch headers), using the 5,000 req/hr budget.
**Files**: `src/app/api/v1/submissions/bulk/route.ts`, `src/lib/scanner.ts`, `src/app/api/v1/submissions/bulk/__tests__/route.intake.test.ts`, `src/lib/__tests__/scanner-check-skillmd.test.ts`

### T-008: Tri-state {exists, transient} + defer transients
**User Story**: US-002 | **Satisfies ACs**: AC-US2-02 | **Status**: [ ] pending
**AC**: AC-US2-02
**Test**: Given a 429 on all branches → When `checkSkillMdExists` runs → Then it returns `{exists:false, transient:true}` and `bulk/route.ts` re-enqueues (counted `deferred`), NOT `status:"error"`; Given a real 404 on all branches → Then `{exists:false, transient:false}` and "not found" is pushed.
**Files**: `src/lib/scanner.ts`, `src/app/api/v1/submissions/bulk/route.ts`, `src/lib/queue/types.ts`, `src/lib/queue/consumer.ts`, `src/lib/queue/bulk-intake-retry.ts`, `src/lib/queue/__tests__/bulk-intake-retry.test.ts`, `src/app/api/v1/submissions/bulk/__tests__/registry-alias.test.ts`, `src/app/api/v1/submissions/bulk/__tests__/route.defer.test.ts`, `src/app/api/v1/submissions/bulk/__tests__/route.skillpath-validation.test.ts`

### T-009: Stop headCache poisoning
**User Story**: US-002 | **Satisfies ACs**: AC-US2-03 | **Status**: [ ] pending
**AC**: AC-US2-03
**Test**: Given a monorepo batch where the first sibling probe hits a transient false → When subsequent siblings resolve → Then the transient is NOT served from `headCache` (each re-probes); only `exists:true`/confirmed-404 are memoized.
**Files**: `src/app/api/v1/submissions/bulk/route.ts`

### T-010: Funnel counters + submit/notfound rates
**User Story**: US-002 | **Satisfies ACs**: AC-US2-04 | **Status**: [ ] pending
**AC**: AC-US2-04
**Test**: Given a run returning `{submitted:8,deferred:1,errors:1}` of 10 → When `/coverage` is read → Then `submit_rate=0.8` and `intake_notfound_rate` reflect only confirmed 404s.
**Files**: `crawl-worker/lib/inline-submitter.js`, `crawl-worker/sources/skills-sh.js`, `crawl-worker/server.js`

---

## Track C — GitHub discovery breadth (size-bisection)

### T-011: splitSizeRange (+ cap open-ended top)
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01 | **Status**: [ ] pending
**AC**: AC-US3-01
**Test**: Given `[0,1000]` → When `splitSizeRange` → Then `[[0,500],[501,1000]]`; Given `[42,42]` → Then `null`; Given the top root `[10001,null]` → Then it is first capped to `[10001,384000]` before splitting.
**Files**: `crawl-worker/sources/github-sharded.js`

### T-012: Parameterize bisectWindow with injected split fn
**User Story**: US-003 | **Satisfies ACs**: AC-US3-02 | **Status**: [ ] pending
**AC**: AC-US3-02
**Test**: Given `bisectWindow(range, countFn, {split: splitSizeRange})` → When a node exceeds the cap → Then it splits via `splitSizeRange`; Given no `split` opt → Then it defaults to `splitDateWindow` (existing date tests still pass).
**Files**: `crawl-worker/sources/github-sharded.js`

### T-013: expandPlanByBisection bisects on size
**User Story**: US-003 | **Satisfies ACs**: AC-US3-02 | **Status**: [ ] pending
**AC**: AC-US3-02
**Test**: Given `shardMode="size-bisect"` and a shard whose probe `total_count>1000` → When `expandPlanByBisection` runs → Then it replaces the shard with `{...shard, size: leaf}` children keyed off `shard.size` (not `shard.date`).
**Files**: `crawl-worker/sources/github-sharded.js`

### T-014: buildShardPlan "size-bisect" mode + honor config.sizeShards
**User Story**: US-003 | **Satisfies ACs**: AC-US3-03 | **Status**: [ ] pending
**AC**: AC-US3-03
**Test**: Given `shardMode="size-bisect"` + `config.sizeShards=[[0,200],[201,null]]` → When `buildShardPlan` runs → Then the plan seeds those size roots (the previously-dead `config.sizeShards` param is now used); `crawl()` gates bisection expansion on the mode; `server.js` passes `shardMode`/`adaptiveBisect`.
**Files**: `crawl-worker/sources/github-sharded.js`, `crawl-worker/server.js`

### T-015: size:N..N rendering + no-gap tiling unit tests
**User Story**: US-003 | **Satisfies ACs**: AC-US3-04 | **Status**: [ ] pending
**AC**: AC-US3-04
**Test**: Given a single-value leaf `[180,180]` → When `buildQuery` renders → Then `size:180..180` (never bare `size:180`); Given a recursive bisection of `[0,N]` → Then the leaf set covers `[0,N]` with no gaps and no overlaps and no leaf probe >1000 (mocked counts).
**Files**: `crawl-worker/sources/github-sharded.js`, `crawl-worker/__tests__/github-sharded-size.test.js` (new)

### T-016: Persist expanded leaf plan in checkpoint
**User Story**: US-003 | **Satisfies ACs**: AC-US3-05 | **Status**: [ ] pending
**AC**: AC-US3-05
**Test**: Given a sweep that checkpoints at `shardIndex=5` of a size-bisect plan → When the next scheduler tick resumes → Then it replays the SAME persisted leaf plan (no re-derivation drift) and continues at index 6.
**Files**: `crawl-worker/sources/github-sharded.js`, `crawl-worker/lib/crawl-state.js`

### T-017: Live size-bisect run proof (≫7k, shardsZeroResultCount≈0)
**User Story**: US-003 | **Satisfies ACs**: AC-US3-06 | **Status**: [ ] pending
**AC**: AC-US3-06
**Test**: Given `SHARD_MODE=size-bisect` against the real API on one VM (post-rotation) → When a sweep completes → Then distinct discovered ≫ 7,000 and `shardsZeroResultCount` ≈ 0 (vs the 42/49-zero `created:` baseline).
**Files**: `crawl-worker/sources/github-sharded.js`, `crawl-worker/__tests__/github-sharded-failure.test.js`, `crawl-worker/README.md` (guard failed sweeps; live proof still gated)

### T-018: Widen github-graphql-check + quarantine Worker dead dimension
**User Story**: US-003 | **Satisfies ACs**: AC-US3-07 | **Status**: [ ] pending
**AC**: AC-US3-07
**Test**: Given `github-graphql-check` config → When loaded → Then `LOOKBACK_MONTHS≈12` and the topic allow-list is extended; Given `github-discovery.ts` → Then `generateTimeShardedQueries` is unreferenced/quarantined with a comment that the VM owns code-search breadth.
**Files**: `crawl-worker/sources/github-graphql-check.js`, `src/lib/crawler/github-discovery.ts`

### T-019: Real-API CI guard (created:→0, size:→>0)
**User Story**: US-003 | **Satisfies ACs**: AC-US3-08 | **Status**: [ ] pending
**AC**: AC-US3-08
**Test**: Given `GITHUB_TEST_TOKEN` set → When the integration test runs → Then `filename:SKILL.md created:..`→0, `filename:SKILL.md`→>1000, `size:0..200`→>0, and bare `size:N`→422 (no `total_count`); Given no token → Then the test skips (not fails).
**Files**: `crawl-worker/__tests__/github-search-dimensions.integration.test.js` (new), `crawl-worker/package.json`, `.github/workflows/crawl-worker-tests.yml`, `crawl-worker/README.md`

---

## Track A↔C bridge + security prerequisite

### T-020: GitHub ground-truth probe + shardsZeroResultCount detector + dead-dimension assertion
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01 | **Status**: [ ] pending
**AC**: AC-US4-01
**Test**: Given a daily `filename:SKILL.md` probe (288,096) and our distinct github-sourced count (7,000) → When the detector runs → Then it alerts (ratio 2.4% < 10%); Given a `github-sharded` run with `shardsZeroResultCount/total > 0.5` → Then it alerts and logs "date qualifier ineffective on code search" when a date-shard is 0 while its parent is >0.
**Files**: `src/lib/alerts/detectors.ts`, `crawl-worker/sources/github-sharded.js`, `crawl-worker/scheduler.js`

### T-021: Secret hygiene — gitignore + untrack VM env files (gates T-017/C6)
**User Story**: US-004 | **Satisfies ACs**: AC-US4-02 | **Status**: [x] completed
**Done**: 13 token files (`.env.vm1-3` + `.env.gcp-vm1-10`) untracked via `git rm --cached`; `.gitignore` patterns `.env.vm*`/`.env.gcp-vm*` + `!.env.vm.example`; `crawl-worker/.env.vm.example` placeholder template + out-of-band provisioning doc added. **Pending (manual, Anton)**: rotate the 2 exposed PATs on github.com; optional git-history purge (BFG/filter-repo) — separate follow-up.
**AC**: AC-US4-02
**Test**: Given the repo → When `.gitignore` is updated and `git rm --cached crawl-worker/.env.vm* crawl-worker/.env.gcp-vm*` is run → Then `git ls-files` no longer lists them and `git check-ignore` returns them as ignored; PATs flagged for Anton to rotate; prod flip (T-017) stays gated until rotation confirmed.
**Files**: `repositories/anton-abyzov/vskill-platform/.gitignore`, `crawl-worker/.env.example`

---

## Incident follow-up (2026-06-24)

### T-022: Harden detector-blind discovery-floor query vs transient cold-connect
**User Story**: US-001 | **Satisfies ACs**: AC-US1-04 | **Status**: [x] completed
**Done**: Prod emailed `[ALERT] Alert evaluator is BLIND — DB operation timed out after 4000ms`. Root cause = FALSE POSITIVE: `readCreated24h` wrapped `db.skill.count(createdAt≥now-24h)` in a single-shot `withDbTimeout(…,4_000)` race; a transient Hyperdrive cold-connect on the per-request fresh PrismaClient breached 4s and paged as an outage — though the query is a ~3ms index-only scan (`Skill_createdAt_idx` present; EXPLAIN ANALYZE'd on prod 178.156.163.74:5433). The 4s breach also fed the global DB circuit breaker (5 trips → 30–120s blackout), self-amplifying one flake. **Fix**: retry (default 3×, env `ALERT_CREATED24H_ATTEMPTS`) with 250/500ms backoff under a connect-tolerant 8s ceiling (env `ALERT_CREATED24H_TIMEOUT_MS`); break immediately on an open circuit; rethrow after exhaustion so a genuinely dead DB still pages (**AC-US3-05 preserved**). Also fixed the **T-014** `parseSizeShards` boot-crash landmine (extracted to `crawl-worker/lib/shard-config.js` + 4 tests). Verified: platform **70/70**, crawl-worker **20/20** green. **NOT yet deployed** (platform deploy would drag incomplete Track B WIP to prod — deploy decision pending).
**Files**: `src/app/api/v1/internal/alerts-evaluator/route.ts`, `…/__tests__/route.test.ts`, `crawl-worker/server.js`, `crawl-worker/lib/shard-config.js`, `crawl-worker/__tests__/shard-config.test.js`
**Test**: Given a transient reject then success → POST 200, no detector-blind email; Given persistent rejects → 500 + detector-blind after 3 attempts; Given `circuit open` → 500 + detector-blind after 1 attempt.

### T-023: Revive the dormant skill re-check / provenance liveness loop
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03 | **Status**: [x] completed
**Root cause**: NOT a missing/disabled source — `runSkillUpdateScan` (`src/lib/skill-update/scanner.ts`) IS wired into the */10 light-cohort cron (`scripts/build-worker-entry.ts:400`), but its `db.skill.findMany({where:{sourceRepoUrl:{not:null}}})` had **no `take` limit**: it loaded the ENTIRE scannable population (67,060 rows in prod) and looped a GitHub commit-fetch + DB write over all of them in one Worker tick. As the table grew past the CPU/timeout cliff (the 2026-05-31 dedup cutover — exactly the freeze date), the unbounded load+loop stopped completing, the scan threw (swallowed by the cron handler at `build-worker-entry.ts:404`), and `lastCheckedAt` froze for ~25 days. (`provenanceCheckedAt` is separately dead — its writer was removed entirely; NOT restored here — future work.)
**Fix**: (1) bound the scan to `take: SKILL_UPDATE_SCAN_BATCH` (default 250) most-stale-first, with an `OR[lastCheckedAt null | < now-SKILL_UPDATE_RECHECK_DAYS]` gate so a caught-up loop stops re-fetching fresh skills → round-robins the 67k over ~2-3 days; (2) new `detectRecheckStale` detector + `recheck-stale` AlertKind + email + evaluator reader (`max(lastCheckedAt)` age) → pages if the newest check ages past `ALERT_RECHECK_STALE_MS` (default 24h) so this can't silently rot again. Verified: platform tests green (scanner batch ×3, detector ×4, 107 total); deployed Version 7860d7ce; live evaluator shows `recheckMaxAgeMs` + fired `recheck-stale` (correct — pages the 25d stall until the scanner catches up).
**Files**: `src/lib/skill-update/scanner.ts`, `src/lib/alerts/detectors.ts`, `src/lib/alerts/types.ts`, `src/lib/email.ts`, `src/app/api/v1/internal/alerts-evaluator/route.ts` (+ tests)

### T-024: Repair required Studio release checks without weakening privacy or paid entitlements
**AC**: AC-REL-01
**Files**: `src/app/layout.tsx`, `src/app/catalog/page.tsx`, `src/app/api/v1/e2e-harness/seed/route.ts`, `src/app/api/v1/e2e-harness/reset/route.ts`, `src/app/api/v1/e2e-harness/__tests__/harness.test.ts`, `tests/e2e/0826/anti-mistake-publish.spec.ts`, `tests/e2e/0826/free-tier-caps.spec.ts`, `tests/e2e/0826/public-private-isolation.spec.ts`, `tests/e2e/0826/_helpers/fixtures.ts`, `src/app/components/PrivacyTernaryField.tsx`
**Test**: Build the production app and run all 0826 Playwright tests headlessly on an isolated disposable local PostgreSQL database. Verify actual 404 status, no private payload leakage, populated public catalog, and paid fixture publishing plus FREE denial.

### T-025: Reconcile VM3 token pool and prepare guarded release
**AC**: AC-US3-06
**Files**: `reports/release-20260928/`, `crawl-worker/DEPLOY-NOTES.md`
**Test**: Read-only authenticated code-search status for existing pool entries, exact runtime/config identities and guarded deployment recipe; after independent root approval, valid completed size-bisect sweep evidence.

### T-026: Reuse database pools only in the long-running Node runtime
**AC**: AC-REL-02
**Files**: `src/lib/db.ts`, `src/lib/__tests__/db-worker-context.test.ts`
**Test**: Runtime regression tests prove Node requests reuse one pool while Cloudflare and explicit worker contexts create fresh clients; all required 0826 browser tests pass with PostgreSQL max_connections=100, no CI capacity increase.

### T-027: Resume adaptive GitHub planning and crawling without losing coverage or intake
**AC**: AC-US3-05, AC-US3-06, AC-US4-01
**Files**: `src/app/api/v1/internal/vm-heartbeat/route.ts`, `src/app/api/v1/internal/vm-heartbeat/__tests__/route.test.ts`, `src/lib/alerts/detectors.ts`, `src/app/api/v1/submissions/bulk/route.ts`, `src/app/api/v1/submissions/bulk/__tests__/route.skillpath-validation.test.ts`, `src/app/api/v1/submissions/bulk/__tests__/route.intake.test.ts`, `crawl-worker/lib/adaptive-search-plan.js`, `crawl-worker/sources/github-sharded.js`, `crawl-worker/lib/source-result.js`, `crawl-worker/lib/inline-submitter.js`, `crawl-worker/scheduler.js`, `crawl-worker/__tests__/adaptive-search-plan.test.js`, `crawl-worker/__tests__/adaptive-search-resume.test.js`, `crawl-worker/__tests__/source-result.test.js`, `crawl-worker/__tests__/inline-submitter.test.js`, `crawl-worker/__tests__/scheduler.test.js`, `crawl-worker/__tests__/github-sharded.test.js`, `crawl-worker/__tests__/github-sharded-crawl.test.js`, `crawl-worker/__tests__/github-sharded-failure.test.js`, `crawl-worker/DEPLOY-NOTES.md`
**Test**: Node22 crawler suite plus fake GitHub/intake HTTP tests across fresh process restarts; validated leaves drain while planning remains pending; planning/page/request budget boundaries retain exact pending state, version/config/legacy mismatch never overwrites, open-ended tails are preserved, capped leaves report incomplete coverage, accepted and durable-deferred work is not resubmitted after partial failure, per-item errors do not advance, private/internal and unknown-visibility inputs never enter the public intake or identity proof, and continuation never produces a completion/dead-man success. Only typed permanent validation receipts may settle rejected input, with totalRejected separate and no known-key warming. Missing mutable content and transient failures stay retryable. Independent review required before deployment; adaptive remains off in production until approved.

**2026-09-28 telemetry amendment**: Preserve the new safe sweep metadata through the authenticated heartbeat receiver and SourceObservation type. Allow only bounded enums/UUID/checksum, booleans and nonnegative safe-integer counters; reject raw identities, path/payload fields and malformed values. Legacy counter mapping remains unchanged. Worktree `0874-heartbeat-progress`, branch `codex/0874-heartbeat-progress`, base `4b7888a19ebce292b3f77d49c052fad31abfe90a`. Reproduce dropped metadata before implementation, then verify receiver, detector and full platform suites and independent root review before release.

### T-028: Bound bulk intake Prisma lifetime to one request
**AC**: AC-US2-01; production intake must not multiply Prisma clients per entry or share Worker I/O across requests.
**Files**: `src/lib/db.ts`, `src/lib/__tests__/db-request-scope.test.ts`, `src/app/api/v1/submissions/bulk/route.ts`, `src/app/api/v1/submissions/bulk/__tests__/route.db-lifecycle.test.ts`
**Test**: Node 22 Vitest request-scope, real-helper bulk lifecycle, existing DB Worker isolation and all bulk intake suites; full platform tests; Worker build and required CI.
**Contract**: Reproduce per-entry client fan-out before implementation. Add explicit asynchronous request scope around bulk handler only; lazy concurrent-safe client reuse within one scope, separate concurrent request connections, no global Hyperdrive URL/client reuse inside scope. Close scope before bounded best-effort disposal; preserve original response/error; reject detached work after close. Keep existing Node singleton/unscoped Worker behavior. No crawler restart, checkpoint reset, manual replay, credentials or submission-policy changes. Independent review before release.
**Evidence**: Real VM3 intake Cloudflare tail returned HTTP 503 / exceededMemory twice; `/tmp/cc-work-release-20260928/0874/t027-tail-receipt-extended.json`. The real-helper regression reproduced 150 clients for 50 entries; the repair uses one owned client. Reviewed 3967d744 merged as 789f423b and deployed as Worker9544aae4 with guards verified. A natural one-item HTTP200 is not a full production batch-load proof; T030 owns the separately observed uniqueness failure, and T027/T017 sweep gates remain open. Owner codex-0874-crawler, isolated branch `codex/0874-bulk-request-memory` from `8d0929aa80628b6d8a43a8f4327f9881a97ad3ee`.

### T-029: Keep registered VM source telemetry and detector state isolated
**AC**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US4-01
**Files**: `src/lib/alerts/source-observations.ts`, `src/lib/alerts/__tests__/source-observations.test.ts`, `src/lib/alerts/detectors.ts`, `src/lib/alerts/__tests__/detectors.test.ts`, `src/app/api/v1/internal/vm-heartbeat/route.ts`, `src/app/api/v1/internal/vm-heartbeat/__tests__/route.test.ts`, `src/app/api/v1/internal/alerts-evaluator/route.ts`, `src/app/api/v1/internal/alerts-evaluator/__tests__/route.test.ts`, `src/app/api/v1/admin/queue-health/route.ts`, `src/app/api/v1/admin/queue-health/__tests__/route.test.ts`
**Test**: Node 22 focused receiver, scoped-reader, detector, evaluator and admin tests; full platform suite; Worker build and required CI. Reproduce interleaved VM overwrite first, then prove independent source histories/baselines/dedup, missing/stale VM semantics, bounded input and concurrency, no malformed/read-error legacy fallback, no raw payload persistence.
**Contract**: New isolated worktree `0874-vm-observations` on `codex/0874-vm-observations` from merged789f423b. Keep aggregate compatibility, add versioned per-registered-VM records, read configured identities only and preserve server-clock freshness. No production heartbeat injection, VM restart, checkpoint change, credential change or deployment before independent review and safe T028 runtime verification.

### T-030: Resolve intake uniqueness races through the exact canonical tuple
**AC**: AC-US2-01
**Acceptance**: Reuse only an exact complete canonical tuple after natural/legacy uniqueness conflicts, including rename and case changes. Preserve published, pending, blocked and rejected states and tenant/private/path/source boundaries. Unknown constraints, other errors and deleted-row races stay explicit retryable errors; never acknowledge an empty-ID pending result or false skip.
**Files**: `src/lib/submission/upsert.ts`, `src/lib/submission/__tests__/upsert.test.ts`, `src/lib/submission/__tests__/upsert-natural-key.test.ts`, `src/app/api/v1/submissions/bulk/__tests__/route.identity-collision.test.ts`
**Test**: npm test -- src/lib/submission/__tests__ src/app/api/v1/submissions/bulk/__tests__
**Verification**: Deterministic red/green natural-key regression receipt; full required checks and independent review before release.
**Contract**: Owner `codex-0874-intake-identity` (live_activity), isolated worktree `0874-intake-identity`, branch `codex/0874-intake-identity`, base `789f423b102d728cac91e808b8369d40e27d9e53`. Integrate the actual merged T029 base before final tests/CI and a separate Worker release. No schema, production database, credential, crawler, checkpoint, scheduler or scanner changes; no manual replay or synthetic production intake. Root authorized after exact uniqueness proof; evidence stays sanitized.
