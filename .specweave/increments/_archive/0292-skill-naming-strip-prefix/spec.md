---
increment: 0292-skill-naming-strip-prefix
title: "Fix skill naming: strip org/repo prefix from slugs"
type: bug
priority: P1
status: completed
created: 2026-02-21
structure: user-stories
test_mode: test-after
coverage_target: 80
---

# Feature: Fix skill naming -- strip org/repo prefix from slugs

## Overview

Published skill slugs currently include the GitHub org and repo name as a prefix (e.g. `anton-abyzov-specweave-sw-frontend` instead of `sw-frontend`). The `makeSlug()` function in `submission-store.ts` concatenates `{owner}-{repo}-{base}` which produces ugly, redundant slugs that differ from community norms (skills.sh uses the clean skill name only). This needs to be fixed at the slug generation layer, and existing KV records need to be migrated to the new clean slugs.

## Problem Analysis

The root cause is the `makeSlug()` function at line 344 of `submission-store.ts`:

```ts
function makeSlug(repoUrl: string, skillName: string): string {
  const match = REPO_URL_RE.exec(repoUrl);
  const base = skillName.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
  if (match) {
    const owner = match[1].toLowerCase();
    const repo = match[2].toLowerCase();
    return `${owner}-${repo}-${base}`;  // <-- THIS IS THE BUG
  }
  return base;
}
```

This produces slugs like `anton-abyzov-specweave-sw-frontend` when the desired slug is just `sw-frontend`.

The slug is used as:
1. KV key: `skill:{slug}` for the published skill record
2. `slug` field in both the skill record and the published-index entries
3. `name` field in `data.ts` when merging published skills into the registry
4. URL path segment: `/skills/{slug}` in the frontend

## User Stories

### US-001: Clean Skill Slug Generation (P1)
**Project**: vskill-platform

**As a** platform user browsing the skill registry
**I want** skills to be named by their clean skill name (e.g. `sw-frontend`) rather than org/repo-prefixed slugs (e.g. `anton-abyzov-specweave-sw-frontend`)
**So that** skill names are concise, human-readable, and consistent with community norms (skills.sh)

**Acceptance Criteria**:
- [x] **AC-US1-01**: `makeSlug()` returns the clean base name only (no org/repo prefix) for newly published skills
- [x] **AC-US1-02**: Collision handling: if two skills from different repos share the same base name, a disambiguating suffix is added (e.g. `sw-frontend-2` or `owner-sw-frontend`)
- [x] **AC-US1-03**: `getPublishedSkill()` correctly resolves skills by their new clean slugs
- [x] **AC-US1-04**: Published index uses clean slugs for dedup and lookup

---

### US-002: KV Data Migration (P1)
**Project**: vskill-platform

**As a** platform operator
**I want** existing KV records with old org-prefixed slugs to be migrated to clean slugs
**So that** previously published skills are accessible under their new clean names

**Acceptance Criteria**:
- [x] **AC-US2-01**: A migration function reads all entries from `skills:published-index`, re-keys each skill record from old slug to new slug
- [x] **AC-US2-02**: The published-index is rewritten with clean slugs
- [x] **AC-US2-03**: Old KV keys (`skill:{old-slug}`) are deleted after migration
- [x] **AC-US2-04**: Migration is idempotent -- running it twice produces the same result
- [x] **AC-US2-05**: Migration handles collisions (two old records mapping to the same new slug) by keeping the most recent one

---

### US-003: Backward-Compatible Lookup (P2)
**Project**: vskill-platform

**As a** user who bookmarked a skill page under the old slug URL
**I want** old slugs to still resolve to the correct skill
**So that** existing links and references do not break

**Acceptance Criteria**:
- [x] **AC-US3-01**: `getPublishedSkill()` falls back to trying the old org-prefixed slug format when the clean slug is not found
- [x] **AC-US3-02**: Frontend skill detail pages (`/skills/[name]`) work with both old and new slug formats

## Functional Requirements

### FR-001: Slug Generation
- `makeSlug()` must return only the cleaned base name: `skillName.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "")`
- No org or repo name should be included in the slug

### FR-002: Collision Handling
- Before publishing, check if a `skill:{slug}` KV key already exists
- If collision found and it belongs to a different repo, append owner as prefix: `{owner}-{base}`
- If that also collides, append repo: `{owner}-{repo}-{base}` (current behavior, as last resort)

### FR-003: KV Migration
- Read `skills:published-index` to get all existing published skills
- For each entry, compute the new clean slug
- Copy skill records to new KV keys, update index, delete old keys
- Expose as an admin API endpoint (`POST /api/v1/admin/migrate-slugs`)

## Success Criteria

- All newly published skills use clean slugs (no org/repo prefix)
- Existing published skills are migrated to clean slugs
- No broken links -- old slug URLs still resolve
- All existing tests pass, new tests cover slug generation and migration

## Out of Scope

- Changing Prisma Skill.name values (DB layer not affected -- slugs are KV-only)
- Changing the discovery crawler's `skillName` field (it already uses clean names from directory/repo name)
- Renaming seed-data skills (these are hardcoded, not generated from `makeSlug`)

## Dependencies

- Cloudflare KV (SUBMISSIONS_KV binding) for migration
- Existing published skills data in KV
