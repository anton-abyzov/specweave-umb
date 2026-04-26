# Tasks: Fix stale process-submission.test.ts ai-router mock

## Task Notation

- `[T###]`: Task ID
- `[ ]`: Not started
- `[x]`: Completed

## Phase 1: Apply test mock

### T-001: Add vi.mock for @/lib/ai/ai-router in process-submission.test.ts

**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03 | **Status**: [x] completed

**Description**: Add a hoisted `mockCreateAiRouter` helper alongside the existing `vi.hoisted()` declarations and a corresponding `vi.mock("@/lib/ai/ai-router", ...)` block alongside the other `vi.mock()` calls in `repositories/anton-abyzov/vskill-platform/src/lib/queue/__tests__/process-submission.test.ts`.

**Implementation**:
- Insert after the existing `mockTryExpandMultiSkill` hoisted line (~line 34):
  ```ts
  const mockCreateAiRouter = vi.hoisted(() => vi.fn(() => ({})));
  ```
- Insert alongside other `vi.mock()` calls (~line 105):
  ```ts
  vi.mock("@/lib/ai/ai-router", () => ({
    createAiRouter: mockCreateAiRouter,
  }));
  ```

**Test Plan**:
  Given the test file has hoisted mocks at lines 36–128 and 14 currently failing tests
  When I add the hoisted `mockCreateAiRouter` helper and the `vi.mock("@/lib/ai/ai-router", ...)` block
  Then `npx vitest run src/lib/queue/__tests__/process-submission.test.ts` reports 0 failures (was 14)
   And `git diff repositories/anton-abyzov/vskill-platform/src/lib/queue/process-submission.ts` shows no change

## Phase 2: Verify

### T-002: Run targeted vitest and confirm 0 failures

**User Story**: US-001 | **Satisfies ACs**: AC-US1-02 | **Status**: [x] completed

**Test Plan**:
  Given T-001 is complete
  When I run `cd repositories/anton-abyzov/vskill-platform && npx vitest run --reporter=basic --no-coverage src/lib/queue/__tests__/process-submission.test.ts`
  Then the output reports 0 failures
   And the prior 14 failing test names appear under passed

### T-003: Confirm no neighbor regressions

**User Story**: US-001 | **Satisfies ACs**: AC-US1-02 | **Status**: [x] completed

**Test Plan**:
  Given T-001 is complete
  When I run `cd repositories/anton-abyzov/vskill-platform && npx vitest run --reporter=basic --no-coverage src/lib/queue/__tests__/`
  Then all neighboring queue tests still pass (consumer.test.ts, recovery.test.ts, state-guard.test.ts, drain-stuck-received.test.ts, etc.)

### T-004: Confirm production file untouched

**User Story**: US-001 | **Satisfies ACs**: AC-US1-03 | **Status**: [x] completed

**Test Plan**:
  Given T-001 is complete
  When I run `git diff repositories/anton-abyzov/vskill-platform/src/lib/queue/process-submission.ts`
  Then the diff is empty
