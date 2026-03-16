# Implementation Plan: Rescan Published Skills for Trust Elevation

## Overview

Single new admin endpoint (`POST /api/v1/admin/rescan-published`) in vskill-platform that queries the Skill table for published skills with trustTier T1 or T2, creates fresh Submission records in RECEIVED state, and enqueues them to CF SUBMISSION_QUEUE for full T1+T2 scanning. The existing pipeline (processSubmission, publishSkill) handles the rest unchanged.

The implementation follows the `bulk-reprocess/route.ts` pattern exactly: same auth, batching (500 per call, 100 per queue chunk), response shape, and audit trail.

## Architecture

### Single Component

**`src/app/api/v1/admin/rescan-published/route.ts`** -- Next.js Route Handler (POST)

No other files are created or modified. The endpoint is self-contained.

### Data Flow

```
Admin (curl/CLI)
    |
    | POST /api/v1/admin/rescan-published
    | Headers: X-Internal-Key | Authorization: Bearer <SUPER_ADMIN>
    | Body: { dryRun?: boolean, skipExistingT2?: boolean }
    |
    v
[Auth Gate] -- same requireAdmin / X-Internal-Key as bulk-reprocess
    |
    v
[Query Skill table] -- trustTier IN ("T1","T2"), NOT T0/blocked, NOT on active blocklist
    |                    LEFT JOIN Submission to skip skills with pending (non-terminal) submissions
    |                    Optional: skip skills that already have a Tier 2 ScanResult
    |
    v
[Create Submission records] -- db.submission.createMany (state: RECEIVED)
    |
    v
[Create SubmissionStateEvent audit records] -- trigger: "rescan-published: trust elevation"
    |
    v
[Enqueue to SUBMISSION_QUEUE] -- chunks of 100, same message shape as bulk-reprocess
    |
    v
[Return JSON response] -- { ok, dryRun, created, enqueued, hasMore, errors? }
```

### Data Model

No schema changes. Uses existing models:

```
Skill (query source)
----------------------------------
id             UUID PK
name           TEXT UNIQUE
repoUrl        TEXT
skillPath      TEXT?
trustTier      TEXT ("T0"-"T4")
...

Submission (created records)
----------------------------------
id             UUID PK
repoUrl        TEXT
skillName      TEXT
skillPath      TEXT
state          SubmissionState (RECEIVED)
skillId        UUID? FK -> Skill.id
...

SubmissionStateEvent (audit trail)
----------------------------------
submissionId   UUID FK
fromState      NULL (new record)
toState        RECEIVED
trigger        "rescan-published: trust elevation"
actor          "system"
actorType      "admin"

BlocklistEntry (exclusion check)
----------------------------------
skillName      TEXT
isActive       BOOLEAN
```

### API Contract

**`POST /api/v1/admin/rescan-published`**

Request:
```json
{
  "dryRun": true,
  "skipExistingT2": false
}
```

All fields optional. Defaults: `dryRun: false`, `skipExistingT2: false`.

Dry-run response:
```json
{
  "ok": true,
  "dryRun": true,
  "eligibleCount": 34342,
  "wouldCreate": 500
}
```

Live response:
```json
{
  "ok": true,
  "created": 500,
  "enqueued": 500,
  "hasMore": true,
  "errors": []
}
```

Auth: 401/403 on missing/invalid credentials (same as bulk-reprocess).

## Technology Stack

- **Runtime**: Next.js 15 Route Handler on Cloudflare Workers (OpenNext)
- **ORM**: Prisma (existing models, no migration)
- **Queue**: CF Queue (SUBMISSION_QUEUE) via `env.SUBMISSION_QUEUE.sendBatch()`
- **Auth**: Existing `requireAdmin` + `X-Internal-Key` pattern

## Architecture Decisions

### AD-1: Query Skill table, not Submission table

The spec is skill-centric ("published skills with low trust tiers"). Querying the Skill table directly gives access to `trustTier` and ensures we process the correct population. Each Skill links back to its Submission records via the `submissions` relation for the pending-check filter.

### AD-2: Create new Submissions rather than reuse old ones

Fresh Submission records avoid state machine conflicts with the existing ones. The old submission stays at its terminal state (PUBLISHED/etc.), and the new one starts clean at RECEIVED. This preserves the audit trail and prevents `processSubmission`'s idempotency logic from treating them as duplicates (it checks by submission ID, not by skill name).

### AD-3: Skip logic uses NOT EXISTS subquery for pending submissions

For AC-US1-03, the query needs: "skip skills that already have a submission in a non-terminal state." The non-terminal states are: RECEIVED, TIER1_SCANNING, TIER2_SCANNING, AUTO_APPROVED, DEQUEUED, RESCAN_REQUIRED, ON_HOLD. In Prisma, this is expressed as:

```
submissions: { none: { state: { in: NON_TERMINAL_STATES } } }
```

This is a `WHERE NOT EXISTS (...)` subquery. It uses the existing `@@index([state])` on Submission and the `skillId` FK index, so performance is acceptable even at 84k skills.

### AD-4: Blocklist exclusion via NOT IN subquery

To satisfy AC-US1-04 (skip blocklisted skills), query active BlocklistEntry names and exclude matching Skill.name values. This is a small set (tens of entries) and does not require a new index.

### AD-5: skipExistingT2 filter uses ScanResult relation

For AC-US1-05, when `skipExistingT2: true`, exclude skills whose submissions have any ScanResult with `tier: 2`. In Prisma: `submissions: { none: { scanResults: { some: { tier: 2 } } } }`. This avoids rescanning skills that already went through LLM analysis and still landed at T2 (indicating T2 is their correct tier).

### AD-6: No KV sync needed

Unlike bulk-reprocess (which resets existing submission KV state), this endpoint creates brand-new submissions. The pipeline's `processSubmission` writes KV state for new submissions during processing. No KV pre-seeding or cleanup is required.

## Implementation Phases

### Phase 1: Endpoint implementation (single task)

1. Create `src/app/api/v1/admin/rescan-published/route.ts`
2. Implement auth gate (copy from bulk-reprocess)
3. Implement body parsing (dryRun, skipExistingT2)
4. Implement Skill query with all filters (trustTier, blocklist, pending, optional T2 scan)
5. Implement dry-run response path
6. Implement live path: createMany submissions, createMany state events, sendBatch queue
7. Implement batching and hasMore response

### Phase 2: Tests

Unit/integration tests following existing admin endpoint patterns.

## Testing Strategy

- **Unit tests**: Mock Prisma and CF queue; verify query filters, batch logic, auth rejection, dry-run vs live paths
- **Integration tests**: Hit the route with test DB; verify Submission and SubmissionStateEvent records created; verify queue messages sent
- **Coverage target**: 90% (per spec)
- **Test file**: `src/app/api/v1/admin/rescan-published/route.test.ts`

## Technical Challenges

### Challenge 1: Prisma nested filter performance at 84k skills

**Solution**: The query filters (trustTier IN, NOT IN blocklist names, none-pending subquery) all hit indexed columns. The `take: 500` limit caps the result set. At 84k total skills with ~34k eligible, each batch query should complete in <100ms on D1.

**Risk**: If the `submissions: { none: { state: { in: [...] } } }` subquery is slow, it can be replaced with a raw SQL NOT EXISTS for the same semantics. Low risk given the existing index on `Submission.state`.

### Challenge 2: Duplicate submissions on repeated calls

**Solution**: The pending-submission skip logic (AD-3) ensures that once a skill has a RECEIVED/scanning submission, it will not be re-queued on the next call. The `hasMore` pagination naturally drains the eligible pool as each batch creates submissions that become non-terminal.

**Risk**: None -- same pattern used by bulk-reprocess for idempotency.
