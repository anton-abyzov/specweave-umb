---
id: US-005
feature: FS-383
title: "Fix assertion drift in skills and infrastructure tests (P1)"
status: completed
priority: P1
created: 2026-02-27T00:00:00.000Z
tldr: "**As a** developer maintaining the skills activation system
**I want** skills trigger and constraint tests to match current behavior
**So that** these test files pass."
project: specweave
---

# US-005: Fix assertion drift in skills and infrastructure tests (P1)

**Feature**: [FS-383](./FEATURE.md)

**As a** developer maintaining the skills activation system
**I want** skills trigger and constraint tests to match current behavior
**So that** these test files pass

---

## Acceptance Criteria

- [x] **AC-US5-01**: `new-skills-trigger-activation.test.ts` infra skill list expectations match current registered skills (10 failures fixed)
- [x] **AC-US5-02**: `stop-auto-v5-helpers.test.ts` line count assertion updated to match actual hook size (currently 249 lines, test asserted <200)
- [x] **AC-US5-03**: `template-validation.test.ts` AGENTS.md template assertions updated to match current template (includes current section names)
- [x] **AC-US5-04**: All three test files pass

---

## Implementation

**Increment**: [0383-fix-develop-tests-automerge](../../../../../increments/0383-fix-develop-tests-automerge/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
