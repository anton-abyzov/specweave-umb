---
increment: 0627-team-lead-agent-teams-api
---

# Tasks

## Phase 1: Communication Protocol

### T-001: Add QUERY_READY message protocol to SKILL.md Section 6
**User Story**: US-001 | **AC**: AC-US1-01 | **Status**: [x] completed
**Test Plan**: Given SKILL.md Section 6 → When reading message types table → Then QUERY_READY, QUERY, SHUTDOWN_AUTHORIZED are documented with sender/receiver/purpose

### T-002: Add broadcast to Section 6 message types
**User Story**: US-003 | **AC**: AC-US3-01 | **Status**: [x] completed
**Test Plan**: Given SKILL.md Section 6 → When reading message types → Then broadcast is documented with usage guidelines (shutdown + global announcements only)

### T-003: Add Section 6b Direct User Interaction documentation
**User Story**: US-004 | **AC**: AC-US4-01, AC-US4-02 | **Status**: [x] completed
**Test Plan**: Given SKILL.md → When reading after Section 6 → Then Section 6b documents Shift+Down, click-into-pane, coordination hazard, and echo-to-team-lead mitigation

## Phase 2: Workflow Updates

### T-004: Add Section 0.7 Display Mode Configuration
**User Story**: US-002 | **AC**: AC-US2-01 | **Status**: [x] completed
**Test Plan**: Given SKILL.md → When reading after Mode Detection → Then Section 0.7 documents teammateMode settings (auto/tmux/in-process) with iTerm2 setup instructions

### T-005: Add stuck detection exclusion for QUERY_READY to Section 8b
**User Story**: US-001 | **AC**: AC-US1-02 | **Status**: [x] completed
**Test Plan**: Given SKILL.md Section 8b → When reading stuck detection rules → Then QUERY_READY state is explicitly excluded

### T-006: Add Section 8c TeammateIdle Quality Hook documentation
**User Story**: US-005 | **AC**: AC-US5-01, AC-US5-02, AC-US5-03 | **Status**: [x] completed
**Test Plan**: Given SKILL.md → When reading after Section 8b → Then Section 8c documents TeammateIdle hook config, circuit breaker (max 3), and supplemental-not-replacement note

### T-007: Add idle query phase to Section 9 workflow summary
**User Story**: US-001 | **AC**: AC-US1-03 | **Status**: [x] completed
**Test Plan**: Given SKILL.md Section 9 workflow → When reading steps → Then Step 6.5 exists between COMPLETION collection and sw-closer spawning with task-count guard (<12)

### T-008: Replace per-agent shutdown with broadcast in Phase 1 cleanup
**User Story**: US-003 | **AC**: AC-US3-02 | **Status**: [x] completed
**Test Plan**: Given SKILL.md Section 9 Phase 1 → When reading shutdown protocol → Then broadcast is used instead of per-agent loop

### T-009: Update Phase 1 cleanup to use SHUTDOWN_AUTHORIZED
**User Story**: US-001 | **AC**: AC-US1-05 | **Status**: [x] completed
**Test Plan**: Given SKILL.md Section 9 Phase 1 → When reading cleanup → Then SHUTDOWN_AUTHORIZED is used for QUERY_READY agents

### T-010: Demote Phase 3 cleanup from MANDATORY to FALLBACK
**User Story**: US-002 | **AC**: AC-US2-02 | **Status**: [x] completed
**Test Plan**: Given SKILL.md Section 9 Phase 3 → When reading heading → Then labeled FALLBACK with conditional guidance

### T-011: Add broadcast to Section 3 CONTRACT_READY flow
**User Story**: US-003 | **AC**: AC-US3-03 | **Status**: [x] completed
**Test Plan**: Given SKILL.md Section 3 → When reading CONTRACT_READY → Then broadcast mentioned for downstream notification

## Phase 3: Agent Templates

### T-012: Add QUERY_READY idle phase to all 5 agent templates
**User Story**: US-001 | **AC**: AC-US1-04 | **Status**: [x] completed
**Test Plan**: Given backend.md, frontend.md, database.md, testing.md, security.md → When reading after COMPLETION block → Then each has QUERY_READY idle phase with wait-for-QUERY/SHUTDOWN_AUTHORIZED instructions
