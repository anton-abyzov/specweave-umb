---
status: completed
---
# 0349 — Persistent Verification Reports & Package History

## Problem

Scan results for submitted skills are stored exclusively in Cloudflare KV with a 7-day TTL. After expiry, submission pages return 404 and all verification data is lost. The Prisma `ScanResult`, `SubmissionStateEvent` models exist in the schema but are never populated by the automated pipeline. There is also no way to query the verification history for a given package (owner + repo + skill).

Additionally, `Submission` records are only created in KV — the `db.submission.update()` calls to link repositories silently fail because no DB row exists.

## User Stories

### US-001 — Persistent Scan Results

**As a** skill author,
**I want** my submission's scan results to be permanently stored in the database,
**so that** I can always view the detailed verification report regardless of when I submitted.

#### Acceptance Criteria

- [x] AC-US1-01: `storeScanResult()` writes a `ScanResult` row to Prisma DB alongside the existing KV write
- [x] AC-US1-02: DB write is best-effort (`.catch()`) — KV hot-path latency is not affected
- [x] AC-US1-03: All `StoredScanResult` fields are captured in DB (including `dependencyRisk`, `scriptScanSummary`, `commitSha` via new schema fields)
- [x] AC-US1-04: Each scan tier (1 and 2) creates a separate `ScanResult` row linked to the submission

### US-002 — Persistent Submission Records & State Events

**As a** platform operator,
**I want** submission records and state transitions to be persisted in the database,
**so that** I have a durable audit trail and can query submissions after KV expiry.

#### Acceptance Criteria

- [x] AC-US2-01: `createSubmission()` creates a `Submission` row in Prisma DB alongside KV write
- [x] AC-US2-02: `createSubmissionsBatch()` creates DB rows for all submissions in the batch
- [x] AC-US2-03: `updateState()` updates `Submission.state` in DB and creates a `SubmissionStateEvent` row
- [x] AC-US2-04: All DB writes are best-effort — pipeline never blocks on DB failures
- [x] AC-US2-05: Repository linking (`db.submission.update({ repositoryId })`) succeeds because DB row now exists

### US-003 — DB Fallback for Expired Submissions

**As a** skill author,
**I want** the submission detail page to show results even after KV data expires,
**so that** I can reference my verification report at any time.

#### Acceptance Criteria

- [x] AC-US3-01: `getSubmissionFull()` falls back to DB when KV returns null (expired)
- [x] AC-US3-02: DB data is mapped back to `StoredSubmission` / `StoredScanResult` / `StateHistoryEntry` shapes
- [x] AC-US3-03: The `/submit/[id]` page renders correctly from DB-backed data (same UI, no changes needed)
- [x] AC-US3-04: KV remains the hot-path for in-flight submissions (no latency regression)

### US-004 — Package History API

**As a** platform user,
**I want** to view the full verification history for a package,
**so that** I can see all past submissions, their outcomes, and reasons for approval/rejection.

#### Acceptance Criteria

- [x] AC-US4-01: `GET /api/v1/packages/:owner/:repo/:skillName/history` returns paginated submission history
- [x] AC-US4-02: Each history entry includes submission state, scan results (per tier), and state events
- [x] AC-US4-03: Response includes the linked published `Skill` record if one exists
- [x] AC-US4-04: Results are ordered by `createdAt` descending (newest first)
- [x] AC-US4-05: `GET /api/v1/packages/:owner/:repo/:skillName/latest` returns the most recent submission report

## Technical Notes

- **Package identity**: `Repository(owner, name)` + `Submission.skillName` — the Repository model already has `@@unique([owner, name])`
- **No new models**: Reuse existing `ScanResult`, `SubmissionStateEvent`, `Submission` models
- **Schema additions**: 3 new fields on `ScanResult` (`dependencyRisk`, `scriptScanSummary`, `commitSha`) + compound index on `Submission`
- **DB access pattern**: Uses existing `getDb()` helper with 8-second query timeout
- **Migration strategy**: Forward-only. Old expired KV data is lost. New submissions persist to DB going forward.

## Out of Scope

- SkillVersion creation on publish (separate increment)
- UI pages for package history (API-only for now)
- Backfill of existing KV data to DB
- Increasing KV TTL
