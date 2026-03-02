# Tasks: Pull-based SAST Scanner

---
increment: 0396-pull-based-sast-scanner
total_tasks: 11
completed: 0
by_user_story:
  US-003: [T-001]
  US-001: [T-002, T-003]
  US-002: [T-004, T-005]
  US-005: [T-006, T-007]
  US-004: [T-008, T-009]
  US-006: [T-010, T-011]
---

## Phase 1: Schema + Platform API

### User Story: US-003 - Schema Migration for Claim Tracking

**Linked ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04
**Tasks**: 1 total, 0 completed

#### T-001: Add claimedAt and claimedBy columns to ExternalScanResult

**User Story**: US-003
**Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04
**Status**: [ ] pending

**Test Plan**:
- **Given** the existing ExternalScanResult Prisma model
- **When** a migration adds nullable `claimedAt DateTime?` and `claimedBy String?` columns
- **Then** the migration runs without data loss, existing rows get null for both columns, and `@@index([status])` is retained

**Test Cases**:
1. **Unit**: Verify Prisma schema compiles after change (`npx prisma validate`)
2. **Integration**: Run `npx prisma migrate dev` against test DB, verify column existence via raw SQL

**Implementation**:
1. Add `claimedAt DateTime?` and `claimedBy String?` to `ExternalScanResult` in `prisma/schema.prisma`
2. Run `npx prisma migrate dev --name add-claim-tracking-to-external-scan`
3. Run `npx prisma generate`
4. Verify `@@index([status])` still present

**Dependencies**: None

---

### User Story: US-001 - Platform API for Pending SAST Scans

**Linked ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04
**Tasks**: 2 total, 0 completed

#### T-002: Implement GET /api/v1/internal/pending-sast-scans endpoint

**User Story**: US-001
**Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04
**Status**: [ ] pending

**Test Plan**:
- **Given** ExternalScanResult rows with various statuses (PENDING, RUNNING with stale claimedAt, PASS, FAIL)
- **When** GET /api/v1/internal/pending-sast-scans is called with valid X-Internal-Key
- **Then** returns only PENDING rows + RUNNING rows where claimedAt >15min, ordered by dispatchedAt ASC, limited to 50, with repoUrl from Skill join

**Test Cases**:
1. **Unit**: `src/app/api/v1/internal/pending-sast-scans/__tests__/route.test.ts`
   - testReturns401WithoutInternalKey(): Missing auth header
   - testReturnsPendingScansOrderedByDispatchedAt(): PENDING rows only
   - testReturnsStuckRunningScans(): RUNNING with claimedAt >15min ago
   - testExcludesRecentlyClaimedRunning(): RUNNING with claimedAt <15min excluded
   - testExcludesTerminalStatuses(): PASS/FAIL/TIMED_OUT rows excluded
   - testLimitsTo50ByDefault(): Default limit enforcement
   - testJoinsSkillForRepoUrl(): Response includes repoUrl from Skill table
   - **Coverage Target**: 90%

**Implementation**:
1. Create `src/app/api/v1/internal/pending-sast-scans/route.ts`
2. Add X-Internal-Key auth check (match existing `internal/pending-submissions` pattern)
3. Raw SQL query joining ExternalScanResult + Skill on skillName
4. WHERE: `status='PENDING' OR (status='RUNNING' AND claimedAt < NOW() - 15min)`
5. ORDER BY dispatchedAt ASC, LIMIT from query param (max 200, default 50)
6. Return `{ scans: [...], count }` response shape

**Dependencies**: T-001

---

#### T-003: Write tests for pending-sast-scans endpoint

**User Story**: US-001
**Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04
**Status**: [ ] pending

**Test Plan**:
- **Given** mocked Prisma DB with ExternalScanResult + Skill data
- **When** various request scenarios are tested
- **Then** auth, filtering, ordering, limit, and response shape are all correct

**Implementation**:
1. Create `src/app/api/v1/internal/pending-sast-scans/__tests__/route.test.ts`
2. Mock DB with `vi.hoisted()` + `vi.mock("@/lib/db")`
3. Test all 7 cases from T-002 test plan
4. Run `npx vitest run` to verify

**Dependencies**: T-002

---

### User Story: US-002 - Atomic Claim Endpoint for SAST Scans

**Linked ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04
**Tasks**: 2 total, 0 completed

#### T-004: Implement POST /api/v1/internal/claim-sast-scan endpoint

**User Story**: US-002
**Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04
**Status**: [ ] pending

**Test Plan**:
- **Given** a PENDING ExternalScanResult row with id "scan-1"
- **When** POST /api/v1/internal/claim-sast-scan is called with `{ scanId: "scan-1", claimedBy: "vm2:9600" }`
- **Then** the row is atomically updated to RUNNING with claimedAt=now, claimedBy="vm2:9600", and response is `{ ok: true, scan: {...} }`

**Test Cases**:
1. **Unit**: `src/app/api/v1/internal/claim-sast-scan/__tests__/route.test.ts`
   - testReturns401WithoutInternalKey(): Auth enforcement
   - testSuccessfulClaimOfPendingScan(): PENDING -> RUNNING transition
   - testSuccessfulReclaimOfStuckScan(): RUNNING + stale claimedAt -> reclaimed
   - testAlreadyClaimedReturnsConflict(): count=0 -> `{ ok: false, reason: "already_claimed" }`
   - testMissingScanIdReturns400(): Validation
   - testResponseShapeOnSuccess(): Verify `{ ok: true, scan: { id, skillName, provider, status } }`
   - **Coverage Target**: 90%

**Implementation**:
1. Create `src/app/api/v1/internal/claim-sast-scan/route.ts`
2. X-Internal-Key auth check
3. Parse body: `{ scanId, claimedBy }`
4. Prisma `updateMany` with WHERE: `id = scanId AND (status='PENDING' OR (status='RUNNING' AND claimedAt < NOW()-15min))`
5. SET: `status='RUNNING', claimedAt=new Date(), claimedBy`
6. If count === 0 -> `{ ok: false, reason: "already_claimed" }`
7. If count > 0 -> fetch updated row, return `{ ok: true, scan: {...} }`

**Dependencies**: T-001

---

#### T-005: Write tests for claim-sast-scan endpoint

**User Story**: US-002
**Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04
**Status**: [ ] pending

**Test Plan**:
- **Given** mocked Prisma DB with updateMany returning count 0 or 1
- **When** various claim scenarios are tested
- **Then** atomicity, auth, and response shapes are correct

**Implementation**:
1. Create `src/app/api/v1/internal/claim-sast-scan/__tests__/route.test.ts`
2. Mock DB updateMany + findUnique
3. Test all 6 cases from T-004 test plan
4. Run `npx vitest run` to verify

**Dependencies**: T-004

---

## Phase 2: Enqueue + Crawl Source

### User Story: US-005 - Lightweight Enqueue (Feature-Flagged Push Bypass)

**Linked ACs**: AC-US5-01, AC-US5-02, AC-US5-03, AC-US5-04, AC-US5-05
**Tasks**: 2 total, 0 completed

#### T-006: Add SAST_PULL_MODE feature flag to dispatchExternalScans

**User Story**: US-005
**Satisfies ACs**: AC-US5-01, AC-US5-02, AC-US5-03, AC-US5-04, AC-US5-05
**Status**: [ ] pending

**Test Plan**:
- **Given** `SAST_PULL_MODE=true` in Cloudflare env
- **When** `dispatchExternalScans()` is called
- **Then** it writes PENDING to KV + upserts DB row, but makes zero HTTP calls to scanner workers

- **Given** `SAST_PULL_MODE` absent or falsy
- **When** `dispatchExternalScans()` is called
- **Then** existing push behavior is preserved unchanged (round-robin POST to SCANNER_WORKERS)

**Test Cases**:
1. **Unit**: `src/lib/__tests__/external-scan-dispatch.test.ts`
   - testPullModeWritesKvAndDb(): SAST_PULL_MODE=true -> KV + DB writes, no HTTP fetch
   - testPullModeSkipsDuplicatePendingOrRunning(): Dedup logic in pull mode
   - testPushModePreservedWhenFlagFalsy(): Existing behavior unchanged
   - testPushModePreservedWhenFlagAbsent(): Undefined env -> push path
   - testAllThreeProvidersEnqueued(): semgrep, njsscan, trufflehog all get DB rows
   - **Coverage Target**: 90%

**Implementation**:
1. Add `SAST_PULL_MODE?: string` to `CloudflareEnv` in `src/lib/env.d.ts`
2. In `dispatchExternalScans()`, after KV PENDING write, check `env.SAST_PULL_MODE`
3. If truthy: upsert `ExternalScanResult` with status=PENDING via `getDb()`, then `continue` (skip HTTP)
4. If falsy: existing push code runs unchanged
5. DB upsert uses `skipDuplicates` WHERE status IN ('PENDING','RUNNING')

**Dependencies**: T-001

---

#### T-007: Write tests for feature-flagged dispatch

**User Story**: US-005
**Satisfies ACs**: AC-US5-01, AC-US5-02, AC-US5-03
**Status**: [ ] pending

**Test Plan**:
- **Given** mocked env with SAST_PULL_MODE set/unset
- **When** dispatchExternalScans() is called
- **Then** correct path executes based on flag

**Implementation**:
1. Create or extend `src/lib/__tests__/external-scan-dispatch.test.ts`
2. Mock CF env, KV, DB, and global fetch
3. Test all 5 cases from T-006 test plan
4. Verify zero fetch calls in pull mode, fetch calls in push mode

**Dependencies**: T-006

---

### User Story: US-004 - Crawl-Worker SAST Scanner Source

**Linked ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04, AC-US4-05, AC-US4-06
**Tasks**: 2 total, 0 completed

#### T-008: Implement sast-scanner.js crawl-worker source

**User Story**: US-004
**Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04, AC-US4-05, AC-US4-06
**Status**: [ ] pending

**Test Plan**:
- **Given** platform API returns 3 pending scans, scanner-worker on localhost:9500 is healthy
- **When** `crawl(config)` is called
- **Then** it claims each scan, dispatches to localhost:9500 with correct payload format, and returns `{ checked: 3, dispatched: 3, skipped: 0, errors: 0 }`

- **Given** platform API returns 2 pending scans, 1 claim fails (already claimed)
- **When** `crawl(config)` is called
- **Then** it dispatches 1, skips 1, returns `{ checked: 2, dispatched: 1, skipped: 1, errors: 0 }`

**Test Cases**:
1. **Unit**: `crawl-worker/sources/__tests__/sast-scanner.test.js`
   - testFetchesPendingAndClaimsSequentially(): Full happy path
   - testSkipsAlreadyClaimedScans(): claim returns ok:false
   - testParsesRepoUrlToOwnerAndName(): github.com/owner/repo -> { owner, repo }
   - testUsesWorkerSecretForScannerAuth(): X-Worker-Signature header
   - testConstructsCorrectCallbackUrl(): {platformUrl}/api/v1/webhooks/scan-results
   - testReturnsStatsObject(): { checked, dispatched, skipped, errors }
   - testHandlesEmptyPendingList(): No scans -> { checked: 0, dispatched: 0, ... }
   - **Coverage Target**: 90%

**Implementation**:
1. Create `crawl-worker/sources/sast-scanner.js`
2. Export default `async function crawl(config)` matching source contract
3. Fetch pending: `GET {config.platformUrl}/api/v1/internal/pending-sast-scans` with X-Internal-Key
4. For each scan: POST claim, parse repoUrl, POST to localhost:9500/scan
5. Sequential processing (no parallelism within a cycle)
6. Return stats summary

**Dependencies**: T-002, T-004

---

#### T-009: Write tests for sast-scanner source

**User Story**: US-004
**Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04, AC-US4-05, AC-US4-06
**Status**: [ ] pending

**Test Plan**:
- **Given** mocked fetch for platform API and scanner-worker
- **When** various crawl scenarios are tested
- **Then** claim flow, payload format, auth headers, and stats are correct

**Implementation**:
1. Create `crawl-worker/sources/__tests__/sast-scanner.test.js`
2. Mock global fetch to intercept platform API + scanner-worker calls
3. Test all 7 cases from T-008 test plan
4. Run tests with Node test runner or Vitest

**Dependencies**: T-008

---

## Phase 3: Scheduler Integration + Deploy

### User Story: US-006 - Scheduler Integration and VM Deployment

**Linked ACs**: AC-US6-01, AC-US6-02, AC-US6-03, AC-US6-04
**Tasks**: 2 total, 0 completed

#### T-010: Register sast-scanner in scheduler and server configs

**User Story**: US-006
**Satisfies ACs**: AC-US6-01, AC-US6-02, AC-US6-03, AC-US6-04
**Status**: [ ] pending

**Test Plan**:
- **Given** the scheduler.js SOURCE_TIMEOUTS and SOURCE_COOLDOWNS maps
- **When** sast-scanner is added
- **Then** timeout is 30min, cooldown is 30s, and sast-scanner is in VALID_SOURCES

**Implementation**:
1. Add `"sast-scanner": 30 * 60 * 1000` to SOURCE_TIMEOUTS in `crawl-worker/scheduler.js`
2. Add `"sast-scanner": 30 * 1000` to SOURCE_COOLDOWNS in `crawl-worker/scheduler.js`
3. Add `"sast-scanner"` to VALID_SOURCES array in `crawl-worker/server.js`
4. Add `sast-scanner` to ASSIGNED_SOURCES in `crawl-worker/.env.vm2`

**Dependencies**: T-008

---

#### T-011: Deploy and verify end-to-end pull-based SAST scanning

**User Story**: US-006
**Satisfies ACs**: AC-US6-01, AC-US6-02, AC-US6-03, AC-US6-04
**Status**: [ ] pending

**Test Plan**:
- **Given** SAST_PULL_MODE=true set as CF secret, sast-scanner deployed on VM-2
- **When** a skill is published (triggering dispatchExternalScans)
- **Then** PENDING rows appear in DB, sast-scanner source on VM-2 picks them up, claims, dispatches to scanner-worker, and webhook callback completes the cycle

**Implementation**:
1. `npx wrangler secret put SAST_PULL_MODE` (value: "true")
2. Build and deploy platform: `npm run db:generate && npm run build && npm run build:worker && npm run deploy`
3. Deploy crawl-worker to VM-2 via deploy.sh
4. Trigger manual scan via admin endpoint, monitor VM-2 crawl-worker logs
5. Verify ExternalScanResult rows transition: PENDING -> RUNNING -> PASS/FAIL

**Dependencies**: T-010
