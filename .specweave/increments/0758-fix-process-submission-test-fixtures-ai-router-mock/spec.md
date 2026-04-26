---
increment: 0758-fix-process-submission-test-fixtures-ai-router-mock
title: Fix stale process-submission.test.ts ai-router mock
type: bug
priority: P1
status: completed
created: 2026-04-26T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Fix stale process-submission.test.ts ai-router mock

## Overview

`src/lib/queue/__tests__/process-submission.test.ts` has 14 failing tests because production `process-submission.ts:521-525` introduced a dynamic `await import("@/lib/ai/ai-router")` that the test fixture never mocked. The unmocked dynamic import throws → execution lands in the catch block at line 647 → `tier1WeightedScore >= 65 && !tier1Result.criticalCount` triggers `updateStateMulti(AUTO_APPROVED, PUBLISHED)` instead of the `updateState(REJECTED)` path the tests expect. The fix is a single hoisted `vi.mock("@/lib/ai/ai-router", ...)` block in the test file. Production code stays untouched.

## User Stories

### US-001: process-submission test suite green (P1)
**Project**: vskill-platform

**As a** vskill-platform maintainer
**I want** `process-submission.test.ts` to pass cleanly
**So that** the test suite reflects current production behavior and doesn't mask real regressions.

**Acceptance Criteria**:
- [x] **AC-US1-01**: A hoisted mock helper `mockCreateAiRouter = vi.hoisted(() => vi.fn(() => ({})))` and a `vi.mock("@/lib/ai/ai-router", () => ({ createAiRouter: mockCreateAiRouter }))` block are added to `repositories/anton-abyzov/vskill-platform/src/lib/queue/__tests__/process-submission.test.ts`.
- [x] **AC-US1-02**: `npx vitest run src/lib/queue/__tests__/process-submission.test.ts` reports **0 failures** (was 14).
- [x] **AC-US1-03**: `git diff repositories/anton-abyzov/vskill-platform/src/lib/queue/process-submission.ts` is empty — production code is unchanged.

## Functional Requirements

### FR-001: Hoisted mock for ai-router
The test file must register `@/lib/ai/ai-router` as a mocked module before `processSubmission` is imported, mirroring the existing pattern used for the other 12+ mocked modules at lines 36–128.

## Success Criteria

- 14 → 0 failures in `process-submission.test.ts`.
- No change to `process-submission.ts` or any other production file.
- No regressions in neighboring queue test files (`consumer.test.ts`, `recovery.test.ts`, etc.).

## Out of Scope

- Refactoring the dynamic import in `process-submission.ts` to inject `createAiRouter` via `opts` (sensible but separate increment).
- Auditing other `await import(...)` calls in the codebase for the same pattern.
- Updating Vitest reporter config (`environmentMatchGlobs` / `'basic'` reporter deprecation warnings).

## Dependencies

None. Single-file test edit.
