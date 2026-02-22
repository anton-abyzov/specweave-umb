# Plan — 0321 Fix Skill Slugs

## Approach

Create a new `slug-migration.ts` module with the recomputation algorithm, and a new
admin endpoint `POST /api/v1/admin/recompute-slugs`. Keep it separate from existing
`migrateSkillSlugs()` (which is broken and reads from empty index blob).

## Algorithm

```
1. Fetch ALL Skill rows from Prisma
2. Partition: vendor (VENDOR_AUTO) → skip set; rest → work set
3. For work set, compute targetSlug = makeSlug("", displayName)
4. Group work set by (repoUrl, targetSlug) → detect duplicates
5. For each duplicate group: pick keeper (one with clean slug), mark others for deletion
6. Group unique skills by targetSlug → detect collisions
7. For each collision group:
   a. If one already holds the base slug → it keeps it
   b. Others: group by owner
      - Unique owner in group → assign owner-targetSlug
      - Same owner, different repos → assign owner-repo-targetSlug
8. Build rename plan: { id, oldSlug, newSlug }[]
9. Build delete plan: { id, slug }[]
10. If dryRun: return plans without executing
11. Execute in batches:
    a. Prisma: update Skill.name for renames, delete for duplicates
    b. KV: write new skill:{newSlug} keys, create alias for old slugs
```

## Files

| File | Action | Purpose |
|------|--------|---------|
| `src/lib/slug.ts` | EDIT | Add `extractOwner()`, `extractRepoName()` helpers |
| `src/lib/slug-migration.ts` | NEW | Core `recomputeSlugs()` algorithm |
| `src/lib/__tests__/slug-migration.test.ts` | NEW | Unit tests (TDD) |
| `src/app/api/v1/admin/recompute-slugs/route.ts` | NEW | Admin endpoint |

## Constraints

- Batch Prisma operations in groups of 100 (Workers CPU limit)
- KV writes are best-effort (if KV fails, DB rename still succeeds)
- Transaction not feasible for 4000+ rows on Workers — use idempotent batches instead
- Endpoint must be idempotent (safe to run multiple times)
