---
increment: 0447-hierarchical-skill-urls
title: "Restructure skill URLs to /{owner}/{repo}/{skill-slug}"
generated_by: sw:test-aware-planner
by_user_story:
  US-001: [T-001, T-002, T-003, T-004]
  US-002: [T-005, T-006, T-007]
  US-003: [T-008, T-009, T-010]
  US-004: [T-011, T-012, T-013]
  US-005: [T-014, T-015]
  US-006: [T-016, T-017]
---

# Tasks: Hierarchical Skill URLs

## User Story: US-001 - Hierarchical Skill URLs

**Linked ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05
**Tasks**: 4 total, 4 completed

---

### T-001: Prisma Schema Migration -- Add Hierarchical Slug Columns

**User Story**: US-001
**Satisfies ACs**: AC-US1-02, AC-US1-03
**Status**: [x] completed

**Test Plan**:
- **Given** the Prisma schema for the `Skill` model
- **When** the Phase 1 migration is applied to the database
- **Then** `Skill` has nullable columns `ownerSlug`, `repoSlug`, `skillSlug`, `legacySlug` and a composite unique constraint on `(ownerSlug, repoSlug, skillSlug)` plus indexes on `legacySlug` and `ownerSlug`

**Test Cases**:
1. **Unit**: `repositories/anton-abyzov/vskill-platform/src/lib/__tests__/schema.test.ts`
   - `testSchemaColumnsExist()`: Query DB for column names on Skill table, verify all 4 new columns exist
   - `testCompositeUniqueConstraint()`: Attempt insert of duplicate `(ownerSlug, repoSlug, skillSlug)` -- expect unique violation
   - `testNullableColumns()`: Insert skill row with all new columns null -- expect success
   - **Coverage Target**: 90%

**Implementation**:
1. Edit `repositories/anton-abyzov/vskill-platform/prisma/schema.prisma` -- add `ownerSlug String? @db.VarChar(100)`, `repoSlug String? @db.VarChar(100)`, `skillSlug String? @db.VarChar(200)`, `legacySlug String? @db.VarChar(500)`, composite unique `@@unique([ownerSlug, repoSlug, skillSlug])`, `@@index([legacySlug])`, `@@index([ownerSlug])`
2. Run `npx prisma migrate dev --name add_hierarchical_slugs` in `repositories/anton-abyzov/vskill-platform/`
3. Verify migration SQL in `prisma/migrations/*/migration.sql`

---

### T-002: Slug Helpers -- `buildHierarchicalName` and `deriveSkillSlug`

**User Story**: US-001
**Satisfies ACs**: AC-US1-02, AC-US1-03
**Status**: [x] completed

**Test Plan**:
- **Given** a GitHub repo URL and a SKILL.md path
- **When** `buildHierarchicalName(repoUrl, skillPath)` is called
- **Then** it returns `{ ownerSlug, repoSlug, skillSlug, name }` where `name` is `owner/repo/skillSlug`

**Test Cases**:
1. **Unit**: `repositories/anton-abyzov/vskill-platform/src/lib/__tests__/slug.test.ts`
   - `testBuildHierarchicalNameNestedPath()`: `buildHierarchicalName("https://github.com/acme/tools", "plugins/linter/skills/eslint-helper/SKILL.md")` returns `{ ownerSlug: "acme", repoSlug: "tools", skillSlug: "eslint-helper", name: "acme/tools/eslint-helper" }`
   - `testBuildHierarchicalNameRootSkillMd()`: `buildHierarchicalName("https://github.com/acme/my-skill", "SKILL.md")` returns `{ skillSlug: "my-skill", name: "acme/my-skill/my-skill" }`
   - `testBuildHierarchicalNameNullPath()`: `buildHierarchicalName("https://github.com/acme/my-skill", null)` uses repo name as `skillSlug`
   - `testDeriveSkillSlugNestedPath()`: `deriveSkillSlug("plugins/a/skills/helper/SKILL.md", "repo")` returns `"helper"`
   - `testDeriveSkillSlugRootPath()`: `deriveSkillSlug("SKILL.md", "my-repo")` returns `"my-repo"`
   - **Coverage Target**: 95%

**Implementation**:
1. Edit `repositories/anton-abyzov/vskill-platform/src/lib/slug.ts` -- add `deriveSkillSlug(skillPath: string | null, repoName: string): string` (parent folder of SKILL.md, fallback to repoName)
2. Add `buildHierarchicalName(repoUrl: string, skillPath: string | null): { ownerSlug: string; repoSlug: string; skillSlug: string; name: string }` -- parse owner/repo from GitHub URL, call `deriveSkillSlug`
3. Mark existing `makeSlug()` with `/** @deprecated Use buildHierarchicalName instead */`

---

### T-003: `skill-url.ts` -- URL Builder Utility

**User Story**: US-001
**Satisfies ACs**: AC-US1-01, AC-US1-04, AC-US1-05
**Status**: [x] completed

**Test Plan**:
- **Given** a skill name in hierarchical format `owner/repo/slug`
- **When** `skillUrl(name)` is called
- **Then** it returns `/skills/owner/repo/slug` with each segment URI-encoded

**Test Cases**:
1. **Unit**: `repositories/anton-abyzov/vskill-platform/src/lib/__tests__/skill-url.test.ts`
   - `testSkillUrlHierarchical()`: `skillUrl("acme/tools/linter")` returns `"/skills/acme/tools/linter"`
   - `testSkillUrlLegacyFallback()`: `skillUrl("acme-tools-linter")` returns `"/skills/acme-tools-linter"` (single segment fallback)
   - `testSkillUrlEncoding()`: `skillUrl("acme/my repo/skill slug")` percent-encodes spaces
   - `testSkillApiPathHierarchical()`: `skillApiPath("acme/tools/linter")` returns `"/api/v1/skills/acme/tools/linter"`
   - `testSkillBadgeUrl()`: `skillBadgeUrl("acme/tools/linter")` returns `"https://verified-skill.com/api/v1/skills/acme/tools/linter/badge"`
   - **Coverage Target**: 95%

**Implementation**:
1. Create `repositories/anton-abyzov/vskill-platform/src/lib/skill-url.ts` with `skillUrl(name)`, `skillApiPath(name)`, `skillBadgeUrl(name)` as per AD-5 in plan.md
2. Export all three functions

---

### T-004: New Page Routes -- `/skills/[owner]/[repo]/[skill]`

**User Story**: US-001
**Satisfies ACs**: AC-US1-01, AC-US1-04
**Status**: [x] completed

**Test Plan**:
- **Given** a skill with hierarchical name `dailydotdev/daily/daily`
- **When** a request arrives at `/skills/dailydotdev/daily/daily`
- **Then** the page resolves the skill by the three path segments and renders with correct metadata and OG tags

**Test Cases**:
1. **Integration**: `repositories/anton-abyzov/vskill-platform/src/app/skills/__tests__/hierarchical-page.test.ts`
   - `testPageResolvesSkillByThreeSegments()`: Mock `getSkillByName("dailydotdev/daily/daily")`, render page, expect skill title in output
   - `testPageReturns404ForUnknownSkill()`: Mock `getSkillByName()` returning null, expect `notFound()` called
   - `testPageMetadataIncludesHierarchicalName()`: Verify `generateMetadata` returns title with `owner/repo/skill` format
   - **Coverage Target**: 90%

**Implementation**:
1. Create directory `repositories/anton-abyzov/vskill-platform/src/app/skills/[owner]/[repo]/[skill]/`
2. Create `page.tsx` -- decode params, construct `name = owner/repo/skill`, call `getSkillByName(name)`, render skill detail (copy from existing `[name]/page.tsx` skill rendering logic)
3. Create `security/page.tsx`, `security/[provider]/page.tsx`, `evals/page.tsx` -- same decode pattern, delegate to existing shared rendering components
4. Move `RepoHealthBadge.tsx` from `[name]/` to `[owner]/[repo]/[skill]/`

---

## User Story: US-002 - Legacy URL Redirects

**Linked ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04
**Tasks**: 3 total, 3 completed

---

### T-005: `getSkillByLegacySlug` + Legacy Page Redirects

**User Story**: US-002
**Satisfies ACs**: AC-US2-01, AC-US2-03
**Status**: [x] completed

**Test Plan**:
- **Given** a skill with `legacySlug = "dailydotdev-daily"` stored in DB
- **When** a request hits `/skills/dailydotdev-daily`
- **Then** the server responds with 301 redirect to `/skills/dailydotdev/daily/daily`

**Test Cases**:
1. **Unit**: `repositories/anton-abyzov/vskill-platform/src/lib/__tests__/data.test.ts`
   - `testGetSkillByLegacySlug()`: Mock Prisma `findFirst({ where: { legacySlug } })`, verify correct field queried
   - `testGetSkillByLegacySlugNotFound()`: Returns `null` when no match
2. **Integration**: `repositories/anton-abyzov/vskill-platform/src/app/skills/__tests__/legacy-redirect.test.ts`
   - `testLegacyPageRedirectsTo301()`: Mock `getSkillByLegacySlug("dailydotdev-daily")` returning skill with name `dailydotdev/daily/daily`, assert `redirect()` called with correct URL and 301 status
   - `testLegacyPageReturns404WhenNoMatch()`: `getSkillByLegacySlug()` returns null, assert `notFound()` called
   - **Coverage Target**: 90%

**Implementation**:
1. Edit `repositories/anton-abyzov/vskill-platform/src/lib/data.ts` -- add `getSkillByLegacySlug(slug: string): Promise<SkillData | null>` querying `WHERE legacySlug = slug`; extend `mapDbSkillToSkillData()` to include `ownerSlug`, `repoSlug`, `skillSlug`, `legacySlug`
2. Edit `repositories/anton-abyzov/vskill-platform/src/app/skills/[name]/page.tsx` -- replace current skill-rendering logic with legacy redirect: call `getSkillByLegacySlug(decoded)`, if found call `redirect(skillUrl(skill.name), 301)`, else `notFound()`
3. Apply same redirect pattern to `[name]/security/page.tsx`, `[name]/security/[provider]/page.tsx`, `[name]/evals/page.tsx`

---

### T-006: Legacy API Route Redirects

**User Story**: US-002
**Satisfies ACs**: AC-US2-01, AC-US2-03
**Status**: [x] completed

**Test Plan**:
- **Given** a skill API endpoint at `/api/v1/skills/dailydotdev-daily`
- **When** a GET request is made with the old flat slug
- **Then** the response is a 301 redirect to `/api/v1/skills/dailydotdev/daily/daily`

**Test Cases**:
1. **Integration**: `repositories/anton-abyzov/vskill-platform/src/app/api/v1/skills/__tests__/legacy-api-redirect.test.ts`
   - `testLegacyApiRouteRedirects301()`: Mock `getSkillByLegacySlug()` returning skill, assert `NextResponse.redirect` with 301 and new hierarchical API path
   - `testLegacyApiRouteReturns404()`: `getSkillByLegacySlug()` returns null, assert 404 JSON response
   - `testNewHierarchicalApiRouteReturnsSkill()`: Mock `getSkillByName("acme/tools/linter")` returning skill, assert 200 with skill data
   - **Coverage Target**: 90%

**Implementation**:
1. Create `repositories/anton-abyzov/vskill-platform/src/lib/api/skill-handlers.ts` with `handleGetSkill(name)`, `handleGetSkillBadge(name, provider?)`, `handleGetInstalls(name)`, `handleGetSecurity(name, provider?)`, `handleGetEval(name)`, `handleGetRepoHealth(name)`
2. Create `repositories/anton-abyzov/vskill-platform/src/lib/api/legacy-redirect.ts` with `buildLegacyApiRedirect(req, legacySlug)` returning `NextResponse | null`
3. Create new route directory `src/app/api/v1/skills/[owner]/[repo]/[skill]/` with `route.ts`, `badge/route.ts`, `badge/[provider]/route.ts`, `installs/route.ts`, `security/route.ts`, `security/[provider]/route.ts`, `eval/route.ts`, `eval/history/route.ts`, `repo-health/route.ts` -- each calls corresponding shared handler
4. Convert all `src/app/api/v1/skills/[name]/*/route.ts` files to redirect handlers using `buildLegacyApiRedirect`

---

### T-007: Data Migration Script -- Backfill Slugs and KV Aliases

**User Story**: US-002
**Satisfies ACs**: AC-US2-02, AC-US2-04
**Status**: [x] completed

**Test Plan**:
- **Given** existing skills with flat `name` values and `repoUrl`/`skillPath` data
- **When** the migration script runs in `--dry-run` mode then in live mode
- **Then** each skill row has `legacySlug` set to old name, `name` updated to `owner/repo/skillSlug`, and KV has both `skill:{newName}` and `skill:alias:{legacySlug}` entries

**Test Cases**:
1. **Unit**: `repositories/anton-abyzov/vskill-platform/src/scripts/__tests__/migrate-hierarchical-slugs.test.ts`
   - `testDryRunLogsChangesWithoutWriting()`: Run with `--dry-run`, assert DB not updated, assert console output contains old and new names
   - `testMigrationSetsLegacySlug()`: Verify `legacySlug` is set to pre-migration `name`
   - `testMigrationUpdatesName()`: Verify `name` updated to `owner/repo/skillSlug` format
   - `testMigrationCreatesKVAlias()`: Verify `skill:alias:{legacySlug}` written to KV with new name value
   - `testMigrationDeletesOldKVKey()`: Verify old `skill:{legacySlug}` KV key deleted
   - `testMigrationBatchesOf50()`: Supply 120 skills, verify processed in 3 batches
   - **Coverage Target**: 90%

**Implementation**:
1. Create `repositories/anton-abyzov/vskill-platform/src/scripts/migrate-to-hierarchical-slugs.ts`
2. Implement batch loop (50 skills at a time): derive `buildHierarchicalName(skill.repoUrl, skill.skillPath)`, set `legacySlug = skill.name`, update DB row, write KV `skill:{newName}`, write KV alias `skill:alias:{legacySlug}`, delete old KV key `skill:{legacySlug}`
3. Update `BlocklistEntry`, `ExternalScanResult`, `SecurityReport` tables: `SET skillName = newName WHERE skillName = legacySlug`
4. Support `--dry-run` flag: log all operations but skip writes

---

## User Story: US-003 - Publishing Pipeline with Hierarchical Names

**Linked ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04, AC-US3-05
**Tasks**: 3 total, 3 completed

---

### T-008: `publishSkill` -- Hierarchical Name Generation

**User Story**: US-003
**Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04
**Status**: [x] completed

**Test Plan**:
- **Given** a submission from `github.com/acme/tools` with SKILL.md at `plugins/linter/skills/eslint-helper/SKILL.md`
- **When** `publishSkill` processes the submission
- **Then** `Skill.name` is `acme/tools/eslint-helper`, `skillSlug` is `eslint-helper`, KV key is `skill:acme/tools/eslint-helper`

**Test Cases**:
1. **Unit**: `repositories/anton-abyzov/vskill-platform/src/lib/__tests__/submission-store.test.ts`
   - `testPublishSkillSetsHierarchicalName()`: Mock `buildHierarchicalName()`, verify `prisma.skill.upsert` called with `name: "acme/tools/eslint-helper"` and new slug fields
   - `testPublishSkillRootSkillMd()`: SKILL.md at root uses repo name as `skillSlug`
   - `testPublishSkillWritesHierarchicalKVKey()`: Verify KV put uses `skill:acme/tools/eslint-helper`
   - `testResolveSlugUsesHierarchicalName()`: `resolveSlug()` calls `buildHierarchicalName()` and returns result without collision logic
   - `testResolveSlugNoHashDisambiguation()`: Verify old hash-based collision code is absent -- expect no `makeSafeSlug` call with hash
   - **Coverage Target**: 90%

**Implementation**:
1. Edit `repositories/anton-abyzov/vskill-platform/src/lib/submission-store.ts` -- update `resolveSlug()` to call `buildHierarchicalName(repoUrl, skillPath)` and return the hierarchical name; remove collision disambiguation branches
2. Update `publishSkill()` Prisma upsert `create` and `update` blocks to set `ownerSlug`, `repoSlug`, `skillSlug`, `legacySlug` (null for new skills that never had a flat slug)
3. Update KV write in `publishSkill()` to use `skill:${owner/repo/skillSlug}` key
4. Update cross-repo overwrite guard to compare `ownerSlug + repoSlug` instead of hash

---

### T-009: Email Templates -- Hierarchical Skill Names in Notifications

**User Story**: US-003
**Satisfies ACs**: AC-US3-05
**Status**: [x] completed

**Test Plan**:
- **Given** a skill with hierarchical name `acme/tools/linter`
- **When** auto-approval email is sent
- **Then** the subject line and body contain `acme/tools/linter`, and the badge URL is `https://verified-skill.com/api/v1/skills/acme/tools/linter/badge`

**Test Cases**:
1. **Unit**: `repositories/anton-abyzov/vskill-platform/src/lib/__tests__/email.test.ts`
   - `testBuildBadgeUrlUsesHierarchicalFormat()`: `buildBadgeUrl("acme/tools/linter")` returns correct URL via `skillBadgeUrl()`
   - `testAutoApproveEmailSubjectHierarchical()`: Email subject contains `acme/tools/linter`
   - `testAutoApproveEmailBadgeMarkdown()`: Badge embed markdown contains 3-segment path
   - **Coverage Target**: 85%

**Implementation**:
1. Edit `repositories/anton-abyzov/vskill-platform/src/lib/email.ts` -- replace `buildBadgeUrl()` body with `return skillBadgeUrl(skillName)` (import from `skill-url.ts`)
2. Verify email subject templates already use `skillName` directly (no change needed if so)
3. Verify badge embed markdown in auto-approved template uses the updated `buildBadgeUrl()`

---

### T-010: KV Read Path -- Hierarchical Key + Alias Fallback

**User Story**: US-003
**Satisfies ACs**: AC-US1-05, AC-US2-04
**Status**: [x] completed

**Test Plan**:
- **Given** a KV store with both `skill:acme/tools/linter` (primary) and `skill:alias:acme-tools-linter` (alias) entries
- **When** code reads a skill by name
- **Then** primary hierarchical key is tried first; if not found, alias key is resolved and primary is fetched

**Test Cases**:
1. **Unit**: `repositories/anton-abyzov/vskill-platform/src/lib/__tests__/kv-cache.test.ts`
   - `testReadHierarchicalKeyDirect()`: `getSkillFromKV("acme/tools/linter")` reads `skill:acme/tools/linter`
   - `testReadViaAliasKey()`: Primary miss reads `skill:alias:acme-tools-linter`, resolves to new name, reads primary
   - `testAliasKeyNotFoundReturnsNull()`: Both primary and alias miss returns null
   - **Coverage Target**: 90%

**Implementation**:
1. Identify KV read function in the codebase (likely in `submission-store.ts` or `data.ts`)
2. Update KV read to: first try `skill:{name}`, if null try `skill:alias:{name}` to get hierarchical name, then try `skill:{hierarchicalName}`
3. Ensure migration script creates alias entries (verified in T-007)

---

## User Story: US-004 - CLI Compatibility with Hierarchical URLs

**Linked ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04, AC-US4-05
**Tasks**: 3 total, 3 completed

---

### T-011: vskill API Client -- 3-Segment Path Routing

**User Story**: US-004
**Satisfies ACs**: AC-US4-01, AC-US4-04, AC-US4-05
**Status**: [x] completed

**Test Plan**:
- **Given** a hierarchical skill name `facebook/react/react-hooks`
- **When** `getSkill("facebook/react/react-hooks")` is called in the API client
- **Then** the HTTP request goes to `/api/v1/skills/facebook/react/react-hooks` (not encoded as a single segment)

**Test Cases**:
1. **Unit**: `repositories/anton-abyzov/vskill/src/api/__tests__/client.test.ts`
   - `testSkillApiPathThreeSegments()`: `skillApiPath("facebook/react/react-hooks")` returns `"/api/v1/skills/facebook/react/react-hooks"`
   - `testSkillApiPathSingleSegment()`: `skillApiPath("old-flat-slug")` returns `"/api/v1/skills/old-flat-slug"` (legacy fallback)
   - `testGetSkillUsesHierarchicalPath()`: Mock HTTP client, call `getSkill("acme/tools/linter")`, verify URL contains 3 segments
   - `testSkillUrlDisplay()`: `getSkillUrl("acme/tools/linter")` returns `"https://verified-skill.com/skills/acme/tools/linter"`
   - **Coverage Target**: 90%

**Implementation**:
1. Edit `repositories/anton-abyzov/vskill/src/api/client.ts` -- add `skillApiPath(name: string)` helper that splits on `/`, if 3 parts encodes each separately; update `getSkill()` and `reportInstall()` to use it
2. Edit `repositories/anton-abyzov/vskill/src/commands/find.ts` -- update `getSkillUrl()` to produce 3-segment URL; simplify `formatRepoSkill()` since API already returns hierarchical name
3. Add blocklist check using hierarchical name in the `name` query param

---

### T-012: vskill Lockfile -- Hierarchical Keys with Backward Compat

**User Story**: US-004
**Satisfies ACs**: AC-US4-02, AC-US4-03
**Status**: [x] completed

**Test Plan**:
- **Given** a newly installed skill with hierarchical name `acme/tools/linter`
- **When** `vskill add acme/tools/linter` completes
- **Then** the lockfile entry key is `acme/tools/linter` and the lockfile can still read old flat-slug keys without error

**Test Cases**:
1. **Unit**: `repositories/anton-abyzov/vskill/src/lockfile/__tests__/lockfile.test.ts`
   - `testLockfileWritesHierarchicalKey()`: After `installFromRegistry("acme/tools/linter")`, lockfile has key `acme/tools/linter`
   - `testLockfileReadsLegacyFlatSlugKey()`: Read lockfile with key `old-flat-slug`, expect graceful read (no crash, returns entry)
   - `testVskillListShowsBothFormats()`: `vskill list` with mixed lockfile shows all entries including legacy flat-slug keys
   - **Coverage Target**: 85%

**Implementation**:
1. Edit `repositories/anton-abyzov/vskill/src/commands/add.ts` -- `installFromRegistry()` uses skill `name` field (already hierarchical from API) as lockfile key
2. Edit `repositories/anton-abyzov/vskill/src/lockfile/types.ts` -- ensure lockfile reader accepts both `owner/repo/skill` and `flat-slug` key formats without parsing errors

---

### T-013: vskill `info` Command -- Hierarchical Name Lookup

**User Story**: US-004
**Satisfies ACs**: AC-US4-04
**Status**: [x] completed

**Test Plan**:
- **Given** the `vskill info acme/tools/linter` command
- **When** the user provides a 3-segment hierarchical name
- **Then** the CLI fetches and displays the skill detail, showing `owner/repo/skillSlug` format

**Test Cases**:
1. **Unit**: `repositories/anton-abyzov/vskill/src/commands/__tests__/info.test.ts`
   - `testInfoCommandHierarchicalName()`: Mock `getSkill("acme/tools/linter")`, assert display output includes name and URL
   - `testInfoCommandFlatSlugFallback()`: `getSkill("old-slug")` still works (API follows 301)
   - **Coverage Target**: 85%

**Implementation**:
1. Verify `repositories/anton-abyzov/vskill/src/commands/info.ts` (or equivalent) passes the name directly to `getSkill()` -- since `skillApiPath()` already handles 3-segment routing, no additional changes needed beyond T-011
2. Ensure output formatting displays hierarchical name correctly (no encodeURIComponent applied to display string)

---

## User Story: US-005 - Admin Interface with Hierarchical Names

**Linked ACs**: AC-US5-01, AC-US5-02, AC-US5-03, AC-US5-04
**Tasks**: 2 total, 2 completed

---

### T-014: Admin Routes -- Catch-All `[...name]` for Block and Delete

**User Story**: US-005
**Satisfies ACs**: AC-US5-01, AC-US5-02
**Status**: [x] completed

**Test Plan**:
- **Given** an admin block request for skill `acme/tools/linter`
- **When** the route receives the path `/api/v1/admin/skills/acme/tools/linter/block`
- **Then** Next.js catch-all routing parses `["acme", "tools", "linter"]` and the block operation succeeds with `skillName = "acme/tools/linter"`

**Test Cases**:
1. **Integration**: `repositories/anton-abyzov/vskill-platform/src/app/api/v1/admin/skills/__tests__/admin-skill-routes.test.ts`
   - `testCatchAllBlockRouteJoinsSegments()`: Call block route with `params.name = ["acme", "tools", "linter"]`, assert `skillName = "acme/tools/linter"` used in DB query
   - `testCatchAllDeleteRouteJoinsSegments()`: Same for delete
   - `testDeleteCleansUpKVHierarchicalAndAlias()`: Delete route removes both `skill:{hierarchicalName}` and `skill:alias:{legacySlug}` from KV
   - `testDeleteCleansUpLegacyAliasFromKV()`: Verify `skill.legacySlug` is read and used for alias cleanup
   - **Coverage Target**: 90%

**Implementation**:
1. Rename/move `repositories/anton-abyzov/vskill-platform/src/app/api/v1/admin/skills/[name]/block/route.ts` to `[...name]/block/route.ts`
2. Rename/move `[name]/delete/route.ts` to `[...name]/delete/route.ts`
3. In both handlers, replace `params.name` (string) with `(await params).name.join("/")`
4. In delete handler, after DB delete, also delete `skill:alias:{skill.legacySlug}` from KV if `legacySlug` exists

---

### T-015: Repo-Block -- Block All Skills by `ownerSlug + repoSlug`

**User Story**: US-005
**Satisfies ACs**: AC-US5-03, AC-US5-04
**Status**: [x] completed

**Test Plan**:
- **Given** a repo-block operation on `dailydotdev/daily`
- **When** the endpoint processes the block
- **Then** all skills with matching `ownerSlug = "dailydotdev"` and `repoSlug = "daily"` are blocked and their KV entries updated

**Test Cases**:
1. **Integration**: `repositories/anton-abyzov/vskill-platform/src/app/api/v1/admin/__tests__/repo-block.test.ts`
   - `testRepoBlockQueriesByOwnerAndRepoSlug()`: Mock Prisma query, verify `WHERE ownerSlug = X AND repoSlug = Y` used
   - `testRepoBlockUpdatesKVForAllMatchingSkills()`: 3 skills in repo -- verify KV blocked flag set for all 3
   - `testAdminSubmissionsListShowsHierarchicalNames()`: Submissions list renders names in `owner/repo/skillSlug` format with correct link to `/skills/owner/repo/skillSlug`
   - **Coverage Target**: 85%

**Implementation**:
1. Edit repo-block route/handler -- update skill query to use `WHERE ownerSlug = owner AND repoSlug = repo` instead of prefix matching on flat name
2. Verify admin submissions list uses `skillUrl(skill.name)` for links (covered by T-016/T-017 component updates, but ensure admin views follow same pattern)

---

## User Story: US-006 - Publisher Page Skill Links

**Linked ACs**: AC-US6-01, AC-US6-02, AC-US6-03, AC-US6-04
**Tasks**: 2 total, 2 completed

---

### T-016: Component URL Updates -- `skillUrl()` Adoption

**User Story**: US-006
**Satisfies ACs**: AC-US6-01, AC-US6-02, AC-US6-03
**Status**: [x] completed

**Test Plan**:
- **Given** a skill with hierarchical name `facebook/react/react-hooks`
- **When** `PublisherSkillsList`, `TrendingSkills`, and `SearchPalette` components render
- **Then** each skill card `href` is `/skills/facebook/react/react-hooks` (3-segment format)

**Test Cases**:
1. **Unit**: `repositories/anton-abyzov/vskill-platform/src/app/components/__tests__/skill-urls.test.ts`
   - `testPublisherSkillsListHierarchicalHref()`: Render with skill `{ name: "fb/react/hooks" }`, assert href is `/skills/fb/react/hooks`
   - `testTrendingSkillsHierarchicalHref()`: Render TrendingSkills, assert link uses 3-segment format
   - `testSearchPaletteHierarchicalHref()`: Render search result, assert href uses 3-segment format
   - `testSkillsPageListHierarchicalHref()`: Render skills browse page, assert card links use `skillUrl()`
   - **Coverage Target**: 85%

**Implementation**:
1. Edit `repositories/anton-abyzov/vskill-platform/src/app/publishers/[name]/PublisherSkillsList.tsx` -- replace `href={/skills/${encodeURIComponent(skill.name)}}` with `href={skillUrl(skill.name)}`
2. Edit `repositories/anton-abyzov/vskill-platform/src/app/components/home/TrendingSkills.tsx` -- same replacement
3. Edit `repositories/anton-abyzov/vskill-platform/src/app/components/SearchPalette.tsx` -- same replacement
4. Edit `repositories/anton-abyzov/vskill-platform/src/app/skills/page.tsx` -- same replacement
5. Edit `VerifiedSkillsTab.tsx`, `submit/[id]/page.tsx`, `TaintWarning.tsx` -- same replacement

---

### T-017: Skill Detail Page -- Badge URL and Final Component Updates

**User Story**: US-006
**Satisfies ACs**: AC-US6-04
**Status**: [x] completed

**Test Plan**:
- **Given** the skill detail page for `acme/tools/linter`
- **When** the badge markdown snippet is displayed
- **Then** the badge link URL is `https://verified-skill.com/api/v1/skills/acme/tools/linter/badge` (3-segment path)

**Test Cases**:
1. **Unit**: `repositories/anton-abyzov/vskill-platform/src/app/skills/__tests__/skill-detail-badge.test.ts`
   - `testSkillDetailBadgeUrlHierarchical()`: Render skill detail page with skill `{ name: "acme/tools/linter" }`, assert badge markdown contains hierarchical URL
   - `testSkillDetailBadgeUrlLegacyFallback()`: Skill with flat name still produces valid badge URL via `skillBadgeUrl()` fallback
   - **Coverage Target**: 85%

**Implementation**:
1. Edit badge markdown snippet in `repositories/anton-abyzov/vskill-platform/src/app/skills/[owner]/[repo]/[skill]/page.tsx` -- use `skillBadgeUrl(skill.name)` for the badge embed code
2. Ensure `skillBadgeUrl()` is imported from `src/lib/skill-url.ts`
3. Run full test suite: `npx vitest run` in `repositories/anton-abyzov/vskill-platform/`
4. Run full test suite: `npx vitest run` in `repositories/anton-abyzov/vskill/`
