---
increment: 0681-versions-route-test-mocks-stale
title: Fix stale mocks in versions API route tests (11 failing)
type: bug
priority: P2
status: completed
created: 2026-04-23T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Bug Fix: Fix stale mocks in versions API route tests (11 failing)

## Overview

All 11 tests in `versions/__tests__/route.test.ts` fail with `TypeError: Cannot read properties of undefined (reading 'findUnique')`. The mock database in the test file is out of sync with a route refactor that added a `db.skill.findUnique()` lookup step. The fix is a ~20-line addition to the `vi.hoisted()` `mockDb` block in the test file — no route or production code changes.

## Problem Statement

- **File with failing tests**: `repositories/anton-abyzov/vskill-platform/src/app/api/v1/skills/[owner]/[repo]/[skill]/versions/__tests__/route.test.ts`
- **Failure signature**: `TypeError: Cannot read properties of undefined (reading 'findUnique')` on all 11 tests
- **Root cause**: The route implementation at `repositories/anton-abyzov/vskill-platform/src/app/api/v1/skills/[owner]/[repo]/[skill]/versions/route.ts:15` calls `db.skill.findUnique({ where: { name: ... } })` as a skill-by-name lookup step. The `vi.hoisted(() => ({ mockDb }))` block near line 16 of the test file declares only `db.skillVersion`, not `db.skill` — so `db.skill` is `undefined` at call time, and reading `.findUnique` throws.
- **Origin**: Mock drift from an earlier route refactor that added the skill-by-name lookup without updating the test double.
- **Impact**: Entire versions API route test suite red; blocks CI and masks any real regressions in that route.

## Interview Coverage

This is a ~20-line test-mock hotfix; the strict-interview categories are acknowledged inline rather than elaborated, since they are not materially in play for a single-file test-double edit.

- **Architecture**: No architectural change. Test double is aligned to existing route surface (`db.skill.findUnique` at `versions/route.ts:15`). Route code is not modified.
- **Integrations**: None. Prisma client is mocked; no real DB, network, or third-party integration is exercised by the fix.
- **UI/UX**: Not applicable. API route tests only; no UI surface.
- **Performance**: Not applicable. Fix affects test-suite runtime only (restores from all-failing to passing); no production performance impact.
- **Security**: Not applicable. No auth, authz, input-handling, or secret surface is touched. Mock data (`id: "sk_1"`) is synthetic.
- **Edge cases**: Default mock returns a skill record for happy-path tests; the "skill not found" branch is covered by per-test `mockResolvedValueOnce(null)` overrides. No new edge cases are introduced; existing test cases are not modified.

## User Stories

### US-001: Restore green test suite for versions API route (P2)
**Project**: vskill-platform

**As a** vskill-platform engineer
**I want** the versions API route test file to pass all 11 tests again
**So that** CI is green, regressions are caught, and the route is safe to refactor

**Acceptance Criteria**:
- [x] **AC-US1-01**: Given the test file has a `skill.findUnique` mock added to the hoisted `mockDb` block, when all 11 tests in `route.test.ts` run under `npx vitest run`, then all 11 pass with no `TypeError: Cannot read properties of undefined (reading 'findUnique')` anywhere in the output.
- [x] **AC-US1-02**: Given the fix is intentionally minimal, when the diff is inspected, then only the `vi.hoisted()` `mockDb` block in `route.test.ts` is modified — no changes to individual test cases, no changes to `route.ts`, no changes to any other production or test file.

## Functional Requirements

### FR-001: Mock surface matches route surface
The `mockDb` declared in the test file's `vi.hoisted()` block MUST expose every `db.<model>.<method>` pair that `route.ts` invokes. Specifically, it MUST include `skill.findUnique` returning a skill record by default (e.g., `{ id: "sk_1", name: "owner/repo/skill-name" }`) so the happy-path tests proceed past the lookup step.

### FR-002: Override path for "skill not found" cases
Any test that needs to exercise the 404 / "skill does not exist" branch MUST be able to override the default via `mockDb.skill.findUnique.mockResolvedValueOnce(null)` without rewiring the hoisted block.

## Success Criteria

- `npx vitest run "src/app/api/v1/skills/[owner]/[repo]/[skill]/versions/__tests__/route.test.ts"` reports 11 passed, 0 failed.
- No `TypeError` occurrences in the test output.
- Diff is confined to a single file (the test file) and a single block (the `vi.hoisted()` `mockDb`).

## Out of Scope

- Changes to `route.ts` (the route implementation is correct; the test double is stale).
- Refactoring any other test file or mock.
- Adding new test cases or coverage for behaviors not already exercised.
- Introducing a shared mock-db helper or broader test infrastructure changes.

## Dependencies

- None. Self-contained hotfix in a single test file.
