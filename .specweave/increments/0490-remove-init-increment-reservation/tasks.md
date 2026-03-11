# Tasks: Remove 0001-project-setup reservation

## Task Notation

- `[T###]`: Task ID
- `[ ]`: Not started
- `[x]`: Completed
- Model hints: haiku (simple), sonnet (default)

## Phase 1: Documentation Updates

### T-001: Update quick-start.md
**User Story**: US-001, US-002 | **Satisfies ACs**: AC-US1-03, AC-US2-01, AC-US2-02, AC-US2-04 | **Status**: [ ] Not Started

**Description**: Remove the `0001-project-setup/` entry from the init output directory tree in quick-start.md. Change all references of `0002-click-counter` to `0001-click-counter`.

**Implementation Details**:
- File: `repositories/anton-abyzov/specweave/docs-site/docs/quick-start.md`
- Remove line 60: `│   └── 0001-project-setup/`
- Change `0002-click-counter` to `0001-click-counter` (lines 75, 83, and any other references)
- Verify the guide reads consistently after changes

**Test Plan**:
- **TC-001**: Verify no reference to `0001-project-setup` remains in quick-start.md
  - Given quick-start.md is updated
  - When searching for `0001-project-setup`
  - Then zero matches found
- **TC-002**: Verify first user increment is `0001`
  - Given quick-start.md is updated
  - When reading the guide sequentially
  - Then the first user-created increment is numbered `0001`

**Dependencies**: None

---

### T-002: Update greenfield glossary
**User Story**: US-002 | **Satisfies ACs**: AC-US2-03 | **Status**: [ ] Not Started

**Description**: Change the `0001-project-setup-and-auth` example in the greenfield glossary to a user-created increment name that does not imply system reservation.

**Implementation Details**:
- File: `repositories/anton-abyzov/specweave/docs-site/docs/glossary/terms/greenfield.md`
- Line 506: Change `/specweave:increment "0001-project-setup-and-auth"` to `/specweave:increment "core-infrastructure-and-auth"` (without numeric prefix, since the CLI auto-assigns the number)

**Test Plan**:
- **TC-003**: Verify no reference to `project-setup` as a system artifact
  - Given greenfield.md is updated
  - When searching for `0001-project-setup`
  - Then zero matches found

**Dependencies**: None

---

## Phase 2: Code Audit

### T-003: Confirm init does not create increment folders
**User Story**: US-001, US-003 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US3-01, AC-US3-02, AC-US3-03 | **Status**: [ ] Not Started

**Description**: Audit the init code path to confirm no increment folder is created during initialization. This is a read-only verification task.

**Implementation Details**:
- Verify `src/cli/helpers/init/directory-structure.ts` `createDirectoryStructure()` only creates: increments/, cache/, state/, logs/reflect/
- Verify `src/cli/commands/init.ts` does not call any increment creation function
- Verify `src/core/living-docs/scaffolding/scaffold.ts` does not create increment folders
- Verify `src/core/increment/increment-utils.ts` `getNextIncrementNumber()` returns `"0001"` for empty increments dir
- Check existing init tests do not assert `0001-project-setup` existence

**Test Plan**:
- **TC-004**: Code audit confirmation
  - Given the source files listed above
  - When reviewing for increment creation during init
  - Then no code path creates an increment folder during `specweave init`
- **TC-005**: Increment numbering starts at 0001
  - Given an empty `.specweave/increments/` directory
  - When `IncrementNumberManager.getNextIncrementNumber()` is called
  - Then it returns `"0001"`

**Dependencies**: None

---

## Phase 3: Verification

### T-004: Run existing tests
**User Story**: US-003 | **Satisfies ACs**: AC-US3-03 | **Status**: [ ] Not Started

**Description**: Run the existing test suite to confirm no tests break from the documentation changes.

**Implementation Details**:
- Run `npx vitest run` in the specweave repository
- Focus on init-related tests: `tests/unit/cli/commands/init.test.ts`, `tests/unit/increment-utils-gap-filling.test.ts`

**Test Plan**:
- **TC-006**: All existing tests pass
  - Given documentation changes are complete
  - When running `npx vitest run`
  - Then all tests pass (no regressions)

**Dependencies**: T-001, T-002, T-003
