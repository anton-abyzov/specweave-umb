---
increment: 0284-homepage-trust-signals-ux
title: "Homepage trust signals and UX clarity improvements"
type: feature
priority: P1
status: completed
created: 2026-02-21
structure: user-stories
test_mode: test-after
coverage_target: 80
---

# Feature: Homepage trust signals and UX clarity improvements

## Overview

Three targeted improvements to the vskill-platform frontend:
1. Add scanner attribution to the security callout banner (powered by vskill scanner, 38 patterns -- not Snyk; Snyk is only used for blocklist seed data)
2. Fix the "verified" count ambiguity -- hero says "1724 verified skills" (total count) but stats show "68 certified + 1656 verified" (tier name). The word "verified" is overloaded as both the total count and a tier name.
3. Skill detail page (`/skills/[name]`) usability review: add missing NPM downloads stat, improve section spacing, add "last updated" info.

## User Stories

### US-001: Scanner Attribution on Security Banner (P1)
**Project**: vskill-platform

**As a** visitor evaluating the platform's credibility
**I want** to see what powers the security scan results shown in the banner
**So that** I understand the scanning is done by vskill's own scanner (38 patterns) rather than assuming it's a third-party tool

**Acceptance Criteria**:
- [x] **AC-US1-01**: Security callout banner on homepage shows "Powered by vskill scanner" attribution text with pattern count (52 patterns)
- [x] **AC-US1-02**: Attribution does NOT reference Snyk (Snyk is only used for blocklist data, not scanning)
- [x] **AC-US1-03**: The pattern count in the banner matches the actual count from `patterns.ts` (52 patterns, normalized across all references)
- [x] **AC-US1-04**: Attribution styling is subtle (uses `--text-faint` color, small font) so it doesn't dominate the banner

---

### US-002: Disambiguate "Verified" Count in Hero and Stats (P1)
**Project**: vskill-platform

**As a** visitor reading the homepage
**I want** the hero headline and stats to use unambiguous terminology
**So that** I'm not confused about whether "verified" means the total skill count or the "VERIFIED" certification tier

**Acceptance Criteria**:
- [x] **AC-US2-01**: Hero headline uses unambiguous phrasing that doesn't conflict with the VERIFIED tier name (e.g., "{totalSkills} skills" or "{totalSkills} security-scanned skills" instead of "{totalSkills} verified skills")
- [x] **AC-US2-02**: Inline stats section clearly shows the tier breakdown with explicit labels (e.g., "68 certified tier" + "1656 verified tier" or uses icons/badges)
- [x] **AC-US2-03**: The "How verification works" tree list uses consistent terminology (currently says "Scanned" / "Verified" / "Certified" -- the tier names should match what's used in badges)

---

### US-003: Skill Detail Page Usability Improvements (P2)
**Project**: vskill-platform

**As a** developer evaluating a specific skill
**I want** to see all relevant metrics and have a clear page layout
**So that** I can quickly assess whether the skill meets my needs

**Acceptance Criteria**:
- [x] **AC-US3-01**: Popularity section includes NPM downloads stat card (data already available in `SkillData.npmDownloads`)
- [x] **AC-US3-02**: Meta section shows "Last updated" date derived from `updatedAt` field
- [x] **AC-US3-03**: Security section shows the correct pattern count (52, matching `patterns.ts`)
- [x] **AC-US3-04**: NPM downloads stat card only renders when `npmDownloads > 0` (avoid displaying zero-value stats)

## Functional Requirements

### FR-001: Scanner Attribution Component
The security callout banner in `page.tsx` (homepage) adds a small attribution line: "Powered by vskill scanner -- 38 patterns" styled with `--text-faint` color and mono font at `0.625rem`.

### FR-002: Count Disambiguation
- Hero: Change from `{totalSkills} verified skills` to `{totalSkills} security-scanned skills`
- Inline stats: Keep "certified" and "verified" tier labels but make them visually distinct (use TierBadge-style colors)
- "How verification works" tree: Use tier names that match the badge system (Scanned/Verified/Certified stays fine as these describe the process tiers, not the badge tiers)

### FR-003: Skill Detail Enhancements
- Add `npmDownloads` StatCard in Popularity section (conditionally rendered)
- Add "Last Updated" MetaRow using `skill.updatedAt`
- Normalize pattern count in Security section label from "37" to "38"

## Success Criteria

- No new components needed -- all changes are inline edits to existing files
- Pattern count references across the codebase are consistent (38)
- Hero text doesn't use "verified" as a descriptor for total count

## Out of Scope

- Snyk attribution or branding changes (Snyk is used for blocklist, not scanning)
- New API endpoints or data model changes
- Tooltip/popover interactive components
- Mobile-specific layout changes beyond existing responsive behavior

## Dependencies

- `src/lib/scanner/patterns.ts` -- source of truth for pattern count (38)
- `src/lib/types.ts` -- SkillData interface (already has `npmDownloads`, `updatedAt`)
- `src/app/page.tsx` -- homepage
- `src/app/skills/[name]/page.tsx` -- skill detail page
- `src/app/skills/[name]/security/page.tsx` -- security detail page (pattern count reference)
