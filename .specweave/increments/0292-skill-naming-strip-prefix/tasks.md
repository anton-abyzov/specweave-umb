# Tasks: Fix skill naming -- strip org/repo prefix from slugs

## Task Notation

- `[T###]`: Task ID
- `[P]`: Parallelizable
- `[ ]`: Not started
- `[x]`: Completed
- Model hints: haiku (simple), opus (default)

## Phase 1: Fix Slug Generation

### T-001: Refactor makeSlug() to return clean base name only
**User Story**: US-001 | **Satisfies ACs**: AC-US1-01 | **Status**: [x] completed

**Description**: Change `makeSlug()` in `submission-store.ts` to return only the cleaned base name without org/repo prefix.

**File**: `repositories/anton-abyzov/vskill-platform/src/lib/submission-store.ts`

**Implementation Details**:
- Remove the `${owner}-${repo}-` prefix from `makeSlug()` return value
- Keep the `REPO_URL_RE` for potential collision detection usage
- The function should simply return `base` in all cases
- Export the function so it can be tested directly

**Test Plan**:
- **File**: `repositories/anton-abyzov/vskill-platform/src/lib/__tests__/submission-store.test.ts`
- **Tests**:
  - **TC-001**: makeSlug with GitHub URL returns clean base name
    - Given repoUrl "https://github.com/anton-abyzov/specweave" and skillName "sw-frontend"
    - When makeSlug() is called
    - Then returns "sw-frontend" (not "anton-abyzov-specweave-sw-frontend")
  - **TC-002**: makeSlug with non-GitHub URL returns base name unchanged
    - Given repoUrl "https://gitlab.com/user/repo" and skillName "My Cool Skill"
    - When makeSlug() is called
    - Then returns "my-cool-skill"
  - **TC-003**: makeSlug handles special characters in skill names
    - Given skillName "My @Skill #1!!"
    - When makeSlug() is called
    - Then returns "my-skill-1"

**Dependencies**: None

---

### T-002: Add collision-aware slug resolution to publishSkill()
**User Story**: US-001 | **Satisfies ACs**: AC-US1-02, AC-US1-04 | **Status**: [x] completed

**Description**: Add collision detection in `publishSkill()` so that if two skills from different repos produce the same base slug, a disambiguating prefix is added.

**File**: `repositories/anton-abyzov/vskill-platform/src/lib/submission-store.ts`

**Implementation Details**:
- Add async `resolveSlug(kv, repoUrl, skillName)` helper:
  1. Compute `baseSlug = makeSlug(repoUrl, skillName)`
  2. Read `skill:{baseSlug}` from KV
  3. If not found or same repoUrl: return `baseSlug`
  4. If found with different repoUrl: try `{owner}-{baseSlug}`
  5. If that also collides: fall back to `{owner}-{repo}-{baseSlug}`
- Update `publishSkill()` to use `resolveSlug()` instead of direct `makeSlug()`

**Test Plan**:
- **File**: `repositories/anton-abyzov/vskill-platform/src/lib/__tests__/submission-store.test.ts`
- **Tests**:
  - **TC-004**: resolveSlug returns base slug when no collision
    - Given no existing skill with same slug in KV
    - When resolveSlug() is called
    - Then returns the clean base slug
  - **TC-005**: resolveSlug adds owner prefix on collision from different repo
    - Given existing skill "my-skill" from repo A in KV
    - When resolveSlug() is called for "my-skill" from repo B
    - Then returns "ownerb-my-skill"
  - **TC-006**: resolveSlug overwrites when same repo re-publishes
    - Given existing skill "my-skill" from repo A in KV
    - When resolveSlug() is called for "my-skill" from same repo A
    - Then returns "my-skill" (same slug, allows overwrite)

**Dependencies**: T-001

---

## Phase 2: Backward Compatibility

### T-003: Add fallback lookup for old-format slugs in getPublishedSkill()
**User Story**: US-003 | **Satisfies ACs**: AC-US3-01, AC-US3-02 | **Status**: [x] completed

**Description**: Update `getPublishedSkill()` to try constructing the old org-prefixed slug format as a fallback when the clean slug is not found.

**File**: `repositories/anton-abyzov/vskill-platform/src/lib/submission-store.ts`

**Implementation Details**:
- After failing to find `skill:{slug}`, try variations:
  - If slug doesn't contain what looks like an owner prefix, try well-known old patterns
  - Alternatively, add a `skill:alias:{old-slug}` -> `{new-slug}` redirect key during migration (simpler)
- Chose alias approach: migration writes alias keys, lookup checks alias on miss

**Test Plan**:
- **File**: `repositories/anton-abyzov/vskill-platform/src/lib/__tests__/submission-store.test.ts`
- **Tests**:
  - **TC-007**: getPublishedSkill finds skill by new clean slug
    - Given skill published with slug "sw-frontend"
    - When getPublishedSkill("sw-frontend") is called
    - Then returns the skill record
  - **TC-008**: getPublishedSkill falls back to alias lookup for old slug
    - Given migration wrote alias `skill:alias:anton-abyzov-specweave-sw-frontend` -> `sw-frontend`
    - When getPublishedSkill("anton-abyzov-specweave-sw-frontend") is called
    - Then resolves alias and returns the skill record

**Dependencies**: T-001

---

## Phase 3: Migration

### T-004: Create KV migration function for existing published skills
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04, AC-US2-05 | **Status**: [x] completed

**Description**: Create a migration function that reads all existing published skills from KV, recomputes clean slugs, copies records under new keys, writes alias keys for old slugs, and rewrites the published index.

**File**: `repositories/anton-abyzov/vskill-platform/src/lib/submission-store.ts`

**Implementation Details**:
- Add `async function migrateSkillSlugs(): Promise<MigrationResult>`
- Steps:
  1. Read `skills:published-index`
  2. For each entry, compute new clean slug using `makeSlug(entry.repoUrl, entry.name)`
  3. If new slug differs from old slug:
     a. Read `skill:{oldSlug}` record
     b. Update the `slug` field in the record
     c. Write to `skill:{newSlug}`
     d. Write alias: `skill:alias:{oldSlug}` -> `newSlug`
     e. Delete `skill:{oldSlug}`
  4. Rewrite `skills:published-index` with updated slugs
  5. Handle collisions: if multiple old entries map to same new slug, keep most recently published
- Return stats: `{ migrated: number, skipped: number, collisions: number }`
- Export the function

**Test Plan**:
- **File**: `repositories/anton-abyzov/vskill-platform/src/lib/__tests__/submission-store.test.ts`
- **Tests**:
  - **TC-009**: Migration converts old slugs to clean slugs
    - Given published index with entry `{ slug: "owner-repo-skill", name: "skill", repoUrl: "..." }`
    - When migrateSkillSlugs() runs
    - Then new KV key `skill:skill` exists with updated slug
    - And alias `skill:alias:owner-repo-skill` points to "skill"
    - And old KV key `skill:owner-repo-skill` is deleted
    - And index entry has slug "skill"
  - **TC-010**: Migration is idempotent
    - Given migration already ran once
    - When migrateSkillSlugs() runs again
    - Then no errors, same result
  - **TC-011**: Migration handles slug collisions
    - Given two entries "owner1-repo1-myskill" and "owner2-repo2-myskill"
    - When migrateSkillSlugs() runs
    - Then most recent gets "myskill", other gets "owner1-myskill" (or vice versa)

**Dependencies**: T-001, T-002

---

### T-005: Create admin API endpoint for slug migration
**User Story**: US-002 | **Satisfies ACs**: AC-US2-01 | **Status**: [x] completed

**Description**: Create an admin-only API endpoint to trigger the KV slug migration.

**File**: `repositories/anton-abyzov/vskill-platform/src/app/api/v1/admin/migrate-slugs/route.ts`

**Implementation Details**:
- `POST /api/v1/admin/migrate-slugs`
- Requires admin authentication
- Calls `migrateSkillSlugs()` and returns the result stats
- Returns 200 with `{ migrated, skipped, collisions }`

**Test Plan**:
- **File**: `repositories/anton-abyzov/vskill-platform/src/app/api/v1/admin/migrate-slugs/__tests__/route.test.ts`
- **Tests**:
  - **TC-012**: POST returns migration stats on success
    - Given admin auth token
    - When POST /api/v1/admin/migrate-slugs
    - Then returns 200 with { migrated, skipped, collisions }
  - **TC-013**: POST returns 401 without admin auth
    - Given no auth token
    - When POST /api/v1/admin/migrate-slugs
    - Then returns 401

**Dependencies**: T-004

---

## Phase 4: Verification

### T-006: Update existing tests and verify full pipeline
**User Story**: US-001, US-002, US-003 | **Satisfies ACs**: AC-US1-03 | **Status**: [x] completed

**Description**: Update any existing tests that assert old slug format, run full test suite to verify nothing breaks.

**Implementation Details**:
- Search for tests that reference old slug patterns (with org/repo prefix)
- Update expected values to use clean slugs
- Run `npm test` in vskill-platform to verify all tests pass

**Test Plan**:
- Run full test suite: `cd repositories/anton-abyzov/vskill-platform && npx vitest run`
- Verify no test failures related to slug format changes

**Dependencies**: T-001, T-002, T-003, T-004, T-005
