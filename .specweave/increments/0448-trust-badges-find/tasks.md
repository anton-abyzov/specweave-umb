# Tasks: Trust badges in vskill find output

## Task Notation

- `[T###]`: Task ID
- `[P]`: Parallelizable
- `[ ]`: Not started
- `[x]`: Completed
- Model hints: haiku (simple), opus (default)

## Phase 1: Platform - Trust Tier in Search API

### US-003: Platform API returns trustTier in search results (P1)

#### T-001: Ensure trustTier in Prisma Skill model and search select
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02 | **Status**: [x] completed

**Description**: Verify that `trustTier` column exists in Prisma schema and is included in `SEARCH_ENTRY_SELECT` for Postgres queries. Verify `SearchIndexEntry` type includes `trustTier` field for KV edge index.

**Implementation Details**:
- `prisma/schema.prisma`: Skill model has `trustTier String?` column
- `src/lib/search-index.ts`: `SEARCH_ENTRY_SELECT` includes `trustTier: true`
- `src/lib/search-index.ts`: `SearchIndexEntry` interface has `trustTier?: string`
- `src/lib/search-index.ts`: `buildSearchEntry()` maps `trustTier` with "T1" default
- `src/lib/search-index.ts`: `compactEntry()` omits trustTier when "T1" to save space

**Test Plan**:
- **File**: `src/lib/__tests__/search-index.test.ts`
- **Tests**:
  - **TC-001**: buildSearchEntry includes trustTier from skill record
    - Given a skill with trustTier "T3"
    - When buildSearchEntry is called
    - Then the entry has trustTier "T3"
  - **TC-002**: compactEntry omits trustTier "T1"
    - Given an entry with trustTier "T1"
    - When compactEntry is called
    - Then the output does not contain trustTier key
  - **TC-003**: compactEntry includes non-default trustTier
    - Given an entry with trustTier "T4"
    - When compactEntry is called
    - Then the output contains trustTier "T4"

**Dependencies**: None
**Status**: [x] Completed

---

#### T-002: Enrich blocked skills with trustTier "T0" in search route
**User Story**: US-003 | **Satisfies ACs**: AC-US3-03 | **Status**: [x] completed

**Description**: In the search API route's `enrichWithBlocklistAndRejected()` function, blocked skills must have `trustTier: "T0"` set alongside `isBlocked: true`.

**Implementation Details**:
- `src/app/api/v1/skills/search/route.ts`: `enrichWithBlocklistAndRejected()` spreads `trustTier: "T0"` on blocked results

**Test Plan**:
- **File**: `src/app/api/v1/skills/search/__tests__/route.test.ts`
- **Tests**:
  - **TC-004**: Blocked skills in search results have trustTier "T0"
    - Given a published skill that is on the blocklist
    - When the search API is called
    - Then the result has isBlocked=true and trustTier="T0"

**Dependencies**: T-001
**Status**: [x] Completed

---

#### T-003: Map trustTier in CLI API client
**User Story**: US-003 | **Satisfies ACs**: AC-US3-04 | **Status**: [x] completed

**Description**: The CLI's `searchSkills()` in `client.ts` must map `trustTier` from the raw API response object to `SkillSearchResult.trustTier`.

**Implementation Details**:
- `src/api/client.ts`: `SkillSearchResult` interface has `trustTier?: string`
- `src/api/client.ts`: `searchSkills()` maps `trustTier: s.trustTier ? String(s.trustTier) : undefined`

**Test Plan**:
- **File**: `src/commands/find.test.ts`
- **Tests**:
  - **TC-005**: Search results with trustTier are passed through to find command
    - Given mock searchSkills returns a result with trustTier "T3"
    - When findCommand renders in non-TTY mode
    - Then the output contains "T3" in the tab-separated line

**Dependencies**: None (parallel with T-001)
**Status**: [x] Completed

## Phase 2: CLI - Badge Rendering

### US-001: See trust badges in find results (P1)

#### T-004: Implement getTrustBadge() function
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-06 | **Status**: [x] completed

**Description**: Create the `getTrustBadge(trustTier)` function in `find.ts` that maps trust tier strings to colored ANSI badge strings.

**Implementation Details**:
- `src/commands/find.ts`: `getTrustBadge()` switch on trustTier:
  - T4 -> green checkmark "certified"
  - T3 -> cyan checkmark "verified"
  - T2 -> yellow "? maybe"
  - T1 -> dim "? maybe"
  - default -> "" (empty)

**Test Plan**:
- **File**: `src/commands/find.test.ts`
- **Tests**:
  - **TC-006**: T4 trust tier displays green "certified" badge
    - Given a skill with trustTier "T4"
    - When rendered in TTY mode
    - Then output contains checkmark + "certified"
  - **TC-007**: T3 trust tier displays cyan "verified" badge
    - Given a skill with trustTier "T3"
    - When rendered in TTY mode
    - Then output contains checkmark + "verified"
  - **TC-008**: T2 trust tier displays yellow "? maybe" badge
    - Given a skill with trustTier "T2"
    - When rendered in TTY mode
    - Then output contains "? maybe"
  - **TC-009**: T1 trust tier displays dim "? maybe" badge
    - Given a skill with trustTier "T1"
    - When rendered in TTY mode
    - Then output contains "? maybe"
  - **TC-010**: Undefined trust tier shows no badge
    - Given a skill with no trustTier
    - When rendered in TTY mode
    - Then output does not contain "certified", "verified", or "? maybe"

**Dependencies**: T-003
**Status**: [x] Completed

---

#### T-005: Integrate badge into TTY output line
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-05 | **Status**: [x] completed

**Description**: In the TTY rendering loop, append the trust badge after the star count. Blocked skills use existing BLOCKED rendering and skip the badge.

**Implementation Details**:
- `src/commands/find.ts` TTY block:
  - Call `getTrustBadge(r.trustTier)` for non-blocked skills
  - Append badge after starsStr with 2-space separator (only if badge is non-empty)
  - Blocked skills continue to use red BLOCKED + threat info rendering

**Test Plan**:
- **File**: `src/commands/find.test.ts`
- **Tests**:
  - **TC-011**: Blocked skills show BLOCKED, not trust badge
    - Given a blocked skill with trustTier "T0"
    - When rendered in TTY mode
    - Then output contains "BLOCKED" and does NOT contain "certified"/"verified"/"maybe"

**Dependencies**: T-004
**Status**: [x] Completed

### US-002: Trust tier in non-TTY and JSON output (P1)

#### T-006: Include trustTier in non-TTY tab-separated output
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-03 | **Status**: [x] completed

**Description**: In the non-TTY (piped) output path, include `trustTier` as the 4th tab-separated column for non-blocked skills. Blocked skills continue to use the existing `name\trepo\tBLOCKED` format.

**Implementation Details**:
- `src/commands/find.ts` non-TTY block:
  - Non-blocked line format: `${name}\t${repo}\t${stars}\t${trustTier}\t${pluginName}\t${altRepos}`
  - Blocked line format: `${name}\t${repo}\tBLOCKED` (unchanged)

**Test Plan**:
- **File**: `src/commands/find.test.ts`
- **Tests**:
  - **TC-012**: Non-TTY output includes trustTier as 4th column
    - Given a skill with trustTier "T3"
    - When rendered in non-TTY mode
    - Then the tab-separated line has "T3" in position 4
  - **TC-013**: Non-TTY blocked output uses BLOCKED as 3rd column
    - Given a blocked skill
    - When rendered in non-TTY mode
    - Then the line ends with "BLOCKED" (no trustTier column)

**Dependencies**: T-003
**Status**: [x] Completed

---

#### T-007: Verify JSON output preserves trustTier
**User Story**: US-002 | **Satisfies ACs**: AC-US2-02 | **Status**: [x] completed

**Description**: The `--json` output path spreads all `SkillSearchResult` fields into the JSON array. Verify trustTier is preserved.

**Implementation Details**:
- `src/commands/find.ts` JSON block: `const enriched = results.map(r => ({ ...r, vskillInstalls: r.vskillInstalls ?? 0 }))`
- trustTier is preserved via spread operator (no explicit mapping needed)

**Test Plan**:
- **File**: `src/commands/find.test.ts`
- **Tests**:
  - **TC-014**: JSON output contains trustTier field
    - Given a skill with trustTier "T4" and --json flag
    - When findCommand is called
    - Then JSON output contains alternateRepos and trustTier fields (already tested via existing JSON tests)

**Dependencies**: T-003
**Status**: [x] Completed

## Phase 3: Verification

#### T-008: Run full test suite
**User Story**: US-001, US-002 | **Satisfies ACs**: All | **Status**: [x] completed

**Description**: Execute `npx vitest run src/commands/find.test.ts` to verify all trust badge tests pass.

**Test Plan**:
- All TC-001 through TC-014 pass
- No regressions in existing find command tests

**Dependencies**: T-004, T-005, T-006, T-007
**Status**: [x] Completed
