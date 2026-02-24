# Tasks — 0349 Persistent Verification Reports

### T-001: Add missing fields to ScanResult schema
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03 | **Status**: [x] completed
**Test**: Given schema.prisma → When migration runs → Then ScanResult has dependencyRisk (Json?), scriptScanSummary (Json?), commitSha (String?) fields

Add to `ScanResult` model in `prisma/schema.prisma`:
- `dependencyRisk Json?` — dependency analysis data
- `scriptScanSummary Json?` — script scanner data
- `commitSha String?` — git commit SHA at scan time

### T-002: Add compound index to Submission
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01 | **Status**: [x] completed
**Test**: Given schema.prisma → When migration runs → Then Submission has @@index([repositoryId, skillName])

Add `@@index([repositoryId, skillName])` to the `Submission` model for efficient package history queries.

### T-003: Run Prisma migration
**User Story**: US-001, US-004 | **Satisfies ACs**: AC-US1-03, AC-US4-01 | **Status**: [x] completed
**Test**: Given schema changes → When `npx prisma migrate dev` runs → Then migration succeeds and `npx prisma generate` completes

### T-004: Add DB dual-write to createSubmission()
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-04, AC-US2-05 | **Status**: [x] completed
**Test**: Given a new submission → When createSubmission() is called → Then both KV and DB have the Submission record

In `src/lib/submission-store.ts`, after KV writes, add:
```
db.submission.create({ data: { id, repoUrl, skillName, skillPath, submitterEmail, userId, state: "RECEIVED" } }).catch(...)
```

### T-005: Add DB dual-write to createSubmissionsBatch()
**User Story**: US-002 | **Satisfies ACs**: AC-US2-02, AC-US2-04 | **Status**: [x] completed
**Test**: Given a batch of submissions → When createSubmissionsBatch() is called → Then DB has all Submission rows

### T-006: Add DB dual-write to updateState()
**User Story**: US-002 | **Satisfies ACs**: AC-US2-03, AC-US2-04 | **Status**: [x] completed
**Test**: Given a state transition → When updateState() is called → Then DB Submission.state is updated AND a SubmissionStateEvent row is created with fromState, toState, trigger, actor

Capture `previousState` before KV update, then:
```
db.submission.update({ where: { id }, data: { state: newState } })
db.submissionStateEvent.create({ data: { submissionId: id, fromState, toState, trigger, actor: "worker", actorType: "worker" } })
```

### T-007: Add DB dual-write to storeScanResult()
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04 | **Status**: [x] completed
**Test**: Given a scan completion → When storeScanResult() is called → Then a ScanResult row exists in DB with tier, verdict, score, findings, dependencyRisk, scriptScanSummary, commitSha

Map `StoredScanResult` fields to Prisma `ScanResult` model fields. Map verdict strings to `ScanVerdict` enum (PASS/CONCERNS/FAIL). Store the full findings JSON.

### T-008: Add DB fallback to getSubmissionFull()
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04 | **Status**: [x] completed
**Test**: Given KV data has expired (returns null) → When getSubmissionFull() is called → Then data is loaded from DB and mapped to StoredSubmission/StoredScanResult/StateHistoryEntry shapes

When `subRaw` is null, query:
```
db.submission.findUnique({ where: { id }, include: { scanResults: { orderBy: { createdAt: "desc" } }, stateEvents: { orderBy: { createdAt: "asc" } } } })
```
Map DB models back to KV shapes for API compatibility.

### T-009: Create package history API endpoint
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04 | **Status**: [x] completed
**Test**: Given submissions exist for owner/repo/skill → When GET /api/v1/packages/:owner/:repo/:skillName/history is called → Then paginated history with scan results and state events is returned

New file: `src/app/api/v1/packages/[owner]/[repo]/[skillName]/history/route.ts`

### T-010: Create latest report API endpoint
**User Story**: US-004 | **Satisfies ACs**: AC-US4-05 | **Status**: [x] completed
**Test**: Given submissions exist → When GET /api/v1/packages/:owner/:repo/:skillName/latest → Then the most recent submission with full scan data is returned

New file: `src/app/api/v1/packages/[owner]/[repo]/[skillName]/latest/route.ts`

### T-011: Write tests for DB dual-write functions
**User Story**: US-001, US-002, US-003 | **Satisfies ACs**: AC-US1-01, AC-US2-01, AC-US3-01 | **Status**: [x] completed
**Test**: Unit tests verify DB writes happen alongside KV writes, DB fallback works when KV returns null, and verdict mapping is correct

### T-012: Write tests for package history endpoints
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-05 | **Status**: [x] completed
**Test**: API tests verify history endpoint returns paginated results and latest endpoint returns most recent submission
