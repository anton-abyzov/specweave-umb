---
increment: 0360-consistent-rejection-handling
title: Consistent Rejection Handling
type: feature
priority: P1
status: completed
created: 2026-02-24T00:00:00.000Z
structure: user-stories
test_mode: test-after
coverage_target: 80
---

# Feature: Consistent Rejection Handling

## Overview

Skills that fail the verification pipeline (REJECTED, TIER1_FAILED, DEQUEUED) are invisible to CLI users and Trust Center visitors. The CLI only checks the blocklist — `vskill add owner/repo` installs a skill the platform already rejected. The Trust Center shows "Verified" and "Blocked" tabs but has no visibility into rejected submissions.

This increment makes rejection a first-class concept alongside blocking — distinct (failed verification != malicious) but both resulting in a hard install block from the CLI.

## User Stories

### US-001: Extend Blocklist Check API with Rejection Status (P1)
**Project**: vskill-platform

**As a** CLI tool
**I want** the blocklist check endpoint to also return rejection status
**So that** I can prevent installation of both blocked and rejected skills with a single API call

**Acceptance Criteria**:
- [x] **AC-US1-01**: `GET /api/v1/blocklist/check?name=X` returns `{ blocked, rejected }` fields (backward-compatible — old CLIs ignore `rejected`)
- [x] **AC-US1-02**: When a skill has a rejected submission, the response includes `rejection: { skillName, state, reason, score, rejectedAt }`
- [x] **AC-US1-03**: The rejection query uses `Submission.findFirst` with `state IN (REJECTED, TIER1_FAILED, DEQUEUED)`, ordered by `updatedAt desc`
- [x] **AC-US1-04**: When no rejected submission exists, `rejected: false` is returned (no `rejection` field)
- [x] **AC-US1-05**: Hash-only queries (`?hash=X` without `?name=`) do not check rejections (rejections are name-based)

---

### US-002: CLI Blocks Installation of Rejected Skills (P1)
**Project**: vskill

**As a** CLI user
**I want** `vskill add` to refuse installing a skill that failed platform verification
**So that** I don't install skills the platform has determined are problematic

**Acceptance Criteria**:
- [x] **AC-US2-01**: New `checkInstallSafety(skillName)` function calls `GET /api/v1/blocklist/check?name=X` and returns `{ blocked, entry?, rejected, rejection? }`
- [x] **AC-US2-02**: When API is unreachable, falls back to local `checkBlocklist()` with `rejected: false` (graceful degradation)
- [x] **AC-US2-03**: All 5 `checkBlocklist()` call sites in `add.ts` (lines 506, 714, 940, 1313, 1426) replaced with `checkInstallSafety()`
- [x] **AC-US2-04**: Rejected skill without `--force` prints "REJECTED: Skill failed platform verification" with score/state/reason and exits
- [x] **AC-US2-05**: Rejected skill with `--force` prints warning and proceeds with installation
- [x] **AC-US2-06**: Blocked takes priority over rejected (if both, shows blocked error)
- [x] **AC-US2-07**: New types `RejectionInfo` and `InstallSafetyResult` added to `blocklist/types.ts`

---

### US-003: Trust Center Rejected Skills Tab (P1)
**Project**: vskill-platform

**As a** Trust Center visitor
**I want** to see skills that failed verification in a dedicated "Rejected Skills" tab
**So that** I can understand which skills were submitted but did not pass

**Acceptance Criteria**:
- [x] **AC-US3-01**: Trust Center page shows three tabs: "Verified Skills", "Blocked Skills", "Rejected Skills"
- [x] **AC-US3-02**: `GET /api/v1/rejections` returns paginated rejected submissions with scan result summaries
- [x] **AC-US3-03**: Rejected Skills tab shows columns: Skill Name, Repo, Status badge (REJECTED/TIER1_FAILED/DEQUEUED), Score, Rejected Date
- [x] **AC-US3-04**: Rows are expandable showing scan result details (finding counts by severity)
- [x] **AC-US3-05**: Client-side search filters by skill name
- [x] **AC-US3-06**: Tab is accessible via `?tab=rejected` query parameter

---

### US-004: Cross-Reference Rejections in Blocked Skills Detail (P2)
**Project**: vskill-platform

**As a** Trust Center visitor
**I want** to see if a blocked skill was also rejected in the verification pipeline
**So that** I understand the full history of a flagged skill

**Acceptance Criteria**:
- [x] **AC-US4-01**: Blocked Skills expanded detail shows "Also rejected in verification pipeline" badge when the skill has a rejected submission
- [x] **AC-US4-02**: The badge is fetched lazily when the detail row is expanded (not on page load)

## Functional Requirements

### FR-001: Backward-Compatible API Extension
The `GET /api/v1/blocklist/check` response MUST remain backward-compatible. Old CLIs that only read `{ blocked, entry }` MUST continue to work.

### FR-002: Graceful Degradation
When the platform API is unreachable, the CLI MUST fall back to local blocklist cache and skip rejection checks. Installation should not be blocked by network issues.

### FR-003: Distinct Messaging
CLI error messages for blocked vs rejected MUST be visually distinct. Blocked = "Known-malicious skill", Rejected = "Skill failed platform verification".

## Success Criteria

- `vskill add` of a rejected skill without `--force` exits with rejection error
- `vskill add` of a rejected skill with `--force` shows warning and installs
- Trust Center `/trust?tab=rejected` shows rejected submissions
- Blocked skill expanded detail shows rejection cross-reference when applicable
- All existing tests pass

## Out of Scope

- Changing the Prisma `SubmissionState` enum
- Auto-blocklisting Tier 2 failures (future increment)
- Email notifications for rejected submissions (separate concern)
- Internal refactoring of state category helpers (separate increment)

## Dependencies

- Existing `Submission` model with `state` field and `@@index([skillName])`
- Existing `ScanResult` model linked to submissions
- Existing `BlocklistEntry` model and blocklist API
- CLI `checkBlocklist()` function and `add.ts` install paths
