---
id: US-004
feature: FS-383
title: "Fix assertion drift in CLI and plugin tests (P1)"
status: completed
priority: P1
created: 2026-02-27T00:00:00.000Z
tldr: "**As a** developer maintaining CLI and plugin systems
**I want** CLI and plugin test expectations to match current source behavior
**So that** these test files pass."
project: specweave
---

# US-004: Fix assertion drift in CLI and plugin tests (P1)

**Feature**: [FS-383](./FEATURE.md)

**As a** developer maintaining CLI and plugin systems
**I want** CLI and plugin test expectations to match current source behavior
**So that** these test files pass

---

## Acceptance Criteria

- [x] **AC-US4-01**: `update.test.ts` mock expectations match current implementation (2 failures fixed)
- [x] **AC-US4-02**: `selection-strategy.test.ts` regex matching expectation updated (expects current return count)
- [x] **AC-US4-03**: `claude-plugin-cli.test.ts` plugin registration argument expectations match current signature
- [x] **AC-US4-04**: `plugin-scope-config.test.ts` returns correct scope value matching current behavior
- [x] **AC-US4-05**: All four test files pass

---

## Implementation

**Increment**: [0383-fix-develop-tests-automerge](../../../../../increments/0383-fix-develop-tests-automerge/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
