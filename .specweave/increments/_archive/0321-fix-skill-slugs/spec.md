---
status: completed
---
# 0321 — Fix Skill Slugs: Recompute All from DisplayName

## Problem

77.5% of skills (3,977 of 5,131) have incorrect slugs with `owner-repo-skillname` format
(e.g., `dirnbauer-webconsulting-skills-ipados-design` instead of `ipados-design`).

**Root cause**: Three compounding failures:
1. `migrateSkillSlugs()` (increment 0292) only reads from `skills:published-index` blob, which was empty (bug from 0306)
2. `rebuild-index` (increment 0306) takes KV key names as-is — does NOT recompute slugs through `makeSlug()`
3. No combined endpoint exists that enumerates AND recomputes

## Data Analysis (verified against production)

| Category | Count | Action |
|----------|-------|--------|
| Correct slug, no collision | 937 | Skip |
| Bad slug, no collision | 2,990 | Rename → `makeSlug(displayName)` |
| Collision winner (holds base slug) | ~168 | Skip |
| Collision, diff owners | ~964 | Rename → `owner-baseSlug` |
| Collision, same owner diff repos (14 groups) | ~28 | Rename → `owner-repo-baseSlug` |
| Duplicates (same identity, 2 rows) | 72 | Delete old prefixed one |
| Vendor/custom (VENDOR_AUTO) | 40 | Skip |

## User Stories

### US-001: Admin Slug Recomputation Endpoint

As a platform admin, I want an endpoint that recomputes all skill slugs from displayName
so that slugs match the current `makeSlug()` logic and are clean/user-friendly.

**Acceptance Criteria:**

- [x] AC-US1-01: Endpoint computes target slug as `makeSlug("", displayName)` for all non-vendor skills
- [x] AC-US1-02: Skills with `certMethod = VENDOR_AUTO` are skipped entirely
- [x] AC-US1-03: Same-identity duplicates (same repoUrl + same displayName) — keep the one with the correct base slug, delete the old prefixed one; create KV alias for deleted slug
- [x] AC-US1-04: No-collision skills — rename to base slug directly
- [x] AC-US1-05: Cross-repo collision, different owners — existing base-slug holder keeps it; others get `owner-baseSlug`
- [x] AC-US1-06: Cross-repo collision, same owner different repos — get `owner-repo-baseSlug`
- [x] AC-US1-07: KV `skill:{slug}` keys updated alongside DB renames (new key written, old key gets alias redirect)
- [x] AC-US1-08: Endpoint requires SUPER_ADMIN or X-Internal-Key auth
- [x] AC-US1-09: Returns stats: `{ renamed, skipped, duplicatesRemoved, collisions, errors }`
- [x] AC-US1-10: Supports `?dryRun=true` query param that returns what WOULD change without mutating
- [x] AC-US1-11: Batched execution to stay within Cloudflare Workers CPU limits

## Slug Rules (exhaustive)

1. **Identity**: `(owner, repo, makeSlug(displayName))` uniquely identifies a skill
2. **Target slug**: `makeSlug("", displayName)` — derived from displayName only
3. **No collision**: use target slug directly
4. **Cross-repo collision, different owners**: holder of base slug keeps it; others get `{owner}-{targetSlug}`
5. **Cross-repo collision, same owner, different repos**: `{owner}-{repo}-{targetSlug}`
6. **Duplicates**: keep row with clean slug, delete old prefixed row, create alias
7. **Vendor/custom**: `certMethod = VENDOR_AUTO` → skip (intentionally curated slugs)

## Technical Notes

- Prisma `Skill.name` = the slug (unique constraint)
- KV keys are `skill:{slug}` — must be re-keyed in sync
- Create `slug-migration.ts` module (separate from existing `submission-store.ts`)
- Chunk DB updates in batches of ~100 to avoid Workers CPU timeout
- `extractRepoName()` helper needed in `slug.ts`
