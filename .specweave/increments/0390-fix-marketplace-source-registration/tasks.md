---
increment: 0390-fix-marketplace-source-registration
total_tasks: 4
completed_tasks: 4
by_user_story:
  US-001: [T-001, T-002, T-003]
  US-002: [T-001, T-002]
---

# Tasks: Fix marketplace temp dir registered as source

## User Story: US-001 - Persistent marketplace registration after plugin install

**Linked ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04
**Tasks**: 3 total, 3 completed

### T-001: RED - Write tests asserting GitHub source registration

**User Story**: US-001, US-002
**Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03
**Status**: [x] completed

**Test Plan**:
- **Given** `registerMarketplace` is called with `"owner/repo"` format
- **When** the CLI command is constructed
- **Then** `execSync` receives `claude plugin marketplace add "owner/repo"`
- **Given** `installMarketplaceRepo` runs with owner=`"owner"`, repo=`"repo"`
- **When** Claude CLI is available and marketplace registration succeeds
- **Then** `mockRegisterMarketplace` is called with `"owner/repo"` (not a `/tmp/` path)
- **Given** existing tests for local paths and paths-with-spaces
- **When** all tests run
- **Then** no regressions in existing test cases

**Test Cases**:
1. **Unit**: `src/utils/claude-cli.test.ts`
   - Add test: `registerMarketplace` with GitHub `owner/repo` shorthand
   - **Coverage Target**: 95%
2. **Integration**: `src/commands/add.test.ts`
   - Update marketplace test TC-004 assertion: `mockRegisterMarketplace` called with `"owner/repo"`
   - **Coverage Target**: 95%

**Implementation**:
1. In `claude-cli.test.ts`, add test case for `owner/repo` input format
2. In `add.test.ts`, update TC-004 and related marketplace tests to assert `mockRegisterMarketplace` receives `"owner/repo"` instead of temp dir path
3. Verify existing path-based tests still exist and are unchanged
4. Run `npx vitest run src/utils/claude-cli.test.ts src/commands/add.test.ts` -- new assertions FAIL (RED)

### T-002: GREEN - Fix registerMarketplace call in installMarketplaceRepo

**User Story**: US-001
**Satisfies ACs**: AC-US1-01, AC-US1-03, AC-US1-04
**Status**: [x] completed

**Test Plan**:
- **Given** `installMarketplaceRepo("owner", "repo", manifest, opts)` is called
- **When** Claude CLI is available and clone succeeds
- **Then** `registerMarketplace` is called with `"owner/repo"` (not `tmpDir`)
- **Given** the shallow clone to tmpDir
- **When** marketplace registration uses GitHub source
- **Then** tmpDir is still created for extraction fallback, but not passed to `registerMarketplace`
- **Given** `tryNativeClaudeInstall()` in the `--plugin-dir` path
- **When** it calls `registerMarketplace(resolve(basePath))`
- **Then** it is unchanged -- still uses the persistent local path

**Implementation**:
1. In `src/commands/add.ts` line ~256, change `registerMarketplace(tmpDir)` to `registerMarketplace(\`${owner}/${repo}\`)`
2. Verify tmpDir clone block is untouched (still needed for extraction)
3. Verify `tryNativeClaudeInstall` is untouched
4. Run `npx vitest run src/commands/add.test.ts src/utils/claude-cli.test.ts` -- all tests PASS (GREEN)

### T-003: REFACTOR - Update registerMarketplace JSDoc and parameter name

**User Story**: US-001
**Satisfies ACs**: AC-US1-02
**Status**: [x] completed

**Test Plan**:
- **Given** `registerMarketplace()` function signature
- **When** JSDoc and parameter name are updated
- **Then** `@param` documents path, URL, and `owner/repo` as valid inputs
- **Then** parameter is renamed from `marketplacePath` to `marketplaceSource`
- **Then** all existing tests still pass with no changes needed (parameter rename is internal)

**Implementation**:
1. In `src/utils/claude-cli.ts`, rename `marketplacePath` to `marketplaceSource`
2. Update JSDoc `@param` to describe all accepted formats
3. Run full test suite: `npx vitest run` -- all tests PASS

## User Story: US-002 - Test coverage for GitHub source registration

**Linked ACs**: AC-US2-01, AC-US2-02, AC-US2-03
**Tasks**: Covered by T-001 (shared task)

All AC-US2 acceptance criteria are satisfied by T-001 which writes the RED-phase tests.

---

### T-004: Final verification

**User Story**: US-001, US-002
**Satisfies ACs**: all
**Status**: [x] completed

**Test Plan**:
- **Given** all changes applied
- **When** full test suite runs
- **Then** 0 failures, no regressions

**Implementation**:
1. Run `npx vitest run` (full suite)
2. Verify all ACs checked in spec.md
