# Tasks: Fix submission published-skill link collision

## Overview

7 tasks across 3 phases (RED → GREEN → REFACTOR/verify). All work in `repositories/anton-abyzov/vskill-platform/`. TDD discipline: every implementation task is preceded by a failing-test task.

## Phase 1: TDD RED — write failing tests

### T-001: Add failing test — getSubmissionFull returns publishedSkillName
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01, AC-US3-01 | **Status**: [x] completed

**Description**: Add a vitest case in `src/lib/__tests__/data-submission-full.test.ts` (new file) covering `getSubmissionFull` returning `publishedSkillName` when `submission.skillId` is set, and `null` when it isn't.

**Test Plan** (Given/When/Then):
- **TC-001a — published submission**: Given a Submission row with `skillId = "sk_123"` and an existing Skill `{id: "sk_123", name: "anton-abyzov/greet-anton/greet-anton-abyzov"}`, When `getSubmissionFull(id)` resolves, Then the result has `publishedSkillName === "anton-abyzov/greet-anton/greet-anton-abyzov"`.
- **TC-001b — unpublished submission**: Given a Submission with `skillId = null`, When `getSubmissionFull(id)` resolves, Then `publishedSkillName === null`.

Mock the Prisma client via `vi.hoisted()` + `vi.mock("@/lib/db", ...)`. Test must FAIL initially (function does not yet return the field).

---

### T-002: Add failing test — submission API exposes publishedSkillName
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02, AC-US3-02 | **Status**: [x] completed

**Description**: Add a vitest case in `src/app/api/v1/submissions/[id]/__tests__/route.test.ts` (new file or extend existing) that mocks `getSubmissionFull` to return `publishedSkillName: "owner/repo/skill"` and asserts the JSON response body includes that field verbatim.

**Test Plan**:
- **TC-002 — API surfaces publishedSkillName**: Given `getSubmissionFull(id)` returns `{ submission: {...}, scanResult, stateHistory, publishedSkillName: "anton-abyzov/greet-anton/greet-anton-abyzov" }`, When `GET /api/v1/submissions/[id]` is called, Then the JSON body includes `publishedSkillName === "anton-abyzov/greet-anton/greet-anton-abyzov"`.

Test must FAIL initially.

---

### T-003: Add failing test — legacy-redirect refuses ambiguous match
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US3-03 | **Status**: [x] completed

**Description**: Add a vitest case in `src/app/api/v1/legacy-redirect/[slug]/__tests__/route.test.ts` (new file) covering all three branches.

**Test Plan**:
- **TC-003a — single match**: Given `db.skill.findMany` returns one row, When `GET /api/v1/legacy-redirect/<slug>`, Then 301 redirect to `/skills/<owner>/<repo>/<skill>`.
- **TC-003b — zero matches**: Given `findMany` returns `[]`, When the route is called, Then 404 (no `X-Legacy-Ambiguous` header).
- **TC-003c — ambiguous match**: Given `findMany` returns 2 rows, When the route is called, Then 404 with `X-Legacy-Ambiguous: true` response header.

Test must FAIL initially (current handler uses `findFirst`, no ambiguity branch).

---

## Phase 2: TDD GREEN — implement

### T-004: Extend getSubmissionFull to include publishedSkillName
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 | **Status**: [x] completed

**Description**: Modify `src/lib/data.ts` `getSubmissionFull(id)` so the returned object includes `publishedSkillName: string | null`. Use the existing Prisma `submission` fetch with an `include: { skill: { select: { name: true } } }` clause; if the function reads from KV/in-memory store rather than Prisma, do a follow-up `db.skill.findUnique({ where: { id: submission.skillId }, select: { name: true } })` only when `skillId` is truthy.

**Implementation Details**:
- Update the function's return-type annotation.
- Set `publishedSkillName = submission.skill?.name ?? null` (or equivalent for the chosen fetch path).
- Make TC-001a + TC-001b pass.

**Test**: `npx vitest run src/lib/__tests__/data-submission-full.test.ts`

---

### T-005: Surface publishedSkillName in /api/v1/submissions/[id]
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02 | **Status**: [x] completed

**Description**: Modify `src/app/api/v1/submissions/[id]/route.ts` to add `publishedSkillName: data.publishedSkillName` to the JSON response object (alongside `skillName` at line 58). Preserve all existing fields and `Cache-Control: no-cache` header.

**Test**: `npx vitest run src/app/api/v1/submissions/[id]/__tests__/route.test.ts` — TC-002 passes.

---

### T-006: Submit page prefers publishedSkillName for the View link
**User Story**: US-001 | **Satisfies ACs**: AC-US1-03, AC-US1-04 | **Status**: [x] completed

**Description**: In `src/app/submit/[id]/page.tsx`, replace the `href={skillUrl(data.skillName)}` at line 647 with:
```tsx
href={skillUrl(data.publishedSkillName ?? data.skillName)}
```
This relies on `skillUrl()` already handling both 3-segment and flat names. When `publishedSkillName` is set, the URL is canonical; when null, behaviour matches today.

**Test Plan**:
- **TC-006 — page renders canonical href**: render the published branch with mocked fetch returning `publishedSkillName: "owner/repo/skill"`; assert anchor `href === "/skills/owner/repo/skill"`. Add to existing page test file or `src/app/submit/[id]/__tests__/page.test.tsx` (whichever exists; create if not).

**Test**: `npx vitest run src/app/submit/[id]/__tests__/`

---

### T-007: Legacy-redirect handler refuses ambiguous match
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02 | **Status**: [x] completed

**Description**: Modify `src/app/api/v1/legacy-redirect/[slug]/route.ts`:
- Replace `db.skill.findFirst({...})` with `db.skill.findMany({ where: {...}, take: 2, select: { ownerSlug: true, repoSlug: true, skillSlug: true, name: true } })`.
- Branch on `matches.length`:
  - `0` → return 404 (existing behaviour).
  - `1` → use `matches[0]` for the existing canonical-URL build + 301 redirect.
  - `>= 2` → return `new Response("Not Found", { status: 404, headers: { "X-Legacy-Ambiguous": "true" } })`.
- Catch path (DB error) unchanged: 503.

**Test**: `npx vitest run src/app/api/v1/legacy-redirect/[slug]/__tests__/route.test.ts` — TC-003a/b/c pass.

---

## Phase 3: REFACTOR + verify

### T-008: Run full suite + manual verify
**User Story**: US-003 | **Satisfies ACs**: all | **Status**: [x] completed

**Description**:
- Run `npx vitest run` from `repositories/anton-abyzov/vskill-platform/` — must be green.
- After deploy, manually visit the production submission `sub_8f8f75d7-67b6-4357-9dd1-1d46d87bacf0?from=queue` and click "View published skill". Confirm it lands on the user's actual skill page (or 404, never an unrelated skill).

**Test**: full vitest suite green; manual repro confirms the user's reported bug is gone.
