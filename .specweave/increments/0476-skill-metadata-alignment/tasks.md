---
increment: 0476-skill-metadata-alignment
generated_by: sw:test-aware-planner
by_user_story:
  US-001: [T-001, T-002]
  US-002: [T-003]
  US-003: [T-004, T-005]
total_tasks: 5
---

# Tasks: Fix stale/inconsistent skill metadata display

## User Story: US-001 - Accurate repo health badge

**Linked ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05
**Tasks**: 2 total, 2 completed

---

### T-001: Add UNKNOWN status to repo health type and checker

**User Story**: US-001
**Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-05
**Status**: [x] completed

**Test Plan**:
- **Given** the repo health checker calls the GitHub API
- **When** the response status is 404
- **Then** the result status is `OFFLINE`
- **When** the response status is 403, 429, or 5xx
- **Then** the result status is `UNKNOWN`
- **When** a network error or timeout occurs
- **Then** the result status is `UNKNOWN` with 300s TTL (same as OFFLINE)

**Test Cases**:
1. **Unit**: `src/lib/__tests__/repo-health-checker.test.ts`
   - Update TC-011: network error now asserts `UNKNOWN` (was `OFFLINE`)
   - Update TC-013: 403 response now asserts `UNKNOWN` (was `OFFLINE`)
   - Add TC-014: 429 response returns `UNKNOWN`
   - Add TC-015: 500 response returns `UNKNOWN`
   - Keep TC-010: 404 still returns `OFFLINE`
   - **Coverage Target**: 95%

**Implementation**:
1. `src/lib/repo-health-store.ts`: add `"UNKNOWN"` to `RepoHealthResult.status` union; set `UNKNOWN` TTL to `OFFLINE_TTL_SECONDS` (300s)
2. `src/lib/repo-health-checker.ts`: change `checkRepoHealth` so only `res.status === 404` maps to `OFFLINE`; all other non-ok responses return `UNKNOWN`; catch block returns `UNKNOWN` instead of `OFFLINE`; keep non-GitHub URL path returning `OFFLINE`
3. `src/app/api/v1/skills/[owner]/[repo]/[skill]/repo-health/route.ts`: change `getCloudflareContext` fallback from `OFFLINE` to `UNKNOWN`
4. Run `npx vitest run src/lib/__tests__/repo-health-checker.test.ts`

---

### T-002: Hide badge for UNKNOWN status in RepoHealthBadge

**User Story**: US-001
**Satisfies ACs**: AC-US1-04
**Status**: [x] completed

**Test Plan**:
- **Given** a cached `UNKNOWN` status is returned for a skill
- **When** the RepoHealthBadge component renders
- **Then** the component returns null and renders nothing

**Test Cases**:
1. **Unit**: `src/app/skills/[owner]/[repo]/[skill]/__tests__/RepoHealthBadge.test.tsx`
   - testUnknownStatusRendersNull(): mock status `UNKNOWN`, assert component renders null
   - **Coverage Target**: 90%

**Implementation**:
1. `src/app/skills/[owner]/[repo]/[skill]/RepoHealthBadge.tsx`: add early return `null` when `status === "UNKNOWN"`
2. Verify existing null-return path for falsy status is preserved
3. Run `npx vitest run` scoped to badge test

---

## User Story: US-002 - Complete eval verdict chip mapping

**Linked ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05, AC-US2-06
**Tasks**: 1 total, 1 completed

---

### T-003: Fix verdict-to-status mapping and scanColor for all five EvalVerdict values

**User Story**: US-002
**Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05, AC-US2-06
**Status**: [x] completed

**Test Plan**:
- **Given** a skill with `evalVerdict = "EFFECTIVE"`
- **When** the ScanChip renders
- **Then** status is `PASS` (green)
- **Given** a skill with `evalVerdict = "MARGINAL"`
- **When** the ScanChip renders
- **Then** status is `WARN` (amber)
- **Given** a skill with `evalVerdict = "INEFFECTIVE"`
- **When** the ScanChip renders
- **Then** status is `NEUTRAL` (gray)
- **Given** a skill with `evalVerdict = "DEGRADING"`
- **When** the ScanChip renders
- **Then** status is `FAIL` (red)
- **Given** a skill with `evalVerdict = "ERROR"`
- **When** the ScanChip renders
- **Then** status is `ERROR` (red)
- **Given** `scanColor` is called with `WARN`, `NEUTRAL`, or `ERROR`
- **Then** returns `#F59E0B`, `#6B7280`, `#EF4444` respectively

**Test Cases**:
1. **Unit**: `src/app/skills/[owner]/[repo]/[skill]/__tests__/page.test.tsx`
   - Add TC-016: `scanColor("WARN")` returns `#F59E0B`
   - Add TC-017: `scanColor("NEUTRAL")` returns `#6B7280`
   - Add TC-018: `scanColor("ERROR")` returns `#EF4444`
   - Add TC-019: `VERDICT_TO_STATUS` maps all five verdicts correctly
   - **Coverage Target**: 90%

**Implementation**:
1. `src/app/skills/[owner]/[repo]/[skill]/page.tsx`: replace inline ternary on line ~348 with a `VERDICT_TO_STATUS` lookup object: `{ EFFECTIVE: "PASS", MARGINAL: "WARN", INEFFECTIVE: "NEUTRAL", DEGRADING: "FAIL", ERROR: "ERROR" }`
2. Add `WARN: "#F59E0B"`, `NEUTRAL: "#6B7280"`, `ERROR: "#EF4444"` entries to `scanColor`
3. Run `npx vitest run` scoped to page tests

---

## User Story: US-003 - Eval freshness timestamp

**Linked ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04
**Tasks**: 2 total, 2 completed

---

### T-004: Await Skill DB update in eval-store and propagate failures

**User Story**: US-003
**Satisfies ACs**: AC-US3-03, AC-US3-04
**Status**: [x] completed

**Test Plan**:
- **Given** `storeEvalRun` executes and the Skill DB update fails
- **When** the function runs
- **Then** the error is logged and re-thrown (not swallowed silently)
- **Given** the KV write fails but the DB update succeeds
- **When** the function runs
- **Then** `evalRun.id` is still returned (KV stays fire-and-forget)

**Test Cases**:
1. **Unit**: `src/lib/eval/__tests__/eval-store.test.ts`
   - Add TC-020: mock `db.skill.update` to reject; assert `storeEvalRun` throws
   - Add TC-021: mock KV write to reject; assert `storeEvalRun` resolves with `evalRun.id`
   - **Coverage Target**: 90%

**Implementation**:
1. `src/lib/eval/eval-store.ts`: replace fire-and-forget `.catch()` on lines ~101-114 with `await db.skill.update(...)` inside try/catch that logs and re-throws
2. Leave KV write (lines ~117-143) as fire-and-forget
3. Run `npx vitest run src/lib/eval`

---

### T-005: Display lastEvalAt freshness timestamp on skill detail page

**User Story**: US-003
**Satisfies ACs**: AC-US3-01, AC-US3-02
**Status**: [x] completed

**Test Plan**:
- **Given** a skill with `lastEvalAt` set to a non-null date
- **When** the eval section renders
- **Then** a relative timestamp (e.g., "3d ago") appears inline after the run count
- **Given** a skill with `lastEvalAt` is null (never evaluated)
- **When** the eval section renders
- **Then** no freshness timestamp is shown

**Test Cases**:
1. **Unit**: `src/app/skills/[owner]/[repo]/[skill]/__tests__/page.test.tsx`
   - testFreshnessTimestampShown(): render with non-null `lastEvalAt`, assert relative timestamp visible after run count
   - testFreshnessTimestampHidden(): render with `lastEvalAt = null`, assert no timestamp in output
   - **Coverage Target**: 90%

**Implementation**:
1. `src/app/skills/[owner]/[repo]/[skill]/page.tsx`: add `lastEvalAt` freshness inline after run count using existing `formatTimeAgo` helper; conditionally render only when `lastEvalAt` is non-null
2. Run `npx vitest run` scoped to page tests
3. Manual verification gate: inspect skill detail page for a skill with eval data to confirm timestamp renders correctly
