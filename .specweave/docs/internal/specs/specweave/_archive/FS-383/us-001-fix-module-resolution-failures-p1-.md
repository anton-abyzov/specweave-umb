---
id: US-001
feature: FS-383
title: "Fix module resolution failures (P1)"
status: completed
priority: P1
created: 2026-02-27T00:00:00.000Z
tldr: "**As a** developer on the develop branch
**I want** all test imports to resolve to valid source modules
**So that** tests can execute without 'module not found' errors."
project: specweave
---

# US-001: Fix module resolution failures (P1)

**Feature**: [FS-383](./FEATURE.md)

**As a** developer on the develop branch
**I want** all test imports to resolve to valid source modules
**So that** tests can execute without "module not found" errors

---

## Acceptance Criteria

- [x] **AC-US1-01**: `context.test.ts` imports resolve correctly after `/src/cli/commands/context.js` was moved/renamed, or test file is deleted if source was removed with no replacement
- [x] **AC-US1-02**: All 5 playwright-cli test files resolve correctly after `/plugins/specweave-testing/lib/playwright-ci-defaults.js` was moved/renamed, or test files are deleted if source was removed with no replacement
- [x] **AC-US1-03**: Zero "Cannot find module" errors remain in the test suite

---

## Implementation

**Increment**: [0383-fix-develop-tests-automerge](../../../../../increments/0383-fix-develop-tests-automerge/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
