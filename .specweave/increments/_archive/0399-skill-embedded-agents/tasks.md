# Tasks — 0399-skill-embedded-agents

## Phase 1: Token Isolation (Quick Wins)

### T-001: Add `context: fork` + `model: opus` to architect, test-aware-planner, grill
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03 | **Status**: [x] completed
**Test**: Given skill frontmatter → When loaded → Then runs in isolated context with Opus model

## Phase 2: Agent Extraction

### T-002: Create 5 agent .md files for team-lead
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 | **Status**: [x] completed
**Test**: Given agents/ directory → When files read → Then each contains role, ownership, workflow, rules

### T-003: Refactor team-lead SKILL.md to reference agent files
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02, AC-US1-03 | **Status**: [x] completed
**Test**: Given refactored SKILL.md → When line count checked → Then reduced by ~250 lines

## Phase 3: vskill Distribution

### T-004: Fix vskill `shouldSkipFromCommands` filter
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01 | **Status**: [x] completed
**Test**: Given path `skills/team-lead/agents/frontend.md` → When filtered → Then NOT skipped

### T-005: Update vskill canonical installer for agents/ support
**User Story**: US-003 | **Satisfies ACs**: AC-US3-02, AC-US3-03 | **Status**: [x] completed
**Test**: Given installSymlink/installCopy with agentFiles → When called → Then agents/ written alongside SKILL.md

## Phase 4: Verification

### T-006: Run tests and verify behavioral equivalence
**User Story**: US-001, US-002, US-003 | **Satisfies ACs**: AC-US1-04, AC-US2-04, AC-US3-04 | **Status**: [x] completed
**Test**: Given all changes → When tests run → Then 9/9 canonical tests pass, filter logic verified

## Phase 5: Agent Memory

### T-007: Add lightweight agent execution memory
**User Story**: N/A | **Status**: [x] completed
**Test**: Given skill-memories/agents.md → When read → Then contains team composition, spawning, and communication learnings
