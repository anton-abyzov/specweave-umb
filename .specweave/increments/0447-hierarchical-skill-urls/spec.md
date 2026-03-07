---
increment: 0447-hierarchical-skill-urls
title: "Restructure skill URLs to /{owner}/{repo}/{skill-slug}"
type: feature
priority: P1
status: completed
created: 2026-03-07
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Restructure skill URLs to /{owner}/{repo}/{skill-slug}

## Problem Statement

Skills currently use flat slugs (e.g., `dailydotdev-daily`) that obscure the source repository and create collision risks when different repos produce identically-named skills. The flat slug format makes it impossible to determine at a glance which GitHub owner and repository a skill comes from, reducing trust transparency and discoverability.

## Goals

- Replace flat skill slugs with a 3-segment hierarchical format: `{owner}/{repo}/{skill-slug}`
- Preserve all existing bookmarks and links via 301 redirects from legacy flat slugs
- Update the full stack: DB schema, URL routing, KV keys, publishing pipeline, CLI, and email templates
- Eliminate slug collision resolution entirely (owner/repo/slug is inherently unique)

## User Stories

### US-001: Hierarchical Skill URLs (P0)
**Project**: vskill-platform
**As a** user
**I want** skill URLs to follow the format `/skills/{owner}/{repo}/{skill-slug}`
**So that** I can identify the source repository directly from the URL

**Acceptance Criteria**:
- [x] **AC-US1-01**: Given a skill from `github.com/dailydotdev/daily` with SKILL.md in `plugins/news/skills/daily/SKILL.md`, when I visit `/skills/dailydotdev/daily/daily`, then the skill detail page renders correctly
- [x] **AC-US1-02**: Given Prisma schema, when the migration runs, then `Skill` model has new columns `ownerSlug`, `repoSlug`, `skillSlug`, and `legacySlug` (all non-null after migration), and the unique constraint is on `(ownerSlug, repoSlug, skillSlug)` instead of flat `name`
- [x] **AC-US1-03**: Given the `Skill.name` field, when a skill is created or updated, then `name` stores the format `owner/repo/skillSlug` (e.g., `dailydotdev/daily/daily`)
- [x] **AC-US1-04**: Given Next.js App Router, when the route `/skills/[owner]/[repo]/[skillSlug]` is requested, then the page resolves the skill by the three path segments and renders the detail page with correct badge URLs, metadata, and OG tags
- [x] **AC-US1-05**: Given KV cache entries, when a skill is published or updated, then the KV key uses the hierarchical format `skill:owner/repo/skillSlug` instead of `skill:flat-slug`

---

### US-002: Legacy URL Redirects (P0)
**Project**: vskill-platform
**As a** developer
**I want** old flat-slug URLs (`/skills/dailydotdev-daily`) to redirect to the new hierarchical URL
**So that** existing bookmarks, README badges, and external links continue to work

**Acceptance Criteria**:
- [x] **AC-US2-01**: ~~Given a skill with `legacySlug = "dailydotdev-daily"`, when a request hits `/skills/dailydotdev-daily`, then the server responds with a 301 redirect to `/skills/dailydotdev/daily/daily`~~ — DESCOPED: No backward compat needed per user decision; old routes removed entirely
- [x] **AC-US2-02**: Given the data migration, when it runs on existing skills, then every skill row has `legacySlug` populated with its current flat `name` value before the name is updated to hierarchical format
- [x] **AC-US2-03**: ~~Given the redirect route, when a slug matches no `legacySlug` and no hierarchical skill, then a 404 page is shown~~ — DESCOPED: Old routes removed entirely
- [x] **AC-US2-04**: ~~Given KV alias entries, when the migration runs, then `skill:alias:{legacySlug}` KV keys point to the new `owner/repo/skillSlug` value for fast redirect resolution without DB lookup~~ — DESCOPED: No KV aliases needed without legacy redirects

---

### US-003: Publishing Pipeline with Hierarchical Names (P0)
**Project**: vskill-platform
**As a** skill publisher
**I want** the publishing pipeline to generate hierarchical `owner/repo/skill-slug` names
**So that** newly submitted skills get correct URLs from the start

**Acceptance Criteria**:
- [x] **AC-US3-01**: Given a submission from `github.com/acme/tools` with SKILL.md at `plugins/linter/skills/eslint-helper/SKILL.md`, when `publishSkill` runs, then `Skill.name` is set to `acme/tools/eslint-helper` and `skillSlug` is `eslint-helper` (parent folder name of SKILL.md)
- [x] **AC-US3-02**: Given a submission with SKILL.md at the repository root (`SKILL.md`), when `publishSkill` runs, then `skillSlug` is derived from the repo name (e.g., repo `acme/my-skill` produces `skillSlug = "my-skill"`)
- [x] **AC-US3-03**: Given the new naming scheme, when `resolveSlug` is called, then it no longer needs hash-based collision disambiguation (owner/repo/slug is inherently unique), and the old `makeSlug` flat-slug function is deprecated
- [x] **AC-US3-04**: Given the `slug.ts` module, when updated, then a new `buildHierarchicalName(repoUrl, skillPath)` function computes `ownerSlug`, `repoSlug`, and `skillSlug` from the repo URL and SKILL.md path
- [x] **AC-US3-05**: Given email notifications (submitted, auto-approved, rejected), when sent, then skill names in subject lines and body text use the hierarchical format, and badge URLs point to the new 3-segment path

---

### US-004: CLI Compatibility with Hierarchical URLs (P1)
**Project**: vskill
**As a** CLI user
**I want** `vskill find`, `vskill add`, and `vskill submit` to work with the new hierarchical skill names
**So that** I can search, install, and submit skills using the updated URL scheme

**Acceptance Criteria**:
- [x] **AC-US4-01**: Given `vskill find react`, when the API returns skills with hierarchical names (e.g., `facebook/react/react-hooks`), then the CLI displays the name in `owner/repo/skill-slug` format and the URL as `https://verified-skill.com/skills/facebook/react/react-hooks`
- [x] **AC-US4-02**: Given the lockfile (`vskill.lock`), when a skill is installed, then the lockfile key uses the hierarchical name `owner/repo/skillSlug` instead of the flat slug
- [x] **AC-US4-03**: Given backward compatibility, when a lockfile contains old flat-slug keys, then `vskill list` and `vskill update` still read them correctly (graceful degradation)
- [x] **AC-US4-04**: Given the `vskill info <name>` command, when the user provides a hierarchical name like `acme/tools/linter`, then the CLI fetches and displays the skill detail
- [x] **AC-US4-05**: Given the blocklist check, when comparing skill names, then the check uses the hierarchical name format and the API endpoint accepts hierarchical names in the `name` query parameter

---

### US-005: Admin Interface with Hierarchical Names (P1)
**Project**: vskill-platform
**As an** admin
**I want** the admin block, delete, and submissions interfaces to work with hierarchical skill names
**So that** I can manage skills using the new URL format

**Acceptance Criteria**:
- [x] **AC-US5-01**: Given the admin skill block endpoint (`/api/v1/admin/skills/[name]/block`), when the route receives a hierarchical name with slashes, then Next.js catch-all routing (`[...name]`) correctly parses `owner/repo/skillSlug` and the block operation succeeds
- [x] **AC-US5-02**: Given the admin skill delete endpoint (`/api/v1/admin/skills/[name]/delete`), when called with a hierarchical name, then the skill is deleted and its KV entries (both hierarchical key and legacy alias) are cleaned up
- [x] **AC-US5-03**: Given the admin submissions list, when displaying pending or processed submissions, then skill names are shown in `owner/repo/skillSlug` format with links to the new URL structure
- [x] **AC-US5-04**: Given the repo-block endpoint, when a repo is blocked, then all skills from that repo (identified by `ownerSlug` + `repoSlug`) are blocked and their KV entries updated

---

### US-006: Publisher Page Skill Links (P1)
**Project**: vskill-platform
**As a** publisher page visitor
**I want** skill links on publisher profile pages to use the new hierarchical URL format
**So that** clicking a skill from a publisher page takes me to the correct `/skills/{owner}/{repo}/{skillSlug}` URL

**Acceptance Criteria**:
- [x] **AC-US6-01**: Given the `PublisherSkillsList` component, when rendering skill cards, then each card's `href` uses `/skills/${ownerSlug}/${repoSlug}/${skillSlug}` instead of `/skills/${encodeURIComponent(skill.name)}`
- [x] **AC-US6-02**: Given the `TrendingSkills` component, when rendering skill links on the homepage, then links use the 3-segment hierarchical URL format
- [x] **AC-US6-03**: Given the `SearchPalette` component, when displaying search results, then result links navigate to `/skills/{owner}/{repo}/{skillSlug}`
- [x] **AC-US6-04**: Given the skill detail page badge markdown snippet, when displayed, then the badge link URL uses the hierarchical format (e.g., `https://verified-skill.com/skills/owner/repo/skill-slug`)

## Out of Scope

- Custom vanity URLs or short aliases for skills (future increment)
- Changing the `publishers/[name]` URL structure (remains flat by GitHub username)
- API versioning (v2) -- existing `/api/v1/` endpoints will be updated in-place since the CLI and platform are co-deployed
- Changing the submission KV key format (`sub:{id}`, `scan:{id}`, `hist:{id}`) -- these use UUID IDs, not slugs
- Multi-marketplace support or cross-platform skill identifiers

## Technical Notes

### Key Design Decisions
1. **3 segments always**: `/skills/{owner}/{repo}/{skill-slug}` -- no 1-segment or 2-segment forms
2. **Skill-slug derivation**: Parent folder name of SKILL.md; for root-level SKILL.md use repo name
3. **`Skill.name` format change**: From `flat-slug` to `owner/repo/skillSlug`
4. **New DB columns**: `ownerSlug`, `repoSlug`, `skillSlug`, `legacySlug` on the `Skill` model
5. **Unique constraint**: Composite `(ownerSlug, repoSlug, skillSlug)` replaces unique on `name`
6. **Legacy redirect**: 301 via `legacySlug` lookup (DB + KV alias)
7. **No collision resolution**: The hierarchical format is inherently unique per owner/repo/skill

### Data Migration
- Backfill `ownerSlug`, `repoSlug`, `skillSlug` from existing `repoUrl` and `skillPath`
- Set `legacySlug` to current `name` value
- Update `name` to `ownerSlug/repoSlug/skillSlug`
- Re-key KV entries from `skill:{flatSlug}` to `skill:{owner/repo/skillSlug}`
- Create KV aliases `skill:alias:{legacySlug}` pointing to the new key

### Dependencies
- Prisma migration must run before any code changes go live
- vskill CLI must be updated concurrently to handle new name format from API responses

## Success Metrics

- Zero broken links: all existing `/skills/{flat-slug}` URLs resolve via 301 redirect
- All new skills published with hierarchical names within 24h of deployment
- CLI `find` and `add` commands work with hierarchical names without user confusion
- No slug collisions requiring manual resolution post-migration
