---
increment: 0446-rename-authors-to-publishers
title: "Rename Authors to Publishers + Show publisher/skill-name Format"
by_user_story:
  US-001: [T-007, T-008]
  US-002: [T-006]
  US-003: [T-009, T-010]
  US-004: [T-001, T-002, T-003]
  US-005: [T-004, T-005]
---

# Tasks: Rename Authors to Publishers + Show publisher/skill-name Format

> Execution order follows plan phases (types-first for compiler-driven verification).

---

## User Story: US-004 - TypeScript Type and Function Renames

**Linked ACs**: AC-US4-01, AC-US4-02, AC-US4-03, AC-US4-04, AC-US4-05
**Tasks**: 3 total, 0 completed

---

### T-001: Rename types in src/lib/types.ts

**User Story**: US-004
**Satisfies ACs**: AC-US4-01, AC-US4-03, AC-US4-04
**Status**: [x] completed

**Test Plan**:
- **Given** `src/lib/types.ts` exports `AuthorSummary`, `AuthorFilters`, `AuthorRepo`
- **When** each interface is renamed to its `Publisher*` equivalent
- **Then** `npx tsc --noEmit` produces compile errors in all files still importing the old names (serving as the diff checklist), `SkillData.author` and `SkillFilters.author` fields remain unchanged, and after all downstream files are updated the compiler emits zero errors

**Test Cases**:
1. **Unit**: `src/lib/__tests__/types.test.ts` (update existing or create)
   - `testPublisherSummaryShape()`: Assert `PublisherSummary` has expected fields (login, name, avatar_url, etc.)
   - `testAuthorFieldPreserved()`: Assert `SkillData.author` still exists as a string field
   - **Coverage Target**: 90%

2. **Compile verification**:
   - After rename: `npx tsc --noEmit 2>&1 | grep -c "AuthorSummary\|AuthorFilters\|AuthorRepo"` -- count should be zero after all files updated
   - **Coverage Target**: 100% of type references resolved

**Implementation**:
1. In `src/lib/types.ts`: rename `AuthorSummary` -> `PublisherSummary`, `AuthorFilters` -> `PublisherFilters`, `AuthorRepo` -> `PublisherRepo`
2. Update section comment `// ---- Author browsing ----` -> `// ---- Publisher browsing ----`
3. Do NOT rename `SkillData.author`, `SkillFilters.author` fields
4. Run `npx tsc --noEmit` -- collect all files with errors (they are the update checklist for T-002, T-003)

---

### T-002: Rename functions in src/lib/data.ts

**User Story**: US-004
**Satisfies ACs**: AC-US4-02, AC-US4-03
**Status**: [x] completed

**Test Plan**:
- **Given** `src/lib/data.ts` exports `getAuthors`, `getAuthorCount`, `getAuthorStats`, `getAuthorBlockedSkills`, `getAuthorRepos`
- **When** each function is renamed to its `getPublisher*` equivalent
- **Then** internal Prisma queries referencing `by: ["author"]` and `where: { author: ... }` remain unchanged, all imports of the old names in other files produce TypeScript errors (driving file-by-file update), and after all callers are updated `npx tsc --noEmit` passes

**Test Cases**:
1. **Unit**: `src/lib/__tests__/data.test.ts` (update existing)
   - `testGetPublishers()`: Mock Prisma, assert `getPublishers()` returns `PublisherSummary[]`
   - `testGetPublisherCount()`: Assert returns numeric count
   - `testGetPublisherStats()`: Assert returns stats shape for a given login
   - **Coverage Target**: 85%

2. **Integration**: Verify API routes at `/api/v1/authors/` still compile and respond correctly (imports updated, paths unchanged)

**Implementation**:
1. In `src/lib/data.ts`: rename all five exported functions
2. Update internal variable names (e.g., `authorStats` -> `publisherStats`) and `console.warn` tags
3. Do NOT change Prisma query fields (`by: ["author"]`, `where: { author: ... }`)
4. Update all callers identified by `tsc --noEmit` errors:
   - `src/app/api/v1/authors/route.ts`
   - `src/app/api/v1/authors/[name]/route.ts`
   - `src/lib/trust/taint-backfill.ts`
   - Any page files still under `src/app/authors/` (will be moved in T-007)
5. Run `npx vitest run src/lib/__tests__/data.test.ts`

---

### T-003: Rename cache/cron utility files and update all importers

**User Story**: US-004
**Satisfies ACs**: AC-US4-05, AC-US4-03
**Status**: [x] completed

**Test Plan**:
- **Given** `src/lib/cache/author-cache.ts` and `src/lib/cron/authors-cache-refresh.ts` exist with author-prefixed exports
- **When** both files are renamed and their exported symbols updated (keeping KV string values unchanged)
- **Then** all importers compile without errors, KV string values `"authors:detail:"`, `"authors:list:"`, `"authors:skills:"` remain identical at runtime, and `npx tsc --noEmit` passes

**Test Cases**:
1. **Unit**: `src/lib/cache/__tests__/publisher-cache.test.ts` (rename from author-cache.test.ts if exists, else create)
   - `testKVDetailValueUnchanged()`: Assert `PUBLISHER_DETAIL_PREFIX === "authors:detail:"`
   - `testKVListValueUnchanged()`: Assert `PUBLISHER_LIST_PREFIX === "authors:list:"`
   - `testInvalidatePublisherCaches()`: Mock KV, assert all three prefixes are deleted
   - **Coverage Target**: 90%

2. **Unit**: `src/lib/cron/__tests__/publishers-cache-refresh.test.ts`
   - `testRefreshPublishersCache()`: Mock KV + fetch, assert cache refresh runs and sets correct keys
   - **Coverage Target**: 85%

**Implementation**:
1. `git mv src/lib/cache/author-cache.ts src/lib/cache/publisher-cache.ts`
2. Inside `publisher-cache.ts`: rename exports `AUTHOR_DETAIL_PREFIX` -> `PUBLISHER_DETAIL_PREFIX`, `AUTHOR_SKILLS_PREFIX` -> `PUBLISHER_SKILLS_PREFIX`, `AUTHOR_LIST_PREFIX` -> `PUBLISHER_LIST_PREFIX`, `invalidateAuthorCaches` -> `invalidatePublisherCaches` (keep all string values unchanged)
3. `git mv src/lib/cron/authors-cache-refresh.ts src/lib/cron/publishers-cache-refresh.ts`
4. Inside `publishers-cache-refresh.ts`: rename `AUTHORS_CACHE_PREFIX` -> `PUBLISHERS_CACHE_PREFIX`, `refreshAuthorsCache` -> `refreshPublishersCache` (keep string value unchanged)
5. Update all importers: `src/lib/submission-store.ts`, `src/app/api/v1/admin/taint-rescan/route.ts`, `src/app/api/v1/admin/repo-block/route.ts`, `src/app/api/v1/admin/skills/[name]/block/route.ts`, `src/app/api/v1/authors/[name]/route.ts`, cron worker entrypoint
6. Run `npx vitest run` to confirm no test regressions

---

## User Story: US-005 - CSS Class and File Renames

**Linked ACs**: AC-US5-01, AC-US5-02, AC-US5-03, AC-US5-04
**Tasks**: 2 total, 0 completed

---

### T-004: Rename AuthorLink component to PublisherLink with skillName prop

**User Story**: US-005
**Satisfies ACs**: AC-US5-03, AC-US3-04
**Status**: [x] completed

**Test Plan**:
- **Given** `src/app/components/AuthorLink.tsx` renders a clickable author link to `/authors/[name]`
- **When** the file is renamed to `PublisherLink.tsx`, the component renamed to `PublisherLink`, and an optional `skillName` prop added
- **Then** `<PublisherLink author="specweave" />` renders identical output to before (backwards compatible), `<PublisherLink author="specweave" skillName="architect" />` renders `specweave/architect` with the publisher portion as a clickable link to `/publishers/specweave`, and all existing callers compile after their imports are updated

**Test Cases**:
1. **Unit**: `src/app/components/__tests__/PublisherLink.test.tsx` (create)
   - `testBasicRender()`: `<PublisherLink author="specweave" />` renders link to `/publishers/specweave`
   - `testWithSkillName()`: `<PublisherLink author="specweave" skillName="architect" />` renders `specweave/architect` text
   - `testPublisherLinkClickable()`: Publisher portion navigates to `/publishers/specweave`
   - `testBackwardsCompatible()`: No `skillName` prop -- renders same as old `AuthorLink`
   - **Coverage Target**: 95%

**Implementation**:
1. `git mv src/app/components/AuthorLink.tsx src/app/components/PublisherLink.tsx`
2. Inside `PublisherLink.tsx`: rename `AuthorLinkProps` -> `PublisherLinkProps`, add optional `skillName?: string` prop, rename function `AuthorLink` -> `PublisherLink`, update href from `/authors/...` to `/publishers/...`, update CSS class `author-link` -> `publisher-link`
3. Implement `skillName` rendering per plan: `{author}` as clickable, then `/{skillName}` in muted color when provided
4. Update all importers found by `tsc --noEmit`: skill pages, publisher pages
5. Run `npx vitest run src/app/components/__tests__/PublisherLink.test.tsx`

---

### T-005: Rename CSS classes from .author-* to .publisher-* and update all JSX references

**User Story**: US-005
**Satisfies ACs**: AC-US5-01, AC-US5-02
**Status**: [x] completed

**Test Plan**:
- **Given** `src/app/globals.css` defines `.author-card`, `.authors-grid`, `.author-link`, `.author-link:hover` and component JSX files reference these class names
- **When** all CSS class definitions are renamed to `.publisher-*` and all JSX `className` references are updated in the same operation
- **Then** no `.author-` class names remain in either CSS or TSX/JSX files (verified by grep), styles render correctly in the browser (no broken styling)

**Test Cases**:
1. **Static analysis**:
   - `grep -r "author-card\|authors-grid\|author-link" src/` -- must return zero matches after rename
   - `grep -r "publisher-card\|publishers-grid\|publisher-link" src/app/globals.css` -- must return all expected class definitions
   - **Coverage Target**: 100% (zero missed references)

2. **Visual regression** (manual): Load `/publishers` page and confirm card grid renders with correct spacing and hover states

**Implementation**:
1. Grep all TSX/JSX files for `.author-card`, `.authors-grid`, `.author-link` to build exhaustive list: `grep -rn "author-card\|authors-grid\|author-link" src/`
2. In `src/app/globals.css`: rename `.authors-grid` -> `.publishers-grid`, `.author-card` -> `.publisher-card`, `.author-link` -> `.publisher-link` (including `:hover` variants and responsive media query references)
3. In each TSX/JSX file from step 1: update `className` strings to the new `.publisher-*` names
4. Run `grep -r "className.*author" src/` to verify zero remaining author CSS class references

---

## User Story: US-001 - URL Rename with Backwards-Compatible Redirects

**Linked ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04, AC-US1-05
**Tasks**: 2 total, 0 completed

---

### T-007: Move src/app/authors/ directory to src/app/publishers/ and rename internal components

**User Story**: US-001
**Satisfies ACs**: AC-US1-01, AC-US1-02, AC-US1-05, AC-US5-04
**Status**: [x] completed

**Test Plan**:
- **Given** `src/app/authors/` contains `page.tsx`, `AuthorsSearch.tsx`, `[name]/page.tsx`, `[name]/AuthorSkillsList.tsx`, `[name]/CollapsibleRepos.tsx`
- **When** the directory is moved to `src/app/publishers/` using `git mv` and internal component files renamed
- **Then** `src/app/authors/` no longer exists, `/publishers` route resolves in Next.js, `/publishers/[name]` route resolves, all internal imports within the moved files remain valid (path depth unchanged), and `npx tsc --noEmit` passes

**Test Cases**:
1. **Route resolution**:
   - `GET /publishers` returns HTTP 200 with publishers listing HTML
   - `GET /publishers/specweave` returns HTTP 200 with publisher detail HTML
   - `ls src/app/authors` -- directory must not exist after move
   - **Coverage Target**: 100% of routes

2. **Unit**: `src/app/publishers/__tests__/page.test.tsx` (rename from authors test if exists)
   - `testPublishersPageRenders()`: Mock data functions, assert publishers listing renders with `PublisherSummary[]` data
   - **Coverage Target**: 85%

**Implementation**:
1. Ensure T-001 through T-005 are complete (types, data functions, cache symbols, component renamed)
2. `git mv src/app/authors src/app/publishers`
3. `git mv src/app/publishers/AuthorsSearch.tsx src/app/publishers/PublishersSearch.tsx`
4. `git mv src/app/publishers/[name]/AuthorSkillsList.tsx src/app/publishers/[name]/PublisherSkillsList.tsx`
5. Inside moved files, update:
   - Component names (`AuthorsSearch` -> `PublishersSearch`, `AuthorSkillsList` -> `PublisherSkillsList`)
   - Imports of renamed types (`PublisherSummary`, `PublisherFilters`, etc.)
   - Imports of renamed data functions (`getPublishers`, `getPublisherStats`, etc.)
   - Imports of renamed cache symbols (`PUBLISHER_DETAIL_PREFIX`)
   - Any hardcoded `/authors/` URLs in JSX -> `/publishers/`
   - Import of `PublisherLink` from `../../components/PublisherLink`
6. Run `npx tsc --noEmit` and fix any remaining errors
7. Run `npx vitest run`

---

### T-008: Add 301 redirects for /authors and /authors/:path* in next.config.ts

**User Story**: US-001
**Satisfies ACs**: AC-US1-03, AC-US1-04
**Status**: [x] completed

**Test Plan**:
- **Given** `next.config.ts` has no redirect rules for `/authors`
- **When** a `redirects()` async function is added returning permanent redirects for `/authors` and `/authors/:path*`
- **Then** a request to `/authors` receives HTTP 301 with `Location: /publishers`, a request to `/authors/specweave` receives HTTP 301 with `Location: /publishers/specweave`, and the Next.js build compiles without error

**Test Cases**:
1. **Unit**: `src/__tests__/redirects.test.ts` (create)
   - `testAuthorsRedirectsConfig()`: Load Next.js redirect config, assert two rules exist with `permanent: true`
   - `testRootRedirect()`: Assert source `/authors` maps to destination `/publishers`
   - `testWildcardRedirect()`: Assert source `/authors/:path*` maps to destination `/publishers/:path*`
   - **Coverage Target**: 100%

2. **Smoke test** (manual after deploy):
   - `curl -I http://localhost:3000/authors` -- verify `HTTP/1.1 301` and `Location: /publishers`
   - `curl -I http://localhost:3000/authors/specweave` -- verify `HTTP/1.1 301` and `Location: /publishers/specweave`

**Implementation**:
1. Open `next.config.ts`
2. Add `async redirects()` method returning:
   ```ts
   [
     { source: "/authors", destination: "/publishers", permanent: true },
     { source: "/authors/:path*", destination: "/publishers/:path*", permanent: true },
   ]
   ```
3. Ensure existing config properties (`output`, `serverExternalPackages`, `outputFileTracingRoot`, etc.) are preserved
4. Run `npx tsc --noEmit` to confirm config file compiles
5. Run `npx vitest run src/__tests__/redirects.test.ts`

---

## User Story: US-002 - UI Text and Navigation Rename

**Linked ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04
**Tasks**: 1 total, 0 completed

---

### T-006: Update navigation and page text from Authors to Publishers

**User Story**: US-002
**Satisfies ACs**: AC-US2-01, AC-US2-02, AC-US2-03, AC-US2-04
**Status**: [x] completed

**Test Plan**:
- **Given** `src/app/layout.tsx` and `src/app/components/MobileNav.tsx` contain nav links with text "Authors" pointing to `/authors`, and publishers listing/detail pages render headings with "Authors"/"Author"
- **When** all nav link text and hrefs, page titles, headings, search placeholders, and labels are updated to "Publishers"/"Publisher"
- **Then** no visible "Authors" or "Author" text appears in the navigation or publishers pages (confirmed by grep and visual check), and all hrefs in nav point to `/publishers`

**Test Cases**:
1. **Unit**: `src/app/__tests__/layout.test.tsx` (create or update)
   - `testDesktopNavPublishersLink()`: Assert nav contains link with text "Publishers" and `href="/publishers"`
   - `testFooterPublishersLink()`: Assert footer contains link to `/publishers`
   - **Coverage Target**: 90%

2. **Unit**: `src/app/components/__tests__/MobileNav.test.tsx` (create or update)
   - `testMobileNavPublishersLink()`: Assert mobile menu link reads "Publishers" with `href="/publishers"`
   - **Coverage Target**: 90%

3. **Static analysis**:
   - `grep -n "Authors\|>Author<" src/app/layout.tsx src/app/components/MobileNav.tsx` -- must return zero matches after update
   - `grep -rn ">Authors<\|>Author<" src/app/publishers/` -- must return zero matches in page headings

**Implementation**:
1. In `src/app/layout.tsx`:
   - Desktop nav: `href="/authors"` -> `href="/publishers"`, text `Authors` -> `Publishers`
   - Footer: same changes
2. In `src/app/components/MobileNav.tsx`: `href="/authors"` -> `href="/publishers"`, text `Authors` -> `Publishers`
3. In `src/app/publishers/page.tsx` (after T-007): update page `<title>`, `<h1>`, search placeholder from "Authors"/"Author" to "Publishers"/"Publisher"
4. In `src/app/publishers/[name]/page.tsx` (after T-007): update headings and labels from "Author" to "Publisher"
5. Run `npx vitest run`

---

## User Story: US-003 - Skill Display with publisher/skill-name Format

**Linked ACs**: AC-US3-01, AC-US3-02, AC-US3-03, AC-US3-04
**Tasks**: 2 total, 0 completed

---

### T-009: Update skill listing page to display publisher/skill-name format

**User Story**: US-003
**Satisfies ACs**: AC-US3-01, AC-US3-02, AC-US3-04
**Status**: [x] completed

**Test Plan**:
- **Given** `src/app/skills/page.tsx` renders skill cards with `<AuthorLink author={skill.author} />`
- **When** the import is updated to `PublisherLink` and `skillName={skill.name}` prop is added
- **Then** each skill card displays `publisher/skill-name` text (e.g., `specweave/architect`), the publisher portion is a clickable link navigating to `/publishers/[name]`, and the skill name portion is non-clickable muted text

**Test Cases**:
1. **Unit**: `src/app/skills/__tests__/page.test.tsx` (create or update)
   - `testSkillListPublisherFormat()`: Mock skills data with `{ author: "specweave", name: "architect" }`, assert rendered output contains `specweave/architect`
   - `testPublisherLinkHref()`: Assert publisher link `href` is `/publishers/specweave`
   - `testSkillNameNotLink()`: Assert `architect` portion has no `<a>` tag
   - **Coverage Target**: 90%

**Implementation**:
1. In `src/app/skills/page.tsx`:
   - Replace `import AuthorLink from "../components/AuthorLink"` with `import PublisherLink from "../components/PublisherLink"`
   - Replace `<AuthorLink author={skill.author} />` with `<PublisherLink author={skill.author} skillName={skill.name} />`
2. Run `npx vitest run src/app/skills/__tests__/page.test.tsx`

---

### T-010: Update skill detail page and run final compile and test verification

**User Story**: US-003
**Satisfies ACs**: AC-US3-03, AC-US3-04
**Status**: [x] completed

**Test Plan**:
- **Given** `src/app/skills/[name]/page.tsx` shows a publisher byline with `{skill.author}` text linking to `/authors/...`, and `src/app/skills/[name]/security/page.tsx` has a MetaItem label "Author"
- **When** the detail page is updated to use `<PublisherLink author={skill.author} skillName={skill.name} />` and security page label changed to "Publisher"
- **Then** the skill detail page renders `publisher/skill-name` with a clickable publisher link to `/publishers/[name]`, the security page shows "Publisher" label, and `npx tsc --noEmit` returns zero errors across the entire codebase

**Test Cases**:
1. **Unit**: `src/app/skills/[name]/__tests__/page.test.tsx` (create or update)
   - `testSkillDetailPublisherFormat()`: Mock skill `{ author: "specweave", name: "architect" }`, assert byline renders `specweave/architect`
   - `testPublisherLinkHref()`: Assert publisher link navigates to `/publishers/specweave`
   - **Coverage Target**: 90%

2. **Compile gate**: `npx tsc --noEmit` -- must exit with code 0 and zero errors

3. **Full test run**: `npx vitest run` -- all tests must pass, zero failures

4. **Grep verification** (zero matches expected):
   - `grep -rn "from.*AuthorLink\|import.*AuthorLink" src/` -- zero results
   - `grep -rn "href=.*\"/authors/" src/app/` (excluding `api/v1/authors`) -- zero results

**Implementation**:
1. In `src/app/skills/[name]/page.tsx`:
   - Update import to `PublisherLink` from `../../components/PublisherLink`
   - Replace publisher byline with `<PublisherLink author={skill.author} skillName={skill.name} />`
   - Update any `/authors/` hrefs to `/publishers/`
2. In `src/app/skills/[name]/security/page.tsx`: change MetaItem label `"Author"` -> `"Publisher"`
3. Run `npx tsc --noEmit` -- fix any remaining errors
4. Run `npx vitest run` -- confirm all pass
5. Run grep verifications to confirm no stale author references in UI paths
