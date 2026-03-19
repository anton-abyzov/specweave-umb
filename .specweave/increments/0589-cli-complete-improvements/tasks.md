# Tasks: CLI Complete Command Improvements

## Task Notation

- `[T###]`: Task ID
- `[P]`: Parallelizable with sibling tasks
- `[ ]`: Not started
- `[x]`: Completed
- Model hints: haiku (simple), sonnet (default), opus (complex)

---

## Phase 1: Parallel Foundation (T-001 and T-003 run in parallel)

### T-001: Extract resolveIncrementId() to shared utility [P]

**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05
**Status**: [ ] Not Started

**Description**: Extract the private `resolveIncrementId()` function from `src/cli/commands/evaluate-completion.ts:59-76` into a new shared utility at `src/utils/resolve-increment-id.ts`. Enhance it to handle ambiguous (multiple-prefix) matches. Update `evaluate-completion.ts` to import from the new shared module and remove its local copy.

**Implementation Details**:
- Create `repositories/anton-abyzov/specweave/src/utils/resolve-increment-id.ts`
- Export `resolveIncrementId(incrementId: string, projectRoot?: string): string | null` — returns full slug or null
- For ambiguous matches (multiple dirs share the same prefix), return the array of matches for the caller to handle — the signature should return `string | string[] | null`: exact match → `string`, single prefix match → `string`, multi match → `string[]`, no match → `null`
- Import `resolveEffectiveRoot` from `../../utils/find-project-root.js` for default projectRoot
- Delete `findProjectRoot()` and `resolveIncrementId()` from `evaluate-completion.ts`, replace with import from shared utility
- Write unit tests at `repositories/anton-abyzov/specweave/tests/unit/utils/resolve-increment-id.test.ts`

**Test Plan**:
- **File**: `tests/unit/utils/resolve-increment-id.test.ts`
- **Tests**:
  - **TC-001**: Exact match returns full slug unchanged
    - Given an increments dir containing `0589-cli-complete-improvements`
    - When `resolveIncrementId('0589-cli-complete-improvements', root)` is called
    - Then it returns `'0589-cli-complete-improvements'`
  - **TC-002**: Short prefix resolves to single match
    - Given an increments dir containing only `0589-cli-complete-improvements`
    - When `resolveIncrementId('0589', root)` is called
    - Then it returns `'0589-cli-complete-improvements'`
  - **TC-003**: No match returns null
    - Given an increments dir with no `9999-*` entries
    - When `resolveIncrementId('9999', root)` is called
    - Then it returns `null`
  - **TC-004**: Ambiguous prefix returns all matches as array
    - Given an increments dir containing `0573-fix-a` and `0573-fix-b`
    - When `resolveIncrementId('0573', root)` is called
    - Then it returns `['0573-fix-a', '0573-fix-b']`
  - **TC-005**: Empty increments dir returns null
    - Given an increments dir that exists but is empty
    - When `resolveIncrementId('0589', root)` is called
    - Then it returns `null`

**Dependencies**: None

---

### T-003: Fix parseTasksWithUSLinks() call site [P]

**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04
**Status**: [ ] Not Started

**Description**: Fix the bug at `completion-validator.ts:400` where `parseTasksWithUSLinks(tasksContent)` is called with the file content string instead of the file path. Change it to pass `tasksPath`. Remove the now-redundant `tasksContent` read (line 394). Verify the existing try/catch already handles parse errors with a warning (degrades gracefully).

**Implementation Details**:
- Edit `repositories/anton-abyzov/specweave/src/core/increment/completion-validator.ts`
- Remove `const tasksContent = await fs.readFile(tasksPath, 'utf-8');` (~line 394)
- Change `parseTasksWithUSLinks(tasksContent)` → `parseTasksWithUSLinks(tasksPath)` (~line 400)
- Confirm the surrounding try/catch (lines ~107-140) emits a warning with the error message when parsing fails — if not already, add the error message to the warning string to satisfy AC-US3-04
- Write unit tests covering both the fix and graceful degradation

**Test Plan**:
- **File**: `tests/unit/core/increment/completion-validator-ac-coverage.test.ts`
- **Tests**:
  - **TC-001**: Correct path is passed to parseTasksWithUSLinks
    - Given a validator instance and a valid tasksPath
    - When `validateACCoverage()` is called
    - Then `parseTasksWithUSLinks` receives the file path, not the file content
  - **TC-002**: Parse error degrades to warning, does not throw
    - Given `parseTasksWithUSLinks` throws a parse error
    - When `validateACCoverage()` is called
    - Then no exception propagates and a warning containing the error message is emitted
  - **TC-003**: Successful parse + violations still block
    - Given a tasks.md with a P0 AC that has no implementing task
    - When `validateACCoverage()` is called
    - Then the result contains a blocking violation (no regression)
  - **TC-004**: Warning message includes parse error detail (AC-US3-04)
    - Given `parseTasksWithUSLinks` throws `Error('unexpected token at line 5')`
    - When `validateACCoverage()` degrades to warning
    - Then the warning text includes `'unexpected token at line 5'`

**Dependencies**: None

---

## Phase 2: Batch Mode (depends on T-001)

### T-002: Add short-ID resolution and batch mode to complete command

**User Story**: US-001, US-002 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05
**Status**: [ ] Not Started

**Description**: Wire `resolveIncrementId()` into `complete.ts` and change the command to accept variadic arguments. Update the Commander.js registration in `bin/specweave.js` from `<increment-id>` to `<increment-id> [more-ids...]`. Add batch loop with per-ID error isolation, summary output, and non-zero exit code if any ID fails.

**Implementation Details**:
- Edit `repositories/anton-abyzov/specweave/src/cli/commands/complete.ts`:
  - Import `resolveIncrementId` from `../../utils/resolve-increment-id.js`
  - Import `resolveEffectiveRoot` from `../../utils/find-project-root.js`
  - Change signature: `completeCommand(incrementId: string, moreIds: string[], options: CompleteCommandOptions)`
  - Merge into `[incrementId, ...moreIds]` and iterate
  - For each ID: resolve via `resolveIncrementId()` → if null emit error + mark failed → else call `completeIncrement()`
  - For ambiguous result (string[]) emit error listing matches + mark failed
  - Collect successes/failures; after loop print summary line
  - Exit with code 1 if any failed
- Edit `repositories/anton-abyzov/specweave/bin/specweave.js` (~line 339):
  - Change `.command('complete <increment-id>')` → `.command('complete <increment-id> [more-ids...]')`
  - Update `.action(async (incrementId, moreIds, options) => ...)` to pass `moreIds`
- Write unit tests at `repositories/anton-abyzov/specweave/tests/unit/cli/complete-command.test.ts`

**Test Plan**:
- **File**: `tests/unit/cli/complete-command.test.ts`
- **Tests**:
  - **TC-001**: Single ID completes successfully
    - Given `resolveIncrementId` returns a full slug and `completeIncrement` returns true
    - When `completeCommand('0589', [], {})` is called
    - Then `completeIncrement` is called once with the resolved slug and process exits 0
  - **TC-002**: Single short ID resolves before completing
    - Given `resolveIncrementId('0589', ...)` returns `'0589-cli-complete-improvements'`
    - When `completeCommand('0589', [], {})` is called
    - Then `completeIncrement` is called with `'0589-cli-complete-improvements'`
  - **TC-003**: Unknown short ID emits error and exits 1
    - Given `resolveIncrementId('9999', ...)` returns null
    - When `completeCommand('9999', [], {})` is called
    - Then an error mentioning `'9999'` is logged and process exits 1
  - **TC-004**: Ambiguous ID lists matches and exits 1
    - Given `resolveIncrementId('0573', ...)` returns `['0573-fix-a', '0573-fix-b']`
    - When `completeCommand('0573', [], {})` is called
    - Then both matches are printed and process exits 1
  - **TC-005**: Batch — all IDs succeed, exit 0
    - Given all three IDs resolve and complete successfully
    - When `completeCommand('0573', ['0562', '0571'], {})` is called
    - Then `completeIncrement` is called 3 times and process exits 0
  - **TC-006**: Batch — one fails, others continue, exit 1 with summary
    - Given `completeIncrement` returns false for `'0562'` and true for the others
    - When `completeCommand('0573', ['0562', '0571'], {})` is called
    - Then all 3 IDs are attempted, summary shows 1 failure, process exits 1
  - **TC-007**: Batch — short-ID resolution applied to all IDs
    - Given `resolveIncrementId` resolves each short ID
    - When multiple short IDs are passed
    - Then each ID is resolved before being passed to `completeIncrement`

**Dependencies**: T-001 (resolveIncrementId shared utility must exist)

---

## Phase 3: Verification

### T-004: Run full test suite and verify all ACs

**User Story**: US-001, US-002, US-003 | **Status**: [ ] Not Started

**Description**: Run `npx vitest run` in the specweave repo. Confirm all new tests pass. Manually verify the three end-to-end scenarios work against a real `.specweave/` directory.

**Test Plan**:
- **TC-001**: `npx vitest run` exits 0 with no failures
- **TC-002**: `specweave complete 0589` resolves and succeeds (AC-US1-01)
- **TC-003**: `specweave complete 0589-cli-complete-improvements` still works (AC-US1-02)
- **TC-004**: `specweave complete 9999` shows clear error (AC-US1-03)
- **TC-005**: `specweave complete 0573 0562 0571` processes all three IDs (AC-US2-01)

**Dependencies**: T-001, T-002, T-003
