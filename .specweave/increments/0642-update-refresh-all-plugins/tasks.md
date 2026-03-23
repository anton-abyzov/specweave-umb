---
increment: 0642-update-refresh-all-plugins
---

# Tasks

## Phase 1: TDD Red

### T-001: Write failing test for all-plugins-by-default
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 | **Status**: [x] completed

**Test Plan**:
- **File**: `tests/unit/cli/commands/update.test.ts`
- **TC-001**: Update calls refreshPluginsCommand with all:true by default
  - Given a SpecWeave project
  - When `updateCommand({ noSelf: true })` is called (no `--all` flag)
  - Then `refreshPluginsCommand` is called with `{ all: true, ... }`

## Phase 2: TDD Green

### T-002: Fix update.ts to default all plugins
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02 | **Status**: [x] completed

**Implementation**:
- Change `all: options.all` to `all: options.all ?? true` at line 394

**Test Plan**:
- Given T-001 test exists
- When fix is applied
- Then T-001 test passes

## Phase 3: TDD Refactor

### T-003: Update docstrings
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 | **Status**: [x] completed

**Implementation**:
- Update update.ts docstring to reflect all plugins refreshed by default
- Update `UpdateOptions.all` JSDoc comment

**Test Plan**:
- Given docstrings updated
- When all tests run
- Then all tests still pass
