# Skills Documentation Reorganization — Two Standards Hub

## Overview

Restructure the Skills documentation section into a clear two-pillar hub: **Extensible Skills Standard** + **Verified Skills Standard**, with proper hub/index pages for each pillar, cross-references to verifiedskill.com, and updated sidebar navigation.

## Current State

The sidebar already has a two-pillar structure with "Extensible Skills Standard" and "Verified Skills Standard" categories, but:
1. No dedicated hub/index page per pillar — each goes straight to individual docs
2. The Skills Overview (index.md) exists but the pillar categories lack their own landing pages
3. Guide files (`claude-skills-deep-dive`, `self-improving-skills`, `agent-skills-extensibility-analysis`) live under `docs/guides/` but are referenced only from the skills sidebar — they should be moved under `docs/skills/` for better content locality
4. The sidebar item labels could be clearer for discoverability

## User Stories

### US-001: Skills Hub Landing Page
As a documentation reader, I want the Skills section to have a clear hub that introduces both standards so I can quickly understand which one applies to my needs.

**Acceptance Criteria:**
- [x] AC-US1-01: Skills index page (index.md) presents both standards with clear descriptions
- [x] AC-US1-02: Each standard has a visual card/section with link to its pillar hub

### US-002: Extensible Skills Pillar Hub
As a skill author, I want a dedicated hub page for the Extensible Skills Standard that lists all related docs so I can find everything about customization in one place.

**Acceptance Criteria:**
- [x] AC-US2-01: New `docs/skills/extensible/index.md` hub page exists with overview + links to all extensible skills docs
- [x] AC-US2-02: Related guide docs moved under `docs/skills/extensible/` for content locality
- [x] AC-US2-03: Sidebar updated to use the new hub structure

### US-003: Verified Skills Pillar Hub
As a developer evaluating skills, I want a dedicated hub page for the Verified Skills Standard that shows the trust tiers and links to security docs so I can evaluate skill safety.

**Acceptance Criteria:**
- [x] AC-US3-01: New `docs/skills/verified/index.md` hub page exists with overview + links to all verified skills docs
- [x] AC-US3-02: Related security docs moved under `docs/skills/verified/` for content locality
- [x] AC-US3-03: Sidebar updated to use the new hub structure

### US-004: Updated Navigation
As a site visitor, I want clear sidebar navigation that reflects the two-pillar structure so I can browse skills documentation intuitively.

**Acceptance Criteria:**
- [x] AC-US4-01: `skillsSidebar` in sidebars.ts reflects new directory structure
- [x] AC-US4-02: All internal cross-references updated (no broken links)
- [x] AC-US4-03: Redirects added for moved pages in docusaurus.config.ts
