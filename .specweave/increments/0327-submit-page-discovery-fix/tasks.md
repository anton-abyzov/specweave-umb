# Tasks: Fix submit page skill discovery bug + remove selection step

## Task Notation

- `[T###]`: Task ID
- `[P]`: Parallelizable
- `[ ]`: Not started
- `[x]`: Completed
- Model hints: haiku (simple), sonnet (default), opus (complex)

## Phase 1: Error propagation in scanner

### T-001: Add error field to DiscoveryResult and propagate GitHub API errors

**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04 | **Status**: [x] completed

**Description**: Extend the `DiscoveryResult` interface with an optional `error` field and update `discoverSkillsEnhanced` to populate it when GitHub API calls fail instead of silently returning empty results.

**File**: `src/lib/scanner.ts`

**Implementation Details**:
1. Add `error?: { code: "rate_limited" | "auth_failed" | "api_error"; message: string }` to `DiscoveryResult` interface
2. In `discoverSkillsEnhanced`, update the tree-fetch path (the `if (!res.ok) return empty;` on ~line 453):
   - If `res.status === 403`: return `{ ...empty, error: { code: "rate_limited", message: "GitHub API rate limit exceeded. Please try again in a few minutes." } }`
   - If `res.status === 401`: return `{ ...empty, error: { code: "auth_failed", message: "GitHub authentication issue. Please try again later." } }`
   - For other non-ok responses: return `{ ...empty, error: { code: "api_error", message: "GitHub API error (HTTP ${res.status}). Please try again." } }`
3. In the marketplace path: if `fetchMarketplaceManifest` returns null (no marketplace), AND the tree-fetch fails, the error should propagate. The marketplace path already falls through to tree-based discovery, so the error detection on the tree path covers both cases.
4. The `catch` block at line 478 should also set an error field: `{ ...empty, error: { code: "api_error", message: "Failed to connect to GitHub API." } }`

**Test Plan**:
- **File**: `src/lib/__tests__/scanner-discovery.test.ts` (extend existing)
- **Tests**:
  - **TC-001**: Given GitHub tree API returns 403, When discoverSkillsEnhanced is called, Then result has `error.code === "rate_limited"` and `skills === []`
  - **TC-002**: Given GitHub tree API returns 401, When discoverSkillsEnhanced is called, Then result has `error.code === "auth_failed"` and `skills === []`
  - **TC-003**: Given GitHub tree API returns 500, When discoverSkillsEnhanced is called, Then result has `error.code === "api_error"` and `skills === []`
  - **TC-004**: Given GitHub tree API succeeds with skills, When discoverSkillsEnhanced is called, Then result has `error === undefined` (backward compat)

**Dependencies**: None
**Model hint**: sonnet

---

### T-002: Update discover route to map error field to HTTP 502

**User Story**: US-001 | **Satisfies ACs**: AC-US1-05, AC-US1-06, AC-US1-07 | **Status**: [x] completed

**Description**: Update the discover route to inspect `result.error` after calling `discoverSkillsEnhanced` and return 502 when present. Add console.warn for missing GITHUB_TOKEN.

**File**: `src/app/api/v1/submissions/discover/route.ts`

**Implementation Details**:
1. After resolving `githubToken`, add: `if (!githubToken) console.warn("GITHUB_TOKEN not configured -- using unauthenticated GitHub API calls");`
2. After `const result = await discoverSkillsEnhanced(repoUrl, githubToken);`, add:
   ```typescript
   if (result.error) {
     return NextResponse.json(
       { error: result.error.message, code: result.error.code },
       { status: 502 },
     );
   }
   ```
3. The existing flow for `result.skills` enrichment and 200 response remains unchanged for non-error cases.

**Test Plan**:
- **File**: `src/app/api/v1/submissions/discover/__tests__/route.test.ts` (extend existing)
- **Tests**:
  - **TC-005**: Given discoverSkillsEnhanced returns result with error field, When POST discover, Then returns 502 with error message and code
  - **TC-006**: Given discoverSkillsEnhanced returns result with no error and empty skills, When POST discover, Then returns 200 (backward compat)
  - **TC-007**: Given GITHUB_TOKEN is undefined (getCloudflareContext returns no token), When POST discover, Then console.warn is called with missing token message
  - **TC-008**: Given discoverSkillsEnhanced returns result with error, When POST discover, Then enrichment is NOT attempted (error short-circuits)

**Dependencies**: T-001
**Model hint**: sonnet

---

## Phase 2: Client-side simplification

### T-003: Remove select phase and dead code from submit page

**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-04, AC-US2-05, AC-US2-06, AC-US2-07, AC-US2-08, AC-US2-09, AC-US2-10 | **Status**: [x] completed

**Description**: Remove the "select" phase from the submit page, including all supporting state, functions, components, and styles.

**File**: `src/app/submit/page.tsx`

**Implementation Details**:
1. Change `Phase` type to `"input" | "discovering" | "submitting" | "done"`
2. Remove state variables: `selected` (line 49), `collapsed` (line 53)
3. Remove functions: `toggleSkill` (lines 197-204), `toggleAll` (lines 206-214), `togglePlugin` (lines 216-226), `toggleCollapse` (lines 228-234)
4. Remove `StatusBadge` component (lines 663-675)
5. Remove `btnSmall` style constant (lines 650-653)
6. Remove entire select rendering block (lines 351-516)
7. Update `reset()` to remove `setSelected(new Set())` and `setCollapsed(new Set())` references
8. Verify file is under 500 lines after cleanup

**Dependencies**: None (can be done in parallel with T-001/T-002)
**Model hint**: sonnet

---

### T-004: Rewrite handleDiscover to auto-submit after discovery

**User Story**: US-002, US-003 | **Satisfies ACs**: AC-US2-02, AC-US2-03, AC-US1-08 | **Status**: [x] completed

**Description**: After successful discovery, automatically trigger submission of all discovered skills instead of transitioning to the "select" phase.

**File**: `src/app/submit/page.tsx`

**Implementation Details**:
1. In `handleDiscover`, after setting `setDiscovered(skills)`:
   - Remove `setSelected(...)` call
   - Remove `setPhase("select")`
   - Instead, call `handleSubmitAll(skills)` directly (pass discovered skills as parameter)
   - Still set `setPlugins`, `setMarketplace`, `setTruncated` for done-phase display
2. Update the error check to display the specific error message from 502 responses:
   - The existing `data.error || Request failed (${res.status})` pattern already handles this correctly since the 502 response includes `{ error: "message" }`
3. Handle the 0-skills-no-error case: keep the "No SKILL.md files found" message for legitimate empty repos

**Dependencies**: T-003
**Model hint**: sonnet

---

### T-005: Rewrite handleSubmitAll to use individual submission endpoint

**User Story**: US-003, US-004 | **Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04, AC-US3-05, AC-US3-06, AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04 | **Status**: [x] completed

**Description**: Replace the bulk+legacy submission flow with a direct individual submission loop using `POST /api/v1/submissions`.

**File**: `src/app/submit/page.tsx`

**Implementation Details**:
1. Rewrite `handleSubmitAll` to accept `skills: DiscoveredSkill[]` parameter (called from handleDiscover)
2. Remove the bulk endpoint attempt (`/api/v1/submissions/bulk`) entirely
3. Remove the `handleSubmitAllLegacy` function (its logic becomes the main path)
4. For each skill, POST to `/api/v1/submissions` with `{ repoUrl, skillName: skill.name, skillPath: skill.path }`
5. Map response shapes to `SubmissionResult`:
   - `res.ok && data.alreadyVerified` -> `{ name, status: "already-verified" }`
   - `res.ok && data.duplicate` -> `{ name, id: data.id, status: "skipped" }`
   - `res.ok` (new submission) -> `{ name, id: data.id }`
   - `!res.ok` -> `{ name, error: data.error || HTTP ${res.status} }`
6. Update progress tracking: `setSubmitProgress(i + 1)` after each skill
7. On error during individual submission, continue to next skill (no early abort)
8. After all skills processed, `setPhase("done")`
9. Update the submitting phase progress display to use `discovered.length` instead of `selected.size`

**Dependencies**: T-003, T-004
**Model hint**: sonnet

---

## Phase 3: Testing and verification

### T-006: Run existing tests and verify no regressions

**User Story**: All | **Satisfies ACs**: All | **Status**: [x] completed

**Description**: Run the existing test suite to ensure no regressions from the changes.

**Implementation Details**:
1. Run `npm test` (or `npx vitest run`) in `repositories/anton-abyzov/vskill-platform/`
2. Verify all existing tests pass
3. Verify new tests from T-001 and T-002 pass
4. Verify page.tsx is under 500 lines: `wc -l src/app/submit/page.tsx`

**Test Plan**:
- All tests in `src/app/api/v1/submissions/discover/__tests__/route.test.ts` pass
- All tests in `src/lib/__tests__/scanner-discovery.test.ts` pass
- No other test files break

**Dependencies**: T-001, T-002, T-003, T-004, T-005
**Model hint**: haiku
