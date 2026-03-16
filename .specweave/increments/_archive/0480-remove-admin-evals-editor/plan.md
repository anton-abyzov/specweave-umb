# Plan: Remove Admin Evals Editor

## Architecture Decision

No new architecture. This is a pure deletion increment removing dead code from vskill-platform.

## Impact Analysis

All targets confirmed to exist and are self-contained:

| Target | Type | Path |
|--------|------|------|
| Evals page | Directory | `src/app/admin/evals/` (page.tsx + __tests__/page.test.tsx) |
| Content route | File | `src/app/api/v1/admin/evals/content/route.ts` |
| Commit route | File | `src/app/api/v1/admin/evals/commit/route.ts` |
| Skills route | File | `src/app/api/v1/admin/evals/skills/route.ts` |
| Route tests | File | `src/app/api/v1/admin/evals/__tests__/routes.test.ts` |
| Eval content lib | File | `src/lib/github/eval-content.ts` |
| Eval content test | File | `src/lib/github/__tests__/eval-content.test.ts` |
| Nav entry | Line edit | `src/app/admin/layout.tsx` -- remove Evals from `NAV_ITEMS` |

**Dependency check**: `eval-content.ts` is imported only by `content/route.ts` and `commit/route.ts` (both deleted). No other source files reference `admin/evals`. Safe to delete everything.

## Implementation Strategy

1. Delete `src/app/admin/evals/` directory (page + test)
2. Delete `src/app/api/v1/admin/evals/` directory (3 routes + test)
3. Delete `src/lib/github/eval-content.ts`
4. Delete `src/lib/github/__tests__/eval-content.test.ts`
5. Edit `src/app/admin/layout.tsx` -- remove the Evals nav item from `NAV_ITEMS`
6. Verify: `npm run build` passes
7. Verify: `npx vitest run` passes

Steps 1-4 are independent directory/file deletions. Step 5 is a single-line edit. Steps 6-7 are verification gates.

## Risks

None. All deleted code is self-contained with no external consumers.

## Domain Delegation

No domain skills needed. The implementation is `rm -rf` + one line edit + build/test verification.
