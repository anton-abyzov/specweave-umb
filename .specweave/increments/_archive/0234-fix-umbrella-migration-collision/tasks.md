# Tasks: Fix umbrella migration collision handling

## Task Notation

- `[T###]`: Task ID
- `[ ]`: Not started
- `[x]`: Completed
- Model hints: haiku (simple), opus (default)

## Phase 1: Core Collision Logic

### US-001: Collision Detection and Classification (P1)

#### T-001: Implement classifyExistingUmbrella()
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04 | **Status**: [x] completed

**Description**: Add collision classification function that detects and categorizes existing umbrella directories.

**Implementation Details**:
- Three-state return: `previous-migration` | `partial-migration` | `unrelated` | `null`
- Check `.specweave/` inside umbrella for previous migration
- Check backup manifest at project root for partial migration
- Default to `unrelated` for any other existing directory

**Test Plan**:
- **File**: `repositories/anton-abyzov/specweave/tests/unit/core/migration/umbrella-migrator-collision.test.ts`
- **Tests**:
  - **TC-001**: Returns null when directory does not exist
    - Given a nonexistent umbrella path
    - When `classifyExistingUmbrella()` is called
    - Then returns null
  - **TC-002**: Returns `previous-migration` when `.specweave/` exists
    - Given umbrella dir with `.specweave/` inside
    - When `classifyExistingUmbrella()` is called
    - Then returns `previous-migration`
  - **TC-003**: Returns `partial-migration` when backup manifest exists
    - Given umbrella dir exists and backup manifest at project root
    - When `classifyExistingUmbrella()` is called
    - Then returns `partial-migration`
  - **TC-004**: Returns `unrelated` for generic directory
    - Given umbrella dir exists without SpecWeave markers
    - When `classifyExistingUmbrella()` is called
    - Then returns `unrelated`

**Dependencies**: None
**File**: `repositories/anton-abyzov/specweave/src/core/migration/umbrella-migrator.ts`

---

#### T-002: Add CLI collision handling
**User Story**: US-001 | **Satisfies ACs**: AC-US1-05, AC-US1-06 | **Status**: [x] completed

**Description**: Integrate collision classification into the CLI command with interactive prompts.

**Implementation Details**:
- Call `classifyExistingUmbrella()` before execution
- `previous-migration`: offer wipe/rename/abort
- `partial-migration`: offer rollback-then-retry/abort
- `unrelated`: offer rename/abort
- `--yes` mode: auto-wipe previous, abort on unrelated

**Dependencies**: T-001
**File**: `repositories/anton-abyzov/specweave/src/cli/commands/migrate-to-umbrella.ts`

---

### US-002: Move Destination Safety (P1)

#### T-003: Add move destination safety check
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03 | **Status**: [x] completed

**Description**: Add `fs.existsSync()` guard in move step to prevent overwriting existing destinations.

**Test Plan**:
- **File**: `repositories/anton-abyzov/specweave/tests/unit/core/migration/umbrella-migrator-collision.test.ts`
- **Tests**:
  - **TC-005**: Fails when move destination already exists
    - Given a pre-created destination for `.specweave/`
    - When `executeMigration()` runs
    - Then result.success is false and error contains "already exists"

**Dependencies**: None
**File**: `repositories/anton-abyzov/specweave/src/core/migration/umbrella-migrator.ts`

---

### US-003: Post-Move Log Path Fix (P1)

#### T-004: Fix post-move log path with dynamic logRoot
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03 | **Status**: [x] completed

**Description**: Switch `logRoot` from `projectRoot` to `umbrellaPath` after `.specweave/` move step completes.

**Test Plan**:
- **File**: `repositories/anton-abyzov/specweave/tests/unit/core/migration/umbrella-migrator-collision.test.ts`
- **Tests**:
  - **TC-006**: No ghost logs in original project after migration
    - Given a successful migration
    - When checking original project path
    - Then `.specweave/logs/` does not exist in original project
    - And `migration.log` exists in umbrella's `.specweave/logs/`

**Dependencies**: None
**File**: `repositories/anton-abyzov/specweave/src/core/migration/umbrella-migrator.ts`
