---
increment: 0446-rename-authors-to-publishers
title: Rename Authors to Publishers + Show publisher/skill-name Format
status: completed
priority: P1
type: feature
created: 2026-03-07T00:00:00.000Z
---

# Rename Authors to Publishers + Show publisher/skill-name Format

## Problem Statement

The vskill-platform UI uses "Authors" to refer to skill owners, but "Publishers" better reflects their role: they publish skills to the marketplace. Additionally, skills are currently shown by name alone, which can be ambiguous when multiple publishers have similarly named skills. Adopting a `publisher/skill-name` display format (analogous to GitHub's `owner/repo`) eliminates ambiguity.

## Goals

- Rename all user-facing "Authors" terminology to "Publishers" across the platform UI
- Introduce `publisher/skill-name` display format on skill listings and detail pages
- Maintain full backwards compatibility for API consumers (CLI) and existing bookmarks
- Keep database schema and KV cache key values unchanged to avoid migration risk

## User Stories

### US-001: URL Rename with Backwards-Compatible Redirects
**Project**: vskill-platform
**As a** site visitor
**I want** publisher pages served at `/publishers` and `/publishers/[name]`
**So that** the URL structure reflects the new terminology while old bookmarks still work

**Acceptance Criteria**:
- [ ] **AC-US1-01**: Given a request to `/publishers`, when the page loads, then the publishers listing page renders with correct data
- [ ] **AC-US1-02**: Given a request to `/publishers/[name]`, when the page loads, then the individual publisher detail page renders with that publisher's skills and stats
- [ ] **AC-US1-03**: Given a request to `/authors`, when the server responds, then a 301 redirect is issued to `/publishers`
- [ ] **AC-US1-04**: Given a request to `/authors/[name]`, when the server responds, then a 301 redirect is issued to `/publishers/[name]`
- [ ] **AC-US1-05**: Given the Next.js app directory, when inspecting `src/app/`, then `src/app/authors/` no longer exists and all pages live under `src/app/publishers/`

---

### US-002: UI Text and Navigation Rename
**Project**: vskill-platform
**As a** site visitor
**I want** all visible text reading "Authors" replaced with "Publishers"
**So that** the terminology is consistent throughout the interface

**Acceptance Criteria**:
- [ ] **AC-US2-01**: Given the desktop navigation bar in `layout.tsx`, when the page loads, then the nav link reads "Publishers" and points to `/publishers`
- [ ] **AC-US2-02**: Given the mobile navigation in `MobileNav.tsx`, when the menu opens, then the link reads "Publishers" and points to `/publishers`
- [ ] **AC-US2-03**: Given the publishers listing page, when rendered, then the page title, headings, and search placeholder use "Publishers" instead of "Authors"
- [ ] **AC-US2-04**: Given the publisher detail page, when rendered, then all headings and labels use "Publisher" instead of "Author"

---

### US-003: Skill Display with publisher/skill-name Format
**Project**: vskill-platform
**As a** user browsing skills
**I want** skills displayed as `publisher/skill-name` with the publisher part being a clickable link
**So that** I can quickly identify who published a skill and navigate to their profile

**Acceptance Criteria**:
- [ ] **AC-US3-01**: Given a skill card or listing entry, when rendered, then the skill is displayed as `publisher/skill-name` (e.g., `specweave/architect`)
- [ ] **AC-US3-02**: Given the `publisher/skill-name` display, when the user clicks the publisher portion, then they are navigated to `/publishers/[publisher-name]`
- [ ] **AC-US3-03**: Given the skill detail page at `/skills/[name]`, when rendered, then the publisher attribution shows the `publisher/skill-name` format with a clickable publisher link
- [ ] **AC-US3-04**: Given the `AuthorLink` component, when renamed to `PublisherLink`, then all imports across the codebase are updated and the component renders the new format

---

### US-004: TypeScript Type and Function Renames
**Project**: vskill-platform
**As a** developer maintaining the codebase
**I want** all author-related TypeScript types, interfaces, and functions renamed to use "publisher" terminology
**So that** the code is internally consistent with the UI terminology

**Acceptance Criteria**:
- [ ] **AC-US4-01**: Given `src/lib/types.ts`, when inspected, then `AuthorSummary` is renamed to `PublisherSummary`, `AuthorFilters` to `PublisherFilters`, and `AuthorRepo` to `PublisherRepo`
- [ ] **AC-US4-02**: Given `src/lib/data.ts`, when inspected, then `getAuthors` is renamed to `getPublishers`, `getAuthorCount` to `getPublisherCount`, `getAuthorStats` to `getPublisherStats`, `getAuthorBlockedSkills` to `getPublisherBlockedSkills`, and `getAuthorRepos` to `getPublisherRepos`
- [ ] **AC-US4-03**: Given all files importing renamed types or functions, when the codebase compiles, then zero TypeScript errors related to missing author-named exports
- [ ] **AC-US4-04**: Given the Prisma schema, when inspected, then the `author` column name is unchanged (backwards compatibility)
- [ ] **AC-US4-05**: Given `src/lib/cron/authors-cache-refresh.ts`, when inspected, then the file is renamed to `publishers-cache-refresh.ts` with updated function names and all imports updated

---

### US-005: CSS Class and File Renames
**Project**: vskill-platform
**As a** developer maintaining the codebase
**I want** CSS classes and component file names using "author" renamed to "publisher"
**So that** styling selectors match the new terminology

**Acceptance Criteria**:
- [ ] **AC-US5-01**: Given `src/app/globals.css`, when inspected, then all `.author-*` CSS classes are renamed to `.publisher-*` (e.g., `.author-card` becomes `.publisher-card`)
- [ ] **AC-US5-02**: Given component files referencing `.author-*` class names in JSX, when inspected, then they reference the new `.publisher-*` class names
- [ ] **AC-US5-03**: Given `src/app/components/AuthorLink.tsx`, when inspected, then the file is renamed to `PublisherLink.tsx`
- [ ] **AC-US5-04**: Given `src/app/authors/AuthorsSearch.tsx` and `src/app/authors/[name]/AuthorSkillsList.tsx`, when the pages are moved to `src/app/publishers/`, then these component files are renamed to `PublishersSearch.tsx` and `PublisherSkillsList.tsx` respectively

## Out of Scope

- **API route paths**: `/api/v1/authors/*` endpoints remain unchanged for CLI backwards compatibility
- **Database schema**: The `author` column in Prisma remains as-is; no migration needed
- **KV cache key values**: Existing `authors:*` cache key strings in KV storage are unchanged; only TS constant names referencing them are renamed
- **SEO/sitemap updates**: Not included in this increment (can follow up separately)
- **i18n/localization**: Single-language rename only

## Technical Notes

### Dependencies
- Next.js `redirects` config in `next.config.ts` for 301 redirects
- No database migration required
- No external service changes

### Constraints
- API v1 paths must remain stable -- the vskill CLI depends on `/api/v1/authors/*`
- Prisma queries will still reference `author` field internally even though TS wrappers say "publisher"
- The `AuthorLink` component rename to `PublisherLink` touches many importing files

### Key Files Affected
- `src/app/authors/` (entire directory moves to `src/app/publishers/`)
- `src/app/components/AuthorLink.tsx` (rename to `PublisherLink.tsx`)
- `src/lib/types.ts` (type renames)
- `src/lib/data.ts` (function renames)
- `src/lib/cron/authors-cache-refresh.ts` (file + function renames)
- `src/app/globals.css` (CSS class renames)
- `src/app/layout.tsx`, `src/app/components/MobileNav.tsx` (nav text)
- `src/app/skills/[name]/page.tsx`, `src/app/skills/page.tsx` (publisher/skill-name display)
- `next.config.ts` (301 redirects)

## Success Metrics

- Zero broken links: all `/authors/*` requests 301-redirect to `/publishers/*`
- Zero TypeScript compilation errors after rename
- All existing tests pass with updated imports
- CLI backwards compatibility: `/api/v1/authors/*` endpoints respond identically
