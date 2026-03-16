---
increment: 0462-rescan-published-trust-elevation
total_tasks: 2
completed_tasks: 2
by_user_story:
  US-001: [T-001]
  US-002: [T-001, T-002]
---

# Tasks: Rescan Published Skills for Trust Elevation

## User Story: US-001 - Rescan Published Skills Endpoint

**Linked ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05
**Tasks**: 1 total, 0 completed

### T-001: Implement POST /api/v1/admin/rescan-published route with tests

**User Story**: US-001, US-002
**Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05, AC-US2-01, AC-US2-02, AC-US2-03
**Status**: [x] completed

**Test Plan**:
- **Given** a POST with `{ "dryRun": true }` and valid auth
- **When** executed against a DB with published T1/T2 skills
- **Then** returns `{ ok, dryRun: true, eligibleCount, wouldCreate }` without writing any records

- **Given** a live call with valid auth
- **When** executed
- **Then** creates up to 500 Submission records (state: RECEIVED), SubmissionStateEvent records with trigger "rescan-published: trust elevation" / actor "system", enqueues to SUBMISSION_QUEUE in chunks of 100, returns `{ ok, created, enqueued, hasMore }`

- **Given** skills with a pending (non-terminal) Submission already exist
- **When** the endpoint runs
- **Then** those skills are excluded from the batch (AC-US1-03)

- **Given** skills with trustTier T0 or on the active blocklist
- **When** the endpoint runs
- **Then** those skills are excluded (AC-US1-04)

- **Given** `{ "skipExistingT2": true }` in the body
- **When** the endpoint runs
- **Then** skills with an existing Tier 2 ScanResult are excluded (AC-US1-05)

- **Given** more than 500 eligible skills remain after a batch
- **When** the response is returned
- **Then** `hasMore: true` is set (AC-US2-01)

- **Given** a request with missing or invalid X-Internal-Key / Bearer token
- **When** the endpoint is called
- **Then** returns 401/403 (AC-US2-03)

**Test Cases**:
1. **Unit**: `src/app/api/v1/admin/rescan-published/__tests__/route.test.ts`
   - `testDryRunReturnsCountsOnly()`: dryRun:true returns eligibleCount/wouldCreate, no DB writes
   - `testLivePathCreatesSubmissionsAndEvents()`: creates Submissions + StateEvents, enqueues in 100-chunk batches
   - `testSkipsSkillsWithPendingSubmissions()`: skills with non-terminal Submission excluded
   - `testSkipsT0AndBlocklistedSkills()`: trustTier T0 and active blocklist entries excluded
   - `testSkipExistingT2Filter()`: skipExistingT2:true excludes skills with tier-2 ScanResult
   - `testHasMoreWhenFullBatch()`: 500 created → hasMore:true; fewer → hasMore:false
   - `testRejectsUnauthorizedRequest()`: missing credentials → 401
   - `testAcceptsXInternalKey()`: valid X-Internal-Key bypasses requireAdmin
   - `testQueueChunking()`: 200 skills → 2 sendBatch calls of 100 each
   - `testAuditEventShape()`: StateEvent has correct trigger, actor, actorType, toState RECEIVED
   - **Coverage Target**: 90%

**Implementation**:
1. Create `src/app/api/v1/admin/rescan-published/route.ts`
2. Auth gate: copy X-Internal-Key || requireAdmin/isAuthError pattern from bulk-reprocess
3. Parse body: `dryRun?: boolean`, `skipExistingT2?: boolean`
4. Build Prisma `where` for Skill: `trustTier: { in: ["T1","T2"] }`, exclude T0, exclude active blocklist names via `name: { notIn: activeBlocklistNames }`, `submissions: { none: { state: { in: NON_TERMINAL_STATES } } }`, optional `submissions: { none: { scanResults: { some: { tier: 2 } } } }`
5. Dry-run path: count eligible, return `{ ok, dryRun: true, eligibleCount, wouldCreate: Math.min(count, 500) }`
6. Live path: `db.skill.findMany({ where, select: { id, name, repoUrl, skillPath }, take: 500 })`
7. `db.submission.createMany(...)` with state RECEIVED, skillId set — map created IDs
8. `db.submissionStateEvent.createMany(...)` with trigger "rescan-published: trust elevation", actor "system", actorType "admin", toState RECEIVED
9. Enqueue chunks of 100 via `env.SUBMISSION_QUEUE.sendBatch(...)` using `process_submission` message shape
10. Return `{ ok, created, enqueued, hasMore: rows.length === 500, errors }`
11. Create `__tests__/route.test.ts` using vi.hoisted() mock pattern; mock `@/lib/db`, `@/lib/auth`, `@opennextjs/cloudflare`

---

## User Story: US-002 - Deploy and Trust-Backfill Verification

**Linked ACs**: AC-US2-01, AC-US2-02
**Tasks**: 1 total, 0 completed

### T-002: Deploy to production and run dry-run verification

**User Story**: US-002
**Satisfies ACs**: AC-US2-01, AC-US2-02
**Status**: [x] completed

**Test Plan**:
- **Given** T-001 is complete and all unit tests pass
- **When** deployed to Cloudflare Workers and dry-run curl is executed
- **Then** response shows eligible T1/T2 skill count (~34k) with no DB changes

- **Given** a single live batch is executed
- **When** complete
- **Then** response shows `created: 500, hasMore: true` and SubmissionStateEvent records in DB have correct trigger

**Test Cases**:
1. **Manual verification** (user-triggered):
   - Dry-run curl → confirm eligibleCount in expected range
   - Live batch curl → confirm `created: 500, hasMore: true`
   - DB query `SELECT count(*) FROM "SubmissionStateEvent" WHERE trigger = 'rescan-published: trust elevation'` → 500 rows
   - Confirm no duplicate submissions for skills with pending pipeline runs
   - **Coverage Target**: 100% of AC scenarios exercised

**Implementation**:
1. Run `npx vitest run src/app/api/v1/admin/rescan-published` — all tests must pass
2. Deploy: `cd repositories/anton-abyzov/vskill-platform && npm run db:generate && npm run build && npm run build:worker && npm run deploy`
3. Dry-run: `curl -s -X POST https://vskill.com/api/v1/admin/rescan-published -H "X-Internal-Key: $INTERNAL_BROADCAST_KEY" -H "Content-Type: application/json" -d '{"dryRun":true}'`
4. Verify eligibleCount matches expected ~34k T1/T2 skills
5. Live batch (user decision — ask before running): `curl -s -X POST ... -H "..." -H "..." -d '{}'`
6. Update spec.md ACs to [x] after manual verification passes
