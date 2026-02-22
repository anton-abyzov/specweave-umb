# Tasks: Multi-Repo Docs Restructuring

## Task Notation

- `[T###]`: Task ID
- `[P]`: Parallelizable
- `[ ]`: Not started
- `[x]`: Completed
- Model hints: haiku (simple), opus (default)

## Phase 1: Project Mapper

### T-001: Create spec-project-mapper module (TDD)
**User Story**: US-001 | **Satisfies ACs**: AC-US1-04, AC-US1-06, AC-US1-07
**Status**: [x] completed

**Description**: Create `src/core/migration/spec-project-mapper.ts` that maps FS-XXX feature IDs to their owning project(s) by scanning increment metadata and spec files.

**Implementation Details**:
- Scan `.specweave/increments/*/metadata.json` for `feature_id` field to build FS-XXX → increment mapping
- Fall back to numeric matching (FS-282 → glob `0282-*`) when `feature_id` is missing
- Parse increment `spec.md` for `**Project**:` lines in user stories
- Return `Map<string, string[]>` (featureId → projectIds[])
- Handle cross-project specs (multiple `**Project**:` values → multiple entries)
- Default to current project folder name when no `**Project**:` field found

**Test Plan**:
- **File**: `src/core/migration/__tests__/spec-project-mapper.test.ts`
- **Tests**:
  - **TC-001**: Maps FS-XXX to project via metadata.json feature_id
    - Given an increment with `feature_id: "FS-282"` and spec.md containing `**Project**: vskill-platform`
    - When `buildFeatureProjectMap()` is called
    - Then FS-282 maps to `["vskill-platform"]`
  - **TC-002**: Falls back to numeric matching when feature_id is null
    - Given increment `0286-vskill-install-ux` with `feature_id: null` and spec.md containing `**Project**: vskill`
    - When `buildFeatureProjectMap()` is called
    - Then FS-286 maps to `["vskill"]`
  - **TC-003**: Handles cross-project specs
    - Given spec.md with `**Project**: vskill-platform` and `**Project**: specweave`
    - When `buildFeatureProjectMap()` is called
    - Then the feature maps to `["vskill-platform", "specweave"]`
  - **TC-004**: Falls back to default project when no Project field
    - Given spec.md with no `**Project**:` field
    - When `buildFeatureProjectMap()` is called
    - Then the feature maps to the current project name (fallback)

**Dependencies**: None

---

### T-002: Create reorganization plan generator (TDD)
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02, AC-US1-05, AC-US1-08
**Status**: [x] completed

**Description**: Create `generateReorganizationPlan()` function that produces a list of move operations for FS-XXX folders based on the project map.

**Implementation Details**:
- Input: project map from T-001, current specs directory path, umbrella childRepos config
- Scan `.specweave/docs/internal/specs/{currentProject}/` for FS-XXX directories
- For each FS-XXX, look up target project(s) from the map
- Generate move operations: `{ source, destination, type: 'move'|'copy' }`
- For cross-project: first project gets a move, others get copies
- Skip FS-XXX folders already in the correct location (idempotency)
- Include assets/ subdirectories in the move (preserve tree)

**Test Plan**:
- **File**: `src/core/migration/__tests__/spec-project-mapper.test.ts` (same file, separate describe block)
- **Tests**:
  - **TC-005**: Generates move plan for single-project spec
    - Given FS-286 mapped to `["vskill"]` and currently under `specs/specweave/`
    - When `generateReorganizationPlan()` is called
    - Then plan includes move from `specs/specweave/FS-286` to `specs/vskill/FS-286`
  - **TC-006**: Generates copy plan for cross-project spec
    - Given FS-277 mapped to `["vskill-platform", "specweave", "vskill"]`
    - When `generateReorganizationPlan()` is called
    - Then plan includes one move + two copies
  - **TC-007**: Skips already-reorganized specs (idempotency)
    - Given FS-286 already at `specs/vskill/FS-286`
    - When `generateReorganizationPlan()` is called
    - Then plan has no operations for FS-286
  - **TC-008**: Preserves assets subdirectories
    - Given FS-282 has an `assets/` subdirectory
    - When plan is generated
    - Then the move operation targets the entire FS-282 folder tree

**Dependencies**: T-001

## Phase 2: CLI + Core Logic

### T-003: Add --reorganize-specs flag to migrate-to-umbrella CLI
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03
**Status**: [x] completed

**Description**: Extend the `migrate-to-umbrella` CLI command with the `--reorganize-specs` flag and wire it to the reorganization logic.

**Implementation Details**:
- Add `--reorganize-specs` option to commander in `bin/specweave.js`
- Add `reorganizeSpecs?: boolean` to `MigrationOptions` type
- In `migrateToUmbrellaCommand()`, add handler for `--reorganize-specs` that:
  - Validates we are in an umbrella project (has `umbrella.enabled = true`)
  - Calls `buildFeatureProjectMap()` to get mappings
  - Calls `generateReorganizationPlan()` to get move plan
  - Displays dry-run plan (default) or executes with `--execute`
- Dry-run output format: `[MOVE] FS-282: specweave/ → vskill-platform/`

**Test Plan**:
- **File**: `src/core/migration/__tests__/reorganize-specs.test.ts`
- **Tests**:
  - **TC-009**: CLI accepts --reorganize-specs flag
    - Given the migrate-to-umbrella command
    - When `--reorganize-specs` is passed
    - Then options.reorganizeSpecs is true
  - **TC-010**: Rejects --reorganize-specs on non-umbrella project
    - Given a project without `umbrella.enabled`
    - When `--reorganize-specs` is called
    - Then an error message is displayed

**Dependencies**: T-001, T-002

---

### T-004: Implement reorganizeSpecs() execution and config update
**User Story**: US-001, US-002 | **Satisfies ACs**: AC-US1-03, AC-US2-01, AC-US2-02, AC-US2-03
**Status**: [x] completed

**Description**: Implement the `reorganizeSpecs()` function that physically moves folders and updates config.json.

**Implementation Details**:
- `reorganizeSpecs(plan, options: { execute: boolean })`: execute the move plan
- For each move operation:
  - `ensureDir()` for target project directory
  - `fs.rename()` (or `fs.cp()` + `fs.rm()` for cross-device) to move folder
  - For copy operations: `fs.cp({ recursive: true })`
- After moves: read `config.json`, set `multiProject.enabled = true`, write back
- If `multiProject.enabled` is already true, skip config write
- Log each operation with source/dest paths

**Test Plan**:
- **File**: `src/core/migration/__tests__/reorganize-specs.test.ts`
- **Tests**:
  - **TC-011**: Moves FS-XXX folder to correct project directory
    - Given a plan with one move operation
    - When `reorganizeSpecs()` is called with `execute: true`
    - Then the folder is moved and source no longer exists
  - **TC-012**: Creates target project directory if missing
    - Given target `specs/vskill/` does not exist
    - When reorganizeSpecs() executes
    - Then `specs/vskill/` is created before the move
  - **TC-013**: Sets multiProject.enabled to true in config.json
    - Given `multiProject.enabled: false` in config
    - When reorganizeSpecs() completes
    - Then config.json has `multiProject.enabled: true`
  - **TC-014**: Skips config update when multiProject already enabled
    - Given `multiProject.enabled: true` already
    - When reorganizeSpecs() completes
    - Then config.json is not rewritten
  - **TC-015**: Handles cross-project copy operations
    - Given a plan with a copy operation for FS-277
    - When reorganizeSpecs() executes
    - Then FS-277 exists in multiple project directories

**Dependencies**: T-001, T-002, T-003

## Phase 3: Verification

### T-005: Verify living-docs sync with multi-project layout
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03
**Status**: [x] completed

**Description**: Verify that after reorganization, `specweave sync-progress` and `specweave living-docs` work correctly with per-project spec folders.

**Implementation Details**:
- Run reorganization on the actual umbrella workspace
- Run `specweave sync-progress` and verify no errors
- Check that `LivingDocsSync.getProjectId()` returns correct project for each repo context
- Verify that `multiProject.enabled = true` causes living-docs-sync to use project-specific paths

**Test Plan**:
- **Tests**:
  - **TC-016**: sync-progress completes without errors after reorganization
    - Given specs reorganized to per-project folders and multiProject enabled
    - When `specweave sync-progress` is run
    - Then no file-not-found or path errors occur
  - **TC-017**: living-docs builder recognizes multi-project structure
    - Given multiProject.enabled = true
    - When living-docs scans for spec folders
    - Then it finds specs under each project subdirectory

**Dependencies**: T-004

---

### T-006: Run full test suite and verify coverage
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04
**Status**: [x] completed

**Description**: Run all tests, verify coverage meets 80% target for new modules.

**Implementation Details**:
- Run `npm test` in specweave repo
- Check coverage for `spec-project-mapper.ts` and reorganization logic
- Fix any failing tests or gaps

**Test Plan**:
- **Tests**:
  - **TC-018**: All new tests pass
  - **TC-019**: Coverage >= 80% for new modules

**Dependencies**: T-001, T-002, T-003, T-004, T-005
