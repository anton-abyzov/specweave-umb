---
increment: 0387-blocklist-dedup-poisoning-fixes
title: >-
  Fix blocklist global poisoning, duplicate blocked submissions, and crawler
  dedup bypass
type: bug
priority: P1
status: completed
created: 2026-02-27T00:00:00.000Z
structure: user-stories
test_mode: test-after
coverage_target: 80
---

# Bug Fix: Blocklist Global Poisoning, Duplicate Blocked Submissions, and Crawler Dedup Bypass

## Overview

Three related bugs in the vskill-platform submission pipeline compromise security and data integrity:

1. **Blocklist global name poisoning**: Blocklist entries match by `skillName` only (`WHERE skillName = X AND isActive = true`), ignoring `sourceUrl`. When a malicious skill named "google" from `snyk-labs/toxicskills-goof` is blocklisted, ALL skills named "google" from ANY repo are blocked. Generic skill names become toxic platform-wide.

2. **Duplicate blocked submissions**: When `checkSubmissionDedup` returns `kind: "rejected"` for a BLOCKED submission, the submission route does NOT short-circuit -- it falls through to create a new submission. The same skill+repo accumulates duplicate BLOCKED submissions, wasting DB storage and confusing the admin queue.

3. **Crawler discovery dedup race**: The `processRepo` function in `github-discovery.ts` calls `markDiscovered` AFTER successful submission POST. When parallel batches process the same repo from different sources, the `hasBeenDiscovered` check can pass for both before either writes the discovery record.

## User Stories

### US-001: Scope blocklist matching to sourceUrl
**Project**: vskill-platform

**As a** platform admin
**I want** blocklist entries to be scoped to the specific source repo/registry, not just the skill name
**So that** blocking a malicious "google" skill from one repo does not block legitimate "google" skills from other repos

**Acceptance Criteria**:
- [x] **AC-US1-01**: `processSubmission` early blocklist check matches on `skillName` AND (`sourceUrl` matches repoUrl OR `sourceUrl IS NULL` for global bans)
- [x] **AC-US1-02**: `finalize-scan` route early blocklist check uses the same scoped matching logic
- [x] **AC-US1-03**: `blocklist/check` API endpoint accepts optional `repoUrl` param and uses scoped matching
- [x] **AC-US1-04**: Blocklist entries with `sourceUrl = null` act as global name bans (backward compat)
- [x] **AC-US1-05**: `upsertBlocklistEntry` dedup lookup includes `sourceUrl` so entries from different repos do not merge
- [x] **AC-US1-06**: Existing seed data entries continue to work correctly -- they block their specific malicious repos
- [x] **AC-US1-07**: `repo-block` route continues to work correctly, creating per-repo scoped blocklist entries

---

### US-002: Prevent duplicate submissions for blocked skills
**Project**: vskill-platform

**As a** platform operator
**I want** the submission endpoint to reject new submissions for skills that are already BLOCKED
**So that** blocked repos do not accumulate duplicate submission records

**Acceptance Criteria**:
- [x] **AC-US2-01**: `checkSubmissionDedup` returns `kind: "blocked"` when the most recent submission is in BLOCKED state
- [x] **AC-US2-02**: POST `/api/v1/submissions` returns HTTP 200 with `{ blocked: true, submissionId }` for blocked skills
- [x] **AC-US2-03**: `checkSubmissionDedupBatch` also returns `kind: "blocked"` for batch submissions
- [x] **AC-US2-04**: Internal/crawler submissions respect blocked dedup via existing `checkSubmissionDedup` call

---

### US-003: Fix crawler discovery dedup race condition
**Project**: vskill-platform

**As a** platform operator
**I want** the crawler dedup to be robust against parallel batch processing races
**So that** the same skill is not submitted multiple times in a single discovery run

**Acceptance Criteria**:
- [x] **AC-US3-01**: `markDiscovered` is called BEFORE the HTTP POST to submissions (write-ahead pattern)
- [x] **AC-US3-02**: If the submission POST fails after `markDiscovered`, the record remains (prevents retry loops)
- [x] **AC-US3-03**: Successful submission updates the discovery record with the submissionId

### US-004: Auto-block on critical scan violations
**Project**: vskill-platform

**As a** platform operator
**I want** skills with critical-severity scan violations (command injection, credential theft, privilege escalation) to be immediately BLOCKED after scan
**So that** dangerous skills don't sit as TIER1_FAILED waiting for manual review or a second failure

**Acceptance Criteria**:
- [x] **AC-US4-01**: When Tier 1 scan finds any `critical`-severity pattern match, submission state transitions to BLOCKED (not TIER1_FAILED)
- [x] **AC-US4-02**: A scoped blocklist entry is auto-created for the skillName + repoUrl on critical block
- [x] **AC-US4-03**: The BLOCKED reason includes which critical patterns were found (e.g., "Immediate block: critical violations CI-001, CT-003")
- [x] **AC-US4-04**: Non-critical failures (high/medium/low only) continue to use TIER1_FAILED as before
- [x] **AC-US4-05**: The blocklist entry created uses `discoveredBy: "system:critical-scan"` to distinguish from manual blocks and auto-block threshold

---

## Functional Requirements

### FR-001: Scoped blocklist matching
All blocklist lookups must use `OR` logic: match if `(skillName = X AND sourceUrl = repoUrl)` OR `(skillName = X AND sourceUrl IS NULL)`. This ensures repo-scoped blocks only affect their target while global bans (null sourceUrl) still work.

### FR-002: Critical scan → immediate block
When Tier 1 scan results contain any pattern with `severity: "critical"`, the submission must transition directly to BLOCKED (bypassing TIER1_FAILED). A scoped blocklist entry is created with `sourceUrl = repoUrl` so the block is repo-specific. The block reason must list the specific critical pattern IDs found.

### FR-003: Blocked dedup kind
`checkSubmissionDedup` and `checkSubmissionDedupBatch` must treat BLOCKED state identically to REJECTED/TIER1_FAILED for dedup purposes, returning `kind: "blocked"` with the existing submission ID.

### FR-004: Write-ahead discovery dedup
Move `markDiscovered()` call before the submission HTTP POST. On POST failure, the discovery record prevents infinite retries. On POST success, update the record with the submissionId.

## Success Criteria

- No false-positive blocks on legitimate skills with common names
- Zero duplicate BLOCKED submissions for the same skill+repo
- Crawler runs produce no duplicate submissions from parallel batch races

## Out of Scope

- Blocklist UI changes (admin dashboard already handles scoped entries)
- Schema migration (BlocklistEntry already has `sourceUrl` column)
- Changing the unique constraint on `[skillName, sourceRegistry]` (not needed; sourceUrl scoping is handled in query logic)

## Dependencies

- No external dependencies -- all changes are within vskill-platform
