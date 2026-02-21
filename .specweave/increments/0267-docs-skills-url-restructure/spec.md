# 0267: Skills Documentation URL Restructure

## Overview

The Extensible Skills page currently lives at `/docs/guides/extensible-skills` — buried under generic guides. The Skills navbar item already groups both standards together in the sidebar, but the URL structure doesn't match. All skills-related content should live under `/docs/skills/` for a clean, discoverable URL hierarchy.

## User Stories

### US-001: Unified Skills URL Namespace
**As a** documentation reader navigating the Skills section,
**I want** all skills-related pages under `/docs/skills/`,
**so that** URLs are predictable and the information architecture matches the navbar.

**Acceptance Criteria:**
- [x] AC-US1-01: `extensible-skills.md` moved from `docs/guides/` to `docs/skills/`
- [ ] AC-US1-02: Redirect configured: `/docs/guides/extensible-skills` -> `/docs/skills/extensible-skills`
- [ ] AC-US1-03: `sidebars.ts` updated — Extensible Skills Standard category references `skills/extensible-skills` instead of `guides/extensible-skills`
- [ ] AC-US1-04: All internal cross-references updated (verified-skills.md, index.md, other guides)
- [ ] AC-US1-05: Existing redirect from `/docs/guides/programmable-skills` chains to new location

### US-002: Skills-Related Guides Migration
**As a** docs maintainer,
**I want** security and skill factory docs also under `/docs/skills/`,
**so that** the Skills sidebar owns all its content without cross-referencing into guides.

**Acceptance Criteria:**
- [ ] AC-US2-01: `skills-ecosystem-security.md` moved from `docs/guides/` to `docs/skills/`
- [ ] AC-US2-02: `secure-skill-factory-standard.md` moved from `docs/guides/` to `docs/skills/`
- [ ] AC-US2-03: `skill-discovery-evaluation.md` moved from `docs/guides/` to `docs/skills/`
- [ ] AC-US2-04: `skill-contradiction-resolution.md` moved from `docs/guides/` to `docs/skills/`
- [ ] AC-US2-05: `skill-development-guidelines.md` moved from `docs/guides/` to `docs/skills/`
- [ ] AC-US2-06: Redirects added for all moved files
- [ ] AC-US2-07: `sidebars.ts` paths updated throughout

### US-003: Build Verification
**As a** developer,
**I want** the docs site to build without broken links,
**so that** the restructure doesn't break any existing bookmarks or SEO.

**Acceptance Criteria:**
- [ ] AC-US3-01: `npm run build` succeeds with zero broken link errors for moved pages
- [ ] AC-US3-02: All redirects verified (old URLs resolve to new locations)

## Target URL Structure

```
/docs/skills/                          <- index.md (hub page, already here)
/docs/skills/extensible-skills         <- MOVED from /docs/guides/
/docs/skills/verified-skills           <- already here
/docs/skills/skills-ecosystem-security <- MOVED from /docs/guides/
/docs/skills/secure-skill-factory-standard <- MOVED from /docs/guides/
/docs/skills/skill-discovery-evaluation    <- MOVED from /docs/guides/
/docs/skills/skill-contradiction-resolution <- MOVED from /docs/guides/
/docs/skills/skill-development-guidelines   <- MOVED from /docs/guides/
```

## Out of Scope

- Homepage changes (see increment 0268)
- New content creation — this is a pure URL/structure migration
- Claude Skills Deep Dive and Self-Improving Skills stay in guides (they're conceptual guides, not standards)
