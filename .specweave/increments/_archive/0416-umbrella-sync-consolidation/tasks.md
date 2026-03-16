---
increment: 0416-umbrella-sync-consolidation
skill_chain_marker: planner:0416-umbrella-sync-consolidation
by_user_story:
  US-001: [T-001, T-002, T-003, T-004, T-005, T-009, T-010]
  US-002: [T-006, T-007, T-009, T-010]
  US-003: [T-001, T-008, T-009]
total_tasks: 10
completed_tasks: 0
---

# Tasks: 0416 Umbrella Sync Consolidation

---

## User Story: US-001 - Distributed External Sync Routing

**Linked ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05
**Tasks**: 5 total, 0 completed

---

### T-001: Add ChildRepoSyncConfig types and syncStrategy to UmbrellaConfig

**User Story**: US-001, US-003
**Satisfies ACs**: AC-US3-01, AC-US3-02
**Status**: [x] completed

**Test Plan**:
- **Given** `src/core/config/types.ts` is compiled in strict mode
- **When** TypeScript checks `ChildRepoConfig.sync` and `UmbrellaConfig.syncStrategy`
- **Then** no `any` errors appear and the fields are properly typed

**Test Cases**:
1. **Unit**: `tests/unit/core/config/types.test.ts`
   - testChildRepoSyncConfigShape(): asserts `sync.github`, `sync.jira`, `sync.ado` are optional with correct field types
   - testSyncStrategyUnion(): asserts `syncStrategy` accepts only `"centralized"` or `"distributed"`
   - **Coverage Target**: 90%

**Implementation**:
1. Open `src/core/config/types.ts`
2. Add `ChildRepoGitHubSync`, `ChildRepoJiraSync`, `ChildRepoAdoSync`, `ChildRepoSyncConfig` interfaces as defined in plan.md AD-2
3. Add `sync?: ChildRepoSyncConfig` to `ChildRepoConfig`
4. Add `syncStrategy?: 'centralized' | 'distributed'` to `UmbrellaConfig`
5. Run `npx tsc --noEmit` to verify no type errors

---

### T-002: Create resolveSyncTarget() utility

**User Story**: US-001
**Satisfies ACs**: AC-US1-01, AC-US1-02
**Status**: [x] completed

**Test Plan**:
- **Given** a `SpecWeaveConfig` with `syncStrategy: "distributed"` and a matching `childRepos` entry
- **When** `resolveSyncTarget(projectName, config)` is called
- **Then** it returns the child repo's `sync.github` target with `source: "child-repo-name"`
- **Given** `syncStrategy` is absent or `"centralized"`
- **When** `resolveSyncTarget` is called
- **Then** it returns the global `config.sync.github` target with `source: "global"`

**Test Cases**:
1. **Unit**: `tests/unit/sync/sync-target-resolver.test.ts`
   - testResolvesByNameWhenDistributed(): phase 1 name match returns child repo target
   - testResolvesByPrefixFallback(): phase 2 prefix match via routeByPrefix
   - testFallsBackToGlobalWhenNoMatch(): phase 3 global fallback when no child repo matches
   - testCentralizedAlwaysReturnsGlobal(): centralized mode bypasses all phase 1/2 logic
   - testUndefinedProjectNameFallsBack(): undefined projectName falls back to global
   - **Coverage Target**: 95%

**Implementation**:
1. Create `src/sync/sync-target-resolver.ts`
2. Export `SyncTargetConfig` interface with `github`, `jira`, `ado`, `source` fields
3. Implement `resolveSyncTarget(projectName, config)` with three-phase resolution (plan.md AD-3)
4. Import and call `routeByPrefix` from `story-router.ts` for phase 2
5. Write unit tests first (TDD: red then green)
6. Run `npx vitest run tests/unit/sync/sync-target-resolver.test.ts`

---

### T-003: Wire LivingDocsSync.syncToGitHub() for distributed mode

**User Story**: US-001
**Satisfies ACs**: AC-US1-01, AC-US1-02
**Status**: [x] completed

**Test Plan**:
- **Given** `syncStrategy: "distributed"` and increment project matches `childRepos[].name === "vskill"`
- **When** `LivingDocsSync.syncToGitHub()` runs
- **Then** `GitHubClientV2` is constructed with vskill child repo's `owner` and `repo`

**Test Cases**:
1. **Unit**: `tests/unit/sync/living-docs-sync.test.ts`
   - testSyncToGitHubUsesChildRepoWhenDistributed(): verifies GitHubClientV2 called with child repo owner/repo
   - testSyncToGitHubUsesGlobalWhenCentralized(): verifies global config used in centralized mode
   - **Coverage Target**: 90%

**Implementation**:
1. Open `src/sync/LivingDocsSync.ts` (or `src/core/living-docs/living-docs-sync.ts`)
2. Import `resolveSyncTarget` from `./sync-target-resolver.js`
3. Extract `projectName` from increment spec.md frontmatter at the call site
4. Call `resolveSyncTarget(projectName, config)` to get resolved target
5. Replace hardcoded `config.sync.github` with `resolvedTarget.github`
6. Run `npx vitest run` to verify no regressions

---

### T-004: Wire sync-progress GitHub AC sync for distributed mode

**User Story**: US-001
**Satisfies ACs**: AC-US1-03
**Status**: [x] completed

**Test Plan**:
- **Given** `syncStrategy: "distributed"` and increment belongs to project `"vskill"`
- **When** `sync-progress` syncs AC checkboxes
- **Then** `GitHubACCheckboxSync` is constructed with the resolved vskill repo owner/repo

**Test Cases**:
1. **Unit**: `tests/unit/cli/commands/sync-progress.test.ts`
   - testACCheckboxSyncUsesResolvedTargetWhenDistributed(): mock resolveSyncTarget, assert GitHubACCheckboxSync gets child repo config
   - testACCheckboxSyncUsesGlobalWhenCentralized(): asserts fallback to global config
   - **Coverage Target**: 85%

**Implementation**:
1. Open `src/cli/commands/sync-progress.ts`
2. Import `resolveSyncTarget`
3. Before constructing `GitHubACCheckboxSync`, call `resolveSyncTarget(projectName, config)`
4. Pass resolved `github` target into the constructor
5. Run `npx vitest run tests/unit/cli/commands/sync-progress.test.ts`

---

### T-005: Wire Jira/ADO routing for distributed mode

**User Story**: US-001
**Satisfies ACs**: AC-US1-04, AC-US1-05
**Status**: [x] completed

**Test Plan**:
- **Given** `syncStrategy: "distributed"` and matching `childRepos[].sync.jira.projectKey`
- **When** `ExternalIssueAutoCreator` creates a Jira issue
- **Then** the resolved `projectKey` is used instead of the global Jira config
- **Given** matching `childRepos[].sync.ado.project`
- **When** `ExternalIssueAutoCreator` creates an ADO work item
- **Then** the resolved `ado.project` is used

**Test Cases**:
1. **Unit**: `tests/unit/sync/external-issue-auto-creator.test.ts`
   - testJiraCreationUsesChildRepoProjectKey(): distributed mode uses resolved Jira projectKey
   - testAdoCreationUsesChildRepoProject(): distributed mode uses resolved ADO project
   - testFallsBackToGlobalJiraWhenNoChildSync(): global Jira used when no child match
   - **Coverage Target**: 90%

**Implementation**:
1. Open `src/sync/ExternalIssueAutoCreator.ts`
2. Import `resolveSyncTarget`
3. Add optional `overrideProjectKey` param to Jira creation path
4. Add optional `overrideProject` param to ADO creation path
5. Call `resolveSyncTarget` and pass resolved values as overrides
6. Run `npx vitest run tests/unit/sync/external-issue-auto-creator.test.ts`

---

## User Story: US-002 - Consolidate Nested Increments

**Linked ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05
**Tasks**: 2 total, 0 completed

---

### T-006: Add --consolidate flag to migrate-to-umbrella CLI

**User Story**: US-002
**Satisfies ACs**: AC-US2-01, AC-US2-05
**Status**: [x] completed

**Test Plan**:
- **Given** `migrate-to-umbrella --consolidate` is invoked without `--execute`
- **When** the command runs
- **Then** it prints a dry-run plan with all planned moves and deletions, making no file changes

**Test Cases**:
1. **Unit**: `tests/unit/cli/commands/migrate-to-umbrella.test.ts`
   - testConsolidateFlagDispatchesToHandleConsolidate(): verifies flag routes to handleConsolidate()
   - testDryRunPrintsWithoutExecuting(): asserts no fs writes when --execute is absent
   - **Coverage Target**: 85%

**Implementation**:
1. Open `src/cli/commands/migrate-to-umbrella.ts`
2. Add `consolidate` and `execute` to options parsing (following existing `rollback`/`addRepo` pattern)
3. Add `handleConsolidate(umbrellaRoot, options)` dispatch branch
4. Import `scanForOrphans` and `executeConsolidation` from `consolidation-engine.ts` (created in T-007)
5. Print dry-run plan always; run execute only when `options.execute` is true
6. Run unit tests

---

### T-007: Implement consolidation engine

**User Story**: US-002
**Satisfies ACs**: AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05
**Status**: [x] completed

**Test Plan**:
- **Given** a nested repo `.specweave/increments/0010-foo/` not present in umbrella root
- **When** `executeConsolidation` runs
- **Then** the directory is moved to umbrella root `.specweave/increments/0010-foo/`
- **Given** increment `0010-foo` exists in both nested repo and umbrella root
- **When** `executeConsolidation` runs
- **Then** umbrella root copy is kept and nested copy is deleted
- **Given** nested `.specweave/docs/` entries exist
- **When** `executeConsolidation` runs
- **Then** they are moved to umbrella root `.specweave/docs/`

**Test Cases**:
1. **Unit**: `tests/unit/core/migration/consolidation-engine.test.ts`
   - testScanDetectsOrphanIncrements(): scanForOrphans populates moves[] for non-duplicate
   - testScanDetectsDuplicates(): scanForOrphans populates deletions[] for umbrella-root duplicates
   - testScanDetectsOrphanLivingDocs(): scanForOrphans populates moves[] for docs
   - testExecuteMovesMissingIncrement(): fs.rename called for move type
   - testExecuteDeletesDuplicate(): fs.rm called for deletion type
   - testExecuteMovesLivingDocs(): fs.rename called for living-doc moves
   - **Coverage Target**: 90%

**Implementation**:
1. Create `src/core/migration/consolidation-engine.ts`
2. Export `ConsolidationPlan` interface with `moves[]` and `deletions[]` (plan.md AD-4)
3. Implement `scanForOrphans(umbrellaRoot)`:
   - Glob `repositories/*/` for nested `.specweave/increments/####-*/`
   - Cross-reference umbrella root; schedule move or deletion
   - Glob `repositories/*/` for nested `.specweave/docs/**`; schedule moves
4. Implement `executeConsolidation(plan, umbrellaRoot)`:
   - `fs.rename()` for moves, `fs.rm({ recursive: true })` for deletions
5. Warn if dirty git state detected in a nested repo
6. Run `npx vitest run tests/unit/core/migration/consolidation-engine.test.ts`

---

## User Story: US-003 - Type System and Bug Fixes

**Linked ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04
**Tasks**: 1 total, 0 completed

---

### T-008: Fix displayName bug and getAvailableProjects childRepos fallback

**User Story**: US-003
**Satisfies ACs**: AC-US3-03, AC-US3-04
**Status**: [x] completed

**Test Plan**:
- **Given** `multi-project-detector.ts` resolves project names from umbrella config
- **When** it reads a `childRepo` entry
- **Then** it reads `repo.name` (not `repo.displayName`) matching the actual schema
- **Given** `umbrella.projects[]` is empty or absent in an umbrella config
- **When** `getAvailableProjects()` is called
- **Then** it returns names derived from `umbrella.childRepos[]`

**Test Cases**:
1. **Unit**: `tests/unit/utils/multi-project-detector.test.ts`
   - testReadsNameFieldNotDisplayName(): asserts `repo.name` is used, not `repo.displayName`
   - **Coverage Target**: 90%

2. **Unit**: `tests/unit/core/project/project-resolution.test.ts`
   - testGetAvailableProjectsFallsBackToChildRepos(): empty `projects[]` falls back to `childRepos[].name`
   - testGetAvailableProjectsWithPopulatedProjects(): populated `projects[]` still used normally
   - **Coverage Target**: 90%

**Implementation**:
1. Open `src/utils/multi-project-detector.ts` (or `src/umbrella/multi-project-detector.ts`)
2. Find reference to `repo.displayName` (plan.md bug table: line 122) and change to `repo.name`
3. Open `src/core/project/project-resolution.ts` (or `src/umbrella/ProjectResolutionService.ts`)
4. In `getAvailableProjects()`, add `else if (config.umbrella?.enabled)` branch that maps `childRepos[].name` to available projects
5. Run all affected unit tests

---

## Cross-Cutting Tasks

---

### T-009: Integration tests covering all ACs

**User Story**: US-001, US-002, US-003
**Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05, AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05, AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04
**Status**: [x] completed

**Test Plan**:
- **Given** a full umbrella config with `syncStrategy: "distributed"` and two child repos
- **When** each sync pathway is exercised end-to-end (living docs, sync-progress, Jira, ADO)
- **Then** each pathway routes to the correct child repo target
- **Given** a fixture umbrella directory with nested `.specweave/` dirs and known orphans
- **When** `--consolidate` dry-run and `--consolidate --execute` are run
- **Then** dry-run output matches expected plan; execute moves/deletes as specified

**Test Cases**:
1. **Integration**: `tests/integration/sync/distributed-routing.test.ts`
   - testFullDistributedRoutingPipeline(): wires all three sync callers with a shared config fixture, asserts each routes to correct child repo
   - testCentralizedModePreservesExistingBehavior(): single-repo config routes all to global
   - **Coverage Target**: 85%

2. **Integration**: `tests/integration/migration/consolidation-integration.test.ts`
   - testConsolidationDryRun(): tmp fixture dirs, dry-run prints plan, no moves made
   - testConsolidationExecute(): moves and deletes confirmed with fs assertions
   - **Coverage Target**: 85%

**Implementation**:
1. Create `tests/integration/sync/distributed-routing.test.ts`
2. Create `tests/integration/migration/consolidation-integration.test.ts`
3. Use `os.tmpdir()` for filesystem fixtures; clean up in `afterEach`
4. Run `npx vitest run tests/integration/`

---

### T-010: Run consolidation and enable distributed sync in umbrella config

**User Story**: US-001, US-002
**Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05, AC-US1-01
**Status**: [x] completed

**Test Plan**:
- **Given** the umbrella root and nested repos are in their current state
- **When** `migrate-to-umbrella --consolidate` dry-run is reviewed and `--execute` is run
- **Then** zero orphaned increments remain in nested `.specweave/` dirs and `syncStrategy: "distributed"` is active

**Test Cases**:
- Manual verification: check umbrella `.specweave/increments/` count before and after
- Manual verification: spot-check one moved increment's `metadata.json` is intact after move
- Manual verification: create a test increment in `vskill` project, run `sync-progress`, confirm GitHub issue appears in vskill repo (not specweave repo)

**Implementation**:
1. Run `specweave migrate-to-umbrella --consolidate` (dry-run) and review output
2. If plan looks correct, run `specweave migrate-to-umbrella --consolidate --execute`
3. Set `syncStrategy: "distributed"` in `.specweave/config.json` under the `umbrella` key
4. Verify nested `.specweave/` dirs are empty of increments
5. Run `npx vitest run` to confirm all tests still pass after live migration
