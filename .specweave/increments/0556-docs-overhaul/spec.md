---
increment: 0556-docs-overhaul
title: Documentation Site Overhaul
status: completed
priority: P1
type: feature
created: 2026-03-17T00:00:00.000Z
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Documentation Site Overhaul

## Problem Statement

The SpecWeave documentation site (spec-weave.com) has grown to 298 pages with severe quality issues: 784 stale `/specweave:` prefix instances across 90 files, 12 ghost plugins that do not exist, 9 ghost commands, self-contradicting statistics, and a `learn/` directory that duplicates `academy/fundamentals/`. The docs claim 19-24 plugins with 100-136 skills when the actual counts are 13 plugins (8 SpecWeave + 5 vskill) and ~48 skills. Users cannot trust the documentation as a reliable source of truth.

## Goals

- Reduce page count from 298 to ~50 well-structured pages
- Eliminate all stale prefixes, ghost plugins, ghost commands, and contradicting statistics
- Establish enforced page template (Title > Subtitle > Intro > Sections > Next Steps)
- Restructure sidebar into 9 clear categories with max 2 depth levels
- Ensure zero broken URLs via redirect map

## User Stories

### US-001: Terminology Consistency (P1)
**Project**: specweave
**As a** documentation reader
**I want** consistent naming conventions across all pages
**So that** I can find and understand features without confusion from stale or incorrect terminology

**Acceptance Criteria**:
- [x] **AC-US1-01**: Given docs contain `/specweave:` prefix instances, when the fix script runs, then all 784 instances across 90 files are replaced with the correct prefix and zero `/specweave:` occurrences remain
- [x] **AC-US1-02**: Given plugin names use inconsistent casing or naming, when terminology is standardized, then every plugin reference matches the canonical name from the plugin registry
- [x] **AC-US1-03**: Given 25+ stale `frontend:` skill references exist, when references are updated, then each either points to a valid skill name or is removed with a note about deprecation

---

### US-002: Content Cleanup (P1)
**Project**: specweave
**As a** documentation maintainer
**I want** non-documentation files and ghost content removed
**So that** the docs site contains only accurate, relevant material

**Acceptance Criteria**:
- [x] **AC-US2-01**: Given 29 files are identified for deletion (scripts/, learn/ dupes, YouTube scripts, Kafka tutorials, DOCUMENTATION-AUDIT, DOCUMENTATION-RESTRUCTURE-PLAN, CATEGORY-PAGES-COMPLETE), when cleanup runs, then all 29 files are deleted from the docs-site/docs/ directory
- [x] **AC-US2-02**: Given 12 ghost plugins are documented that do not exist in the actual plugin registry, when ghost plugins are removed, then zero references to non-existent plugins remain in any docs page
- [x] **AC-US2-03**: Given 9 ghost commands are referenced across docs, when ghost commands are removed, then every CLI command reference maps to an actual implemented command in the SpecWeave CLI

---

### US-003: Content Consolidation (P0)
**Project**: specweave
**As a** documentation reader
**I want** duplicate and fragmented content merged into single authoritative pages
**So that** I find one source of truth per topic instead of conflicting partial pages

**Acceptance Criteria**:
- [x] **AC-US3-01**: Given 5 getting-started pages exist with overlapping content, when consolidation completes, then exactly 1 getting-started page remains containing a unified onboarding flow
- [x] **AC-US3-02**: Given 3 compliance pages, 4 extensible skills pages, 3 living docs pages, 2 features pages, 2 command-decision-tree pages, and 3 cost tracking pages exist, when each group is merged, then each topic has exactly 1 canonical page
- [x] **AC-US3-03**: Given the `learn/` directory duplicates `academy/fundamentals/`, when deduplication completes, then the `learn/` directory is removed and its sidebar entries redirect to `academy/fundamentals/`

---

### US-004: Plugin Ecosystem Accuracy (P0)
**Project**: specweave
**As a** developer evaluating SpecWeave
**I want** the plugin ecosystem documentation to reflect actual available plugins and skills
**So that** I can make informed decisions about what capabilities exist

**Acceptance Criteria**:
- [x] **AC-US4-01**: Given docs claim 19-24 plugins, when the plugins-ecosystem page is rewritten, then it documents exactly 13 plugins: 8 SpecWeave core + 5 vskill plugins
- [x] **AC-US4-02**: Given docs claim 100-136 skills, when skill counts are corrected, then the documented count states ~48 built-in skills and references the verified-skill.com registry for community skills (99,680+)
- [x] **AC-US4-03**: Given each documented plugin, when a reader checks the plugin list, then every entry includes: name, description, skill count, and installation status (bundled vs. installable)

---

### US-005: Statistics Reconciliation (P1)
**Project**: specweave
**As a** documentation reader
**I want** all statistics and numbers across docs pages to be consistent and accurate
**So that** I can trust the documentation as a reliable source of truth

**Acceptance Criteria**:
- [x] **AC-US5-01**: Given self-contradicting statistics exist across multiple pages, when reconciliation completes, then a single authoritative source defines each statistic and all referencing pages use the same value
- [x] **AC-US5-02**: Given plugin counts, skill counts, and community statistics appear on multiple pages, when numbers are updated, then every occurrence matches: 13 plugins, ~48 built-in skills, 99,680+ community skills
- [x] **AC-US5-03**: Given any page displays a numeric claim, when that claim is verified, then it traces to a verifiable source (CLI output, registry API, or git repo count)

---

### US-006: Navigation Restructure (P1)
**Project**: specweave
**As a** documentation reader
**I want** a clean sidebar with logical categories and max 2 depth levels
**So that** I can navigate to any topic within 2 clicks

**Acceptance Criteria**:
- [x] **AC-US6-01**: Given the sidebar is restructured, when a reader views the docs site, then exactly 9 top-level categories appear: Getting Started, Core Concepts, Workflows, Skills & Plugins, Integrations, Agent Teams, Enterprise, Academy, Reference
- [x] **AC-US6-02**: Given max depth is 2 levels, when any sidebar category is expanded, then no item nests deeper than category > page (plugin/skill reference pages are flat)
- [x] **AC-US6-03**: Given the page template is enforced, when any docs page is checked, then it follows the structure: Title > Subtitle > Intro paragraph > Sections > Next Steps footer

---

### US-007: Design System Fixes (P2)
**Project**: specweave
**As a** documentation reader
**I want** consistent visual styling without layout glitches
**So that** the docs site appears polished and professional

**Acceptance Criteria**:
- [x] **AC-US7-01**: Given a global CSS transition rule causes layout shift on page load, when the transition is scoped, then page elements do not animate on initial render
- [x] **AC-US7-02**: Given footer uses hardcoded color tokens, when tokens are replaced, then footer colors use CSS custom properties from the docs theme and render correctly in both light and dark modes

---

### US-008: Glossary Optimization (P2)
**Project**: specweave
**As a** documentation reader
**I want** the glossary to contain only SpecWeave-specific terms
**So that** it serves as a quick reference for domain terminology, not a generic dictionary

**Acceptance Criteria**:
- [x] **AC-US8-01**: Given the glossary contains generic software terms (e.g., "API", "CLI", "JSON"), when optimization completes, then only SpecWeave-specific terms remain (e.g., "increment", "skill chain", "grill report")
- [x] **AC-US8-02**: Given each glossary entry, when a reader checks it, then it includes: term, one-sentence definition, and a link to the relevant docs page

---

### US-009: Redirect Map (P1)
**Project**: specweave
**As a** documentation reader arriving via an old URL
**I want** to be automatically redirected to the correct new page
**So that** bookmarks, search engine results, and external links remain functional after the restructure

**Acceptance Criteria**:
- [x] **AC-US9-01**: Given pages are deleted, merged, or moved during the overhaul, when a redirect map is created, then every removed URL has a corresponding redirect entry in the @docusaurus/plugin-client-redirects configuration
- [x] **AC-US9-02**: Given the redirect map is deployed, when a user visits any old URL that was restructured, then they receive a client-side redirect (not a 404) to the new canonical page
- [x] **AC-US9-03**: Given the `learn/` directory is removed, when a user visits any `/learn/*` URL, then they are redirected to the corresponding `/academy/fundamentals/*` page

## Out of Scope

- Writing new documentation content beyond what exists (this is restructure, not net-new authoring)
- Versioned documentation (confirmed: single version only)
- Internationalization/localization
- Search engine optimization beyond redirect handling
- Documentation for unreleased features
- Changes to the Docusaurus framework version or theme package

## Technical Notes

### Dependencies
- @docusaurus/plugin-client-redirects (already installed)
- Docusaurus sidebar configuration (sidebars.js or sidebars.ts)
- docs-site at `repositories/anton-abyzov/specweave/docs-site/docs/`

### Constraints
- All changes are content/config only -- no Docusaurus framework changes
- Redirect map must be machine-verifiable (script can check for 404s)
- Page template enforcement is structural (linting or review), not runtime

### Architecture Decisions
- Phase 1 (scripted fixes) runs first to reduce manual review surface
- Consolidation merges content into the page with the most complete version, not a blank rewrite
- Glossary retains SpecWeave-specific terms only; generic terms are removed without redirect

## Non-Functional Requirements

- **Performance**: Final docs site builds in under 60 seconds with ~50 pages (down from 298)
- **Accessibility**: All pages maintain semantic heading hierarchy (h1 > h2 > h3, no skipped levels)
- **Compatibility**: Redirect map works on all browsers with JavaScript enabled (client-side redirects)
- **Maintainability**: Page template enforcement documented so future contributors follow the structure

## Edge Cases

- **Merged page with external backlinks**: Redirect map catches these; both old URLs point to the merged page
- **Ghost plugin referenced in user tutorials**: Remove the reference and add a note if the tutorial cannot function without it
- **Stale prefix in code blocks**: Replace inside fenced code blocks as well, not just prose
- **learn/ subdirectory with unique content**: Audit confirms learn/ is a clone; if any unique page is found during implementation, merge it into academy/ rather than deleting

## Risks

| Risk | Probability | Impact | Severity | Mitigation |
|------|-------------|--------|----------|------------|
| Redirect map misses a URL causing 404s from search engines | 0.3 | 7 | 2.1 | Generate redirect map programmatically from git diff of deleted/moved files |
| Merged pages lose nuanced content from one of the source pages | 0.4 | 5 | 2.0 | Diff each merge source before and after; manual review of merged content |
| Stale prefix replacement breaks code examples | 0.2 | 6 | 1.2 | Run prefix replacement with dry-run first; review code block changes separately |
| Page count exceeds ~50 target after consolidation | 0.5 | 3 | 1.5 | Target is guidance not hard ceiling; quality over arbitrary count |

## Success Metrics

- Zero `/specweave:` prefix instances remaining (down from 784)
- Zero ghost plugin or ghost command references
- All statistics consistent across pages (single source of truth per number)
- Page count reduced to ~50 (from 298)
- Zero 404s for previously valid URLs (redirect coverage)
- Every page follows the enforced template structure
