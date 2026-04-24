---
increment: 0692-remove-dead-mockgetskillbyname-wiring
---

# Plan: Remove dead `getSkillByName` mock wiring

## Approach

Deletion-only single-file edit. No architectural decision needed — the wiring is provably dead because the route it used to test no longer imports `getSkillByName`.

## Target file

`repositories/anton-abyzov/vskill-platform/src/app/api/v1/skills/[owner]/[repo]/[skill]/versions/__tests__/route.test.ts`

## Deletions (applied sequentially via `Edit` tool)

1. **L15** — remove hoisted declaration:
   ```ts
   const mockGetSkillByName = vi.hoisted(() => vi.fn());
   ```
2. **L27-29** — remove `vi.mock("@/lib/data", ...)` block:
   ```ts
   vi.mock("@/lib/data", () => ({
     getSkillByName: mockGetSkillByName,
   }));
   ```
3. **L96** — remove `beforeEach` initialization:
   ```ts
   mockGetSkillByName.mockResolvedValue(SKILL);
   ```
4. **L142** — remove from list-endpoint 404 test:
   ```ts
   mockGetSkillByName.mockResolvedValue(null);
   ```
5. **L183** — remove from detail-endpoint 404 test:
   ```ts
   mockGetSkillByName.mockResolvedValue(null);
   ```

## No additional code to read or imports to remove

Confirmed on HEAD: the file has **no top-level import** of `@/lib/data` — only the `vi.mock()` declaration references it. After removing the `vi.mock` block, no further cleanup is needed.

## Why this is safe

Both 404 tests (at L142 and L183 pre-edit) already drive the not-found path through `mockDb.skill.findUnique.mockResolvedValueOnce(null)` on the adjacent line. The route implementation at `versions/route.ts:14-15` never calls the function these mocks pretended to override, so removing them cannot change test behavior.

## Out of scope

- No changes to `route.ts` or `[version]/route.ts`
- No changes to other test files
- No refactoring of the remaining mock setup pattern (the `mockDb` hoisted block stays as-is)
