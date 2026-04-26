---
increment: 0760-fix-consumer-test-fixtures-ai-router-mock
title: Fix stale consumer.test.ts message routing fixtures
type: bug
priority: P1
status: completed
created: 2026-04-26T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Fix stale consumer.test.ts message routing fixtures

## Overview

`src/lib/queue/__tests__/consumer.test.ts` has 5 failing tests. Production `consumer.ts:169` calls `createAiRouter(env)` synchronously when constructing the `processSubmission` arguments. `createAiRouter` (`ai-router.ts:71`) throws `"[ai-router] No AI providers configured"` when env has no AI bindings — which is exactly the case in the test's `makeEnv()`. The throw lands in the consumer's catch block, triggers `message.retry()`, and `processSubmission` is never called — so the assertions `expect(mockProcessSubmission).toHaveBeenCalled()` fail with 0 calls.

This is the same shape of fixture-lag fixed in increment 0758 for `process-submission.test.ts`. Fix: mock `@/lib/ai/ai-router` in `consumer.test.ts`. No production code change.

## User Stories

### US-001: consumer test suite green (P1)
**Project**: vskill-platform

**As a** vskill-platform maintainer
**I want** `consumer.test.ts` to pass cleanly
**So that** the queue routing test suite reflects current production behavior and CI is green.

**Acceptance Criteria**:
- [x] **AC-US1-01**: A hoisted helper `mockCreateAiRouter = vi.hoisted(() => vi.fn(() => ({})))` and a `vi.mock("@/lib/ai/ai-router", () => ({ createAiRouter: mockCreateAiRouter }))` block are added to `repositories/anton-abyzov/vskill-platform/src/lib/queue/__tests__/consumer.test.ts`.
- [x] **AC-US1-02**: `npx vitest run src/lib/queue/__tests__/consumer.test.ts` reports **0 failures** (was 5).
- [x] **AC-US1-03**: `git diff repositories/anton-abyzov/vskill-platform/src/lib/queue/consumer.ts` is empty — production code is unchanged.

## Functional Requirements

### FR-001: Hoisted mock for ai-router in consumer test
The test file must register `@/lib/ai/ai-router` as a mocked module before `handleSubmissionQueue` is imported, mirroring the existing pattern (process-submission, metrics-store, scan-log-store, search-index-consumer, worker-context, submission-store).

## Success Criteria

- 5 → 0 failures in `consumer.test.ts`.
- No change to `consumer.ts` or any other production file.
- The previously-passing tests (`calls retry() on processing failure`, `routes rebuild_search_shard message to handleSearchIndexUpdate`) continue to pass.

## Out of Scope

- Refactoring `consumer.ts` to inject `createAiRouter` via opts (sensible but separate increment).
- Auditing other dynamic-or-eager AI client constructions in the codebase.

## Dependencies

None. Single-file test edit. Parallel to 0758.
