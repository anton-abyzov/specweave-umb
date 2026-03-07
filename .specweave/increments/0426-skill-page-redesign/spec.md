---
increment: 0426-skill-page-redesign
title: "Skill Detail Page Redesign"
type: feature
priority: P1
status: planned
created: 2026-03-05
structure: user-stories
test_mode: TDD
coverage_target: 90
---

# Feature: Skill Detail Page Redesign

## Overview

Redesign the skill detail page (`src/app/skills/[name]/page.tsx`, currently 810 lines) for a world-class, minimalistic, professional display. The current page suffers from duplicated information (category appears in both badge pills and meta section, extensible info appears as both a callout block and a badge pill), an overly verbose meta section, bloated StatCard boxes, and secondary features (badge embed, agent list) that compete visually with primary content. This redesign reorganizes existing data into a clear information hierarchy: hero zone with install command above the fold, single-source-of-truth for every data point, compact inline stats, and demoted secondary content using progressive disclosure (`details`/`summary`).

## Scope

- **Single file**: `src/app/skills/[name]/page.tsx` (the `SkillDetailPage` component and its sub-components)
- **No shared component changes**: `SectionDivider`, `TerminalBlock`, `TierBadge`, `TrustBadge`, `RepoHealthBadge`, `RepoLink`, `ReportProblemModal`, `TaintWarning` remain untouched
- **No new dependencies**: pure React/JSX restructuring with inline styles
- **All existing data preserved**: every field currently rendered continues to be rendered, just reorganized
- **BlockedSkillView untouched**: the blocked-skill branch of the page is out of scope

## User Stories

### US-001: Above-the-fold hero zone (P1)
**Project**: vskill-platform

**As a** developer evaluating a skill
**I want** to see the most important information (name, trust tier, author, install command) immediately
**So that** I can quickly decide whether to install it

**Context**: Currently the page uses `SectionDivider` for the skill name (which renders it as a styled divider, not a semantic heading), places badges in a separate row below, puts meta info (author, repo, version) in a distant table-style section, and buries the install command further down. A developer scanning the page must scroll past popularity stats and meta to reach the install command.

**Acceptance Criteria**:
- [x] **AC-US1-01**: Skill name renders as an `h1` element (not via `SectionDivider`) at the top of the page content, with `TierBadge`, `TrustBadge`, and version string (`v{currentVersion}`) displayed inline on the same row (flex, centered vertically, gap between items). The existing `SectionDivider` call for the header is removed.
- [x] **AC-US1-02**: A byline row appears directly below the h1 row, showing (left to right, separated by a middle-dot or pipe delimiter): author name as a link to `/authors/{author}`, category as plain text from `CATEGORY_LABELS`, repository as a `RepoLink` with adjacent `RepoHealthBadge`, and last-updated date via `formatDate`. All items render inline (flex row, wrapping allowed) in the mono font at the muted/faint color. Source path link (skillPath) also appears in this byline if available.
- [x] **AC-US1-03**: The `TerminalBlock` install section appears immediately after the hero (h1 + byline + description + taint warning if applicable), before any stats or security content. No `SectionDivider` is used for the install heading -- instead a small mono-font label "Install" appears above the terminal block.
- [x] **AC-US1-04**: Security scan summary (Tier 1, Tier 2, and any external scans) renders as a horizontal flex row of compact status chips (label + PASS/FAIL pill) directly adjacent to or immediately below the install section, replacing the current vertical list layout. The "View full security report" link appears inline after the last chip.

---

### US-002: Duplicate elimination (P1)
**Project**: vskill-platform

**As a** developer reading the skill page
**I want** each piece of information to appear exactly once
**So that** the page feels clean and authoritative rather than repetitive

**Context**: Currently the page shows category in three places (badge pill row, meta section `MetaRow`, and potentially in labels), extensible info in two places (callout block and badge pill), and author/version/repo/updated in the meta section which duplicates the hero. The `SectionDivider title="Meta"` section and the category pill are redundant once the hero byline exists.

**Acceptance Criteria**:
- [x] **AC-US2-01**: Category text appears only in the hero byline row (from US-001 AC-US1-02). The category `span` is removed from the badges/pills row. The `MetaRow` for "Category" in the meta section is removed.
- [x] **AC-US2-02**: Extensible info appears only as a compact one-liner under the install section (e.g., "Semi-Extensible -- supports customization via skill-memories" with a "Learn more" link). The standalone callout block (the `borderLeft: 3px solid` div rendered when `skill.extensible` is true, lines 167-225 in current code) is removed. The extensible badge pill in the badges row is removed. The extensibility tier label and link are consolidated into this single one-liner.
- [x] **AC-US2-03**: The entire meta section (the `div` containing `MetaRow` components for Author, Category, Version, Repository, Source, Last Updated -- lines 300-357 in current code) is removed. Author, version, repository, source path, and last-updated date are all rendered in the hero byline (AC-US1-02). No data is lost -- every field from the old meta section appears in the byline.

---

### US-003: Compact stats and demoted secondary content (P2)
**Project**: vskill-platform

**As a** developer browsing skills
**I want** popularity stats displayed compactly and secondary features (badge embed, agent list) demoted
**So that** stats inform without dominating and secondary content is accessible but not distracting

**Context**: Currently 8 `StatCard` box components render in a flex-wrap grid, each with a border, padding, and large font -- taking significant vertical space. Some stats are redundant (Monthly npm downloads alongside Weekly; Unique installs alongside total Installs when counts are equal). The badge embed section takes a full `SectionDivider` + image + code block. The "Works with" agent list for universal skills shows all agents in a pill grid, which is noisy.

**Acceptance Criteria**:
- [x] **AC-US3-01**: The `StatCard` component and its `SectionDivider title="Popularity"` are replaced by inline stat pairs rendered as a single flex row of compact `label: value` spans in mono font (e.g., "Installs 1.2k | Stars 340 | Weekly 890 | 7d Trend 42"). Redundant stats are deduplicated: if `npmDownloadsWeekly > 0`, the Monthly (`npmDownloads`) stat is dropped; if `uniqueInstalls` equals `vskillInstalls`, the Unique stat is dropped. The metrics-refreshed timestamp remains as a small note below the stat row.
- [x] **AC-US3-02**: The badge embed section (current `SectionDivider title="Badge"` block, lines 366-388) is collapsed into a native HTML `details`/`summary` element. The summary text reads "Badge embed". When expanded, it shows the badge image preview and the markdown `TerminalBlock`. No `SectionDivider` is used.
- [x] **AC-US3-03**: The "Works with" section (current `SectionDivider title="Works with"` block, lines 521-582) uses a native HTML `details`/`summary` element for universal skills (when `isUniversal` is true). The summary text reads "Works with all agents ({count})" where count is `visibleAgents.length`. When expanded, the agent pill grid renders as before. For non-universal skills (explicit `compatibleAgentSlugs`), the agent list renders directly without `details`/`summary` since it is a smaller, more relevant set.

## Functional Requirements

### FR-001: Information hierarchy
The page sections render in this order from top to bottom:
1. Back link
2. Hero zone (h1 + badges + byline)
3. Taint warning (if applicable)
4. Description paragraph
5. Labels/pills row (only remaining non-duplicate labels)
6. Install section with terminal block
7. Extensible one-liner (if applicable)
8. Security scan summary (horizontal)
9. Compact stats row
10. Extension Points section (unchanged, only if applicable)
11. Badge embed (collapsed `details`)
12. Works With (collapsed `details` for universal, open for specific)
13. Report a problem button

### FR-002: No visual regression for data
Every data field currently rendered on the page must remain accessible after the redesign. No information is removed, only reorganized or collapsed behind progressive disclosure.

### FR-003: Responsive behavior
The hero byline row and stats row must `flex-wrap` on narrow viewports so items stack gracefully. The security chips row must also wrap.

## Success Criteria

- All existing data points remain visible or accessible (no information loss)
- Zero duplicate data displayed on the page
- Install command is visible without scrolling on a 1080p viewport
- Page line count reduced (target: under 700 lines, down from 810)

## Out of Scope

- BlockedSkillView component (separate branch, untouched)
- Shared components (SectionDivider, TerminalBlock, TierBadge, TrustBadge, etc.)
- New npm dependencies or external libraries
- Backend data changes or API modifications
- Mobile-specific breakpoints (flex-wrap handles narrow viewports)
- Dark/light theme changes (existing CSS variables continue to work)

## Dependencies

- Existing shared components must continue to export their current interfaces
- Skill data model (fields on the `skill` object) must remain unchanged
