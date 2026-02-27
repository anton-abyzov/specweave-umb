---
increment: 0314-auto-blocklist-rejected-submissions
title: "Auto-Blocklist Rejected Queue Submissions"
type: feature
priority: P1
status: active
created: 2026-02-21
structure: user-stories
test_mode: TDD
coverage_target: 80
---

# Feature: Auto-Blocklist Rejected Queue Submissions

## Overview

Automatically create blocklist entries when queue submissions are rejected due to critical Tier 1 failures. Additionally, give admins an opt-in checkbox to add skills to the blocklist when manually rejecting submissions. Blocklist entries use upsert semantics with severity escalation only (never downgrade). Both flows provide inline feedback confirming blocklist actions.

## User Stories

### US-001: Auto-Blocklist on Critical Tier 1 Failure (P1)
**Project**: vskill-platform

**As a** platform operator
**I want** skills that fail Tier 1 scanning with critical findings to be automatically added to the blocklist
**So that** known-dangerous skills are immediately blocked from future resubmission without manual intervention

**Acceptance Criteria**:
- [ ] **AC-US1-01**: When a submission reaches TIER1_FAILED state AND the scan result has `criticalCount > 0`, a blocklist entry is automatically created/upserted for the skill
- [ ] **AC-US1-02**: The auto-created blocklist entry infers `threatType` from the Tier 1 scanner findings categories (e.g., prompt-injection, credential-theft, malicious-code)
- [ ] **AC-US1-03**: The auto-created blocklist entry sets `severity` based on finding severity (critical findings -> "critical", high -> "high")
- [ ] **AC-US1-04**: Low-score rejections (score < 50 but criticalCount == 0) do NOT trigger auto-blocklist
- [ ] **AC-US1-05**: Missing SKILL.md rejections do NOT trigger auto-blocklist
- [ ] **AC-US1-06**: The rejection always succeeds first; blocklist upsert runs after -- failures are logged but never roll back the rejection
- [ ] **AC-US1-07**: The auto-blocklist entry sets `discoveredBy` to "system:tier1-scan" and `reason` includes the critical finding summary

---

### US-002: Admin Opt-In Blocklist on Manual Rejection (P1)
**Project**: vskill-platform

**As an** admin reviewer
**I want** an opt-in checkbox to add a skill to the blocklist when manually rejecting a submission
**So that** I can block malicious skills in a single action without navigating to a separate blocklist page

**Acceptance Criteria**:
- [ ] **AC-US2-01**: The admin submission reject form includes an "Also add to blocklist" checkbox (unchecked by default)
- [ ] **AC-US2-02**: When the checkbox is checked, a `threatType` dropdown appears with options: prompt-injection, credential-theft, malicious-code, policy-violation, admin-rejected (defaulting to "admin-rejected")
- [ ] **AC-US2-03**: When the checkbox is checked, a `severity` dropdown appears defaulting to "medium"
- [ ] **AC-US2-04**: The reject API endpoint accepts optional `addToBlocklist`, `threatType`, and `severity` fields
- [ ] **AC-US2-05**: Rejection always succeeds first; blocklist creation is best-effort (logged on failure, never blocks rejection)
- [ ] **AC-US2-06**: The blocklist entry uses the rejection reason as the blocklist `reason` field

---

### US-003: Blocklist Upsert with Severity Escalation (P1)
**Project**: vskill-platform

**As a** platform operator
**I want** duplicate blocklist entries to be upserted with severity escalation only
**So that** repeated offenses strengthen the block but never accidentally weaken it

**Acceptance Criteria**:
- [ ] **AC-US3-01**: When a blocklist entry already exists for the same `skillName` + `sourceRegistry`, upsert instead of creating a duplicate
- [ ] **AC-US3-02**: Severity escalates only: critical > high > medium > low -- never downgrade
- [ ] **AC-US3-03**: `evidenceUrls` arrays are merged (union of old + new)
- [ ] **AC-US3-04**: `reason` is updated to the latest value
- [ ] **AC-US3-05**: `discoveredAt` and `discoveredBy` from the original entry are preserved
- [ ] **AC-US3-06**: `updatedAt` is always refreshed on upsert

---

### US-004: Blocklist Action Feedback (P2)
**Project**: vskill-platform

**As an** admin reviewer
**I want** inline feedback when a blocklist entry is created or updated during rejection
**So that** I have confirmation the blocklist action occurred without checking separately

**Acceptance Criteria**:
- [ ] **AC-US4-01**: The reject API response includes a `blocklistAction` field indicating "created", "updated" (upserted), or null (no blocklist action)
- [ ] **AC-US4-02**: The admin UI shows a brief inline note/toast: "Blocklist entry created" or "Blocklist entry updated" when a blocklist action occurred
- [ ] **AC-US4-03**: For auto-blocklist (queue failures), the SSE event or state change message includes the blocklist action info

## Functional Requirements

### FR-001: Blocklist Upsert Service
A shared `upsertBlocklistEntry()` function in `src/lib/blocklist-upsert.ts` that both the auto-blocklist and admin reject flows call. This function:
- Checks for existing entry by `skillName` + `sourceRegistry`
- If exists: escalate severity, merge evidenceUrls, update reason, refresh updatedAt
- If new: create entry with provided fields
- Returns `{ action: "created" | "updated", entry }` for feedback

### FR-002: Tier 1 Finding to Threat Type Mapping
Map Tier 1 scanner pattern categories to blocklist `threatType` values:
- `prompt-injection`, `instruction-override` -> "prompt-injection"
- `credential-*`, `env-access` -> "credential-theft"
- `obfuscated-*`, `eval-*`, `shell-*` -> "malicious-code"
- `network-*`, `data-exfil*` -> "data-exfiltration"
- `reverse-shell` -> "reverse-shell"
- All others -> "policy-violation"

### FR-003: Severity Escalation Order
`critical` > `high` > `medium` > `low`. Numeric mapping: critical=4, high=3, medium=2, low=1. Upsert compares numeric values and keeps the higher one.

## Success Criteria

- All critical Tier 1 failures automatically create blocklist entries within the same request cycle (best-effort, non-blocking)
- Admin manual rejection with blocklist opt-in completes in a single user action
- Zero rejections fail due to blocklist errors (separation of concerns)
- Duplicate skills are upserted with severity escalation, never duplicated

## Out of Scope

- Automatic blocklist for Tier 2 failures (only Tier 1 critical triggers auto-block)
- Blocklist entry removal/unblocking (already exists via separate API)
- Batch/bulk auto-blocklist of historical rejections
- Email notifications for blocklist additions

## Dependencies

- Existing `BlocklistEntry` Prisma model (schema.prisma)
- Existing Tier 1 scanner findings structure (`process-submission.ts`)
- Existing admin submission detail page (`/admin/submissions/[id]/page.tsx`)
- Existing admin blocklist API (`/api/v1/admin/blocklist/route.ts`)
