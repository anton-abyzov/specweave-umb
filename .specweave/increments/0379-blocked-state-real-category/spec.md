# 0379 — Make BLOCKED a Real SubmissionState

## Problem

"Blocked" is a virtual category, not a real `SubmissionState` enum value. This causes:

1. **Expensive queries**: The submissions API and stats endpoint must JOIN `BlocklistEntry` + `Submission` tables to compute blocked items — Phase 2 of stats has a 5s timeout and often returns degraded data.
2. **No visual indicator**: `SubmissionTable.STATE_CONFIG` has no BLOCKED entry, so blocked items display their processing state (Queued, Tier 1 Scanning), making the blocked filter indistinguishable from the active view.
3. **No pipeline integration**: Blocked items continue being claimed and scanned by VMs because `claim-submission` and `pending-submissions` only check for RECEIVED state, not blocklist membership.
4. **No formal transitions**: The state machine has no `block`/`unblock` events — blocking lives outside the submission lifecycle.

## Solution

Add `BLOCKED` as a real enum value in `SubmissionState`. When a skill is blocked (admin action or auto-blocklist), all matching active submissions transition to `BLOCKED`. When unblocked, they return to `RECEIVED`.

## User Stories

### US-001: Blocked submissions show BLOCKED state badge
As an admin viewing the queue, I want blocked submissions to display a "Blocked" badge so I can distinguish them from active items.

**Acceptance Criteria:**
- [x] AC-US1-01: SubmissionTable renders a "Blocked" badge (dark red) for state=BLOCKED
- [x] AC-US1-02: Queue page blocked filter shows items with state=BLOCKED (simple query, no JOIN)
- [x] AC-US1-03: Stats endpoint computes blocked count with simple `count({ state: BLOCKED })` in Phase 1

### US-002: Blocking a skill transitions active submissions to BLOCKED
As an admin blocking a skill, I want all active submissions for that skill to immediately stop processing.

**Acceptance Criteria:**
- [x] AC-US2-01: Admin block route bulk-transitions matching RECEIVED/TIER1_SCANNING/TIER2_SCANNING/ON_HOLD submissions to BLOCKED
- [x] AC-US2-02: Auto-blocklist in process-submission transitions the current submission to BLOCKED after creating the blocklist entry
- [x] AC-US2-03: SSE state_changed events fire for each transitioned submission

### US-003: Unblocking a skill re-queues blocked submissions
As an admin removing a block, I want blocked submissions to re-enter the processing queue.

**Acceptance Criteria:**
- [x] AC-US3-01: Unblock route bulk-transitions BLOCKED submissions (matching skillName) back to RECEIVED
- [x] AC-US3-02: Re-queued submissions appear in the active queue and get picked up by VMs

### US-004: Pipeline skips blocked submissions naturally
As the system, blocked submissions should not consume scanner resources.

**Acceptance Criteria:**
- [x] AC-US4-01: pending-submissions endpoint never returns BLOCKED items (already safe — only returns RECEIVED)
- [x] AC-US4-02: claim-submission endpoint cannot claim BLOCKED items (already safe — only claims RECEIVED)
- [x] AC-US4-03: process-submission checks blocklist before scanning and transitions to BLOCKED early if matched

## Non-Goals

- Storing previous state before blocking (always reset to RECEIVED on unblock)
- Blocking items already in terminal states (PUBLISHED, REJECTED, etc.)
- Changing the BlocklistEntry table schema
