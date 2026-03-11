---
increment: 0490-remove-init-increment-reservation
title: "Remove 0001-project-setup reservation"
type: feature
priority: P1
status: planned
created: 2026-03-11
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Remove 0001-project-setup reservation

## Overview

The `specweave init` command was simplified in v1.0.415 to no longer create a reserved `0001-project-setup` increment during initialization. However, documentation (quick-start, greenfield glossary) still references this phantom increment, showing it in directory trees and instructing users that their first feature will be `0002`. The CLAUDE.md template correctly says "Your first increment starts at 0001", but the quick-start guide contradicts this by showing `0001-project-setup/` as an init artifact.

This increment cleans up all stale references to the `0001-project-setup` reservation pattern across docs and templates, ensuring a consistent message: the user's first increment is always `0001`.

## Problem Statement

1. **Inconsistent documentation**: quick-start.md shows `0001-project-setup/` created by init and the first user increment at `0002-click-counter`. The CLAUDE.md template says "Your first increment starts at 0001". Users encounter contradictory guidance.
2. **Wasted number slot in examples**: Docs that show `0001-project-setup-and-auth` as a user-created increment blur the line between system-created and user-created increments.
3. **Confusing onboarding**: New users who follow the quick-start expect to see `0001-project-setup/` after running init, but it does not exist.

## Goals

- Remove all references to `0001-project-setup` as a system-created increment from documentation
- Update quick-start and greenfield guides so the first user increment is `0001`
- Ensure no code path in the init flow creates or depends on a `0001-project-setup` increment
- Validate that `IncrementNumberManager.getNextIncrementNumber()` returns `0001` on a fresh project

## User Stories

### US-001: Clean first increment experience (P1)
**Project**: specweave

**As a** new SpecWeave user
**I want** my first increment to be numbered `0001`
**So that** there are no confusing phantom increments in my project

**Acceptance Criteria**:
- [ ] **AC-US1-01**: Running `specweave init` does not create any folder under `.specweave/increments/`
- [ ] **AC-US1-02**: After init, `IncrementNumberManager.getNextIncrementNumber()` returns `"0001"`
- [ ] **AC-US1-03**: The quick-start guide shows the first user increment as `0001-click-counter` (not `0002`)

---

### US-002: Consistent documentation (P1)
**Project**: specweave

**As a** developer reading SpecWeave docs
**I want** all docs to agree that the first increment is `0001`
**So that** I am not confused by conflicting information

**Acceptance Criteria**:
- [ ] **AC-US2-01**: `docs-site/docs/quick-start.md` no longer references `0001-project-setup` in the init output tree
- [ ] **AC-US2-02**: `docs-site/docs/quick-start.md` shows the first user-created increment as `0001-*` (not `0002-*`)
- [ ] **AC-US2-03**: `docs-site/docs/glossary/terms/greenfield.md` no longer uses `0001-project-setup-and-auth` as a system-reserved example
- [ ] **AC-US2-04**: No doc file under `docs-site/` implies that init creates an increment

---

### US-003: No legacy code paths (P2)
**Project**: specweave

**As a** SpecWeave maintainer
**I want** to confirm there is no residual code that creates a `0001-project-setup` increment during init
**So that** the behavior matches the documentation

**Acceptance Criteria**:
- [ ] **AC-US3-01**: No source file under `src/` contains logic to create an increment folder during the init command
- [ ] **AC-US3-02**: The `createDirectoryStructure` function only creates core directories (increments/, cache/, state/, etc.) without any seed increment
- [ ] **AC-US3-03**: Existing unit tests for init do not assert the existence of `0001-project-setup`

## Functional Requirements

### FR-001: Update quick-start.md directory tree
Remove `0001-project-setup/` from the init output example. Change the first user-created increment from `0002-click-counter` to `0001-click-counter` throughout the guide.

### FR-002: Update greenfield glossary example
Change `0001-project-setup-and-auth` to a plain user-created increment example (e.g., `0001-core-infrastructure-and-auth`).

### FR-003: Audit and confirm no init code creates increments
Verify that `createDirectoryStructure`, `copyTemplates`, `createConfigFile`, and the scaffold flow do not create any increment folders. This is a confirmation task (the code already does not do this as of v1.0.415).

## Success Criteria

- Zero references to `0001-project-setup` as a system-created artifact in `docs-site/docs/` and `src/templates/`
- Quick-start guide is self-consistent (init output matches subsequent steps)
- All existing tests pass without modification (no test depends on the reservation)

## Out of Scope

- Changing the increment numbering algorithm (`IncrementNumberManager`)
- Modifying the init command behavior (it already does not create the reservation)
- Updating the `repository-setup.ts` structureDeferred flow (already deprecated in v1.0.415)
- Changes to external sync or living docs scaffolding

## Dependencies

None. This is a documentation-only change with a code audit confirmation.
