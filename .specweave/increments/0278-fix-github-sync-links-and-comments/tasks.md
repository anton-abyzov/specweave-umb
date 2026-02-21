# Tasks: Fix GitHub Sync Links and AC Comments

## Task Notation

- `[T###]`: Task ID
- `[ ]`: Not started
- `[x]`: Completed
- Model hints: haiku (simple), opus (default)

## Phase 1: Default Branch Detection (US-001)

### T-001: Add detectDefaultBranch method to GitHubFeatureSync
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-04 | **Status**: [x] completed
**Test**: Given a GitHub repo with default branch `main` -> When syncFeatureToGitHub is called -> Then the detected branch is `main` and only one API call is made per sync session

**Implementation Details**:
- Add `private defaultBranch: string | null = null;` instance property to `GitHubFeatureSync`
- Add `private async detectDefaultBranch(): Promise<string>` method
- Uses `gh api repos/{owner}/{repo} --jq '.default_branch'` with `this.getGhEnv()`
- Caches result in `this.defaultBranch` for session reuse
- Falls back to `'main'` if API call fails
- Call in `syncFeatureToGitHub()` before the user story loop

**File**: `repositories/anton-abyzov/specweave/plugins/specweave-github/lib/github-feature-sync.ts`
**Dependencies**: None

---

### T-002: Pass detected branch to UserStoryIssueBuilder
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02 | **Status**: [x] completed
**Test**: Given detectDefaultBranch returns `main` -> When UserStoryIssueBuilder is constructed -> Then repoInfo.branch is `main` (not `develop`)

**Implementation Details**:
- In `syncFeatureToGitHub()`, replace `branch: 'develop'  // TODO: detect from git` with `branch: detectedBranch`
- Call `detectDefaultBranch()` before the user story loop and store result

**File**: `repositories/anton-abyzov/specweave/plugins/specweave-github/lib/github-feature-sync.ts`
**Dependencies**: T-001

---

### T-003: Replace hardcoded 'develop' in UserStoryContentBuilder
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03 | **Status**: [x] completed
**Test**: Given branch parameter is `main` -> When buildIssueBody is called -> Then all URLs use `blob/main/` not `blob/develop/`

**Implementation Details**:
- Add optional `branch` parameter to `buildIssueBody(githubRepo?: string, branch?: string)`
- Replace all hardcoded `develop` in URL construction (lines 163, 199, 212) with `branch || 'main'`
- Three locations to fix: "View full story" link, "Increment" link, task links

**File**: `repositories/anton-abyzov/specweave/plugins/specweave-github/lib/user-story-content-builder.ts`
**Dependencies**: None

## Phase 2: Fix AC Comment Posting (US-002)

### T-004: Rewrite parseIssueLinks to read from metadata.json
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-03 | **Status**: [x] completed
**Test**: Given metadata.json has `github.issues: [{userStory: "US-001", number: 42}]` -> When parseIssueLinks is called -> Then it returns `{"US-001": {issueNumber: 42, issueUrl: "..."}}`

**Implementation Details**:
- Change `parseIssueLinks(content: string)` signature to `parseIssueLinks(specPath: string)` (needs path, not content)
- Derive metadata path: `path.join(path.dirname(specPath), 'metadata.json')`
- Read and parse metadata.json
- Support OLD format: `metadata.github.issues[].userStory` + `.number` + `.url`
- Support NEW format: `metadata.externalLinks.github.issues[US-XXX].issueNumber` + `.issueUrl`
- Return same `Record<string, ParsedUSIssueLink>` shape
- Handle missing metadata.json gracefully (return empty)

**File**: `repositories/anton-abyzov/specweave/plugins/specweave-github/lib/github-ac-comment-poster.ts`
**Dependencies**: None

---

### T-005: Update postACProgressComments to pass specPath to parseIssueLinks
**User Story**: US-002 | **Satisfies ACs**: AC-US2-02 | **Status**: [x] completed
**Test**: Given metadata.json has issue link for US-001 and AC-US1-01 is completed in spec.md -> When postACProgressComments is called -> Then a progress comment is posted to the correct GitHub issue

**Implementation Details**:
- Update the call from `parseIssueLinks(content)` to `parseIssueLinks(specPath)` (line 72)
- No other changes needed since the rest of the function already uses the returned links correctly

**File**: `repositories/anton-abyzov/specweave/plugins/specweave-github/lib/github-ac-comment-poster.ts`
**Dependencies**: T-004

## Phase 3: Fix Links Section (US-003)

### T-006: Fix Links section in UserStoryIssueBuilder to use increment paths
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04 | **Status**: [x] completed
**Test**: Given an umbrella repo setup where living docs are not in the target repo -> When issue body is built -> Then Feature Spec link points to increment spec.md and User Story File link points to increment spec.md with anchor

**Implementation Details**:
- In `buildBody()` Links section (lines 517-551):
- Extract incrementId from the Implementation section (already done at line 539)
- **Feature Spec link**: If incrementId is available, link to `.specweave/increments/{incrementId}/spec.md`. Otherwise keep current behavior.
- **User Story File link**: If incrementId is available, link to `.specweave/increments/{incrementId}/spec.md`. Otherwise keep current behavior.
- **Increment link**: Already correct.
- Keep the `relativeUSPath` link as a secondary "Source" link when it differs from the increment link.

**File**: `repositories/anton-abyzov/specweave/plugins/specweave-github/lib/user-story-issue-builder.ts`
**Dependencies**: None

## Phase 4: Tests and Verification

### T-007: Add unit tests for parseIssueLinks with metadata.json
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01 | **Status**: [x] completed
**Test**: Unit test suite covering old format, new format, missing file, and both-formats-present scenarios

**Implementation Details**:
- Create or update `tests/unit/plugins/github/github-ac-comment-poster.test.ts`
- Test cases:
  - Old format: `github.issues[]` array with userStory + number
  - New format: `externalLinks.github.issues` object with US-XXX keys
  - Missing metadata.json: returns empty
  - Both formats present: old format entries are included
  - Invalid JSON: returns empty gracefully

**File**: `repositories/anton-abyzov/specweave/tests/unit/plugins/github/github-ac-comment-poster.test.ts`
**Dependencies**: T-004

---

### T-008: Add unit test for default branch detection
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-04 | **Status**: [x] completed
**Test**: Unit test for detectDefaultBranch caching and fallback behavior

**Implementation Details**:
- Add tests in `tests/unit/github-feature-sync.test.ts` (or existing test file)
- Test cases:
  - API returns `main` -> uses `main`
  - API fails -> falls back to `main`
  - Second call reuses cached value (no second API call)

**File**: `repositories/anton-abyzov/specweave/tests/unit/github-feature-sync.test.ts`
**Dependencies**: T-001

---

### T-009: Verify TypeScript compilation and existing tests pass
**User Story**: US-001, US-002, US-003 | **Status**: [x] completed
**Test**: Given all edits are made -> When TypeScript is compiled -> Then no type errors and all existing tests pass

**Implementation Details**:
- Run `npm run build` in the specweave repo
- Run `npm test` to verify no regressions
- Fix any type errors or test failures

**File**: `repositories/anton-abyzov/specweave/`
**Dependencies**: T-001, T-002, T-003, T-004, T-005, T-006
