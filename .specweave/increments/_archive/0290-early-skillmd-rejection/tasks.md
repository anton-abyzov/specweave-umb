# Tasks: Reject submissions early when SKILL.md is missing

## Task Notation

- `[T###]`: Task ID
- `[P]`: Parallelizable
- `[ ]`: Not started
- `[x]`: Completed
- Model hints: haiku (simple), sonnet (default), opus (complex)

## Phase 1: Core Implementation

### US-001: Early SKILL.md validation on public submissions (P1)

#### T-001: Add checkSkillMdExists() function to scanner.ts

**Description**: Add a new exported function `checkSkillMdExists(repoUrl, skillPath?)` to `src/lib/scanner.ts` that performs a lightweight HTTP fetch against raw.githubusercontent.com to verify SKILL.md exists. Tries main then master branch. Returns `true` if found (200), `false` if both branches 404, `true` (fail-open) on network errors/timeouts.

**References**: AC-US1-02, AC-US1-03, AC-US2-01, AC-US2-02

**Implementation Details**:
- Parse owner/repo from repoUrl using existing regex pattern
- Use `skillPath || "SKILL.md"` as the target file
- Try `https://raw.githubusercontent.com/{owner}/{repo}/main/{path}` first
- If 404, try master branch
- Use `AbortSignal.timeout(5000)` for fast failure
- On any fetch error (network, timeout), return `true` (fail-open)
- Return `false` only when both branches return 404

**Test Plan**:
- **File**: `src/lib/__tests__/scanner-check-skillmd.test.ts`
- **Tests**:
  - **TC-001**: Returns true when SKILL.md exists on main branch
    - Given a valid repoUrl and fetch returns 200 for main branch
    - When checkSkillMdExists is called
    - Then it returns true
  - **TC-002**: Returns true when SKILL.md exists on master branch (main is 404)
    - Given fetch returns 404 for main, 200 for master
    - When checkSkillMdExists is called
    - Then it returns true
  - **TC-003**: Returns false when SKILL.md is missing on both branches
    - Given fetch returns 404 for both main and master
    - When checkSkillMdExists is called
    - Then it returns false
  - **TC-004**: Returns true (fail-open) on network error
    - Given fetch throws a network error
    - When checkSkillMdExists is called
    - Then it returns true
  - **TC-005**: Returns true (fail-open) on timeout
    - Given fetch throws an AbortError (timeout)
    - When checkSkillMdExists is called
    - Then it returns true
  - **TC-006**: Uses custom skillPath when provided
    - Given skillPath is "plugins/foo/SKILL.md" and fetch returns 200
    - When checkSkillMdExists is called with that skillPath
    - Then it fetches the custom path instead of root SKILL.md
  - **TC-007**: Returns false for invalid repoUrl
    - Given repoUrl is "not-a-github-url"
    - When checkSkillMdExists is called
    - Then it returns false

**Dependencies**: None
**Status**: [x] Completed

---

#### T-002: Integrate pre-check into POST /api/v1/submissions route

**Description**: Add the SKILL.md existence pre-check to the POST handler in `src/app/api/v1/submissions/route.ts`. The check runs after body validation and dedup check but before `createSubmission()`. Only for non-internal requests. Returns 422 if SKILL.md is missing.

**References**: AC-US1-01, AC-US1-04

**Implementation Details**:
- Import `checkSkillMdExists` from `@/lib/scanner`
- After the dedup check block (line ~197), before the `getCloudflareContext` for queue setup
- Guard with `if (!isInternal)` to skip for crawler/admin requests
- Call `const skillMdExists = await checkSkillMdExists(repoUrl!, skillPath)`
- If `!skillMdExists`, return 422 with descriptive error
- If `skillMdExists` or error (fail-open), continue normal flow

**Test Plan**:
- **File**: `src/app/api/v1/submissions/__tests__/route.skillmd-check.test.ts`
- **Tests**:
  - **TC-008**: Returns 422 when SKILL.md is missing for public submission
    - Given checkSkillMdExists returns false
    - When POST is made with valid repoUrl and skillName
    - Then response is 422 with error mentioning SKILL.md
    - And createSubmission is NOT called
  - **TC-009**: Returns 201 when SKILL.md exists for public submission
    - Given checkSkillMdExists returns true
    - When POST is made with valid repoUrl and skillName
    - Then response is 201 and submission is created normally
  - **TC-010**: Bypasses check for internal requests
    - Given X-Internal-Key header matches INTERNAL_BROADCAST_KEY
    - When POST is made
    - Then checkSkillMdExists is NOT called
    - And submission proceeds normally
  - **TC-011**: Proceeds normally when checkSkillMdExists fails (fail-open)
    - Given checkSkillMdExists returns true (fail-open on error)
    - When POST is made
    - Then submission is created normally (not blocked)

**Dependencies**: T-001
**Status**: [x] Completed

---

## Phase 2: Verification

#### T-003: Run full test suite and verify no regressions

**Description**: Run all existing tests in the vskill-platform project to ensure the changes don't break anything. Pay special attention to `process-submission.test.ts` (SKILL.md missing test), `route.dedup.test.ts`, and `route.pagination.test.ts`.

**References**: AC-US1-05

**Implementation Details**:
- Run `npm test` from vskill-platform root
- Verify the "rejects when SKILL.md is missing" test in process-submission.test.ts still passes
- Verify all dedup tests still pass
- Verify no import resolution issues

**Test Plan**:
- Full test suite passes with 0 failures

**Dependencies**: T-001, T-002
**Status**: [x] Completed
