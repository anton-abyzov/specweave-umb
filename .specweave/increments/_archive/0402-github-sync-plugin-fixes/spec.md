# 0402 — GitHub Sync Plugin Critical Fixes

## Overview

The `specweave-github` plugin suite contains 15 bugs across 12 files, identified via grill report. Four are **critical** data-loss or always-failing bugs, seven are **high** correctness/security issues, and four are **medium** hardcoded-value problems. All bugs are in `repositories/anton-abyzov/specweave/plugins/specweave-github/`.

---

## Priority P0 — Critical (Data Loss / Always Broken)

### US-001: Issue body append must not destroy existing content

**As a** user syncing cross-repo issues,
**I want** appended content to be added below existing issue body,
**So that** prior issue context is preserved.

**Bug**: `github-cross-repo-sync.ts:229` — `gh issue edit --body` replaces the entire body instead of appending.

- [x] **AC-US1-01**: Append operation reads existing body first, concatenates new content, then writes the combined body.
- [x] **AC-US1-02**: If the existing body is empty, the new content becomes the full body without leading separators.
- [x] **AC-US1-03**: A horizontal rule (`---`) separates original and appended content.

### US-002: execFileNoThrow exit code check must use correct property

**As a** developer running hierarchical sync,
**I want** process exit codes to be checked correctly,
**So that** sync operations do not always throw false errors.

**Bug**: `github-hierarchical-sync.ts:320` — checks `result.status` but `execFileNoThrow` returns `result.exitCode`. Condition is always `undefined !== 0`, so the function always throws.

- [x] **AC-US2-01**: All `execFileNoThrow` result checks use `result.exitCode` (not `result.status`).
- [x] **AC-US2-02**: Non-zero exit codes produce a descriptive error including the command and exit code.
- [x] **AC-US2-03**: Zero exit codes proceed without throwing.

### US-003: fetchGitHubProject must return real project data

**As a** user syncing specs with GitHub Projects,
**I want** `fetchGitHubProject` to query the actual project title,
**So that** spec titles are not silently overwritten with a hardcoded stub.

**Bug**: `github-spec-sync.ts:664` — stub returns `'Project Title'`. Combined with `resolveConflicts` at `:609`, this overwrites real spec titles.

- [x] **AC-US3-01**: `fetchGitHubProject` calls the GitHub Projects API (GraphQL v2) and returns the actual project title.
- [x] **AC-US3-02**: If the API call fails, it throws an error instead of returning a fallback string.
- [x] **AC-US3-03**: `resolveConflicts` never overwrites a local spec title with an API-sourced title unless the user explicitly chose "remote wins".

### US-004: YAML frontmatter parser must support arrays

**As a** user with YAML frontmatter containing array fields (e.g., `tags`, `labels`),
**I want** the custom YAML parser to round-trip arrays correctly,
**So that** array fields are not destroyed on first sync.

**Bug**: `github-spec-frontmatter-updater.ts:106` — custom parser has no array support. All YAML arrays are silently dropped or corrupted.

- [x] **AC-US4-01**: YAML arrays in block style (`- item`) are parsed and preserved.
- [x] **AC-US4-02**: YAML arrays in flow style (`[a, b, c]`) are parsed and preserved.
- [x] **AC-US4-03**: Round-tripping a frontmatter block with mixed scalars and arrays produces byte-identical output (minus trailing whitespace normalization).
- [x] **AC-US4-04**: Nested arrays (arrays of objects) are preserved.

---

## Priority P1 — High (Correctness / Security)

### US-005: Generated URLs must use the repo's actual default branch

**As a** user viewing sync-generated links,
**I want** URLs to point to the correct default branch,
**So that** links do not 404 on repos that use `main` instead of `develop`.

**Bug**: `enhanced-github-sync.js:168,202` — hardcoded `blob/develop/` in generated URLs.

- [x] **AC-US5-01**: URL generation queries the repo's default branch via `gh repo view --json defaultBranchRef`.
- [x] **AC-US5-02**: The result is cached per repo per sync session to avoid redundant API calls.
- [x] **AC-US5-03**: If the API call fails, the URL omits the branch segment rather than hardcoding a wrong one.

### US-006: Lock detection must work on both macOS and Linux

**As a** user running sync hooks on Linux CI,
**I want** lock file age detection to use cross-platform syntax,
**So that** stale-lock cleanup works on all POSIX systems.

**Bug**: Both shell hooks use `stat -f` (macOS-only). On Linux, `stat -f` parses incorrectly, and lock detection is permanently broken.

- [x] **AC-US6-01**: Lock age detection uses a POSIX-portable method (e.g., `find -mmin` or `date`-based arithmetic).
- [x] **AC-US6-02**: Works correctly on macOS (Darwin) and Linux (GNU coreutils).
- [x] **AC-US6-03**: Stale locks older than the configured threshold are removed on both platforms.

### US-007: Issue listing must paginate to avoid truncation and duplicates

**As a** user with more than 100 issues,
**I want** sync to paginate through all issues,
**So that** no issues are missed or duplicated.

**Bug**: `per-us-sync.ts:258` — no pagination, 100-issue hard limit creates duplicates. `github-multi-project-sync.ts:360` — 30-issue limit.

- [x] **AC-US7-01**: `per-us-sync.ts` uses `--paginate` or iterates pages until exhausted.
- [x] **AC-US7-02**: `github-multi-project-sync.ts` uses `--paginate` or iterates pages until exhausted.
- [x] **AC-US7-03**: Deduplication by issue number is applied before processing.
- [x] **AC-US7-04**: Repos with 150+ issues sync all issues without duplicates.

### US-008: GraphQL queries must not interpolate user input into query strings

**As a** security-conscious user,
**I want** GraphQL variables to be passed as structured parameters,
**So that** injection attacks via repo names or labels are not possible.

**Bug**: `github-graphql-client.ts:36-126` — string interpolation of user input into GraphQL queries. Should use `gh api graphql -F` variable parameters.

- [x] **AC-US8-01**: All GraphQL queries use parameterized variables (`-F` / `variables` field), not string interpolation.
- [x] **AC-US8-02**: Repo names containing special characters (`"`, `\`, `}`) do not break queries.
- [x] **AC-US8-03**: No raw user input appears in query template strings.

### US-009: Config resolution must use a single canonical path

**As a** user configuring owner/repo settings,
**I want** all sync commands to read config from the same path,
**So that** settings are consistent across CLI and hooks.

**Bug**: `github-feature-sync-cli.ts:46-83` — 4 different config paths; shell hook only reads one.

- [x] **AC-US9-01**: A single `resolveGitHubConfig()` function is the sole source of owner/repo config.
- [x] **AC-US9-02**: The resolution order is documented: CLI flag > env var > `.specweave/config.json` > git remote detection.
- [x] **AC-US9-03**: Shell hooks call the same resolution logic (or a shell equivalent that reads the same paths in the same order).

### US-010: Auto-closer must not assume labels exist

**As a** user running auto-close on a fresh repo,
**I want** the auto-closer to create missing labels before applying them,
**So that** it does not fail with "label not found" errors.

**Bug**: `github-us-auto-closer.ts:135` — assumes `status:active` / `status:completed` labels exist.

- [x] **AC-US10-01**: Before applying a label, the auto-closer checks if it exists and creates it if missing.
- [x] **AC-US10-02**: Label creation uses a sensible default color and description.
- [x] **AC-US10-03**: If label creation fails (permissions), a warning is logged and the close operation continues without the label.

### US-011: getLastComment must fetch the actual last comment

**As a** user relying on last-comment detection for sync decisions,
**I want** `getLastComment` to return the chronologically last comment,
**So that** sync logic on issues with 30+ comments behaves correctly.

**Bug**: `github-client-v2.ts:611` — fetches first page only; `.[-1]` gets wrong comment on issues with 30+ comments.

- [x] **AC-US11-01**: `getLastComment` uses `--jq 'last'` with `--paginate`, or queries with `last: 1` sort order.
- [x] **AC-US11-02**: On issues with 50+ comments, the returned comment is the chronologically newest.

---

## Priority P2 — Medium (Hardcoded Values / i18n)

### US-012: Board name must be configurable

**As a** user with a custom project board name,
**I want** the sync orchestrator to read the board name from config,
**So that** sync works with any board name.

**Bug**: `github-sync-orchestrator.ts:109` — hardcoded `'SpecWeave Sync Board'`.

- [x] **AC-US12-01**: Board name is read from `.specweave/config.json` under `github.boardName`.
- [x] **AC-US12-02**: If not configured, defaults to `'SpecWeave Sync Board'`.

### US-013: Milestone due date must be configurable

**As a** user with varying sprint lengths,
**I want** milestone due dates to be configurable,
**So that** milestones reflect actual timelines.

**Bug**: `github-client.ts:52` / `github-client-v2.ts:151` — hardcoded 2-day milestone due date.

- [x] **AC-US13-01**: Milestone due offset is read from config (`github.milestoneDueDays`).
- [x] **AC-US13-02**: Default remains 2 days if not configured.
- [x] **AC-US13-03**: The due date is calculated from the creation timestamp, not from a fixed date.

### US-014: Cross-team spec detection must not hardcode English keywords

**As a** user with non-English spec titles,
**I want** cross-team detection to use configurable patterns,
**So that** internationalized specs are correctly identified.

**Bug**: `github-spec-sync.ts:935-944` — `isCrossTeamSpec()` hardcodes English keywords.

- [x] **AC-US14-01**: Detection patterns are configurable via `github.crossTeamKeywords` array in config.
- [x] **AC-US14-02**: Default keywords match current English set for backward compatibility.
- [x] **AC-US14-03**: Pattern matching is case-insensitive.

### US-015: Auto-create config split must be documented and reconciled

**As a** user configuring auto-creation of GitHub issues,
**I want** `autoSync` and `auto_create_github_issue` to be clearly documented,
**So that** I know which flag controls what behavior.

**Bug**: `github-auto-create-handler.sh:78-83` — `autoSync` vs `auto_create_github_issue` undocumented split.

- [x] **AC-US15-01**: Both flags are documented in the plugin README with their distinct scopes.
- [x] **AC-US15-02**: If both are set, the handler logs which one takes precedence.
- [x] **AC-US15-03**: A config validation warning fires if only one of the two is set (likely misconfiguration).

---

## Out of Scope

- Rewriting the entire sync plugin architecture.
- Adding new sync features (this increment is bugfix-only).
- Migrating from `gh` CLI to Octokit SDK.
