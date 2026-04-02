# Tasks: sw:umbrella skill for automated workspace creation

## Phase 1: Implementation

### T-001: Create SKILL.md skill definition
**User Story**: US-001, US-002 | **Satisfies ACs**: AC-US1-01 through AC-US1-06, AC-US2-01 through AC-US2-04 | **Status**: [x] Completed
**Test Plan**:
- Given the skill file exists at `plugins/specweave/skills/umbrella/SKILL.md`
- When `specweave refresh-plugins` is run
- Then the skill appears in available skills list

## Phase 2: Verification

### T-002: Verify skill loads and is discoverable
**User Story**: US-001 | **Status**: [x] Completed
**Test Plan**:
- Given T-001 is complete
- When running `specweave refresh-plugins`
- Then `sw:umbrella` appears in skill list
