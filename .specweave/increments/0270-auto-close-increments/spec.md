---
increment: 0270-auto-close-increments
title: "Auto-Close Increments in Auto/Team-Lead Modes"
type: feature
priority: P1
status: planned
created: 2026-02-21
structure: user-stories
test_mode: test-after
coverage_target: 80
---

# Feature: Auto-Close Increments in Auto/Team-Lead Modes

## Overview

When `/sw:auto` or `/sw:team-lead` finishes all tasks in an increment, the increment is left in `active` status. The user must manually invoke `/sw:done` to close it. This is because:

1. **stop-auto-v5.sh approves (exits) when all tasks complete** -- it should instead block with a "run /sw:done" instruction so Claude continues working.
2. **/sw:done requires explicit user confirmation** -- in auto/team-lead mode there is no user to confirm.
3. **team-lead has no explicit auto-close step** -- after all agents complete, the orchestrator moves to `/sw:team-merge` but never runs `/sw:done` for the umbrella increment.

This increment fixes all three gaps so that auto and team-lead modes produce fully closed increments without manual intervention.

## User Stories

### US-001: Stop Hook Blocks on All-Complete to Trigger Closure (P1)
**Project**: specweave

**As a** developer using `/sw:auto`
**I want** the stop hook to block (not approve) when all tasks are complete
**So that** Claude receives a systemMessage instructing it to run `/sw:done` and the session does not silently end with an unclosed increment

**Acceptance Criteria**:
- [ ] **AC-US1-01**: When all tasks and ACs are complete, stop-auto-v5.sh emits `{"decision":"block"}` with a systemMessage containing `/sw:done`
- [ ] **AC-US1-02**: The block message includes the increment ID(s) that need closure
- [ ] **AC-US1-03**: Session state files (auto-mode.json, turn counter) are NOT cleaned up on all-complete block -- they are only cleaned up after /sw:done succeeds or turn limit is hit
- [ ] **AC-US1-04**: A dedicated reason code `"all_complete_needs_closure"` is used so it is distinguishable from `"work_remaining"` blocks

---

### US-002: /sw:done --auto Flag for Unattended Closure (P1)
**Project**: specweave

**As a** developer using `/sw:auto` or `/sw:team-lead`
**I want** `/sw:done` to accept an `--auto` flag that skips user confirmation prompts
**So that** increments can be closed programmatically in unattended sessions

**Acceptance Criteria**:
- [ ] **AC-US2-01**: `/sw:done <id> --auto` skips the "yes to close, no to cancel" confirmation prompt in Step 4
- [ ] **AC-US2-02**: All other validation gates (grill, judge-llm, Gate 0, PM gates) still execute normally
- [ ] **AC-US2-03**: The `--auto` flag is documented in the skill's Usage section
- [ ] **AC-US2-04**: When grill or judge-llm finds BLOCKERs/CRITICALs, `--auto` mode still blocks (does not auto-override safety gates)

---

### US-003: Auto Mode Runs /sw:done After All-Complete Block (P1)
**Project**: specweave

**As a** developer using `/sw:auto`
**I want** the auto skill instructions to explicitly tell Claude to run `/sw:done --auto` when it receives an all-complete block
**So that** increments are automatically closed at the end of autonomous sessions

**Acceptance Criteria**:
- [ ] **AC-US3-01**: The `/sw:auto` SKILL.md Step 3 includes explicit instruction to run `/sw:done --auto <id>` when all tasks are complete
- [ ] **AC-US3-02**: After `/sw:done` succeeds, the auto session cleans up state files and emits `<!-- auto-complete:DONE -->`
- [ ] **AC-US3-03**: If `/sw:done` fails (gate failure), the auto session reports the failure and does NOT clean up session state

---

### US-004: Team-Lead Orchestrator Auto-Closes After All Agents Complete (P1)
**Project**: specweave

**As a** developer using `/sw:team-lead`
**I want** the team-lead to automatically run `/sw:done --auto` for each increment after all agents signal completion
**So that** team-lead sessions produce fully closed increments without manual `/sw:done` invocation

**Acceptance Criteria**:
- [ ] **AC-US4-01**: The team-lead SKILL.md Section 8 (Quality Gates > Orchestrator Quality Gate) includes an explicit step to run `/sw:done --auto <id>` for each increment in dependency order
- [ ] **AC-US4-02**: The `/sw:team-merge` skill runs `/sw:done --auto <id>` instead of bare `/sw:done <id>` in Step 4
- [ ] **AC-US4-03**: If any `/sw:done --auto` fails, team-lead reports the failure and continues with remaining increments

## Functional Requirements

### FR-001: Stop Hook All-Complete Behavior Change
When section 9 ("All complete -> approve") fires, change from `loud_approve` to `block` with a closure-instructing systemMessage. The block message must include the increment ID and `/sw:done --auto` as the action.

### FR-002: /sw:done --auto Flag
Add `--auto` as a recognized option. When present, bypass the explicit user approval gate in Step 4 (Status Validation) where it says "Require explicit user confirmation before closure". All other gates remain enforced.

### FR-003: Auto Skill Closure Loop
Add to `/sw:auto` Step 3 a closure substep: after all tasks are marked complete and quality gates pass, invoke `/sw:done --auto <id>` for each increment in the session.

### FR-004: Team-Lead Auto-Close
Add to `/sw:team-lead` Section 8 an explicit step between quality gates and `/sw:team-merge` where the orchestrator runs `/sw:done --auto <id>` in dependency order.

## Success Criteria

- Autonomous sessions (`/sw:auto`) end with increments in `completed` status (not `active`)
- Team-lead sessions produce fully closed increments after all agents finish
- No regressions: manual `/sw:done` without `--auto` still requires user confirmation
- Stop hook tests pass with updated behavior

## Out of Scope

- Changing the stop hook to directly modify metadata.json (hook remains a gate only)
- Adding auto-close to `/sw:do` (manual mode should not auto-close)
- Removing any existing quality gates from `/sw:done`

## Dependencies

- stop-auto-v5.sh (hook script)
- `/sw:done` SKILL.md (done skill specification)
- `/sw:auto` SKILL.md (auto skill specification)
- `/sw:team-lead` SKILL.md (team-lead skill specification)
- `/sw:team-merge` SKILL.md (team-merge skill specification)
