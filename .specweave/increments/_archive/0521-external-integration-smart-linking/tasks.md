# Tasks: External Integration Health Check & Smart Linking

## Task Notation

- `[T###]`: Task ID
- `[P]`: Parallelizable
- `[ ]`: Not started
- `[x]`: Completed
- Model hints: haiku (simple), opus (default)

## Phase 1: Health Check Wiring

### US-001: Integration Health Check at Setup Time (P1)

#### T-001: Wire health checks into sync-setup completion
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02
**Status**: [x] Completed

**Description**: After `setupIssueTracker()` returns successfully in `sync-setup.ts`, detect which provider was configured and call the appropriate health check function. Display results using `formatHealthCheckResults()`.

**Implementation Details**:
- Import `checkJiraIntegration`, `checkAdoIntegration`, `checkGitHubIntegration`, `formatHealthCheckResults` from `../../sync/integration-health-check.js`
- After `setupIssueTracker()` returns `true`, read the updated config to determine provider
- Call the matching health check function with credentials from config/.env
- Display formatted results (already includes fix suggestions per AC-US1-02)

**Test Plan**:
- **File**: `tests/unit/cli/commands/sync-setup.test.ts`
- **Tests**:
  - **TC-001**: Given sync-setup completes successfully with JIRA configured, When the command finishes, Then `checkJiraIntegration` is called and results are displayed
  - **TC-002**: Given sync-setup completes successfully with ADO configured, When the command finishes, Then `checkAdoIntegration` is called and results are displayed
  - **TC-003**: Given sync-setup fails (returns false), When the command finishes, Then no health checks are run
  - **TC-004**: Given health check has failures, When results are displayed, Then fix suggestions are shown for each failing check

**Dependencies**: None

---

### US-004: Standalone Sync Health Command (P2)

#### T-002: Create sync-health CLI command
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03
**Status**: [x] Completed

**Description**: Create a new `specweave sync-health` command that reads config, determines enabled providers, runs health checks for each, and outputs results. Supports `--json` flag and correct exit codes.

**Implementation Details**:
- Create `src/cli/commands/sync-health.ts`
- Read `.specweave/config.json` to determine enabled providers (sync.github.enabled, sync.jira.enabled, sync.ado.enabled)
- For JIRA: read domain from config, email/token from process.env
- For ADO: read org/project from config, PAT from process.env
- For GitHub: call `checkGitHubIntegration()` directly (uses gh CLI)
- `--json` flag outputs `{ results: HealthCheckResult[], healthy: boolean }`
- Exit codes: 0 = all pass, 1 = any fail, 2 = no providers configured
- Register command in CLI router

**Test Plan**:
- **File**: `tests/unit/cli/commands/sync-health.test.ts`
- **Tests**:
  - **TC-005**: Given JIRA and GitHub are enabled, When `sync-health` runs, Then both providers are checked and results displayed
  - **TC-006**: Given `--json` flag, When command runs, Then output is valid JSON with results array
  - **TC-007**: Given all checks pass, When command completes, Then exit code is 0
  - **TC-008**: Given JIRA auth fails, When command completes, Then exit code is 1
  - **TC-009**: Given no providers configured, When command runs, Then exit code is 2 with helpful message

**Dependencies**: None

---

#### T-003: Register sync-health in CLI router
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01
**Status**: [x] Completed

**Description**: Add the `sync-health` command to the CLI command registry so it's accessible via `specweave sync-health`.

**Implementation Details**:
- Find CLI command registration (likely in `src/cli/index.ts` or similar router)
- Add `sync-health` with options `--json` and optional `--provider <name>` filter
- Wire to `syncHealthCommand` function

**Test Plan**:
- **File**: `tests/unit/cli/commands/sync-health.test.ts`
- **Tests**:
  - **TC-010**: Given CLI is invoked with `sync-health`, When parsed, Then `syncHealthCommand` is called

**Dependencies**: T-002

---

## Phase 2: Branch Naming with External Ticket Keys

### US-002: Branch Naming with External Ticket Keys (P1)

#### T-004: Extend GitConfig with includeExternalKey option
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02
**Status**: [x] Completed

**Description**: Add `includeExternalKey?: boolean` to the `GitConfig` interface in `src/core/config/types.ts`. Default to `false` in `DEFAULT_CONFIG`.

**Implementation Details**:
- Add `includeExternalKey?: boolean` field to `GitConfig` interface
- Add JSDoc: "Include external ticket key (JIRA/ADO) as branch prefix. Default: false"
- Add `includeExternalKey: false` to `DEFAULT_CONFIG.cicd.git`

**Test Plan**:
- **File**: `tests/unit/core/config/types.test.ts`
- **Tests**:
  - **TC-011**: Given DEFAULT_CONFIG, When accessing cicd.git.includeExternalKey, Then value is false

**Dependencies**: None

---

#### T-005: Create branch name builder utility
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03
**Status**: [x] Completed

**Description**: Create `buildBranchName()` utility that composes branch names with optional external ticket key prefix.

**Implementation Details**:
- Create `src/core/cicd/branch-utils.ts`
- Function: `buildBranchName(incrementId: string, metadata: any, gitConfig: GitConfig): string`
- When `gitConfig.includeExternalKey` is true:
  - Call `resolveExternalBranchPrefix(metadata)` from `../../sync/pr-linker.js`
  - If key returned: `{ticketKey}/{branchPrefix}{incrementId}` (e.g., `PROJ-123/sw/0521-smart-linking`)
  - If no key: fall back to `{branchPrefix}{incrementId}`
- When `includeExternalKey` is false: `{branchPrefix}{incrementId}` (existing behavior)
- Export `buildBranchName` for use by PR creation code

**Test Plan**:
- **File**: `tests/unit/core/cicd/branch-utils.test.ts`
- **Tests**:
  - **TC-012**: Given includeExternalKey=true and JIRA key exists, When buildBranchName called, Then returns `PROJ-123/sw/0521-smart-linking`
  - **TC-013**: Given includeExternalKey=true and ADO ID exists, When buildBranchName called, Then returns `AB#123/sw/0521-smart-linking`
  - **TC-014**: Given includeExternalKey=true but no external key, When buildBranchName called, Then returns `sw/0521-smart-linking`
  - **TC-015**: Given includeExternalKey=false, When buildBranchName called, Then returns `sw/0521-smart-linking` regardless of metadata

**Dependencies**: T-004

---

#### T-006: Expose buildBranchName as CLI command for skill consumption
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01
**Status**: [x] Completed

**Description**: PR-based closure branch creation is driven by Claude skills reading config, not TypeScript code. The `buildBranchName()` utility is exported for skill and CLI consumption. Branch names are constructed by skills using the exported function and GitConfig.includeExternalKey setting.

**Implementation Details**:
- `buildBranchName()` exported from `src/core/cicd/branch-utils.ts`
- Skills read `cicd.git.includeExternalKey` from config and use `resolveExternalBranchPrefix()` from pr-linker
- Integration point: SKILL.md instructions for pr-based closure

**Test Plan**:
- **File**: `tests/unit/core/cicd/branch-utils.test.ts`
- **Tests**: Covered by T-005 tests (TC-012 through TC-015)

**Dependencies**: T-005

---

## Phase 3: Auto PR-to-Ticket Linking

### US-003: Automatic PR-to-Ticket Linking on PR Creation (P1)

#### T-007: Wire linkPrToExternalTickets into PR creation flow
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03
**Status**: [x] Completed

**Description**: PR-to-ticket linking infrastructure is complete. The `specweave link-pr` CLI command calls `linkPrToExternalTickets()` which handles both JIRA remote links and ADO hyperlinks with non-blocking error handling. Skills call `specweave link-pr --increment <id> --pr-url <url> --pr-number <num>` after creating a PR.

**Implementation Details**:
- `link-pr` CLI command already exists and calls `linkPrToExternalTickets()`
- `linkPrToExternalTickets()` handles JIRA addRemoteLink and ADO addHyperlink
- Errors are collected as warnings, never thrown (AC-US3-03)
- Skills are the integration point — they call `specweave link-pr` after PR creation

**Test Plan**:
- **File**: `tests/unit/sync/pr-linker.test.ts` (existing, 8 tests pass)
- **Tests**: Covered by existing pr-linker tests

**Dependencies**: None

---

## Phase 4: Verification

#### T-008: Integration test — full sync-setup → health check flow
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01
**Status**: [x] Completed

**Description**: Verify end-to-end that sync-setup triggers health checks. Mock external APIs but verify the call chain.

**Test Plan**:
- **File**: `tests/integration/sync-setup-health.test.ts`
- **Tests**:
  - **TC-022**: Given sync-setup wizard completes for JIRA, When done, Then health check results appear in output

**Dependencies**: T-001

---

#### T-009: Run full test suite and verify coverage
**User Story**: All | **Satisfies ACs**: All
**Status**: [x] Completed

**Description**: Run `npx vitest run` and verify all new tests pass with >=90% coverage on new code.

**Test Plan**:
- Run `npx vitest run` — all tests pass
- Run `npx vitest run --coverage` — new files >=90%

**Dependencies**: T-001, T-002, T-003, T-004, T-005, T-006, T-007, T-008
