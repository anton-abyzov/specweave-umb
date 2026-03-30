# Tasks: Add --bare flag to Claude CLI subprocess spawns

## Task Notation

- `[T###]`: Task ID
- `[P]`: Parallelizable
- `[ ]`: Not started
- `[x]`: Completed
- Model hints: haiku (simple), opus (default)

## Phase 1: TDD Red - Write Failing Tests

### T-001: Write failing test for claude-code-provider --bare flag
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03 | **Status**: [x] completed

**Test Plan**:
- **File**: `tests/unit/core/llm/providers/claude-code-provider.test.ts`
- **Tests**:
  - **TC-001**: --bare flag present in analyze() spawn args
    - Given a ClaudeCodeProvider instance
    - When analyze() is called with a prompt
    - Then the spawned process args array includes '--bare' as the first argument
  - **TC-002**: --bare coexists with --system-prompt flag
    - Given a ClaudeCodeProvider instance
    - When analyze() is called with a systemPrompt option
    - Then args contain both '--bare' and '--system-prompt'
  - **TC-003**: --bare present in getStatus() health check
    - Given a ClaudeCodeProvider instance
    - When getStatus() is called
    - Then the spawned process args include '--bare'

**Dependencies**: None

---

### T-002: Write failing test for completion-evaluator --bare flag
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02 | **Status**: [x] completed

**Test Plan**:
- **File**: `tests/unit/core/auto/completion-evaluator.test.ts`
- **Tests**:
  - **TC-004**: --bare flag in LLM evaluation calls
    - Given an evaluation context with llm_evaluate criterion
    - When evaluateViaLLM() is invoked
    - Then the claude CLI args include '--bare' before '-p'
  - **TC-005**: --bare flag in extractSuccessCriteria()
    - Given a user prompt for auto mode
    - When extractSuccessCriteria() is called
    - Then the claude CLI args include '--bare'

**Dependencies**: None

---

### T-003: Write failing test for llm-plugin-detector --bare flag
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02 | **Status**: [x] completed

**Test Plan**:
- **File**: `tests/unit/core/lazy-loading/llm-plugin-detector.test.ts`
- **Tests**:
  - **TC-006**: --bare replaces --setting-sources in detectIntent
    - Given a user prompt for intent detection
    - When detectIntent() calls executeClaudeCli
    - Then args include '--bare' and do NOT include '--setting-sources'
  - **TC-007**: --bare is first arg before -p
    - Given a user prompt
    - When detectIntent() builds CLI args
    - Then '--bare' appears before '-p' in the args array

**Dependencies**: None

## Phase 2: TDD Green - Implement Changes

### T-004: Add --bare to claude-code-provider.ts
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03 | **Status**: [x] completed

**Implementation**:
- In `executeClaudeCommand()`, initialize args with `['--bare']` instead of `[]`
- No other changes needed -- existing flags append after

**Dependencies**: T-001

---

### T-005: Add --bare to completion-evaluator.ts
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02 | **Status**: [x] completed

**Implementation**:
- In `evaluateViaLLM()` call (line ~294), prepend `'--bare'` to args
- In `extractSuccessCriteria()` call (line ~561), prepend `'--bare'` to args

**Dependencies**: T-002

---

### T-006: Add --bare to llm-plugin-detector.ts, remove --setting-sources
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02 | **Status**: [x] completed

**Implementation**:
- In `detectIntent()` call (line ~902), prepend `'--bare'` and remove `'--setting-sources', ''`

**Dependencies**: T-003

## Phase 3: TDD Refactor + Verification

### T-007: Run full test suite and verify no regressions
**User Story**: US-001, US-002, US-003 | **Satisfies ACs**: All | **Status**: [x] completed

**Test Plan**:
- Run `npx vitest run` in specweave repo
- Verify all tests pass including new --bare assertions
- Verify no existing tests broke

**Dependencies**: T-004, T-005, T-006
