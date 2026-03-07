---
increment: 0451-skill-naming-plugin-metadata
title: "Fix Skill Naming with Plugin as Separate Metadata"
type: feature
priority: P0
status: active
created: 2026-03-07
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Fix Skill Naming with Plugin as Separate Metadata

## Problem Statement

Skills inside Claude Code plugins currently get ugly concatenated names like "specweave-release-release-expert" instead of the clean leaf folder name "release-expert". The plugin folder name (e.g., "specweave-release") is baked into the skill name and slug, making discovery harder and URLs longer than necessary. The plugin name should be extracted as a separate metadata field -- visible in search results and detail pages but absent from URLs and skill names.

## Goals

- Derive skill names from the leaf folder containing SKILL.md, not concatenated paths
- Extract plugin folder name as a separate `pluginName` metadata field
- Show plugin name as a teal badge in platform UI and CLI find output
- Backfill all existing skills with correct pluginName and ensure no flat names remain

## User Stories

### US-PLAT-001: Derive Plugin Name from Skill Path (P0)
**Project**: vskill-platform

**As a** platform maintainer
**I want** a `derivePluginName()` function that extracts the plugin folder from a SKILL.md path
**So that** plugin context is captured as structured metadata rather than mangled into the skill name

**Acceptance Criteria**:
- [ ] **AC-US1-01**: Given path `plugins/specweave-release/skills/release-expert/SKILL.md`, `derivePluginName()` returns `"specweave-release"`
- [ ] **AC-US1-02**: Given path `skills/architect/SKILL.md` (no plugin folder), `derivePluginName()` returns `null`
- [ ] **AC-US1-03**: Given path `SKILL.md` (root-level), `derivePluginName()` returns `null`
- [ ] **AC-US1-04**: Given `null` or `undefined` input, `derivePluginName()` returns `null`
- [ ] **AC-US1-05**: Function is exported from `slug.ts` alongside existing slug utilities

---

### US-PLAT-002: Set Plugin Name During Publish (P0)
**Project**: vskill-platform

**As a** platform maintainer
**I want** `publishSkill()` to call `derivePluginName()` and persist the result to the Skill record
**So that** every newly published skill has its plugin context captured at write time

**Acceptance Criteria**:
- [ ] **AC-US2-01**: When publishing a skill with path `plugins/foo/skills/bar/SKILL.md`, the DB Skill record has `pluginName = "foo"`
- [ ] **AC-US2-02**: When publishing a skill with path `skills/bar/SKILL.md`, the DB Skill record has `pluginName = null`
- [ ] **AC-US2-03**: On re-publish (upsert update), `pluginName` is updated to the current derived value

---

### US-PLAT-003: Backfill Plugin Name for Legacy Records (P0)
**Project**: vskill-platform

**As a** platform admin
**I want** the `backfill-slugs` admin route to populate `pluginName` for existing skills that have a `skillPath`
**So that** legacy records gain plugin metadata without manual intervention

**Acceptance Criteria**:
- [ ] **AC-US3-01**: Skills with a `skillPath` containing a `plugins/` segment get `pluginName` set to the plugin folder name
- [ ] **AC-US3-02**: Skills with `skillPath = null` are skipped silently (no error, no update)
- [ ] **AC-US3-03**: Skills with a `skillPath` that has no `plugins/` segment get `pluginName = null`
- [ ] **AC-US3-04**: All flat skill names (no `/` in name) are converted to hierarchical `owner/repo/skillSlug` format -- flat names must never remain
- [ ] **AC-US3-05**: Dry-run mode reports planned `pluginName` changes without mutating the database

---

### US-PLAT-004: Show Plugin Badge in Search and List UI (P1)
**Project**: vskill-platform

**As a** skill browser
**I want** to see a teal pill badge showing the plugin name next to skills that belong to a plugin
**So that** I can understand the plugin context of a skill at a glance

**Acceptance Criteria**:
- [ ] **AC-US4-01**: In `SearchPalette`, skills with a non-null `pluginName` display a teal pill badge with the raw plugin folder name (e.g., "specweave-release")
- [ ] **AC-US4-02**: In the skills list page (`/skills`), skills with a non-null `pluginName` display the same teal pill badge
- [ ] **AC-US4-03**: Skills with `pluginName = null` show no plugin badge
- [ ] **AC-US4-04**: The badge is purely informational -- not clickable, no link

---

### US-PLAT-005: Show Plugin Badge on Skill Detail Page (P1)
**Project**: vskill-platform

**As a** skill browser
**I want** to see the plugin name badge in the byline metadata row on the skill detail page
**So that** I know which plugin a skill belongs to when viewing its details

**Acceptance Criteria**:
- [ ] **AC-US5-01**: On the skill detail page, the plugin badge appears in the byline metadata row after the repo link and before the skillPath
- [ ] **AC-US5-02**: The badge uses the same teal pill styling as the search/list pages
- [ ] **AC-US5-03**: The badge does not appear in the page title or header area

---

### US-CLI-006: Show Plugin Badge in CLI Find Output (P1)
**Project**: vskill

**As a** CLI user
**I want** to see the plugin name as a dim bracketed suffix in `vskill find` results
**So that** I can identify plugin-based skills in terminal output

**Acceptance Criteria**:
- [ ] **AC-US6-01**: In TTY mode, skills with a non-null `pluginName` display as `release-expert [specweave-release]` with the bracketed portion in dim styling
- [ ] **AC-US6-02**: Skills with `pluginName = null` display without any bracketed suffix
- [ ] **AC-US6-03**: In non-TTY (piped) mode, `pluginName` is included as an additional tab-separated field when present

## Out of Scope

- Schema/migration changes (the `pluginName` DB column already exists)
- Plugin name prettification or formatting (raw folder name only)
- Clickable/filterable plugin badges (purely informational for now)
- Changes to skill URL structure (URLs remain `owner/repo/skillSlug`)
- Inference of pluginName from displayName or name fields for records missing skillPath

## Technical Notes

### Dependencies
- `slug.ts` -- new `derivePluginName()` function added here
- `submission-store.ts` -- `publishSkill()` calls `derivePluginName()`
- `backfill-slugs/route.ts` -- extended to populate `pluginName`
- Prisma Skill model -- `pluginName` column already exists, no migration needed

### Constraints
- `derivePluginName()` must handle all path formats: `plugins/X/skills/Y/SKILL.md`, `skills/Y/SKILL.md`, `SKILL.md`, `null`
- Backfill must be idempotent (safe to run multiple times)
- Teal badge color: `#0D9488` (matches existing teal used for extensible badges)

### Architecture Decisions
- Plugin name is metadata only -- it does not affect slug derivation, URL structure, or the `name` unique key
- The `derivePluginName()` function looks for a `plugins/` segment in the path and returns its immediate child folder name
- Backfill reuses existing admin auth (X-Internal-Key or SUPER_ADMIN JWT)

## Success Criteria

- Zero skills in the database with flat (non-hierarchical) names after backfill
- All plugin-based skills display `pluginName` in UI and CLI
- Non-plugin skills show no plugin badge anywhere
