# Implementation Plan: Fix stale mocks in versions API route tests (11 failing)

## Approach: extend hoisted mock to include `db.skill.findUnique`

The route at `repositories/anton-abyzov/vskill-platform/src/app/api/v1/skills/[owner]/[repo]/[skill]/versions/route.ts:15` calls `db.skill.findUnique({ where: { name: ... } })`. The test file's `vi.hoisted(() => ({ mockDb }))` block (around line 16 of `route.test.ts`) only declares `db.skillVersion`, so `db.skill` resolves to `undefined` and every test throws `TypeError: Cannot read properties of undefined (reading 'findUnique')`.

Fix — add to the hoisted `mockDb` block:

```ts
skill: {
  findUnique: vi.fn().mockResolvedValue({ id: "sk_1", name: "owner/repo/skill-name" }),
},
```

Tests that need the "skill not found" branch use `mockDb.skill.findUnique.mockResolvedValueOnce(null)` per-case.

## Scope

- **Files modified**: 1 — `repositories/anton-abyzov/vskill-platform/src/app/api/v1/skills/[owner]/[repo]/[skill]/versions/__tests__/route.test.ts`
- **Files created**: 0
- **Production code changes**: none (`route.ts` is correct)
- **Architecture changes**: none
- **New dependencies**: none

## Verification

```
cd repositories/anton-abyzov/vskill-platform
npx vitest run "src/app/api/v1/skills/[owner]/[repo]/[skill]/versions/__tests__/route.test.ts"
```

Expected: 11/11 passing, no `TypeError`.
