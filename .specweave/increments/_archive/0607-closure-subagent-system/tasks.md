---
increment: 0607-closure-subagent-system
total_tasks: 7
completed_tasks: 7
---

# Tasks: Closure Subagent System

## US-001: Fresh-Context Closure via Subagent

### T-001: Create sw-closer subagent definition
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04
**Status**: [x] Completed
**Test**: Given sw-closer.md exists → When spawned via Agent(subagent_type: "sw:sw-closer") → Then runs sw:done in fresh context with retry awareness

## US-002: Auto-Closure from Team-Lead and Auto Mode

### T-002: Update do/SKILL.md Step 9 with closure subagent pattern
**User Story**: US-002 | **Satisfies ACs**: AC-US2-03
**Status**: [x] Completed
**Test**: Given all tasks complete in sw:do → When Step 9 executes → Then spawns sw-closer (Claude Code) or invokes sw:done (non-cloud)

### T-003: Update auto/SKILL.md Step 3.5 with sw-closer spawning
**User Story**: US-002 | **Satisfies ACs**: AC-US2-04
**Status**: [x] Completed
**Test**: Given stop hook blocks with all_complete_needs_closure → When auto processes signal → Then spawns sw-closer per increment

### T-004: Update team-merge/SKILL.md Step 4 with sw-closer pattern
**User Story**: US-002 | **Satisfies ACs**: AC-US2-02
**Status**: [x] Completed
**Test**: Given team-merge closing increments → When Step 4 runs → Then uses sw-closer subagent (4a) or direct sw:done (4b)

### T-005: Update team-lead/SKILL.md Section 8c with sw-closer spawning
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01
**Status**: [x] Completed
**Test**: Given all agents signal COMPLETION → When closure phase begins → Then spawns sw-closer per increment in dependency order

## US-003: Batch Closure for Stuck Increments

### T-006: Create close-all skill
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04
**Status**: [x] Completed
**Test**: Given 3 increments at 100% → When /sw:close-all runs → Then discovers all 3 and closes each via sw-closer

## US-004: Non-Cloud Environment Support

### T-007: Verify non-cloud fallback paths in all modified skills
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02
**Status**: [x] Completed
**Test**: Given non-cloud tool without Agent() → When closure triggers → Then falls back to direct sw:done invocation
