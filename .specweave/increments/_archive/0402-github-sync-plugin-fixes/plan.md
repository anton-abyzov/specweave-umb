# 0402 — Implementation Plan

## Approach

Fix bugs in priority order (P0 > P1 > P2). Each fix is isolated to one or two files, so tasks are parallelizable within priority tiers. Every fix includes a unit test proving the bug existed and is now resolved.

**Base path**: `repositories/anton-abyzov/specweave/plugins/specweave-github/`

---

## Phase 1: P0 Critical Fixes (T-001 through T-004)

These are data-loss or always-broken bugs. Must be fixed first.

### 1.1 Issue body append (T-001)
- **File**: `github-cross-repo-sync.ts`
- **Fix**: Before `gh issue edit --body`, fetch current body with `gh issue view --json body`. Concatenate with `---` separator, then write combined body.
- **Risk**: Race condition if issue is edited concurrently. Acceptable for CLI tool — not a server.

### 1.2 exitCode property (T-002)
- **File**: `github-hierarchical-sync.ts`
- **Fix**: Replace `result.status` with `result.exitCode`. Grep all files for same pattern to catch other instances.
- **Risk**: Minimal — straightforward property rename.

### 1.3 fetchGitHubProject stub (T-003)
- **File**: `github-spec-sync.ts`
- **Fix**: Implement real API call using `gh api graphql` with the ProjectV2 query. Add guard in `resolveConflicts` to never overwrite local title with remote unless explicit user choice.
- **Risk**: Requires GraphQL query for Projects v2 API. Test with mock.

### 1.4 YAML array support (T-004)
- **File**: `github-spec-frontmatter-updater.ts`
- **Fix**: Extend custom YAML parser to handle block arrays (`- item`), flow arrays (`[a, b]`), and nested structures. Add round-trip test with mixed content.
- **Risk**: Custom parsers are fragile. Consider replacing with `yaml` npm package if complexity exceeds ~50 lines of parser additions.

## Phase 2: P1 High Fixes (T-005 through T-011)

### 2.1 Default branch detection (T-005)
- **File**: `enhanced-github-sync.js`
- **Fix**: Replace hardcoded `develop` with `gh repo view --json defaultBranchRef --jq .defaultBranchRef.name`. Cache result per repo.

### 2.2 Cross-platform stat (T-006)
- **Files**: Shell hooks (identify exact files via grep for `stat -f`)
- **Fix**: Replace `stat -f` with `find <file> -mmin +<threshold>` which is POSIX-portable.

### 2.3 Pagination (T-007)
- **Files**: `per-us-sync.ts`, `github-multi-project-sync.ts`
- **Fix**: Add `--paginate` flag to `gh` list commands. Add dedup by issue number.

### 2.4 GraphQL injection (T-008)
- **File**: `github-graphql-client.ts`
- **Fix**: Refactor all queries to use `-F` variable parameters. Ensure no raw user input in template strings.

### 2.5 Config path unification (T-009)
- **File**: `github-feature-sync-cli.ts` + shell hooks
- **Fix**: Extract `resolveGitHubConfig()` with documented precedence. Wire all call sites to use it.

### 2.6 Label existence check (T-010)
- **File**: `github-us-auto-closer.ts`
- **Fix**: Before `gh issue edit --add-label`, check `gh label list --search` and create if missing.

### 2.7 Last comment fetch (T-011)
- **File**: `github-client-v2.ts`
- **Fix**: Use `gh api` with `last: 1` ordering, or `--paginate` + `jq 'last'`.

## Phase 3: P2 Medium Fixes (T-012 through T-015)

### 3.1 Configurable board name (T-012)
- **File**: `github-sync-orchestrator.ts`
- **Fix**: Read `github.boardName` from config, fallback to current default.

### 3.2 Configurable milestone due date (T-013)
- **Files**: `github-client.ts`, `github-client-v2.ts`
- **Fix**: Read `github.milestoneDueDays` from config, fallback to 2.

### 3.3 Configurable cross-team keywords (T-014)
- **File**: `github-spec-sync.ts`
- **Fix**: Read `github.crossTeamKeywords` from config. Default to current English set.

### 3.4 Auto-create config documentation (T-015)
- **File**: `github-auto-create-handler.sh` + plugin README
- **Fix**: Add precedence logic and validation warning. Document in README.

---

## Testing Strategy

- **Unit tests**: Each fix gets a test file or test block proving the bug is fixed.
- **Integration**: Run full sync dry-run against a test repo after all P0 fixes.
- **Verification**: `npx vitest run` after each task.

## Rollback Plan

Each fix is a single commit. Revert individual commits if a fix causes regressions.

## Dependencies

- None external. All fixes are within the plugin codebase.
- Phase 2 T-009 (config unification) should land before T-012/T-013/T-014 since those add new config keys.
