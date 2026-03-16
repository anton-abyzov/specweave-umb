---
title: Fix team-lead stuck sessions — Implementation Plan
increment: "0528"
---

# Implementation Plan

## Architecture Decision

All changes are to markdown skill definitions (SKILL.md + agent templates). No code compilation needed. Changes take effect after plugin cache sync.

## Change Strategy

### Change 1: Async Plan Notification (US-001)

**Current**: Agents send PLAN_READY → block → team-lead reviews files → PLAN_APPROVED/PLAN_REJECTED → agent proceeds
**New**: Agents send PLAN_READY (with structured summary) → proceed immediately → team-lead reviews async → PLAN_CORRECTION only if needed

Files: SKILL.md §3b, all 5 agent templates (steps 8-10)

### Change 2: Batch Closure (US-002)

**Current**: Team-lead runs grill+done per-agent as COMPLETION signals arrive (interleaved with active agents)
**New**: Team-lead collects ALL COMPLETION signals, THEN runs closure sequentially in dependency order

Files: SKILL.md §8, §9

### Change 3: Heartbeat Protocol (US-003)

**Current**: No STATUS messages. Stuck detection = "hasn't messaged" → manual STATUS_CHECK → wait → declare stuck
**New**: Agents send `STATUS: T-{N}/{total}` after each task. Team-lead tracks per-agent. Stuck = 2 turns with no STATUS.

Files: SKILL.md §6, §8b, all 5 agent templates

## Edge Cases

| Edge Case | Handling |
|-----------|----------|
| Agent proceeds with bad plan | PLAN_CORRECTION stops agent mid-task; agent revises |
| Agent ignores PLAN_CORRECTION | shutdown_request + report to user |
| Stuck-in-loop (task number unchanged 3+ heartbeats) | Declare stuck, proceed with others |
| Closure context overflow | 2-retry cap per increment; skip and report on failure |
| Single-agent team | No plan review needed |
| Phase 1 slow but not stuck | Heartbeats differentiate slow vs stuck |

## Files Modified

| File | Sections Changed |
|------|-----------------|
| `SKILL.md` | §3b, §6, §7, §8, §8b, §9 |
| `agents/backend.md` | Steps 9-10, add heartbeat |
| `agents/frontend.md` | Steps 9-10, add heartbeat |
| `agents/database.md` | Steps 8-9, add heartbeat |
| `agents/testing.md` | Steps 8-9, add heartbeat |
| `agents/security.md` | Steps 8-9, add heartbeat |

## Post-Implementation

Run `specweave refresh-plugins` to sync source → cache.
