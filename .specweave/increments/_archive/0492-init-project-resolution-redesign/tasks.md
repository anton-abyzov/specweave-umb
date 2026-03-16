# Tasks: Redesign specweave init project resolution

## Task Notation

- `[T###]`: Task ID
- `[P]`: Parallelizable
- `[ ]`: Not started
- `[x]`: Completed
- Model hints: haiku (simple), sonnet (default), opus (complex)

---

## Phase 1: Extract umbrella config helper

### T-001: Create buildUmbrellaConfig helper function
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-03 | **Status**: [x] Completed

Extract the duplicated umbrella config generation logic from `init.ts` into a reusable function in `path-utils.ts`.

**Implementation Details**:
- Add `buildUmbrellaConfig(discovery: UmbrellaDiscoveryResult, projectName: string)` to `src/cli/helpers/init/path-utils.ts`
- Move the prefix deduplication loop (3-char uppercase, numeric suffix on collision) and childRepos mapping from `init.ts` lines ~361-380
- Return `{ umbrella: { enabled, projectName, childRepos }, repository: { umbrellaRepo: true } }`

**Test Plan**:
- **File**: `tests/unit/cli/helpers/init/build-umbrella-config.test.ts`
- **Tests**:
  - **TC-001**: Given a discovery with 1 repo, When buildUmbrellaConfig is called, Then returns config with single childRepo and 3-char prefix
  - **TC-002**: Given a discovery with 2 repos whose names share the same 3-char prefix, When buildUmbrellaConfig is called, Then the second repo gets a deduplicated prefix (2-char + numeric suffix)
  - **TC-003**: Given a discovery with 3 repos from 2 orgs, When buildUmbrellaConfig is called, Then all repos are included with correct org, name, path, and unique prefixes

**Dependencies**: None

---

### T-002: Export buildUmbrellaConfig from barrel and update init.ts call sites
**User Story**: US-002 | **Satisfies ACs**: AC-US2-02, AC-US2-04 | **Status**: [x] Completed

Wire up the new helper and replace both inline blocks in `init.ts`.

**Implementation Details**:
- Add `buildUmbrellaConfig` to exports in `src/cli/helpers/init/index.ts`
- Replace the first inline block (~lines 361-380 in `init.ts`) with a call to `buildUmbrellaConfig(umbrellaDiscovery, finalProjectName)`
- Replace the second inline block (~lines 420-437 in `init.ts`) with the same call
- Merge the returned config fragment into the main config object

**Test Plan**:
- **File**: existing init integration tests
- **Tests**:
  - **TC-004**: Given an init with repositories/ containing repos, When init completes, Then config.json has umbrella config with correct prefixes (regression)
  - **TC-005**: Given an init where repos are cloned during post-scaffold, When init completes, Then config.json umbrella config matches the cloned repos (regression)

**Dependencies**: T-001

---

## Phase 2: Unify path resolution

### T-003: Collapse undefined/dot path resolution branches
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-05 | **Status**: [x] Completed

Unify the `!projectName` and `projectName === '.'` code paths in `initCommand`.

**Implementation Details**:
- At the top of `initCommand`, normalize: `if (!projectName) projectName = '.';`
- The existing `if (!projectName || projectName === '.')` branch becomes `if (projectName === '.')` after normalization
- Add inline comment: `// No args = init in CWD, same as explicit '.'`
- Remove the redundant `!projectName` check from the condition

**Test Plan**:
- **File**: `tests/unit/cli/commands/init-path-resolution.test.ts`
- **Tests**:
  - **TC-006**: Given initCommand called with undefined, When path resolution runs, Then targetDir equals process.cwd()
  - **TC-007**: Given initCommand called with '.', When path resolution runs, Then targetDir equals process.cwd()
  - **TC-008**: Given initCommand called with 'my-project', When path resolution runs, Then targetDir equals path.resolve(cwd, 'my-project')

**Dependencies**: None (can run in parallel with Phase 1)

---

### T-004: Verify home directory safety guard with no-args
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02 | **Status**: [x] Completed

Confirm that the home directory guard fires correctly when `specweave init` is run without arguments from `~`.

**Test Plan**:
- **File**: `tests/unit/cli/commands/init-path-resolution.test.ts`
- **Tests**:
  - **TC-009**: Given process.cwd() returns os.homedir(), When initCommand(undefined) runs, Then process.exit(1) is called with the home directory error message

**Dependencies**: T-003

---

### T-005: Verify project name prompt preserved for non-matching CWD names
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03, AC-US1-04 | **Status**: [x] Completed

Ensure the existing name prompt behavior is unchanged when CWD name contains special characters.

**Test Plan**:
- **File**: `tests/unit/cli/commands/init-path-resolution.test.ts`
- **Tests**:
  - **TC-010**: Given CWD is named "My Project" (spaces, uppercase), When initCommand(undefined) runs in interactive mode, Then user is prompted for project name with suggested slug "my-project"
  - **TC-011**: Given initCommand called with 'new-project', When path resolution runs, Then a subdirectory is created at cwd/new-project/

**Dependencies**: T-003

---

## Phase 3: Improve error messages and relax post-scaffold guard

### T-006: Add resolved target path to guard-clause error messages
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02 | **Status**: [~] Descoped

Descoped — PM agent added US-003 beyond the approved plan scope. Guard clause messages already show umbrella root and suspicious segment, which is sufficient. Can be addressed in a follow-up increment if needed.

---

### T-007: Relax post-scaffold guard to allow prompt with existing .git
**User Story**: US-003 | **Satisfies ACs**: AC-US3-03, AC-US3-04 | **Status**: [~] Descoped

Descoped — the approved plan says "skip if .git or repositories/ exists", matching the current `!hasGit && !hasRepos` condition. Relaxing to `!hasRepos` was PM scope creep. Current behavior is correct per the approved plan.

**Dependencies**: None

---

## Phase 4: Verification

### T-008: Run existing test suite and verify no regressions
**User Story**: US-001, US-002 | **Satisfies ACs**: all implemented | **Status**: [x] Completed

All 102 relevant tests pass (init.test.ts: 83, repo-connect.test.ts: 15, build-umbrella-config.test.ts: 4). No regressions.

**Dependencies**: T-001, T-002, T-003, T-004, T-005
