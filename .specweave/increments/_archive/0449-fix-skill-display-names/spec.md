---
increment: 0449-fix-skill-display-names
title: Fix skill display names after hierarchical URL migration
type: bugfix
priority: P1
status: completed
created: 2026-03-07T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Fix Skill Display Names After Hierarchical URL Migration

## Problem Statement

Increment 0447 introduced hierarchical skill URLs (`owner/repo/skillSlug`) and stored the full hierarchical string in the `name` field. Frontend components and CLI that previously displayed `name` as a short label now show duplicated or garbled text:

1. **SearchPalette** (`SearchPalette.tsx:344`): `label: \`${r.author}/${r.name}\`` produces `dailydotdev/dailydotdev/daily/news-digest` because `r.name` is already `dailydotdev/daily/news-digest`.
2. **TrendingSkills** (`TrendingSkills.tsx:48-49`): `{skill.author}/{skill.name}` produces the same duplication.
3. **Skills browse** (`skills/page.tsx:265`): `<PublisherLink skillName={skill.name}>` passes the full hierarchical name into the component which renders `author / owner/repo/slug` instead of `author / slug`.
4. **CLI find** (`find.ts:27-29`): `formatSkillId` builds `owner/repo@owner/repo/skillSlug` by prepending the repo extracted from `repoUrl` onto an already-hierarchical `name`.

## Goals

- Display the pure skill folder name (the `skillSlug` segment) as the skill's visible name in all UI surfaces and CLI output.
- Show `ownerSlug/repoSlug` as a separate, secondary publisher/repo context label.
- Surface `ownerSlug`, `repoSlug`, and `skillSlug` fields through all intermediate data types so components never need to parse `name`.
- Backfill any NULL slug fields in the database and rebuild the KV search index with the new fields.

## User Stories

### US-001: Platform Display Fix (P1)
**Project**: vskill-platform

**As a** skill marketplace user
**I want** skill names to display as their short folder name with a separate publisher/repo label
**So that** I can quickly identify skills without seeing duplicated or garbled owner prefixes

**Acceptance Criteria**:
- [x] **AC-US1-01**: Given `SearchIndexEntry`, `SearchResult`, `TrendingSkillEntry`, and `SkillData` types, when the type definitions are inspected, then each includes `ownerSlug: string`, `repoSlug: string`, and `skillSlug: string` fields alongside the existing `name` field.
- [x] **AC-US1-02**: Given a search API response, when the search query endpoint (`/api/v1/skills/search`) returns results, then each result object includes populated `ownerSlug`, `repoSlug`, and `skillSlug` values sourced from the DB columns.
- [x] **AC-US1-03**: Given the search palette, when a user types a query and sees results, then each result label shows `skillSlug` as the primary name and `ownerSlug/repoSlug` as a secondary context (no owner duplication in the label).
- [x] **AC-US1-04**: Given the trending skills section on the homepage, when trending skills render, then each skill shows `skillSlug` as the primary name and `ownerSlug/repoSlug` as the faint publisher prefix (replacing the current `skill.author/skill.name` pattern).
- [x] **AC-US1-05**: Given the skills browse page, when `PublisherLink` receives skill data, then it receives `skillSlug` for the display name (not the full hierarchical `name`) and renders `author / skillSlug` without duplication.

---

### US-002: CLI Display Fix (P1)
**Project**: vskill

**As a** CLI user running `vskill find`
**I want** search results to show the short skill name with a clear repo identifier
**So that** I can identify and install skills without seeing duplicated `owner/repo@owner/repo/skillSlug` text

**Acceptance Criteria**:
- [x] **AC-US2-01**: Given the `SkillSearchResult` interface in the CLI API client, when the type definition is inspected, then it includes `ownerSlug?: string`, `repoSlug?: string`, and `skillSlug?: string` fields.
- [x] **AC-US2-02**: Given `vskill find <query>` output, when results render in the terminal, then the label shows `ownerSlug/repoSlug@skillSlug` (or just `skillSlug` if slug fields are absent for backwards compatibility) instead of the current `owner/repo@owner/repo/skillSlug` duplication.
- [x] **AC-US2-03**: Given a skill with a hierarchical `name` field but missing slug fields in the API response, when `formatSkillId` renders the label, then it falls back gracefully to parsing `name` into segments rather than duplicating prefixes.

## Out of Scope

- Changing the `name` field value in the DB (it stays as `owner/repo/skillSlug` for URL routing).
- Modifying the `skillUrl()` helper or URL routing logic (those already handle hierarchical names correctly).
- Changing the skill detail page layout (it already uses `[owner]/[repo]/[skill]` route params).
- Adding new DB columns (ownerSlug, repoSlug, skillSlug already exist from increment 0447).

## Technical Notes

### Data Model Context
- DB columns `ownerSlug`, `repoSlug`, `skillSlug` already exist on the `Skill` table (added in 0447 migration `20260315100000`).
- A migration script (`migrate-to-hierarchical-slugs.ts`) already populated these for many skills, but some may still have NULL values.
- The `name` field stores the full hierarchical string `owner/repo/skillSlug` and should continue to do so for URL construction.

### Key Files (vskill-platform)
- Types: `src/lib/types.ts` (SkillData), `src/lib/search-index.ts` (SearchIndexEntry), `src/lib/search.ts` (SearchResult), `src/lib/stats-compute.ts` (TrendingSkillEntry)
- Components: `src/app/components/SearchPalette.tsx`, `src/app/components/home/TrendingSkills.tsx`, `src/app/skills/page.tsx`, `src/app/components/PublisherLink.tsx`
- Data layer: search API route, stats compute, search index builder

### Key Files (vskill)
- Types: `src/api/client.ts` (SkillSearchResult)
- Display: `src/commands/find.ts` (formatSkillId)

## Success Criteria

- Zero instances of duplicated owner text in skill names across SearchPalette, TrendingSkills, skills browse, and CLI find output.
- All intermediate types carry `ownerSlug`, `repoSlug`, `skillSlug` fields.
- No NULL slug fields remain in the Skill table after backfill.
- KV search index rebuilt with new slug fields.
