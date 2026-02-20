# Tasks: Multi-Skill Repo Install & Queue Admin Gating

## Task Notation

- `[T###]`: Task ID
- `[P]`: Parallelizable
- `[ ]`: Not started
- `[x]`: Completed
- Model hints: haiku (simple), opus (default)

## Phase 1: Discovery Module (vskill CLI)

### T-001: Create GitHub Trees discovery module
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 | **Status**: [x] Completed

**Description**: Create `src/discovery/github-tree.ts` that calls the GitHub Trees API and returns discovered SKILL.md paths.

**Implementation Details**:
- Create new file `repositories/anton-abyzov/vskill/src/discovery/github-tree.ts`
- Export `discoverSkills(owner: string, repo: string): Promise<DiscoveredSkill[]>`
- Call `GET https://api.github.com/repos/{owner}/{repo}/git/trees/main?recursive=1`
- Filter tree entries matching `SKILL.md` at root or `skills/*/SKILL.md`
- Derive skill name: root SKILL.md -> repo name, `skills/{name}/SKILL.md` -> name
- Build raw.githubusercontent.com URL for each
- Handle 404/rate-limit by returning empty array (caller falls back to single-skill fetch)
- All imports must use `.js` extensions (ESM `nodenext`)

**Test Plan**:
- **File**: `src/discovery/github-tree.test.ts`
- **Tests**:
  - **TC-001**: Discovers root SKILL.md and skills/*/SKILL.md from tree response
    - Given a GitHub tree response with `SKILL.md`, `skills/foo/SKILL.md`, `skills/bar/SKILL.md`
    - When `discoverSkills("owner", "repo")` is called
    - Then returns 3 entries with correct names ("repo", "foo", "bar") and raw URLs
  - **TC-002**: Returns only root SKILL.md when no skills/ directory exists
    - Given a tree response with only `SKILL.md` at root
    - When `discoverSkills` is called
    - Then returns 1 entry with name = repo name
  - **TC-003**: Returns empty array when no SKILL.md files found
    - Given a tree response with no SKILL.md files
    - When `discoverSkills` is called
    - Then returns empty array
  - **TC-004**: Returns empty array on API error (404, rate-limited)
    - Given the GitHub API returns 404 or 403
    - When `discoverSkills` is called
    - Then returns empty array without throwing
  - **TC-005**: Ignores SKILL.md in nested non-skill directories
    - Given tree entries like `docs/SKILL.md`, `examples/SKILL.md`, `node_modules/SKILL.md`
    - When `discoverSkills` is called
    - Then only returns root and `skills/*/SKILL.md` matches

**Dependencies**: None

---

### T-002: Extract single-skill install function from addCommand
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02, AC-US1-03 | **Status**: [x] Completed

**Description**: Refactor the GitHub path in `src/commands/add.ts` to extract the fetch-scan-install pipeline for a single skill into a reusable function.

**Implementation Details**:
- Extract lines 408-551 of `add.ts` into a new function `installSingleSkill(owner, repo, skillName, skillSubpath, opts, agents)`
- This function handles: fetch SKILL.md, blocklist check, platform security check, tier1 scan, agent install, lockfile update
- Returns a result object: `{ skillName, verdict, installed: boolean, error?: string }`
- The existing `addCommand` calls this function for the single-skill case (`--skill` flag or fallback)
- All existing tests must pass without modification

**Test Plan**:
- **File**: `src/commands/add.test.ts` (existing file -- verify regression)
- **Tests**:
  - **TC-006**: All existing add.test.ts tests pass after refactor
    - Given the existing test suite
    - When tests run after refactor
    - Then all existing tests pass unchanged

**Dependencies**: None

---

## Phase 2: Multi-Skill Install Loop (vskill CLI)

### T-003: Implement multi-skill discovery + install loop in addCommand
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05, AC-US1-06, AC-US1-07 | **Status**: [ ] Not Started

**Description**: Wire the discovery module into `addCommand` so that `vskill add owner/repo` discovers and installs all skills.

**Implementation Details**:
- In `addCommand`, when `--skill` is NOT provided:
  1. Call `discoverSkills(owner, repo)` to find all SKILL.md paths
  2. If discovery returns empty, fall back to single root SKILL.md fetch (current behavior)
  3. If discovery returns 1 result (root only), install it (identical to current)
  4. If discovery returns N > 1 results, loop through each calling `installSingleSkill`
  5. Collect results and print multi-skill summary
- When `--skill` IS provided, skip discovery entirely (backward compat, AC-US1-06)
- Each skill gets its own lockfile entry (AC-US1-04)
- Print per-skill verdict in summary (AC-US1-05)
- If one skill fails scan, continue to next (AC-US1-03)

**Test Plan**:
- **File**: `src/commands/add.test.ts`
- **Tests**:
  - **TC-007**: Multi-skill repo installs all discovered skills
    - Given a repo with root SKILL.md and skills/foo/SKILL.md and skills/bar/SKILL.md
    - When `addCommand("owner/repo", {})` is called
    - Then 3 skills are installed, lockfile has 3 entries
  - **TC-008**: Single-skill repo behaves identically to before
    - Given a repo with only root SKILL.md
    - When `addCommand("owner/repo", {})` is called
    - Then 1 skill installed, identical to current behavior
  - **TC-009**: --skill flag bypasses discovery
    - Given any repo
    - When `addCommand("owner/repo", { skill: "specific" })` is called
    - Then discovery is NOT called, only `skills/specific/SKILL.md` is fetched
  - **TC-010**: Failed scan for one skill does not block others
    - Given a repo with 3 skills, middle skill has FAIL verdict
    - When `addCommand("owner/repo", {})` is called
    - Then 2 skills installed, 1 skipped, summary shows individual verdicts
  - **TC-011**: Discovery API failure falls back to single-skill install
    - Given discovery returns empty (API error)
    - When `addCommand("owner/repo", {})` is called
    - Then falls back to fetching root SKILL.md directly

**Dependencies**: T-001, T-002

---

## Phase 3: Queue Admin Gate (vskill-platform)

### T-004: Gate batch submission form behind isAdmin check [P]
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-05 | **Status**: [ ] Not Started

**Description**: Wrap the batch submission UI section on the queue page with an `isAdmin` conditional.

**Implementation Details**:
- In `src/app/queue/page.tsx`, the batch submit section (lines 251-339) currently shows for any user
- Wrap the entire "Submit Skills" button + collapsible form in `{isAdmin && (...)}`
- The `isAdmin` value is already available from `useAdminStatus()` (line 85)
- Remove the separate `authed` state check within the batch form since admin implies authenticated
- Keep the queue list, stats bar, SSE connection, and execution log visible to all users
- Remove `batchOpen`, `batchUrls`, `batchSubmitting`, `batchResults` state from rendering when not admin (lazy)

**Test Plan**:
- **File**: `src/app/queue/__tests__/page.test.tsx` (new file)
- **Tests**:
  - **TC-012**: Admin user sees batch submit button
    - Given `useAdminStatus` returns `{ isAdmin: true, isLoading: false }`
    - When queue page renders
    - Then "Submit Skills" button is present in the DOM
  - **TC-013**: Non-admin authenticated user does NOT see batch submit button
    - Given `useAdminStatus` returns `{ isAdmin: false, isLoading: false }` and auth check returns valid user
    - When queue page renders
    - Then "Submit Skills" button is NOT in the DOM
  - **TC-014**: Unauthenticated user does NOT see batch submit button
    - Given `useAdminStatus` returns `{ isAdmin: false, isLoading: false }` and auth check returns null
    - When queue page renders
    - Then "Submit Skills" button is NOT in the DOM

**Dependencies**: None (parallel with Phase 1-2)

---

## Phase 4: Verification

### T-005: Run full test suite and verify acceptance criteria
**User Story**: US-001, US-002 | **Satisfies ACs**: All | **Status**: [ ] Not Started

**Description**: Run all tests across both projects and verify every AC is satisfied.

**Implementation Details**:
- Run `npm test` in `repositories/anton-abyzov/vskill/` -- all existing + new tests pass
- Run `npm test` in `repositories/anton-abyzov/vskill-platform/` -- all existing + new tests pass
- Manually verify AC checklist against implementation

**Dependencies**: T-003, T-004
