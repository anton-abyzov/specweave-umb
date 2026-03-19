# Tasks: Universal SKILL.md + Dead Code Cleanup

## Phase 1: SKILL.md Restructure

### T-001: Restructure increment SKILL.md to CLI-first universal format
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04 | **Status**: [x] completed
**Test Plan**:
- Given the SKILL.md file
- When I search for TeamCreate, Agent(), SendMessage
- Then they only appear in the Step 4a "Enhanced" optional section

## Phase 2: Dead Code Removal

### T-002: Remove dead ID pre-generation from create-increment.ts
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03 | **Status**: [x] completed
**Test Plan**:
- Given autoId=true and a name
- When create-increment runs
- Then resolvedId is empty string, template-creator handles atomic ID

### T-003: Update next-id help text
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01 | **Status**: [x] completed
**Test Plan**:
- Given the specweave CLI
- When I check the next-id command description
- Then it recommends create-increment --auto-id
