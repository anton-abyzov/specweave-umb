# Tasks: Fix stale mocks in versions API route tests (11 failing)

## Task Notation

- `[T###]`: Task ID
- `[ ]` not started | `[x]` completed

## US-001: Restore green test suite for versions API route

### T-001: Add `skill.findUnique` to hoisted `mockDb` in versions route test file

**User Story**: US-001 | **AC**: AC-US1-01, AC-US1-02 | **Status**: [ ] Not Started

**Description**: Extend the `vi.hoisted(() => ({ mockDb }))` block (around line 16) in `repositories/anton-abyzov/vskill-platform/src/app/api/v1/skills/[owner]/[repo]/[skill]/versions/__tests__/route.test.ts` to include a `skill.findUnique` mock that returns a default skill record. This aligns the test double with the route implementation at `versions/route.ts:15`, which calls `db.skill.findUnique({ where: { name: ... } })`.

**Implementation Details**:
- Edit only the `vi.hoisted()` `mockDb` block — do NOT modify individual tests, other files, or `route.ts`.
- Add:
  ```ts
  skill: {
    findUnique: vi.fn().mockResolvedValue({ id: "sk_1", name: "owner/repo/skill-name" }),
  },
  ```
- For any existing test that exercises the "skill not found" branch, add a local override: `mockDb.skill.findUnique.mockResolvedValueOnce(null)`.

**Test Plan (BDD)**:
- **File**: `repositories/anton-abyzov/vskill-platform/src/app/api/v1/skills/[owner]/[repo]/[skill]/versions/__tests__/route.test.ts`
- **TC-001**: Happy path — all 11 tests pass after mock fix
  - **Given** the test file at the path above has `skill.findUnique` added to the `vi.hoisted()` `mockDb` block
  - **When** `npx vitest run "src/app/api/v1/skills/[owner]/[repo]/[skill]/versions/__tests__/route.test.ts"` is executed from `repositories/anton-abyzov/vskill-platform`
  - **Then** the output shows 11 passed / 0 failed and contains no `TypeError: Cannot read properties of undefined (reading 'findUnique')`
- **TC-002**: Minimal diff — scope is constrained
  - **Given** the fix is applied
  - **When** `git diff` is inspected
  - **Then** only the `vi.hoisted()` `mockDb` block in `route.test.ts` is modified; no changes to individual test cases, to `route.ts`, or to any other file

**Dependencies**: None

## Phase: Verification

- [ ] [T-002] Run `npx vitest run "src/app/api/v1/skills/[owner]/[repo]/[skill]/versions/__tests__/route.test.ts"` from `repositories/anton-abyzov/vskill-platform` — confirm 11/11 passing, no `TypeError`.
