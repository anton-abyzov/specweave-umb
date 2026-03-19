# Tasks: Init Multi-Repo Patterns and Add-More Loop

## Phase 1: Tests (TDD Red)

### T-001: Write tests for promptRepoUrlsLoop

**User Story**: US-001, US-002 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US2-01, AC-US2-02, AC-US2-03
**Status**: [x] Completed

**Description**: Write failing tests for the new `promptRepoUrlsLoop()` function before implementing it. Tests should cover:
- Individual repo input (backward compatibility)
- Glob pattern detection and routing to bulk path
- Mixed input (individual + glob tokens)
- Add-more loop (continues on "yes", stops on "no")
- Background clone dispatch for bulk repos
- Auth token resolution for bulk operations

**Test Plan**:
- **File**: `src/cli/helpers/init/__tests__/repo-connect.test.ts`
- **Tests**:
  - **TC-001**: Given individual repo input `org/repo` → When promptRepoUrlsLoop runs → Then parseRepoInput is called, foreground clone executes, returns results
    - Given `org/repo` entered, When `parseBulkSource()` returns null, Then falls through to individual path
  - **TC-002**: Given glob pattern `org/*` → When promptRepoUrlsLoop runs → Then parseBulkSource detects bulk, getAuthToken + buildBulkRepoList + launchCloneJob called
    - Given `org/*` entered, When `parseBulkSource()` returns `{org:"org", pattern:null}`, Then bulk path executes
  - **TC-003**: Given glob pattern `org/prefix-*` → When promptRepoUrlsLoop runs → Then pattern is forwarded to buildBulkRepoList
    - Given `org/prefix-*`, When `parseBulkSource()` returns `{org:"org", pattern:"prefix-*"}`, Then buildBulkRepoList receives "prefix-*"
  - **TC-004**: Given mixed input `org-a/* my-org/my-repo` → When promptRepoUrlsLoop runs → Then bulk token routed to bulk path, individual token to individual path
  - **TC-005**: Given first batch processed → When confirm "add more?" returns true → Then prompt shown again for second batch
    - Given user answers "yes" to add-more, When second batch entered, Then both batches' results accumulated
  - **TC-006**: Given first batch processed → When confirm "add more?" returns false → Then function returns accumulated results
  - **TC-007**: Given bulk clone → When launchCloneJob called → Then job ID included in returned jobIds array

**Dependencies**: None

### T-002: Write tests for i18n strings

**User Story**: US-003 | **Satisfies ACs**: AC-US3-01
**Status**: [x] Completed

**Description**: Write tests verifying new i18n strings exist for en, ru, es.

**Test Plan**:
- **File**: `src/cli/helpers/init/__tests__/repo-connect.test.ts`
- **Tests**:
  - **TC-008**: Given language "en" → When getProjectSetupStrings called → Then repoPromptPattern, addMoreRepos, bulkDetected strings present
  - **TC-009**: Given language "ru" → When getProjectSetupStrings called → Then same keys present with non-empty Russian translations
  - **TC-010**: Given language "es" → When getProjectSetupStrings called → Then same keys present with non-empty Spanish translations

**Dependencies**: None

## Phase 2: Implementation (TDD Green)

### T-003: Implement promptRepoUrlsLoop in repo-connect.ts

**User Story**: US-001, US-002 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US2-01, AC-US2-02, AC-US2-03
**Status**: [x] Completed

**Description**: Implement the `promptRepoUrlsLoop()` function in `repo-connect.ts` to make all T-001 tests pass.

**Implementation Details**:
1. Add imports: `parseBulkSource`, `buildBulkRepoList`, `getAuthToken` from `../get/bulk-get.js`; `launchCloneJob` from `../../../core/background/job-launcher.js`; `confirm` from `@inquirer/prompts`
2. Add i18n strings for new prompts (en, ru, es)
3. Implement `promptRepoUrlsLoop(projectPath, language)`:
   - do-while loop with confirm prompt
   - Token splitting and routing (parseBulkSource vs parseRepoInput)
   - Bulk path: getAuthToken → buildBulkRepoList → launchCloneJob
   - Individual path: mapParsedReposToCloneOptions → runForegroundClone or launchCloneJob
   - Accumulate results and job IDs
4. Export the function

**Dependencies**: T-001

### T-004: Wire promptRepoUrlsLoop into init.ts

**User Story**: US-001, US-002 | **Satisfies ACs**: AC-US1-01, AC-US2-01
**Status**: [x] Completed

**Description**: Replace the existing `promptRepoUrls()` + inline clone block in `init.ts` (lines 366-393) with a call to `promptRepoUrlsLoop()`.

**Implementation Details**:
1. Import `promptRepoUrlsLoop` from `repo-connect.js`
2. Replace lines 366-393 with: `const loopResult = await promptRepoUrlsLoop(targetDir, language);`
3. Use `loopResult` to determine if `umbrellaDiscovery` needs refresh (if any foreground clones succeeded)
4. Show job status for any background jobs launched

**Dependencies**: T-003

### T-005: Add i18n strings

**User Story**: US-003 | **Satisfies ACs**: AC-US3-01
**Status**: [x] Completed

**Description**: Add translated strings for en, ru, es to `getProjectSetupStrings()` in `repo-connect.ts`.

**Implementation Details**: Add to existing strings object:
- `repoPromptPattern`: Updated prompt with pattern examples
- `addMoreRepos`: "Do you want to add more repositories?" prompt
- `bulkDetected`: Status message for pattern detection
- `bulkMatched`: Status message for matched repo count
- `cloneJobStarted`: Background job started message

**Dependencies**: T-002

## Phase 3: Verify

### T-006: Run full test suite

**User Story**: US-001, US-002, US-003 | **Satisfies ACs**: All
**Status**: [x] Completed

**Description**: Run `npx vitest run` to verify all tests pass and no regressions.

**Dependencies**: T-003, T-004, T-005
