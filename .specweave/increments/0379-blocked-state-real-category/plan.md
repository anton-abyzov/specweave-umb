# 0379 — Implementation Plan

## Approach

Bottom-up: schema → categories → state machine → API simplifications → pipeline → admin routes → UI → backfill migration.

## Phase 1: Schema & Core Types
Add BLOCKED to Prisma enum, TypeScript type union, submission categories, and state machine. This is the foundation everything else depends on.

## Phase 2: API Simplifications
Replace the virtual blocked filter in submissions API with a simple state query. Move blocked count from Phase 2 (expensive JOIN) to Phase 1 (simple count) in stats.

## Phase 3: Pipeline Integration
Add early blocklist check in process-submission. Transition to BLOCKED on auto-blocklist. This stops wasting scanner resources on blocked skills.

## Phase 4: Admin Routes
Add bulk state transitions to block/unblock routes. When blocking, transition active submissions to BLOCKED. When unblocking, transition back to RECEIVED.

## Phase 5: UI
Add BLOCKED badge to SubmissionTable STATE_CONFIG and ON_HOLD (missing too).

## Phase 6: Backfill Migration
One-time script to transition existing "virtually blocked" submissions to the real BLOCKED state.

## Key Decisions

1. **BLOCKED is non-terminal but non-active**: Not in ACTIVE_STATES (scanners skip it), not in SUCCESS/FAILED_STATES. Added to a new BLOCKED_STATES category.
2. **Unblock always resets to RECEIVED**: No "previous state" tracking — simpler, items re-enter the queue cleanly.
3. **Backfill runs post-deploy**: SQL query transitions existing blocked items.
