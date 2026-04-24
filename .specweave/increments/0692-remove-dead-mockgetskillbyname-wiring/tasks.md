# Tasks: Remove dead `getSkillByName` mock wiring

## US-001: Remove dead mock wiring

### T-001: Apply 5 surgical deletions + verify

**User Story**: US-001 | **AC**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04 | **Project**: vskill-platform | **Status**: [x] Completed

**Description**: Apply the five deletions described in plan.md to `repositories/anton-abyzov/vskill-platform/src/app/api/v1/skills/[owner]/[repo]/[skill]/versions/__tests__/route.test.ts` via sequential `Edit` tool calls. Do not modify any other file.

**Test Plan (BDD)**:
- **Given** the test file currently has 5 references to `mockGetSkillByName` and one `vi.mock("@/lib/data", ...)` block
- **When** the 5 deletions from plan.md are applied
- **Then** `grep -c "getSkillByName\|@/lib/data" route.test.ts` returns `0`
- **And** `npx vitest run "src/app/api/v1/skills/[owner]/[repo]/[skill]/versions/__tests__/route.test.ts"` returns 11 passed / 0 failed
- **And** `git diff` on the test file shows only `-` lines (no `+` lines with content)

**Files**: `repositories/anton-abyzov/vskill-platform/src/app/api/v1/skills/[owner]/[repo]/[skill]/versions/__tests__/route.test.ts`

**Dependencies**: None
