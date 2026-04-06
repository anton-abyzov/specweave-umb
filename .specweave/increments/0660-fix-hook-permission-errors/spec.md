---
increment: 0660-fix-hook-permission-errors
title: Fix shell hook permission errors by removing ; true
type: bug
priority: P1
status: completed
created: 2026-04-06T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Fix shell hook permission errors by removing ; true

## Overview

Remove semicolon-true from all DCI hook patterns. Claude Code flags semicolons as multiple operations, breaking skill loading for users with default permissions.

## User Stories

### US-001: Skill Hook Compatibility (P1)
**Project**: specweave

**As a** SpecWeave user with default Claude Code permissions
**I want** skill hooks to execute without permission errors
**So that** I can use `/sw:increment`, `/sw:doctor`, and other skills normally

**Acceptance Criteria**:
- [x] **AC-US1-01**: No SKILL.md file contains `; true` in DCI hook patterns
- [x] **AC-US1-02**: No command .md file contains inline DCI patterns (the `s="name"; for d in...` format)
- [x] **AC-US1-03**: All command .md files use `.specweave/scripts/skill-memories.sh <name> 2>/dev/null` format
- [x] **AC-US1-04**: All skill-context.sh DCI calls have `; true` removed
- [x] **AC-US1-05**: Tests are updated to not assert presence of `; true`
- [x] **AC-US1-06**: All existing tests pass after the changes

## Out of Scope

- Changes to skill-memories.sh or skill-context.sh scripts (already correct)
- Changes to Claude Code's permission system
