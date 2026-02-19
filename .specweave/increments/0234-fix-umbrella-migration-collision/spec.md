---
increment: 0234-fix-umbrella-migration-collision
title: "Fix umbrella migration collision handling"
type: feature
priority: P1
status: completed
closed: 2026-02-18
created: 2026-02-17
completed: 2026-02-17
structure: user-stories
test_mode: test-after
coverage_target: 80
---

# Feature: Fix umbrella migration collision handling

## Overview

Add collision detection when target umbrella directory already exists, fix post-move log path to avoid ghost directories, and add move destination safety check to prevent silent data overwrites during migration.

## User Stories

### US-001: Collision Detection and Classification (P1)
**Project**: specweave

**As a** developer migrating to an umbrella structure
**I want** the migration tool to detect and classify existing umbrella directories
**So that** I can make an informed decision about how to proceed

**Acceptance Criteria**:
- [x] **AC-US1-01**: `classifyExistingUmbrella()` returns null when target directory does not exist
- [x] **AC-US1-02**: Returns `previous-migration` when target contains `.specweave/` directory
- [x] **AC-US1-03**: Returns `partial-migration` when backup manifest exists at project root
- [x] **AC-US1-04**: Returns `unrelated` when target exists without SpecWeave markers
- [x] **AC-US1-05**: CLI presents appropriate options based on collision type (wipe/rename/rollback/abort)
- [x] **AC-US1-06**: `--yes` mode auto-wipes previous migrations and aborts on unrelated directories

---

### US-002: Move Destination Safety Check (P1)
**Project**: specweave

**As a** developer running umbrella migration
**I want** the migration to refuse overwriting existing destinations
**So that** I don't silently lose data during the move operation

**Acceptance Criteria**:
- [x] **AC-US2-01**: Move step throws error when destination already exists
- [x] **AC-US2-02**: Error message contains "already exists" and suggests collision handling
- [x] **AC-US2-03**: Migration result reports failure with descriptive error

---

### US-003: Post-Move Log Path Fix (P1)
**Project**: specweave

**As a** developer running umbrella migration
**I want** migration logs to be written to the correct location after `.specweave/` moves
**So that** ghost `.specweave/logs/` directories are not created in the original project

**Acceptance Criteria**:
- [x] **AC-US3-01**: After `.specweave/` moves to umbrella, subsequent logs write to umbrella path
- [x] **AC-US3-02**: No ghost `.specweave/logs/` directory is created in the original project
- [x] **AC-US3-03**: `migration.log` exists in the umbrella's `.specweave/logs/` after successful migration

## Out of Scope

- Automatic merging of colliding umbrella directories
- Remote/cloud-based collision detection
- Multi-project collision resolution (only single-project migration)

## Dependencies

- Increment 0219 (Multi-Repo Migration Tool) - base migration infrastructure

## Success Criteria

- All 6 collision-related tests pass
- No ghost log directories created during migration
- Move operations fail safely when destination exists
