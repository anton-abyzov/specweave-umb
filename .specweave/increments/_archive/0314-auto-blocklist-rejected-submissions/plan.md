# Implementation Plan: Auto-Blocklist Rejected Queue Submissions

## Overview

Add automatic blocklist entry creation when queue submissions are rejected with critical Tier 1 findings, and an opt-in blocklist checkbox for admin manual rejections. Both flows use a shared upsert service with severity escalation semantics. The rejection path always succeeds independently of blocklist operations (best-effort, non-blocking).

## Architecture

### Components

1. **Blocklist Upsert Service** (`src/lib/blocklist-upsert.ts`): Shared logic for creating/upserting blocklist entries with severity escalation. Used by both the auto-blocklist pipeline hook and the admin reject API.

2. **Tier 1 Threat Type Mapper** (`src/lib/scanner/threat-type-mapper.ts`): Maps Tier 1 scanner `PatternCategory` values to blocklist `threatType` values.

3. **Process Submission Hook** (modify `src/lib/queue/process-submission.ts`): After a Tier 1 FAIL with `criticalCount > 0`, call the upsert service best-effort.

4. **Admin Reject API** (modify `src/app/api/v1/admin/submissions/[id]/route.ts`): Accept optional `addToBlocklist`, `threatType`, `severity` fields. Call upsert service when opt-in is enabled.

5. **Admin UI Reject Form** (modify `src/app/admin/submissions/[id]/page.tsx`): Add "Also add to blocklist" checkbox with conditional threatType/severity dropdowns.

### Data Model

No schema changes required. The existing `BlocklistEntry` model already supports all needed fields:
- `skillName`, `sourceUrl`, `sourceRegistry`, `contentHash`
- `threatType`, `severity`, `reason`, `evidenceUrls`
- `discoveredAt`, `discoveredBy`, `addedById`
- `isActive`, `createdAt`, `updatedAt`
- Unique constraint: `@@unique([skillName, sourceRegistry])`

### API Contracts

#### Modified: `PATCH /api/v1/admin/submissions/:id`
New optional request fields:
```typescript
{
  action: "reject",
  reason: string,
  addToBlocklist?: boolean,    // opt-in checkbox
  threatType?: string,         // required if addToBlocklist
  severity?: string            // defaults to "medium" if addToBlocklist
}
```

Response augmented with:
```typescript
{
  submission: { ... },
  blocklistAction: "created" | "updated" | null
}
```

#### New internal: `upsertBlocklistEntry()`
```typescript
interface UpsertBlocklistInput {
  skillName: string;
  sourceUrl?: string;
  sourceRegistry?: string;
  contentHash?: string;
  threatType: string;
  severity: string;
  reason: string;
  evidenceUrls?: string[];
  discoveredBy: string;
}

interface UpsertBlocklistResult {
  action: "created" | "updated";
  entry: BlocklistEntry;
}
```

## Technology Stack

- **Language/Framework**: TypeScript, Next.js 15, Prisma ORM
- **Database**: PostgreSQL (via Prisma)
- **Testing**: Vitest with TDD (RED-GREEN-REFACTOR)
- **Runtime**: Cloudflare Workers (via OpenNext)

**Architecture Decisions**:

1. **Separate calls, not transactional**: Rejection and blocklist upsert are separate database operations. Rejection always succeeds first. Blocklist failures are logged but never roll back the rejection. This prevents blocklist errors from degrading the core rejection flow.

2. **Shared upsert service**: Both auto-blocklist and admin opt-in use the same `upsertBlocklistEntry()` function to guarantee consistent severity escalation and dedup semantics.

3. **Severity escalation only**: Numeric severity mapping (critical=4, high=3, medium=2, low=1) ensures upserts only escalate, never downgrade. This prevents a low-confidence scan from weakening a previous critical blocklist entry.

4. **Scanner category to threat type mapping**: The mapper is a pure function with a static lookup table, making it trivially testable and extensible.

## Implementation Phases

### Phase 1: Core Service (TDD)
- Blocklist upsert service with severity escalation
- Threat type mapper from scanner categories
- Full unit test coverage for both

### Phase 2: Pipeline Integration
- Wire auto-blocklist into `processSubmission()` on TIER1_FAILED with criticalCount > 0
- Wire admin reject API with optional blocklist fields
- Integration tests

### Phase 3: UI Updates
- Add "Also add to blocklist" checkbox to admin reject form
- Add threatType/severity dropdowns (conditional on checkbox)
- Add inline toast/note for blocklist feedback
- Component tests

## Testing Strategy

TDD approach: write failing tests first, then implement.

- **Unit tests**: `blocklist-upsert.test.ts`, `threat-type-mapper.test.ts`
- **Integration tests**: `process-submission.test.ts` (auto-blocklist path), admin reject route test (opt-in blocklist path)
- **Component tests**: Admin submission detail page (checkbox, dropdowns, toast feedback)

## Technical Challenges

### Challenge 1: Race conditions on concurrent upserts
**Solution**: Use Prisma `upsert` with the existing `@@unique([skillName, sourceRegistry])` constraint. The database handles atomicity. For severity escalation, use a conditional update: `severity = CASE WHEN new_severity_num > old_severity_num THEN new_severity ELSE old_severity END`. In Prisma, implement as findFirst + conditional create/update within a transaction.
**Risk**: Low. Single-writer pattern for auto-blocklist (runs in the scan pipeline). Admin concurrent upserts are rare.

### Challenge 2: Best-effort semantics without blocking rejection
**Solution**: Wrap blocklist upsert in try/catch with console.error logging. The rejection state update completes before the blocklist call. If blocklist fails, the response still indicates success for the rejection with `blocklistAction: null` and logs the error.
**Risk**: Minimal. Blocklist is advisory; rejection is the critical path.
