# 0402 — Tasks

**Base path**: `repositories/anton-abyzov/specweave/plugins/specweave-github/`

---

## Phase 1: P0 Critical Fixes

### T-001: Fix issue body append to preserve existing content
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03 | **Status**: [x] completed
**Test**: Given an issue with existing body "Original text" → When cross-repo sync appends "New content" → Then the issue body is "Original text\n---\nNew content"
**File**: `github-cross-repo-sync.ts:229`
**Fix**: Fetch existing body with `gh issue view --json body -q .body` before editing. Concatenate with `---` separator. Handle empty-body case.

### T-002: Fix exitCode property name in hierarchical sync
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03 | **Status**: [x] completed
**Test**: Given `execFileNoThrow` returns `{ exitCode: 0, stdout: "ok" }` → When the result is checked → Then no error is thrown
**File**: `github-hierarchical-sync.ts:320`
**Fix**: Replace `result.status` with `result.exitCode`. Grep entire plugin dir for other `result.status` misuses.

### T-003: Implement real fetchGitHubProject and guard resolveConflicts
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03 | **Status**: [x] completed
**Test**: Given a GitHub project "My Real Project" → When `fetchGitHubProject` is called → Then it returns "My Real Project" (not "Project Title")
**File**: `github-spec-sync.ts:664, :609`
**Fix**: Implement GraphQL ProjectV2 query. Add guard in `resolveConflicts` requiring explicit user choice for title overwrites.

### T-004: Add YAML array support to frontmatter parser
**User Story**: US-004 | **Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04 | **Status**: [x] completed
**Test**: Given frontmatter `tags:\n  - foo\n  - bar` → When parsed and serialized → Then output matches input byte-for-byte
**File**: `github-spec-frontmatter-updater.ts:106`
**Fix**: Extend parser for block arrays, flow arrays, and nested arrays. Consider replacing with `yaml` package if complexity exceeds ~50 LOC.

---

## Phase 2: P1 High Fixes

### T-005: Replace hardcoded branch with default branch detection
**User Story**: US-005 | **Satisfies ACs**: AC-US5-01, AC-US5-02, AC-US5-03 | **Status**: [x] completed
**Test**: Given a repo with default branch `main` → When a sync URL is generated → Then the URL contains `blob/main/` (not `blob/develop/`)
**File**: `enhanced-github-sync.js:168,202`
**Fix**: Query `gh repo view --json defaultBranchRef --jq .defaultBranchRef.name`. Cache per repo per session. Omit branch on failure.

### T-006: Replace macOS-only stat with POSIX-portable lock detection
**User Story**: US-006 | **Satisfies ACs**: AC-US6-01, AC-US6-02, AC-US6-03 | **Status**: [x] completed
**Test**: Given a lock file 10 minutes old with threshold 5 minutes → When lock detection runs on Linux → Then the stale lock is removed
**Files**: Shell hooks (grep for `stat -f` to identify exact files)
**Fix**: Replace `stat -f` with `find <lockfile> -mmin +<threshold>` which works on both macOS and Linux.

### T-007: Add pagination to issue listing in per-us-sync and multi-project-sync
**User Story**: US-007 | **Satisfies ACs**: AC-US7-01, AC-US7-02, AC-US7-03, AC-US7-04 | **Status**: [x] completed
**Test**: Given a repo with 150 issues → When per-us-sync lists issues → Then all 150 are returned without duplicates
**Files**: `per-us-sync.ts:258`, `github-multi-project-sync.ts:360`
**Fix**: Add `--paginate` to `gh issue list` / `gh api` calls. Deduplicate by issue number before processing.

### T-008: Parameterize GraphQL queries to prevent injection
**User Story**: US-008 | **Satisfies ACs**: AC-US8-01, AC-US8-02, AC-US8-03 | **Status**: [x] completed
**Test**: Given a repo named `evil"}{mutation}` → When a GraphQL query runs → Then the query executes safely with the name as a variable (not interpolated)
**File**: `github-graphql-client.ts:36-126`
**Fix**: Refactor all `gh api graphql` calls to use `-F` for variable binding. Remove all string interpolation of user input into query templates.

### T-009: Unify config resolution for owner/repo across CLI and hooks
**User Story**: US-009 | **Satisfies ACs**: AC-US9-01, AC-US9-02, AC-US9-03 | **Status**: [x] completed
**Test**: Given owner/repo set in `.specweave/config.json` → When both CLI and shell hook resolve config → Then both return the same owner/repo
**Files**: `github-feature-sync-cli.ts:46-83`, shell hooks
**Fix**: Extract `resolveGitHubConfig()` with precedence: CLI flag > env var > config.json > git remote. Wire all 4 call sites.
**Dependency**: Must land before T-012, T-013, T-014 (they add new config keys).

### T-010: Auto-create missing labels before applying them
**User Story**: US-010 | **Satisfies ACs**: AC-US10-01, AC-US10-02, AC-US10-03 | **Status**: [x] completed
**Test**: Given a repo without `status:completed` label → When auto-closer runs → Then the label is created and applied (no error thrown)
**File**: `github-us-auto-closer.ts:135`
**Fix**: Before `--add-label`, check `gh label list --search <name>`. If missing, create with `gh label create`. On permission error, log warning and continue.

### T-011: Fix getLastComment to return chronologically newest comment
**User Story**: US-011 | **Satisfies ACs**: AC-US11-01, AC-US11-02 | **Status**: [x] completed
**Test**: Given an issue with 50 comments → When `getLastComment` is called → Then the returned comment is the 50th (newest), not the 30th
**File**: `github-client-v2.ts:611`
**Fix**: Use `gh api /repos/{owner}/{repo}/issues/{number}/comments --paginate --jq 'last'` or query with reverse sort and `per_page=1`.

---

## Phase 3: P2 Medium Fixes

### T-012: Make sync board name configurable
**User Story**: US-012 | **Satisfies ACs**: AC-US12-01, AC-US12-02 | **Status**: [x] completed
**Test**: Given `github.boardName: "Sprint Board"` in config → When orchestrator runs → Then it targets "Sprint Board"
**File**: `github-sync-orchestrator.ts:109`
**Fix**: Read `github.boardName` from config. Default to `'SpecWeave Sync Board'`.
**Dependency**: T-009 (config unification).

### T-013: Make milestone due date configurable
**User Story**: US-013 | **Satisfies ACs**: AC-US13-01, AC-US13-02, AC-US13-03 | **Status**: [x] completed
**Test**: Given `github.milestoneDueDays: 14` in config → When a milestone is created → Then due date is 14 days from now
**Files**: `github-client.ts:52`, `github-client-v2.ts:151`
**Fix**: Read `github.milestoneDueDays` from config. Default to 2. Calculate from creation timestamp.
**Dependency**: T-009 (config unification).

### T-014: Make cross-team spec keywords configurable
**User Story**: US-014 | **Satisfies ACs**: AC-US14-01, AC-US14-02, AC-US14-03 | **Status**: [x] completed
**Test**: Given `github.crossTeamKeywords: ["equipe", "platforma"]` in config → When `isCrossTeamSpec("Equipe Alpha")` is called → Then it returns true
**File**: `github-spec-sync.ts:935-944`
**Fix**: Read `github.crossTeamKeywords` from config. Default to current English keywords. Case-insensitive matching.
**Dependency**: T-009 (config unification).

### T-015: Document and reconcile auto-create config flags
**User Story**: US-015 | **Satisfies ACs**: AC-US15-01, AC-US15-02, AC-US15-03 | **Status**: [x] completed
**Test**: Given only `autoSync: true` set (but not `auto_create_github_issue`) → When handler runs → Then a config validation warning is logged
**File**: `github-auto-create-handler.sh:78-83`, plugin README
**Fix**: Add precedence logic, validation warning for partial config, and README documentation.
