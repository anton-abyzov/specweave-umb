# Tasks — 0331: Universal Skills Migration

## Phase 1: vskill — Add Plugin Structure

### T-001: Copy generic plugins to vskill/plugins/
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 | **Status**: [x] completed
**Test**: Given specweave plugins → When copied to vskill/plugins/ → Then all SKILL.md files exist

### T-002: Create security plugin from core skills
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-04 | **Status**: [x] completed
**Test**: Given 3 core skills → When new plugin created → Then skill-memories boilerplate stripped

### T-003: Create docs plugin (generic subset)
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 | **Status**: [x] completed
**Test**: Given 3 generic docs skills → When new plugin created → Then only generic skills included

### T-004: Create marketplace.json
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03 | **Status**: [x] completed
**Test**: Given vskill root → When marketplace.json created → Then lists all 15 plugins

### T-005: Update plugin.json files
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02 | **Status**: [x] completed
**Test**: Given all plugin.json → When updated → Then name field has no sw- prefix

### T-006: Fix cross-skill references
**User Story**: US-001 | **Satisfies ACs**: AC-US1-05 | **Status**: [x] completed
**Test**: Given migrated skills → When grep for /sw- → Then zero matches

### T-007: Strip SpecWeave references
**User Story**: US-001 | **Satisfies ACs**: AC-US1-04 | **Status**: [x] completed
**Test**: Given all SKILL.md → When grep for specweave → Then zero matches

## Phase 2: vskill CLI — --repo flag

### T-008: Add --repo flag to vskill add command
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03 | **Status**: [x] completed
**Test**: Given --repo flag → When vskill add --repo owner/repo --plugin name → Then skills installed with namespace

### T-009: Add tests for --repo flag
**User Story**: US-002 | **Satisfies ACs**: AC-US2-04 | **Status**: [x] completed
**Test**: Given test suite → When tests run → Then --repo flow is covered

## Phase 3: SpecWeave Cleanup

### T-010: Delete migrated plugin directories
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02 | **Status**: [x] completed
**Test**: Given specweave/plugins → When dirs deleted → Then only framework-specific plugins remain

### T-011: Update specweave marketplace.json
**User Story**: US-003 | **Satisfies ACs**: AC-US3-03 | **Status**: [x] completed
**Test**: Given marketplace.json → When updated → Then no migrated plugin entries

## Phase 4: Platform

### T-012: Add submit-vskill.sh script
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02 | **Status**: [x] completed
**Test**: Given script → When --dry-run → Then lists all skills with correct paths
