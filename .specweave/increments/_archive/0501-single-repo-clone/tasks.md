---
increment: 0501-single-repo-clone
generated_by: sw:test-aware-planner
tdd_mode: strict
coverage_target: 90
by_user_story:
  US-001: [T-001, T-002]
  US-002: [T-003]
  US-003: [T-004, T-005]
  US-004: [T-006]
  US-005: [T-007]
---

# Tasks: Single Repo Clone via --repo Flag

## User Story: US-001 - Parse Repository Identifier from Multiple Formats

**Linked ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05
**Tasks**: 2 total, 2 completed

---

### T-001: Write failing tests for parseRepoIdentifier()

**User Story**: US-001
**Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05
**Status**: [x] completed

**Test Plan**:
- **Given** `tests/unit/core/repo-structure/url-generator.test.ts` exists with tests for `parseGitRemoteUrl`
- **When** new `parseRepoIdentifier` test cases are added (RED phase -- function does not exist yet)
- **Then** all new tests fail with "parseRepoIdentifier is not a function" or similar import error

**Test Cases**:
1. **Unit**: `tests/unit/core/repo-structure/url-generator.test.ts`
   - `parseShorthand()`: `"owner/repo"` -> `{ owner: "owner", repo: "repo", inputType: "shorthand" }`
   - `parseBareHost()`: `"github.com/owner/repo"` -> `{ owner: "owner", repo: "repo", inputType: "https" }`
   - `parseHttpsUrl()`: `"https://github.com/owner/repo"` -> `{ owner: "owner", repo: "repo", inputType: "https" }`
   - `parseHttpsGit()`: `"https://github.com/owner/repo.git"` -> `{ owner: "owner", repo: "repo", inputType: "https" }`
   - `parseSshUrl()`: `"git@github.com:owner/repo.git"` -> `{ owner: "owner", repo: "repo", inputType: "ssh" }`
   - `parseInvalid()`: `"invalid-string"` -> `null`
   - `parseEmpty()`: `""` -> `null`
   - `parseTrailingSlash()`: `"owner/repo/"` -> `{ owner: "owner", repo: "repo", inputType: "shorthand" }`
   - `parseTrailingGit()`: `"owner/repo.git"` -> `{ owner: "owner", repo: "repo", inputType: "shorthand" }`
   - `parseExtraPath()`: `"https://github.com/owner/repo/tree/main"` -> `{ owner: "owner", repo: "repo", inputType: "https" }`
   - `parseHyphensAndDots()`: `"my-org/my.repo"` -> `{ owner: "my-org", repo: "my.repo", inputType: "shorthand" }`
   - **Coverage Target**: 95% (pure function, all branches exercised)

**Implementation**:
1. Open `tests/unit/core/repo-structure/url-generator.test.ts`
2. Add `import { parseRepoIdentifier } from "../../../../src/core/repo-structure/url-generator.js"`
3. Add a `describe("parseRepoIdentifier", ...)` block with all 11 test cases above
4. Run `npx vitest run tests/unit/core/repo-structure/url-generator.test.ts` -- confirm all new tests FAIL (RED)

---

### T-002: Implement parseRepoIdentifier() to make tests pass

**User Story**: US-001
**Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05
**Status**: [x] completed

**Test Plan**:
- **Given** the failing tests from T-001 are in place
- **When** `parseRepoIdentifier()` is implemented in `src/core/repo-structure/url-generator.ts`
- **Then** all 11 test cases pass (GREEN), including edge cases for trailing `.git`, trailing slash, extra path segments, and hyphenated names

**Test Cases**:
1. **Unit**: `tests/unit/core/repo-structure/url-generator.test.ts`
   - All 11 test cases from T-001 must pass
   - No existing `parseGitRemoteUrl` tests may regress
   - **Coverage Target**: 95%

**Implementation**:
1. Open `src/core/repo-structure/url-generator.ts`
2. Add exported `parseRepoIdentifier(input: string)` following plan.md D-1 and D-7:
   - Pre-process HTTPS URLs with extra path segments: strip to `https://github.com/owner/repo` before delegating
   - Delegate to existing `parseGitRemoteUrl()` for `https://` and `git@` URLs
   - Handle `github.com/owner/repo` (bare host, no protocol)
   - Handle `owner/repo` shorthand (exactly two path segments)
   - Return `{ owner, repo, inputType }` or `null`
   - Strip `.git` suffix and trailing slashes in all paths
3. Run `npx vitest run tests/unit/core/repo-structure/url-generator.test.ts` -- confirm all tests PASS (GREEN)
4. Refactor pass: ensure no duplication with `parseGitRemoteUrl`, clean up intermediate variables

---

## User Story: US-002 - Validate Repository Exists on GitHub

**Linked ACs**: AC-US2-01, AC-US2-02, AC-US2-03
**Tasks**: 1 total, 1 completed

---

### T-003: Implement and test GitHub API repo validation inside cloneSingleGitHubRepo()

**User Story**: US-002
**Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03
**Status**: [x] completed

**Test Plan**:
- **Given** `tests/unit/cli/helpers/init/github-repo-cloning.test.ts` exists with tests for existing clone helpers
- **When** tests for validation behavior of `cloneSingleGitHubRepo()` are added (RED), then GREEN is reached by implementing the function
- **Then** the function calls `GET /repos/{owner}/{repo}`, returns success on 200, returns the specified error message on 404, and exits before the API call when no token is available for non-SSH input

**Test Cases**:
1. **Unit**: `tests/unit/cli/helpers/init/github-repo-cloning.test.ts`
   - `validatesRepoExists_success()`: mock `fetch` returning 200 -> result has no `error`
   - `validatesRepoExists_notFound()`: mock `fetch` returning 404 -> `result.error` equals `"Repository owner/repo not found or you don't have access. Check the repo name and ensure your token has 'repo' scope."`
   - `validatesRepoExists_missingToken()`: no GH_TOKEN/GITHUB_TOKEN in env, HTTPS input -> `result.error` contains missing-token message, `fetch` is never called
   - `validatesRepoExists_sshNoToken()`: no token, SSH input (`git@github.com:owner/repo.git`) -> no token-missing error returned
   - **Coverage Target**: 90%

**Implementation**:
1. Write 4 failing tests in `tests/unit/cli/helpers/init/github-repo-cloning.test.ts` (RED)
   - Mock `fetch` with `vi.hoisted()` + `vi.mock()` per existing ESM patterns in the file
   - Mock `launchCloneJob` and `fs.existsSync`
   - Import `cloneSingleGitHubRepo` (will fail until implemented)
2. Add `export` keyword to `buildGitHubCloneUrl` in `src/cli/helpers/init/github-repo-cloning.ts` (trivial)
3. Add `cloneSingleGitHubRepo()` with steps 1-3 of data flow:
   - Step 1: call `parseRepoIdentifier(repoIdentifier)` -- return parse-error if null
   - Step 2: resolve token from `process.env.GH_TOKEN ?? process.env.GITHUB_TOKEN`; if missing and inputType !== 'ssh', return missing-token error
   - Step 3: `fetch("https://api.github.com/repos/{owner}/{repo}", { headers: { Authorization: "token {pat}" } })`; return 404 error with exact message from AC-US2-02
4. Run `npx vitest run tests/unit/cli/helpers/init/github-repo-cloning.test.ts` -- validation tests PASS

---

## User Story: US-003 - Clone Single Repo into Umbrella Structure

**Linked ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04, AC-US3-05
**Tasks**: 2 total, 2 completed

---

### T-004: Write failing tests for clone path, skip, and URL format behavior

**User Story**: US-003
**Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04, AC-US3-05
**Status**: [x] completed

**Test Plan**:
- **Given** `cloneSingleGitHubRepo()` exists (from T-003) but clone path, skip, and URL-format behavior is not yet implemented
- **When** tests for the full clone data flow are added
- **Then** tests fail on assertions about `launchCloneJob` call arguments, `alreadyCloned` detection, and clone URL format

**Test Cases**:
1. **Unit**: `tests/unit/cli/helpers/init/github-repo-cloning.test.ts`
   - `clonesRepo_shorthand()`: shorthand input -> `launchCloneJob` called with `repositories[0].path = "repositories/owner/repo"`, `cloneUrl` contains HTTPS URL with PAT
   - `skipsAlreadyCloned()`: `fs.existsSync` returns true for `.git` path -> `result.alreadyCloned === true`, `launchCloneJob` not called
   - `childReposPath()`: repo path follows `repositories/{owner}/{repo}` convention (assertion on `launchCloneJob` first arg)
   - `sshInputUsesSshUrl()`: SSH input -> `cloneUrl` starts with `git@github.com:` (no PAT embedded)
   - `httpsInputUsesHttpsUrl()`: HTTPS input -> `cloneUrl` starts with `https://` and includes PAT
   - **Coverage Target**: 90%

**Implementation**:
1. Add 5 test cases to `tests/unit/cli/helpers/init/github-repo-cloning.test.ts` (RED)
2. Run `npx vitest run tests/unit/cli/helpers/init/github-repo-cloning.test.ts` -- confirm new tests fail

---

### T-005: Implement clone dispatch in cloneSingleGitHubRepo()

**User Story**: US-003
**Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04, AC-US3-05
**Status**: [x] completed

**Test Plan**:
- **Given** failing tests from T-004 covering clone path, skip, and URL format
- **When** steps 4-7 of the data flow are implemented in `cloneSingleGitHubRepo()`
- **Then** all T-004 tests pass: repo clones to `repositories/{owner}/{repo}`, already-cloned repos are skipped, SSH input uses SSH URL, HTTPS/shorthand uses HTTPS URL with PAT

**Test Cases**:
1. **Unit**: `tests/unit/cli/helpers/init/github-repo-cloning.test.ts`
   - All 5 tests from T-004 must pass
   - All tests from T-003 must still pass (no regression)
   - **Coverage Target**: 90%

**Implementation**:
1. Extend `cloneSingleGitHubRepo()` in `src/cli/helpers/init/github-repo-cloning.ts` with steps 4-7:
   - Step 4: `fs.existsSync(path.join(projectPath, "repositories", owner, repo, ".git"))` -> return `{ cloned: false, alreadyCloned: true, owner, repo }` if true
   - Step 5: `const urlFormat = parsed.inputType === 'ssh' ? 'ssh' : 'https'` then `buildGitHubCloneUrl(owner, repo, pat, urlFormat)`
   - Step 6: call `launchCloneJob({ projectPath, repositories: [{ owner, name: repo, path: \`repositories/${owner}/${repo}\`, cloneUrl }] })`
   - Step 7: return `{ cloned: true, jobId, owner, repo }`
2. Run `npx vitest run tests/unit/cli/helpers/init/github-repo-cloning.test.ts` -- all tests PASS
3. Run `npx vitest run` -- full suite, zero regressions

---

## User Story: US-004 - Flag Precedence and Dry-Run Support

**Linked ACs**: AC-US4-01, AC-US4-02, AC-US4-03
**Tasks**: 1 total, 1 completed

---

### T-006: Implement and test dry-run and parse-error handling

**User Story**: US-004
**Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03
**Status**: [x] completed

**Test Plan**:
- **Given** `cloneSingleGitHubRepo()` handles valid input (from T-005)
- **When** `dryRun: true` is passed or `repoIdentifier` is unparseable
- **Then** dry-run validates but does not call `launchCloneJob`; unparseable input returns an error listing all supported formats; flag precedence over `--org` is handled by the clone.md skill caller (not inside the function)

**Test Cases**:
1. **Unit**: `tests/unit/cli/helpers/init/github-repo-cloning.test.ts`
   - `dryRunSkipsCloneJob()`: `dryRun: true` + 200 from API -> `fetch` called, `launchCloneJob` not called, `result.cloned === false`
   - `dryRunValidatesRepo()`: `dryRun: true` + 404 from API -> `result.error` contains not-found message (validation still runs)
   - `unparseableInput()`: `repoIdentifier: "not-a-repo"` -> `result.error` contains description of supported formats
   - **Coverage Target**: 90%

**Implementation**:
1. Write 3 failing tests (RED)
2. Extend `cloneSingleGitHubRepo()`:
   - Parse check: if `parsed === null`, return `{ cloned: false, error: "Invalid repo format. Supported formats: owner/repo, github.com/owner/repo, https://github.com/owner/repo, git@github.com:owner/repo.git" }`
   - After validation: if `options.dryRun`, return `{ cloned: false, owner, repo }` without calling `launchCloneJob`
3. Run `npx vitest run tests/unit/cli/helpers/init/github-repo-cloning.test.ts` -- all tests PASS
4. Run `npx vitest run` -- full suite clean

---

## User Story: US-005 - Update Clone Skill Definition

**Linked ACs**: AC-US5-01, AC-US5-02
**Tasks**: 1 total, 1 completed

---

### T-007: Document --repo flag in plugins/specweave-github/commands/clone.md

**User Story**: US-005
**Satisfies ACs**: AC-US5-01, AC-US5-02
**Status**: [x] completed

**Test Plan**:
- **Given** `plugins/specweave-github/commands/clone.md` currently documents only org-level cloning
- **When** a `--repo` section is added with syntax examples and format list
- **Then** the skill definition includes usage examples for all 4 supported input formats, describes `--repo` precedence over `--org`, and explains dry-run behavior

**Test Cases**:
1. **Documentation review** (manual): `plugins/specweave-github/commands/clone.md`
   - `--repo` flag appears in the flags/options table with a description
   - At least one usage example per format: `owner/repo`, `github.com/owner/repo`, `https://github.com/owner/repo`, `git@github.com:owner/repo.git`
   - Documents that `--repo` takes precedence over `--org`/`--pattern`
   - Documents dry-run behavior: validates but does not clone
   - No existing `--org` documentation removed or broken
   - File stays under 1500 lines (CLAUDE.md limit)
   - **Coverage Target**: 100% of AC-US5-01 and AC-US5-02 items

**Implementation**:
1. Read `plugins/specweave-github/commands/clone.md` to understand current structure
2. Add `--repo` to the flags table: "Clone a single repository. Accepts owner/repo, HTTPS URL, or SSH URL. Takes precedence over --org."
3. Add section `## Single Repo Clone (--repo)` with:
   - All 4 supported input format examples
   - Dry-run example: `specweave clone --repo owner/repo --dry-run`
   - Precedence note: "When --repo is provided, --org and --pattern are ignored"
   - Token note: HTTPS/shorthand requires GH_TOKEN; SSH uses SSH key auth
4. Verify file length stays under 1500 lines
