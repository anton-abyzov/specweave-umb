# Tasks: Fix `/versions/diff` 502 Bad Gateway

> Strict TDD per `.specweave/config.json`. Each task is RED → GREEN → REFACTOR.
> All paths relative to `repositories/anton-abyzov/vskill-platform/`.

## Phase 1 — Diff route adapter

### T-001: RED — failing test for the new diff route
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01 | **Status**: [x] completed
**Test Plan (BDD)**:
- **Given** no file at `src/app/api/v1/skills/[owner]/[repo]/[skill]/versions/diff/route.ts`
- **When** vitest imports the test file `versions/diff/__tests__/route.test.ts`
- **Then** every test in the suite fails (file-not-found at import time)
- **Test file**: `src/app/api/v1/skills/[owner]/[repo]/[skill]/versions/diff/__tests__/route.test.ts` (NEW)
- **Cases**:
  1. happy path — both versions exist, GitHub diff → returns `{from, to, diffSummary, contentDiff}` with non-empty `contentDiff`
  2. local-content fallback — non-GitHub repoUrl → returns same shape with LCS-derived `contentDiff`
  3. missing `from` query param → 400
  4. malformed `from` value (e.g. `not-a-version`) → 400
  5. skill not found → 404
  6. version not found → 400
- **RED**: import of `../route` throws ENOENT; vitest reports import-error suite-failure.

### T-002: GREEN — implement diff route as compare adapter
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05, AC-US1-06, AC-US1-07 | **Status**: [x] completed
**Test Plan (BDD)**:
- **Given** the failing tests from T-001
- **When** I add `src/app/api/v1/skills/[owner]/[repo]/[skill]/versions/diff/route.ts` that:
  1. Calls the compare route's `GET` handler
  2. Returns the compare response unchanged on non-2xx
  3. On 2xx: extracts `files`, picks SKILL.md (or first), maps `patch` → `contentDiff`
  4. Looks up `diffSummary` for the `to` row from the DB
  5. Returns `{ from, to, diffSummary, contentDiff }`
- **Then** all 6 cases in T-001 pass
- **Files added**: `src/app/api/v1/skills/[owner]/[repo]/[skill]/versions/diff/route.ts`

## Phase 2 — Cleanup

### T-003: REFACTOR — remove dead /diff branch from versions/route.ts
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02 | **Status**: [x] completed
**Test Plan (BDD)**:
- **Given** `versions/route.ts` contains the unreachable `if (url.pathname.endsWith("/diff"))` branch and the `handleDiff` / `computeSimpleDiff` / `positionalDiff` functions
- **When** those four pieces are deleted and any now-unused imports pruned
- **Then** existing tests in `versions/__tests__/route.test.ts` (if present) and the rest of the test suite still pass
- **Files modified**: `src/app/api/v1/skills/[owner]/[repo]/[skill]/versions/route.ts`

### T-004: VERIFY — full suite passes
**User Story**: US-003 | **Satisfies ACs**: AC-US3-02, AC-US3-03 | **Status**: [x] completed
**Test Plan (BDD)**:
- **Given** T-001/T-002/T-003 are GREEN
- **When** I run `npx vitest run` in `repositories/anton-abyzov/vskill-platform/`
- **And** `npx vitest run src/eval-server` in `repositories/anton-abyzov/vskill/`
- **Then** every test passes; no skipped/todo'd tests left behind
- **No files modified** — pure verification.

### T-005: VERIFY — manual studio repro
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US1-02 | **Status**: [x] completed
> Verified by Playwright (`test-fetch-diff.mjs`): commit 7b37b5a deployed; studio proxy on a fresh test instance hit `/api/skills/mobile/appstore/versions/diff?from=1.0.0&to=1.0.1` → HTTP 200 with `{from, to, diffSummary, contentDiff}` shape and a real unified-patch body. The 502 is gone.
**Test Plan (BDD)**:
- **Given** the platform changes are deployed (or local dev server running on the same port the studio's PLATFORM_BASE points at)
- **When** I open Skill Studio's Versions tab on a real skill with ≥2 versions and click two version rows
- **Then** the diff viewer renders below the timeline (no 502 in the network panel) and the content panel shows a unified patch.
- **No files modified** — pure verification.
