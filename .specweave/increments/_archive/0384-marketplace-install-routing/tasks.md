# Tasks: Fix marketplace install routing and find grouping

## Task Notation

- `[T###]`: Task ID
- `[P]`: Parallelizable
- `[ ]`: Not started
- `[x]`: Completed
- Model hints: haiku (simple), sonnet (medium), opus (complex)

---

## Phase 1: Foundation (US-001, US-005)

### US-005: Rate-limit warning (P2)

#### T-001: Add `warnRateLimitOnce` helper to github-tree.ts

**User Story**: US-005 | **Satisfies ACs**: AC-US5-01, AC-US5-02, AC-US5-03 | **Status**: [x] completed

**Description**: Add a module-level deduplicated rate-limit warning helper to `src/discovery/github-tree.ts`. This is a shared utility used by both `detectMarketplaceRepo` (in add.ts) and `discoverSkills`.

**Implementation Details**:
- Add module-level `let rateLimitWarned = false` flag
- Export `warnRateLimitOnce(res: Response): void` that checks `res.status === 403` AND `res.headers.get("x-ratelimit-remaining") === "0"`
- If both match and `!rateLimitWarned`, print yellow warning: `"GitHub API rate limit reached. Set GITHUB_TOKEN for higher limits."` and set flag
- Export `_resetRateLimitWarned()` for testing (prefixed with _ like existing `_resetBranchCache`)

**File**: `src/discovery/github-tree.ts`

**Test Plan**:
- **File**: `src/discovery/github-tree.test.ts`
- **Tests**:
  - **TC-001**: prints warning on 403 with x-ratelimit-remaining: 0
    - Given a Response with status 403 and header `x-ratelimit-remaining: 0`
    - When `warnRateLimitOnce` is called
    - Then yellow warning is printed to stderr containing "rate limit" and "GITHUB_TOKEN"
  - **TC-002**: does not print warning on 403 without rate-limit header
    - Given a Response with status 403 but no `x-ratelimit-remaining` header
    - When `warnRateLimitOnce` is called
    - Then no output is printed
  - **TC-003**: prints warning only once across multiple calls
    - Given two sequential 403 rate-limit responses
    - When `warnRateLimitOnce` is called twice
    - Then warning is printed exactly once
  - **TC-004**: _resetRateLimitWarned allows re-warning in tests
    - Given a rate-limit warning was already printed
    - When `_resetRateLimitWarned()` is called then `warnRateLimitOnce` is called again
    - Then warning is printed again

**Dependencies**: None
**Model**: sonnet

---

### US-001: Resilient marketplace detection (P1)

#### T-002: Add `hasPlugin` helper to marketplace.ts

**User Story**: US-001 | **Satisfies ACs**: (supports AC-US2-01, AC-US2-02) | **Status**: [x] completed

**Description**: Add a convenience function `hasPlugin(name: string, content: string): boolean` to `src/marketplace/marketplace.ts`. Thin wrapper: returns `getPluginSource(name, content) !== null`.

**Implementation Details**:
- Add function to `src/marketplace/marketplace.ts`
- Export from `src/marketplace/index.ts` barrel

**File**: `src/marketplace/marketplace.ts`, `src/marketplace/index.ts`

**Test Plan**:
- **File**: `src/marketplace/marketplace.test.ts`
- **Tests**:
  - **TC-005**: returns true when plugin exists in manifest
    - Given valid marketplace.json with plugin "sw"
    - When `hasPlugin("sw", content)` is called
    - Then returns `true`
  - **TC-006**: returns false when plugin does not exist
    - Given valid marketplace.json without plugin "nonexistent"
    - When `hasPlugin("nonexistent", content)` is called
    - Then returns `false`
  - **TC-007**: returns false for invalid JSON
    - Given invalid JSON string
    - When `hasPlugin("sw", invalidJson)` is called
    - Then returns `false` (no throw)

**Dependencies**: None
**Model**: haiku

---

#### T-003: Make `detectMarketplaceRepo` resilient with retry + raw fallback

**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03 | **Status**: [x] completed

**Description**: Refactor `detectMarketplaceRepo` in `src/commands/add.ts` to retry the Contents API once on failure, then fall back to `raw.githubusercontent.com`, and call `warnRateLimitOnce` on 403 responses.

**Implementation Details**:
- Import `warnRateLimitOnce` and `getDefaultBranch` into add.ts (getDefaultBranch already imported)
- Wrap existing Contents API call in retry logic: try → (fail) → wait 1s → retry → (fail) → raw fallback
- On any 403 response, call `warnRateLimitOnce(res)` before proceeding
- Raw fallback URL: `https://raw.githubusercontent.com/${owner}/${repo}/${branch}/.claude-plugin/marketplace.json`
- Branch from `getDefaultBranch(owner, repo)` (cached)
- Parse raw content with existing `getAvailablePlugins` validation
- On all failures, return `{ isMarketplace: false }` (existing behavior preserved)

**File**: `src/commands/add.ts` (lines ~73-115)

**Test Plan**:
- **File**: `src/commands/add.test.ts`
- **Tests**:
  - **TC-008**: succeeds on first Contents API attempt
    - Given Contents API returns 200 with valid marketplace.json
    - When `detectMarketplaceRepo` is called
    - Then returns `{ isMarketplace: true, manifestContent }` with no retry
  - **TC-009**: retries once after Contents API failure, succeeds on retry
    - Given Contents API returns 500 first, then 200 on retry
    - When `detectMarketplaceRepo` is called
    - Then returns `{ isMarketplace: true }` after retry
  - **TC-010**: falls back to raw after both Contents API attempts fail
    - Given Contents API returns 500 twice, raw endpoint returns 200
    - When `detectMarketplaceRepo` is called
    - Then returns `{ isMarketplace: true }` via raw fallback
  - **TC-011**: calls warnRateLimitOnce on 403 with rate-limit header
    - Given Contents API returns 403 with `x-ratelimit-remaining: 0`
    - When `detectMarketplaceRepo` is called
    - Then `warnRateLimitOnce` is called and fallback proceeds
  - **TC-012**: returns false when all attempts fail
    - Given Contents API 500 twice and raw returns 404
    - When `detectMarketplaceRepo` is called
    - Then returns `{ isMarketplace: false }`
  - **TC-013**: returns false for non-marketplace repo (all 404)
    - Given Contents API returns 404 (no retry needed for 404)
    - When `detectMarketplaceRepo` is called
    - Then returns `{ isMarketplace: false }` immediately (404 = not a marketplace, no retry)

**Dependencies**: T-001
**Model**: opus

---

## Phase 2: Core Routing (US-002, US-004)

### US-002: Marketplace-first routing (P1)

#### T-004: Add `preSelected` parameter to `installMarketplaceRepo`

**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02 (prerequisite) | **Status**: [x] completed

**Description**: Add optional `preSelected?: string[]` parameter to `installMarketplaceRepo`. When set, matching plugins are pre-checked in the checkbox list. When `--yes` + `preSelected`, install only the pre-selected plugins instead of all.

**Implementation Details**:
- Add `preSelected?: string[]` to function signature (after `opts`)
- In the checkbox list construction (line ~173), set `checked: preSelected?.includes(p.name) ?? false`
- In the `opts.yes || opts.all` branch (line ~167-169), if `preSelected` is set, filter to only matching plugins: `selectedPlugins = plugins.filter(p => preSelected.includes(p.name))`
- If `preSelected` is set but no matches found, fall through to existing behavior (show all)

**File**: `src/commands/add.ts` (lines ~124-186)

**Test Plan**:
- **File**: `src/commands/add.test.ts`
- **Tests**:
  - **TC-014**: preSelected pre-checks matching plugins in checkbox list
    - Given marketplace with plugins ["sw", "sw-github", "sw-jira"]
    - When `installMarketplaceRepo` is called with `preSelected: ["sw"]`
    - Then checkbox prompt has "sw" checked and others unchecked
  - **TC-015**: --yes with preSelected installs only pre-selected plugins
    - Given `opts.yes = true` and `preSelected: ["sw"]`
    - When `installMarketplaceRepo` is called
    - Then only "sw" plugin is installed (not all 3)
  - **TC-016**: preSelected with no matches falls through to show all
    - Given `preSelected: ["nonexistent"]`
    - When `installMarketplaceRepo` is called
    - Then all plugins shown unchecked (existing behavior)

**Dependencies**: None
**Model**: sonnet

---

#### T-005: Route 3-part format through marketplace check

**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-03, AC-US2-04 | **Status**: [x] completed

**Description**: In the 3-part format branch (`owner/repo/skill`), insert marketplace detection before `installSingleSkillLegacy`. If marketplace AND name matches a plugin, route to `installMarketplaceRepo` with pre-selection.

**Implementation Details**:
- At line ~1441, before `return installSingleSkillLegacy(...)`:
  ```
  const detection = await detectMarketplaceRepo(threeOwner, threeRepo);
  if (detection.isMarketplace && detection.manifestContent) {
    if (hasPlugin(threeSkill, detection.manifestContent)) {
      return installMarketplaceRepo(threeOwner, threeRepo, detection.manifestContent, opts, [threeSkill]);
    }
  }
  // existing fallthrough to installSingleSkillLegacy
  ```
- Import `hasPlugin` from marketplace module

**File**: `src/commands/add.ts` (lines ~1440-1444)

**Test Plan**:
- **File**: `src/commands/add.test.ts`
- **Tests**:
  - **TC-017**: 3-part format routes to marketplace when plugin matches
    - Given `vskill install anton-abyzov/specweave/sw` and repo is marketplace with plugin "sw"
    - When `addCommand` is called
    - Then `installMarketplaceRepo` is called with preSelected ["sw"]
  - **TC-018**: 3-part format falls through to legacy when plugin doesn't match
    - Given `vskill install anton-abyzov/specweave/unknown` and repo is marketplace without "unknown"
    - When `addCommand` is called
    - Then `installSingleSkillLegacy` is called (existing behavior)
  - **TC-019**: 3-part format falls through to legacy when not marketplace
    - Given `vskill install owner/repo/skill` and repo is NOT a marketplace
    - When `addCommand` is called
    - Then `installSingleSkillLegacy` is called (existing behavior preserved)

**Dependencies**: T-002, T-003, T-004
**Model**: sonnet

---

#### T-006: Route `--skill` flag through marketplace check

**User Story**: US-002 | **Satisfies ACs**: AC-US2-02, AC-US2-03, AC-US2-04 | **Status**: [x] completed

**Description**: In the `--skill` flag branch, insert marketplace detection before `installSingleSkillLegacy`. Same pattern as T-005.

**Implementation Details**:
- At line ~1457, before `return installSingleSkillLegacy(...)`:
  ```
  const detection = await detectMarketplaceRepo(owner, repo);
  if (detection.isMarketplace && detection.manifestContent) {
    if (hasPlugin(opts.skill, detection.manifestContent)) {
      return installMarketplaceRepo(owner, repo, detection.manifestContent, opts, [opts.skill]);
    }
  }
  // existing fallthrough
  ```

**File**: `src/commands/add.ts` (lines ~1456-1459)

**Test Plan**:
- **File**: `src/commands/add.test.ts`
- **Tests**:
  - **TC-020**: --skill routes to marketplace when plugin matches
    - Given `vskill install anton-abyzov/specweave --skill sw` and repo is marketplace
    - When `addCommand` is called
    - Then `installMarketplaceRepo` is called with preSelected ["sw"]
  - **TC-021**: --skill falls through to legacy when not marketplace
    - Given `vskill install owner/repo --skill myskill` and repo is NOT marketplace
    - When `addCommand` is called
    - Then `installSingleSkillLegacy` is called (unchanged)

**Dependencies**: T-002, T-003, T-004
**Model**: sonnet

---

### US-004: Fix tip message and discovery scope (P1)

#### T-007: Fix tip message in `installFromRegistry`

**User Story**: US-004 | **Satisfies ACs**: AC-US4-01 | **Status**: [x] completed

**Description**: Fix the tip message at line ~1690 in `installFromRegistry` that currently suggests the broken `owner/repo/skill` 3-part format.

**Implementation Details**:
- Line ~1690: Change from `vskill install ${ownerRepo}/${detail.name}` to:
  - When `detail.pluginName`: `vskill install ${ownerRepo} --plugin ${detail.pluginName}`
  - When no `pluginName`: `vskill install ${ownerRepo}`
- Line ~1449: Change tip text from `"Prefer owner/repo or owner/repo/skill format"` to `"Prefer owner/repo format for direct GitHub installs."`

**File**: `src/commands/add.ts` (lines ~1449, ~1690)

**Test Plan**:
- **File**: `src/commands/add.test.ts`
- **Tests**:
  - **TC-022**: tip with pluginName shows --plugin flag
    - Given registry returns `pluginName: "sw"` and `repoUrl` for `owner/repo`
    - When `installFromRegistry` falls back to GitHub install
    - Then tip contains `vskill install owner/repo --plugin sw`
  - **TC-023**: tip without pluginName shows plain owner/repo
    - Given registry returns no `pluginName`
    - When `installFromRegistry` falls back to GitHub install
    - Then tip contains `vskill install owner/repo` (no `/skillname`)

**Dependencies**: None
**Model**: haiku

---

#### T-008: Add discovery scope guard test

**User Story**: US-004 | **Satisfies ACs**: AC-US4-02, AC-US4-03 | **Status**: [x] completed

**Description**: Add negative test confirming `discoverSkills` regex does NOT match `plugins/*/SKILL.md` paths. Add defensive comment on the regex.

**Implementation Details**:
- In `github-tree.ts` line ~131, add comment: `// IMPORTANT: Only match skills/ directory. Never plugins/ — those are handled by installRepoPlugin.`
- In `github-tree.test.ts`, add test cases for non-matching paths

**File**: `src/discovery/github-tree.ts`, `src/discovery/github-tree.test.ts`

**Test Plan**:
- **File**: `src/discovery/github-tree.test.ts`
- **Tests**:
  - **TC-024**: `plugins/foo/SKILL.md` not matched by discovery
    - Given tree contains `plugins/specweave/SKILL.md`
    - When `discoverSkills` is called
    - Then result does NOT include any skill from `plugins/` path
  - **TC-025**: `plugins/specweave/skills/pm/SKILL.md` not matched
    - Given tree contains `plugins/specweave/skills/pm/SKILL.md`
    - When `discoverSkills` is called
    - Then result does NOT include any skill from nested `plugins/` path
  - **TC-026**: `skills/pm/SKILL.md` IS matched (positive control)
    - Given tree contains `skills/pm/SKILL.md`
    - When `discoverSkills` is called
    - Then result includes skill "pm" from `skills/pm/SKILL.md`

**Dependencies**: None
**Model**: haiku

---

## Phase 3: Find Grouping (US-003)

#### T-009: Group find results by repository

**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04, AC-US3-05 | **Status**: [x] completed

**Description**: In the find command, group search results by `repoUrl` when multiple skills share a repo. Show marketplace header with install hint for groups. Keep JSON output flat.

**Implementation Details**:
- In `findCommand` in `src/commands/find.ts`, after receiving results:
- Extract base `owner/repo` from `repoUrl` (parse URL, strip `/tree/...` suffix)
- Group results by base repo: `Map<string, SkillSearchResult[]>`
- Groups with 2+ skills: render marketplace header (bold owner/repo, skill count, install hint) then indented skill rows
- Singletons and skills without `repoUrl`: render as before
- JSON output (`--json`): skip grouping, return flat array (existing behavior)
- Interactive mode hints: add `m install marketplace` alongside existing `i install`

**File**: `src/commands/find.ts`

**Test Plan**:
- **File**: `src/commands/find.test.ts`
- **Tests**:
  - **TC-027**: groups 2+ skills from same repo under marketplace header
    - Given 3 search results with same base `repoUrl`
    - When `findCommand` is called
    - Then output contains marketplace header with `owner/repo` and install hint
  - **TC-028**: singleton skills not grouped
    - Given 1 search result with unique `repoUrl`
    - When `findCommand` is called
    - Then skill renders as standalone row (no group header)
  - **TC-029**: skills without repoUrl not grouped
    - Given search results where some have no `repoUrl`
    - When `findCommand` is called
    - Then those skills render as standalone rows
  - **TC-030**: JSON output remains flat array
    - Given `--json` flag and grouped results
    - When `findCommand` is called
    - Then JSON output is flat array (no grouping structure)

**Dependencies**: None (can be done in parallel with Phase 2)
**Model**: opus

---

## Phase 4: Validation

#### T-010: Run existing test suite and verify no regressions

**User Story**: All | **Satisfies ACs**: All | **Status**: [x] completed

**Description**: Run `npx vitest run` in the vskill repo to verify all existing tests pass alongside new tests.

**Implementation Details**:
- Run full test suite from `repositories/anton-abyzov/vskill/`
- Fix any regressions
- Verify test count increased by ~20 tests

**Dependencies**: T-001 through T-009
**Model**: sonnet

---

## Summary

| Phase | Tasks | ACs Covered |
|-------|-------|-------------|
| Phase 1: Foundation | T-001, T-002, T-003 | US-001 (3 ACs), US-005 (3 ACs) |
| Phase 2: Core Routing | T-004, T-005, T-006, T-007, T-008 | US-002 (4 ACs), US-004 (3 ACs) |
| Phase 3: Find Grouping | T-009 | US-003 (5 ACs) |
| Phase 4: Validation | T-010 | All |

**Total**: 10 tasks, 30 test cases, ~395 lines across 8 files (4 source + 4 test)

**Parallelizable**: T-001+T-002 (Phase 1 helpers), T-005+T-006 (same pattern), T-007+T-008 (independent fixes), T-009 (independent of Phase 2)
