---
increment: 0451-skill-naming-plugin-metadata
title: "Fix Skill Naming with Plugin as Separate Metadata"
generated_by: sw:test-aware-planner
by_user_story:
  US-PLAT-001: [T-001]
  US-PLAT-002: [T-002]
  US-PLAT-003: [T-003]
  US-PLAT-004: [T-004]
  US-PLAT-005: [T-005]
  US-CLI-006: [T-006]
---

# Tasks: Fix Skill Naming with Plugin as Separate Metadata

## User Story: US-PLAT-001 - Derive Plugin Name from Skill Path

**Linked ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05
**Tasks**: 1 total, 0 completed

### T-001: Add `derivePluginName()` pure function to slug.ts

**User Story**: US-PLAT-001
**Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05
**Status**: [x] completed

**Test Plan**:
- **Given** a skill path `plugins/specweave-release/skills/release-expert/SKILL.md`
- **When** `derivePluginName()` is called
- **Then** it returns `"specweave-release"`

- **Given** a path with no `plugins/` segment (e.g., `skills/architect/SKILL.md`)
- **When** `derivePluginName()` is called
- **Then** it returns `null`

- **Given** `null` or `undefined` input
- **When** `derivePluginName()` is called
- **Then** it returns `null` without throwing

**Test Cases**:
1. **Unit**: `repositories/anton-abyzov/vskill-platform/src/lib/__tests__/slug.test.ts`
   - `derivePluginName_withPluginPath_returnsPluginFolderName()`: path `plugins/specweave-release/skills/release-expert/SKILL.md` -> `"specweave-release"`
   - `derivePluginName_withShortPluginPath_returnsShortName()`: path `plugins/sw/skills/pm/SKILL.md` -> `"sw"`
   - `derivePluginName_withNoPluginsSegment_returnsNull()`: path `skills/architect/SKILL.md` -> `null`
   - `derivePluginName_withRootSkillMd_returnsNull()`: path `SKILL.md` -> `null`
   - `derivePluginName_withNull_returnsNull()`: input `null` -> `null`
   - `derivePluginName_withUndefined_returnsNull()`: input `undefined` -> `null`
   - `derivePluginName_withBackslashes_normalizesAndReturnsPluginName()`: Windows-style path returns correct plugin name
   - **Coverage Target**: 95%

**Implementation**:
1. Open `repositories/anton-abyzov/vskill-platform/src/lib/__tests__/slug.test.ts` -- write failing tests first (TDD red)
2. Open `repositories/anton-abyzov/vskill-platform/src/lib/slug.ts` -- add `derivePluginName()` export after existing slug utilities
3. Algorithm: normalize backslashes -> find `plugins/` segment -> return immediate child folder name or `null`
4. Run `npx vitest run src/lib/__tests__/slug.test.ts` -- all tests must pass (TDD green)

---

## User Story: US-PLAT-002 - Set Plugin Name During Publish

**Linked ACs**: AC-US2-01, AC-US2-02, AC-US2-03
**Tasks**: 1 total, 0 completed

### T-002: Wire `derivePluginName()` into `publishSkill()` in submission-store.ts

**User Story**: US-PLAT-002
**Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03
**Status**: [x] completed

**Test Plan**:
- **Given** a submission with `skillPath = "plugins/foo/skills/bar/SKILL.md"`
- **When** `publishSkill()` is called
- **Then** the DB upsert includes `pluginName: "foo"` in both create and update branches

- **Given** a submission with `skillPath = "skills/bar/SKILL.md"`
- **When** `publishSkill()` is called
- **Then** the DB upsert includes `pluginName: null`

- **Given** a skill re-published with a new path changing the plugin folder
- **When** `publishSkill()` is called
- **Then** `pluginName` in the update branch reflects the newly derived value

**Test Cases**:
1. **Unit**: `repositories/anton-abyzov/vskill-platform/src/lib/__tests__/submission-store.test.ts`
   - `publishSkill_withPluginPath_setsPluginName()`: verifies upsert called with `pluginName: "foo"`
   - `publishSkill_withNonPluginPath_setsPluginNameNull()`: verifies upsert called with `pluginName: null`
   - `publishSkill_onRepublish_updatesPluginName()`: verifies update branch also sets `pluginName`
   - **Coverage Target**: 90%

**Implementation**:
1. Add failing tests to `submission-store.test.ts` for pluginName behavior (TDD red)
2. Add `derivePluginName` to the import from `./slug` in `submission-store.ts`
3. Before the `db.skill.upsert()` call in `publishSkill()`, compute `const pluginNameVal = derivePluginName(sub.skillPath)`
4. Add `pluginName: pluginNameVal` to both `create` and `update` data objects in the upsert
5. Run `npx vitest run src/lib/__tests__/submission-store.test.ts` (TDD green)

---

## User Story: US-PLAT-003 - Backfill Plugin Name for Legacy Records

**Linked ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04, AC-US3-05
**Tasks**: 1 total, 0 completed

### T-003: Extend `backfill-slugs` route to populate `pluginName`

**User Story**: US-PLAT-003
**Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04, AC-US3-05
**Status**: [x] completed

**Test Plan**:
- **Given** a skill record with `skillPath = "plugins/specweave-release/skills/release-expert/SKILL.md"`
- **When** the backfill endpoint is called (non-dry-run)
- **Then** the DB update includes `pluginName: "specweave-release"`

- **Given** a skill record with `skillPath = null`
- **When** the backfill endpoint is called
- **Then** the record is skipped with no error and no DB update for that skill

- **Given** `dryRun=true`
- **When** the backfill endpoint is called
- **Then** the response contains the planned `pluginName` changes without any DB mutations

**Test Cases**:
1. **Unit**: `repositories/anton-abyzov/vskill-platform/src/app/api/v1/admin/backfill-slugs/__tests__/route.test.ts`
   - `backfill_withPluginPath_setsPluginName()`: DB update called with correct pluginName
   - `backfill_withNullSkillPath_skipsRecord()`: no DB update for null-path skills
   - `backfill_withNonPluginPath_setsPluginNameNull()`: update called with `pluginName: null`
   - `backfill_dryRun_includesPluginNameInChanges()`: response body contains pluginName field, no DB mutations
   - `backfill_idempotent_safeToRunTwice()`: second run produces same result
   - **Coverage Target**: 90%

**Implementation**:
1. Write failing tests for backfill pluginName behavior (TDD red)
2. Import `derivePluginName` from `@/lib/slug` in `backfill-slugs/route.ts`
3. Extend `Change` interface to add `pluginName: string | null`
4. Add `skillPath: true` to the `findMany` select clause if not already present
5. In the skills loop, compute `pluginNameVal = derivePluginName(skill.skillPath)` alongside existing slug derivation
6. Include `pluginName: pluginNameVal` in the `db.skill.update()` data object
7. Include `pluginName` in the dry-run `changes` array entries
8. Run `npx vitest run` to confirm green (TDD green)

---

## User Story: US-PLAT-004 - Show Plugin Badge in Search and List UI

**Linked ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04
**Tasks**: 1 total, 0 completed

### T-004: Add teal plugin badge to SearchPalette and skills list page

**User Story**: US-PLAT-004
**Satisfies ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04
**Status**: [x] completed

**Test Plan**:
- **Given** a search result with `pluginName = "specweave-release"`
- **When** the SearchPalette renders that result
- **Then** a teal pill badge with text "specweave-release" appears in the result row

- **Given** a skill in the list with `pluginName = null`
- **When** the skills list page renders
- **Then** no plugin badge appears for that skill

- **Given** a skill with `pluginName` set
- **When** the user views the badge
- **Then** it has no anchor or button wrapper (purely informational)

**Test Cases**:
1. **Unit**: `repositories/anton-abyzov/vskill-platform/src/app/components/__tests__/SearchPalette.test.tsx`
   - `SearchPalette_withPluginName_showsTealBadge()`: renders badge with plugin name text
   - `SearchPalette_withoutPluginName_hidesBadge()`: no badge element in output
   - `SearchPalette_pluginBadge_isNotClickable()`: no anchor or button wrapping the badge
   - **Coverage Target**: 85%

2. **Unit**: `repositories/anton-abyzov/vskill-platform/src/app/skills/__tests__/page.test.tsx`
   - `SkillsListPage_withPluginName_showsTealBadge()`: badge rendered for skill with pluginName
   - `SkillsListPage_withoutPluginName_hidesBadge()`: no badge for skill without pluginName
   - **Coverage Target**: 85%

**Implementation**:
1. Write failing tests for SearchPalette badge (TDD red)
2. In `SearchPalette.tsx` -- after the publisher badge in the name flex row, add:
   `{item.pluginName && <span style={tealBadgeStyle}>{item.pluginName}</span>}`
   Teal style: `fontSize: "0.5625rem"`, padding `0.05rem 0.3rem`, borderRadius `3px`, color `#0D9488`, bg `rgba(13,148,136,0.1)`, border `1px solid rgba(13,148,136,0.3)`, whiteSpace `nowrap`, flexShrink `0`
3. Write failing tests for skills list page badge (TDD red)
4. In `skills/page.tsx` -- after `PublisherLink` in the baseline flex div, add the same conditional badge with slightly larger padding/radius per plan
5. Run `npx vitest run` to confirm green (TDD green)

---

## User Story: US-PLAT-005 - Show Plugin Badge on Skill Detail Page

**Linked ACs**: AC-US5-01, AC-US5-02, AC-US5-03
**Tasks**: 1 total, 0 completed

### T-005: Add teal plugin badge to skill detail page byline

**User Story**: US-PLAT-005
**Satisfies ACs**: AC-US5-01, AC-US5-02, AC-US5-03
**Status**: [x] completed

**Test Plan**:
- **Given** a skill detail page where the skill has `pluginName = "specweave-release"`
- **When** the page renders
- **Then** the teal badge appears in the byline row, after the repo link and before the skillPath

- **Given** a skill detail page where `pluginName = null`
- **When** the page renders
- **Then** no plugin badge appears anywhere in the byline

- **Given** a skill detail page with `pluginName` set
- **When** the user inspects the page structure
- **Then** the badge does not appear in the page `<h1>` title or header area

**Test Cases**:
1. **Unit**: `repositories/anton-abyzov/vskill-platform/src/app/skills/[owner]/[repo]/[skill]/__tests__/page.test.tsx`
   - `SkillDetailPage_withPluginName_showsBadgeInByline()`: badge with plugin name in byline section
   - `SkillDetailPage_withoutPluginName_noBadge()`: no badge element rendered
   - `SkillDetailPage_pluginBadge_notInTitle()`: badge absent from h1/title area
   - **Coverage Target**: 85%

**Implementation**:
1. Write failing tests for skill detail page badge (TDD red)
2. Open `repositories/anton-abyzov/vskill-platform/src/app/skills/[owner]/[repo]/[skill]/page.tsx`
3. After the `RepoHealthBadge` block and before the `skillPath` block in the byline row, add:
   ```tsx
   {skill.pluginName && (
     <>
       <span style={bylineSep}>.</span>
       <span style={{fontFamily: MONO, fontSize: "0.6875rem", fontWeight: 600,
         textTransform: "uppercase", padding: "0.1rem 0.35rem", borderRadius: "4px",
         color: "#0D9488", backgroundColor: "rgba(13,148,136,0.1)",
         border: "1px solid rgba(13,148,136,0.3)"}}>
         {skill.pluginName}
       </span>
     </>
   )}
   ```
4. Run `npx vitest run` to confirm green (TDD green)

---

## User Story: US-CLI-006 - Show Plugin Badge in CLI Find Output

**Linked ACs**: AC-US6-01, AC-US6-02, AC-US6-03
**Tasks**: 1 total, 0 completed

### T-006: Add plugin name suffix to `vskill find` TTY and piped output

**User Story**: US-CLI-006
**Satisfies ACs**: AC-US6-01, AC-US6-02, AC-US6-03
**Status**: [x] completed

**Test Plan**:
- **Given** a TTY terminal and a skill result with `pluginName = "specweave-release"`
- **When** `vskill find` is run
- **Then** the output line includes `[specweave-release]` in dim styling after the skill name

- **Given** a skill result with `pluginName = null` in TTY mode
- **When** `vskill find` is run
- **Then** no bracketed suffix appears in the output line

- **Given** piped (non-TTY) mode and a skill with `pluginName = "specweave-release"`
- **When** `vskill find` output is piped
- **Then** the tab-separated output includes `pluginName` as an additional field

**Test Cases**:
1. **Unit**: `repositories/anton-abyzov/vskill/src/commands/__tests__/find.test.ts`
   - `findCommand_ttyMode_withPluginName_showsDimBracketedSuffix()`: output includes `[specweave-release]`
   - `findCommand_ttyMode_withoutPluginName_noSuffix()`: no bracketed text in output
   - `findCommand_pipedMode_withPluginName_includesTabField()`: tab-separated line ends with `\tspecweave-release`
   - `findCommand_pipedMode_withoutPluginName_noExtraField()`: standard tab count, no trailing plugin field
   - **Coverage Target**: 85%

**Implementation**:
1. Write failing tests for find.ts TTY and piped output (TDD red)
2. Open `repositories/anton-abyzov/vskill/src/commands/find.ts`
3. In TTY mode display loop -- after stars/trust badge, compute:
   `const pluginSuffix = r.pluginName ? \`  ${dim(\`[${r.pluginName}]\`)}\` : "";`
   Append `pluginSuffix` to the `console.log` line
4. In non-TTY mode output -- compute:
   `const pluginField = r.pluginName ? \`\t${r.pluginName}\` : "";`
   Append `pluginField` to the tab-separated `console.log` line
5. Run `npx vitest run src/commands/__tests__/find.test.ts` (TDD green)
