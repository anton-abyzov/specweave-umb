---
increment: 0504-install-skill-discovery
title: "Install Command Skill Discovery & Disambiguation"
status: planned
by_user_story:
  US-001: [T-001, T-002]
  US-002: [T-003, T-004]
  US-003: [T-005]
  US-004: [T-006, T-007]
  US-005: [T-008]
---

# Tasks: Install Command Skill Discovery & Disambiguation

## Task Notation

- `[ ]` not started | `[x]` completed
- `[P]` parallelizable

---

## User Story: US-001 - Search Registry on Flat Name Install

**Linked ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04
**Tasks**: T-001, T-002 | 0 completed

---

### T-001: Create `src/utils/skill-display.ts` with extracted helpers and `rankSearchResults`

**User Story**: US-001
**Satisfies ACs**: AC-US1-01, AC-US4-01, AC-US4-02, AC-US4-03
**Status**: [ ] pending

**Test Plan**:
- **Given** four private helpers (`extractBaseRepo`, `formatSkillId`, `getSkillUrl`, `getTrustBadge`) currently in `find.ts`
- **When** they are extracted into `src/utils/skill-display.ts` and a new `rankSearchResults()` is added
- **Then** both `find.ts` (re-importing) and `add.ts` (new importer) render identical output and ranking is deterministic

**Test Cases** (`src/utils/skill-display.test.ts` — new file):

1. **Unit** — `extractBaseRepo`
   - `extractBaseRepo_githubUrl_returnsOwnerRepo()`: Given `https://github.com/owner/repo.git` → returns `"owner/repo"`
   - `extractBaseRepo_treeUrl_stripsTree()`: Given `https://github.com/owner/repo/tree/main` → returns `"owner/repo"`
   - `extractBaseRepo_undefined_returnsNull()`: Given `undefined` → returns `null`

2. **Unit** — `formatSkillId`
   - `formatSkillId_withSlugs_formatsCorrectly()`: Given result with `ownerSlug/repoSlug/skillSlug` → returns `"owner/repo/skill"`
   - `formatSkillId_noSlugs_fallsBackToRepoUrl()`: Given result with only `repoUrl` and `name` → returns derived path

3. **Unit** — `getTrustBadge`
   - `getTrustBadge_certified_returnsGreenBadge()`: Given `certTier="CERTIFIED"` → returns green string
   - `getTrustBadge_verified_returnsCyanBadge()`: Given `certTier="VERIFIED"` → returns cyan string
   - `getTrustBadge_unknown_returnsEmpty()`: Given both undefined → returns `""`

4. **Unit** — `rankSearchResults` (coverage target: 95%)
   - `rank_blockedAtEnd()`: Blocked results always sort after non-blocked
   - `rank_exactSlugMatch_promotedFirst()`: Result with `skillSlug` matching query (case-insensitive) → position 0
   - `rank_certTierOrder()`: CERTIFIED before VERIFIED before others among non-blocked, non-exact
   - `rank_starsTiebreaker()`: Equal cert tier → higher stars first
   - `rank_scoreTiebreaker()`: Equal cert tier and stars → higher score first
   - `rank_allBlocked_preservesOrder()`: All blocked → sorted within blocked group
   - `rank_noQuery_skipsExactPromotion()`: No `exactQuery` → no promotion applied

**Implementation**:
1. Create `src/utils/skill-display.ts`
2. Move `extractBaseRepo`, `formatSkillId`, `getSkillUrl`, `getTrustBadge` verbatim from `find.ts` (preserve JSDoc)
3. Add `rankSearchResults(results: SkillSearchResult[], exactQuery?: string): SkillSearchResult[]` with sort logic per AC-US4-01/02
4. Export all five functions
5. Update `find.ts`: replace local function definitions with `import { ... } from "../utils/skill-display.js"`
6. Verify `find.test.ts` still passes (no behavior change)
7. Create `src/utils/skill-display.test.ts` with all test cases above

**Dependencies**: None
**Coverage Target**: 95%

---

### T-002: Implement `resolveViaSearch()` in `add.ts` and wire flat-name branch

**User Story**: US-001
**Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04
**Status**: [ ] pending

**Test Plan**:
- **Given** a user calls `vskill install skill-creator` (flat name, no slashes)
- **When** `addCommand("skill-creator", opts)` reaches the `parts.length !== 2` branch
- **Then** `resolveViaSearch("skill-creator", opts)` is called instead of `installFromRegistry` directly

**Test Cases** (added to `src/commands/add.test.ts`, coverage target: 90%):

1. **Unit** — single installable result auto-installs
   - `resolveViaSearch_singleResult_callsAddCommandWithFullPath()`:
     - Given `searchSkills` returns one non-blocked result with all slug fields
     - When `resolveViaSearch("skill-creator", opts)` is called
     - Then `addCommand("owner/repo/skill", opts)` is called (re-entry with 3-part path)

2. **Unit** — zero results prints error
   - `resolveViaSearch_zeroResults_printsErrorAndSuggestFind()`:
     - Given `searchSkills` returns empty array
     - When `resolveViaSearch("skill-creator", opts)` is called
     - Then console output includes "vskill find skill-creator" suggestion and process exits with code 1

3. **Unit** — search API error falls back to `installFromRegistry`
   - `resolveViaSearch_searchThrows_fallsBackToInstallFromRegistry()`:
     - Given `searchSkills` throws a network error
     - When `resolveViaSearch("skill-creator", opts)` is called
     - Then `installFromRegistry("skill-creator", opts)` is called (original behavior)

4. **Unit** — single result that is blocked treated as zero installable
   - `resolveViaSearch_singleBlockedResult_treatsAsZero()`:
     - Given `searchSkills` returns one result where `blocked=true`
     - When `resolveViaSearch` is called
     - Then error is printed, not install

**Implementation**:
1. Add import for `searchSkills` to `add.ts` (already imported — verify)
2. Add import for `rankSearchResults`, `formatSkillId`, `getSkillUrl`, `getTrustBadge` from `../utils/skill-display.js`
3. Add import for `isTTY`, `createPrompter` from `../utils/prompts.js`
4. Implement `resolveViaSearch(flatName: string, opts: AddOptions): Promise<void>`:
   - Call `searchSkills(flatName)` in try/catch; on error → `return installFromRegistry(flatName, opts)`
   - Call `rankSearchResults(results, flatName)`
   - Filter installable: `!r.blocked && r.ownerSlug && r.repoSlug && r.skillSlug`
   - If 0 installable → print list (blocked with labels), print error + `vskill find` suggestion, `process.exit(1)`
   - If 1 installable → `return addCommand(\`${r.ownerSlug}/${r.repoSlug}/${r.skillSlug}\`, opts)`
   - Otherwise → handled in T-003/T-005 branches
5. Replace lines 1919-1924 in `add.ts`: call `return resolveViaSearch(source, opts)` instead of `installFromRegistry`
6. Add test cases to `src/commands/add.test.ts` (mock `searchSkills` via `vi.hoisted()` + `vi.mock`)

**Dependencies**: T-001 (needs `skill-display.ts` module and `rankSearchResults`)
**Coverage Target**: 90%

---

## User Story: US-002 - Interactive Disambiguation for Multiple Matches

**Linked ACs**: AC-US2-01, AC-US2-02, AC-US2-03
**Tasks**: T-003, T-004 | 0 completed

---

### T-003: TTY interactive disambiguation with `promptChoice`

**User Story**: US-002
**Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03
**Status**: [ ] pending

**Test Plan**:
- **Given** multiple non-blocked search results and `isTTY()` returns true
- **When** `resolveViaSearch` is called without `--yes`
- **Then** a `promptChoice` is displayed showing ranked results (same format as `vskill find`) and the selected result is installed

**Test Cases** (added to `src/commands/add.test.ts`):

1. **Unit** — multiple TTY results show prompt and install selected
   - `resolveViaSearch_multipleTTY_promptsAndInstallsSelected()`:
     - Given `searchSkills` returns 3 non-blocked results, `isTTY()=true`, user selects index 1
     - When `resolveViaSearch` is called
     - Then `promptChoice` is called with entries matching `vskill find` format
     - Then `addCommand("owner1/repo1/skill1", opts)` is called for selected item

2. **Unit** — blocked results appear in list but not in selectable choices
   - `resolveViaSearch_mixedBlockedResults_blockedNotSelectable()`:
     - Given results contain 2 non-blocked + 1 blocked, `isTTY()=true`
     - When prompt is displayed
     - Then `promptChoice` options count equals 2 (blocked excluded)
     - Then blocked entry still displays with "BLOCKED" label in list output

3. **Unit** — user cancels prompt (promptChoice returns undefined/null)
   - `resolveViaSearch_promptCancelled_exitsGracefully()`:
     - Given user presses Ctrl-C / returns undefined
     - When `resolveViaSearch` handles the cancel
     - Then process exits with code 1 or returns without install

**Implementation** (within `resolveViaSearch` — extend T-002's implementation):
1. In the N-installable branch: check `isTTY()`
2. If TTY and no `--yes`: build choice list from ranked installable results with display format
3. Include blocked results in display output (with BLOCKED label) but not in `promptChoice` options
4. Call `createPrompter().promptChoice(label, choices)` where each choice value is the `owner/repo/skill` string
5. On selection → `return addCommand(selection, opts)`
6. On cancel/undefined → `process.exit(1)`
7. Add test cases using `vi.mock("../utils/prompts.js")` via `vi.hoisted()`

**Dependencies**: T-002
**Coverage Target**: 90%

---

### T-004: Display format parity with `vskill find`

**User Story**: US-002
**Satisfies ACs**: AC-US2-01
**Status**: [ ] pending

**Test Plan**:
- **Given** `resolveViaSearch` renders search results before prompting
- **When** comparing output format to `vskill find` output
- **Then** each result line includes skill ID, stars, trust badge, and URL in the same structure

**Test Cases** (added to `src/utils/skill-display.test.ts`):

1. **Unit** — `formatResultLine` or display output matches find format
   - `displayLine_withAllFields_includesIdStarsBadgeUrl()`:
     - Given a result with `skillSlug`, `githubStars=42`, `certTier="VERIFIED"`, valid slugs
     - When display is rendered
     - Then output contains the skill ID, "42", verified badge text, and verified-skill.com URL

**Implementation**:
1. Extract a `formatResultLine(r: SkillSearchResult, index: number, isBlocked: boolean): string` helper into `skill-display.ts`
2. Use it in both `resolveViaSearch` (in `add.ts`) and optionally in `findCommand` for consistency
3. Test output structure matches `find` format

**Dependencies**: T-001, T-003
**Coverage Target**: 85%

---

## User Story: US-003 - Non-TTY Disambiguation

**Linked ACs**: AC-US3-01, AC-US3-02
**Tasks**: T-005 | 0 completed

---

### T-005: Non-TTY exit with ranked list and actionable error

**User Story**: US-003
**Satisfies ACs**: AC-US3-01, AC-US3-02
**Status**: [ ] pending

**Test Plan**:
- **Given** multiple search results and `isTTY()` returns false (CI/piped environment)
- **When** `resolveViaSearch` is called without `--yes`
- **Then** the ranked result list is printed and the process exits with code 1 with a message instructing to use `owner/repo/skill` format

**Test Cases** (added to `src/commands/add.test.ts`):

1. **Unit** — non-TTY prints list and exits 1
   - `resolveViaSearch_multipleNonTTY_printsListAndExits()`:
     - Given `searchSkills` returns 3 results, `isTTY()=false`, no `--yes` flag
     - When `resolveViaSearch` is called
     - Then console output includes all ranked results
     - Then output includes message about specifying exact `owner/repo/skill` path
     - Then `process.exit(1)` is called

2. **Unit** — non-TTY error message instructs exact path format
   - `resolveViaSearch_nonTTY_errorMsgMentionsExactPath()`:
     - Given non-TTY with multiple results
     - When output is captured
     - Then message contains "owner/repo/skill" substring

**Implementation** (within `resolveViaSearch` N-installable branch):
1. Check `!isTTY()` and no `--yes` flag
2. Print ranked full list with same format as find output
3. Print error: `"Ambiguous match. Specify the exact skill: vskill install owner/repo/skill"`
4. Call `process.exit(1)`
5. Add mock for `isTTY` in test via `vi.hoisted()` pattern

**Dependencies**: T-002, T-003
**Coverage Target**: 90%

---

## User Story: US-004 - Result Ranking with Exact Match Priority

**Linked ACs**: AC-US4-01, AC-US4-02, AC-US4-03
**Tasks**: T-006, T-007 | 0 completed

---

### T-006: Validate ranking function edge cases

**User Story**: US-004
**Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03
**Status**: [ ] pending

**Test Plan**:
- **Given** `rankSearchResults()` implemented in T-001
- **When** edge case inputs are provided
- **Then** sorting is correct and deterministic in all cases

**Test Cases** (added to `src/utils/skill-display.test.ts`):

1. **Unit** — all results blocked → shows blocked list, prints no-installable error
   - `rank_allBlocked_displayedWithLabels()`:
     - Given array of 3 blocked results
     - When `rankSearchResults` is called
     - Then all appear in output, each labeled BLOCKED
     - Then error message says no installable skills found

2. **Unit** — results with missing slug fields excluded from installable set
   - `rank_missingSlug_excludedFromInstallable()`:
     - Given result where `repoSlug` is undefined but not blocked
     - When installable filtering is applied
     - Then result is not in installable set, but still appears in display list

3. **Unit** — exact match is case-insensitive
   - `rank_exactMatch_caseInsensitive()`:
     - Given query `"Skill-Creator"` and result with `skillSlug="skill-creator"`
     - When `rankSearchResults("Skill-Creator")` is called
     - Then that result is at position 0

**Implementation**:
1. These cases are handled by `rankSearchResults` already specified in T-001
2. Add the additional test cases to `src/utils/skill-display.test.ts`
3. Confirm `resolveViaSearch` respects "missing slug → display but not selectable" rule from plan

**Dependencies**: T-001
**Coverage Target**: 95%

---

### T-007: Regression tests for existing `owner/repo` and `owner/repo/skill` paths

**User Story**: US-004
**Satisfies ACs**: AC-US4-01
**Status**: [ ] pending

**Test Plan**:
- **Given** the flat-name branch in `add.ts` is replaced with `resolveViaSearch`
- **When** existing `owner/repo` and `owner/repo/skill` inputs are used
- **Then** those paths are completely unaffected (no behavioral change)

**Test Cases** (verify in existing `src/commands/add.test.ts`):

1. **Regression** — `owner/repo` path unchanged
   - `addCommand_twoPartPath_skipsResolveViaSearch()`:
     - Given source is `"owner/repo"` (2 parts)
     - When `addCommand` is called
     - Then `resolveViaSearch` is never called

2. **Regression** — `owner/repo/skill` path unchanged
   - `addCommand_threePartPath_skipsResolveViaSearch()`:
     - Given source is `"owner/repo/skill"` (3 parts)
     - When `addCommand` is called
     - Then `resolveViaSearch` is never called

**Implementation**:
1. Review existing test cases in `add.test.ts` for 2-part and 3-part paths
2. Add explicit spy/mock to assert `resolveViaSearch` (or `searchSkills`) is NOT called for these paths
3. Run full `add.test.ts` suite — all pre-existing tests must remain green

**Dependencies**: T-002
**Coverage Target**: 90%

---

## User Story: US-005 - `--yes` Flag Auto-Pick

**Linked ACs**: AC-US5-01, AC-US5-02
**Tasks**: T-008 | 0 completed

---

### T-008: `--yes` flag auto-selects first ranked non-blocked result

**User Story**: US-005
**Satisfies ACs**: AC-US5-01, AC-US5-02
**Status**: [ ] pending

**Test Plan**:
- **Given** the `--yes` flag is set and multiple search results exist
- **When** `resolveViaSearch` is called
- **Then** the first non-blocked ranked result (after exact-match promotion) is auto-installed without prompting

**Test Cases** (added to `src/commands/add.test.ts`):

1. **Unit** — `--yes` with multiple results auto-picks first ranked
   - `resolveViaSearch_yesFlag_autoPicksFirstNonBlocked()`:
     - Given `opts.yes=true`, `searchSkills` returns 3 non-blocked results, `isTTY()=true`
     - When `resolveViaSearch` is called
     - Then `promptChoice` is NOT called
     - Then `addCommand("owner0/repo0/skill0", opts)` is called (first after ranking)

2. **Unit** — `--yes` with all blocked → exits with code 1
   - `resolveViaSearch_yesFlag_allBlocked_exits1()`:
     - Given `opts.yes=true`, all results are blocked
     - When `resolveViaSearch` is called
     - Then `process.exit(1)` is called with error message

3. **Unit** — `--yes` on non-TTY also auto-picks (not just interactive)
   - `resolveViaSearch_yesFlag_nonTTY_autoPicksFirst()`:
     - Given `opts.yes=true`, `isTTY()=false`, multiple results
     - When `resolveViaSearch` is called
     - Then install proceeds without exit 1

**Implementation** (within `resolveViaSearch` N-installable branch):
1. Check `opts.yes` flag before TTY check
2. If `opts.yes` → auto-select `installable[0]`, call `addCommand(path, opts)`, return
3. Print log message indicating auto-selection: `"Auto-selecting first result: owner/repo/skill"`
4. Add test cases using `vi.hoisted()` + `vi.mock` pattern for `searchSkills` and `isTTY`

**Dependencies**: T-002, T-003, T-005
**Coverage Target**: 90%
