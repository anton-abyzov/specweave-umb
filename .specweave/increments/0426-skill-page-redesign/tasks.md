---
increment: 0426-skill-page-redesign
title: "Skill Detail Page Redesign"
status: planned
total_tasks: 10
completed_tasks: 0
by_user_story:
  US-001: [T-001, T-002, T-003, T-004]
  US-002: [T-005, T-006, T-007]
  US-003: [T-008, T-009, T-010]
---

# Tasks: Skill Detail Page Redesign

Target file: `repositories/anton-abyzov/vskill-platform/src/app/skills/[name]/page.tsx`

---

## User Story: US-001 - Above-the-fold hero zone

**Linked ACs**: AC-US1-01, AC-US1-02, AC-US1-03, AC-US1-04
**Tasks**: 4 total, 0 completed

---

### T-001: Add new style constants and InlineStat component

**User Story**: US-001
**Satisfies ACs**: AC-US1-01, AC-US1-02
**Status**: [ ] pending

**Test Plan**:
- **Given** the file has existing style constants (`MONO`, `TIER_LABELS`, etc.)
- **When** new constants (`heroRowStyle`, `bylineStyle`, `bylineItemStyle`, `bylineSepStyle`, `sectionLabelStyle`, `chipRowStyle`, `scanChipStyle`, `statsRowStyle`, `summaryStyle`, `labelPillStyle`) and the `InlineStat` component are added
- **Then** the file compiles without TypeScript errors and `InlineStat` renders label and value in mono font with correct color variables

**Test Cases**:
1. **Unit**: `repositories/anton-abyzov/vskill-platform/src/app/skills/[name]/page.test.tsx`
   - `rendersInlineStatLabelAndValue()`: Render `<InlineStat label="Installs" value="1.2k" />` and assert label text, value text, and fontFamily mono are present
   - **Coverage Target**: 90%

**Implementation**:
1. Open `src/app/skills/[name]/page.tsx`
2. Add style constants block after existing `MONO`/`TIER_LABELS`: `heroRowStyle`, `bylineStyle`, `bylineItemStyle`, `bylineSepStyle`, `sectionLabelStyle`, `chipRowStyle`, `statsRowStyle`, `summaryStyle`, `labelPillStyle`
3. Add `scanChipStyle(color: string): CSSProperties` function
4. Add `InlineStat` component (12 lines, per plan Decision 5)
5. Run TypeScript check: `cd repositories/anton-abyzov/vskill-platform && npx tsc --noEmit`

---

### T-002: Rewrite hero zone (h1 row + byline row)

**User Story**: US-001
**Satisfies ACs**: AC-US1-01, AC-US1-02
**Status**: [ ] pending

**Test Plan**:
- **Given** a skill with `displayName`, `authorUsername`, `categoryKey`, repo info, `skillPath`, `currentVersion`, `TierBadge`, `TrustBadge`, and `lastUpdated`
- **When** the page renders the hero section
- **Then** the skill name appears as an `h1`, `TierBadge`/`TrustBadge`/version appear inline in the same flex row, and the byline row shows author link, category text, `RepoLink`+`RepoHealthBadge`, source path, and formatted date separated by middle-dot delimiters

**Test Cases**:
1. **Unit**: `repositories/anton-abyzov/vskill-platform/src/app/skills/[name]/page.test.tsx`
   - `rendersH1WithSkillName()`: Assert `<h1>` element contains skill `displayName`
   - `rendersBylineAuthorLink()`: Assert byline contains `href="/authors/{author}"`
   - `rendersBylineCategoryText()`: Assert category label text appears in byline
   - `rendersVersionInHeroRow()`: Assert `v{currentVersion}` text in hero row
   - **Coverage Target**: 90%

**Implementation**:
1. Locate the current `SectionDivider title={skill.displayName}` block at top of SkillDetailPage render
2. Replace with hero zone JSX: `div[heroRowStyle] > h1 + TierBadge + (TrustBadge if applicable) + span(version)`
3. Add byline row `div[bylineStyle]` immediately after: author `a`, sep, category `span` (from `CATEGORY_LABELS`), sep, `RepoLink`+`RepoHealthBadge`, sep, source `a` (if `skillPath`), sep, `formatDate(lastUpdated)` `span`
4. Use `\u00B7` middle-dot character for separators, wrapped in `span[bylineSepStyle]`
5. Run TypeScript check

---

### T-003: Move install section above stats and replace its SectionDivider

**User Story**: US-001
**Satisfies ACs**: AC-US1-03
**Status**: [ ] pending

**Test Plan**:
- **Given** the current page order places the install `TerminalBlock` after Meta and Popularity sections
- **When** the install section is moved to immediately follow the hero + description block
- **Then** the install block renders before security/stats content, the `SectionDivider title="Install"` is replaced by a small mono-font "Install" label (`sectionLabelStyle`), and no `SectionDivider` wraps the terminal

**Test Cases**:
1. **Unit**: `repositories/anton-abyzov/vskill-platform/src/app/skills/[name]/page.test.tsx`
   - `rendersInstallLabelNotSectionDivider()`: Assert the string "Install" appears as a plain label element, and no `SectionDivider` with title "Install" is rendered
   - **Coverage Target**: 85%

**Implementation**:
1. Cut the install section JSX (TerminalBlock + surrounding wrapper)
2. Paste it at position 6 in the new render order (after description, before extensible one-liner)
3. Replace `<SectionDivider title="Install" />` with `<span style={sectionLabelStyle}>Install</span>`
4. Run TypeScript check

---

### T-004: Convert security scans to horizontal chip layout

**User Story**: US-001
**Satisfies ACs**: AC-US1-04
**Status**: [ ] pending

**Test Plan**:
- **Given** a skill with Tier 1, Tier 2, and external security scan results
- **When** the security section renders
- **Then** all scan results appear as compact inline chips in a single flex row (not a vertical column), each chip contains label + PASS/FAIL + optional score, and "View full security report" link appears as the last inline item

**Test Cases**:
1. **Unit**: `repositories/anton-abyzov/vskill-platform/src/app/skills/[name]/page.test.tsx`
   - `rendersSecurityChipsHorizontally()`: Assert security container does not use `flexDirection:column`, and all scan chips are children of a single container
   - `rendersViewReportLinkInline()`: Assert "View full security report" link is inside the chip-row container
   - **Coverage Target**: 85%

**Implementation**:
1. Locate security section JSX (currently uses `flexDirection: column` container)
2. Replace parent container styles with `chipRowStyle` (flex, wrap, gap, alignItems center)
3. Replace each vertical scan item with `<span style={scanChipStyle(color)}>{label} {status}{score ? ` ${score}/100` : ""}</span>`
4. Remove `scanRowStyle` and `scanLabelStyle` constants (replaced by `chipRowStyle` and `scanChipStyle`)
5. Move "View full security report" link inside `chipRowStyle` container as the last child
6. Run TypeScript check

---

## User Story: US-002 - Duplicate elimination

**Linked ACs**: AC-US2-01, AC-US2-02, AC-US2-03
**Tasks**: 3 total, 0 completed

---

### T-005: Remove category from badges row and meta section

**User Story**: US-002
**Satisfies ACs**: AC-US2-01
**Status**: [ ] pending

**Test Plan**:
- **Given** the page after T-002 renders category in the hero byline
- **When** the category pill is removed from the badges/pills row and the `MetaRow` for "Category" is removed from the meta section
- **Then** category text appears exactly once (in the byline), no category pill exists in the labels row, and no "Category" label appears in any meta/table section

**Test Cases**:
1. **Unit**: `repositories/anton-abyzov/vskill-platform/src/app/skills/[name]/page.test.tsx`
   - `categoryAppearsOnlyOnce()`: Query all elements containing the resolved category label text and assert count === 1
   - **Coverage Target**: 85%

**Implementation**:
1. Locate category `span` in the badges/pills row and delete it
2. Locate `<MetaRow label="Category" ...>` and delete it
3. Note that `basePillStyle` may now be unused by category pill (confirm in T-007)
4. Run TypeScript check

---

### T-006: Replace extensible callout block and badge pill with one-liner

**User Story**: US-002
**Satisfies ACs**: AC-US2-02
**Status**: [ ] pending

**Test Plan**:
- **Given** a skill where `skill.extensible` is truthy
- **When** the page renders
- **Then** the multi-line callout block (border-left div, lines ~167-225) is absent, the extensible badge pill in the badges row is absent, and a single compact one-liner appears below the install section with the tier label, description text, and "Learn more" link

**Test Cases**:
1. **Unit**: `repositories/anton-abyzov/vskill-platform/src/app/skills/[name]/page.test.tsx`
   - `extensibleCalloutBlockRemoved()`: Assert no element has `borderLeft` style containing "3px solid" when `skill.extensible` is set
   - `extensibleOneLineRenders()`: Assert one-liner text includes the extensibility tier label and "Learn more" link
   - `extensiblePillRemovedFromBadgesRow()`: Assert no extensible pill in the labels/badges section
   - **Coverage Target**: 90%

**Implementation**:
1. Delete the extensible callout block JSX (the `borderLeft: "3px solid"` div, approximately lines 167-225)
2. Delete the extensible badge pill from the badges row
3. Add compact one-liner at position 7 in render order (after install section), conditional on `skill.extensible`:
   `<p style={{fontFamily:MONO, fontSize:"0.8125rem", color:"var(--text-muted)"}}>{tierLabel} -- {description}. <a href={learnMoreUrl}>Learn more</a></p>`
4. Run TypeScript check

---

### T-007: Delete entire meta section (MetaRow components)

**User Story**: US-002
**Satisfies ACs**: AC-US2-03
**Status**: [ ] pending

**Test Plan**:
- **Given** author, version, repository, source path, and last-updated are all rendered in the hero byline (T-002)
- **When** the meta section div (containing all `MetaRow` components) is deleted
- **Then** the `MetaRow` component and `SectionDivider title="Meta"` are gone, all data fields remain accessible in the byline, and no data is lost

**Test Cases**:
1. **Unit**: `repositories/anton-abyzov/vskill-platform/src/app/skills/[name]/page.test.tsx`
   - `metaSectionAbsent()`: Assert no `SectionDivider` with title "Meta" and no `MetaRow` instances in the output
   - `authorStillRenderedInByline()`: Assert author link exists in hero byline after meta removal
   - **Coverage Target**: 85%

**Implementation**:
1. Delete the entire meta section `div` (~60 lines: `MetaRow` components for Author, Category, Version, Repository, Source, Last Updated)
2. Delete the `MetaRow` component definition (~14 lines at end of file)
3. Delete `basePillStyle` and `pillStyle` alias -- now fully unused (category and extensible pills were the only callers, both removed in T-005 and T-006)
4. Add `labelPillStyle` (from T-001) to `displayLabels` render as replacement
5. Run TypeScript check; confirm zero remaining references to `MetaRow` with grep

---

## User Story: US-003 - Compact stats and demoted secondary content

**Linked ACs**: AC-US3-01, AC-US3-02, AC-US3-03
**Tasks**: 3 total, 0 completed

---

### T-008: Replace StatCard/Popularity section with InlineStat row

**User Story**: US-003
**Satisfies ACs**: AC-US3-01
**Status**: [ ] pending

**Test Plan**:
- **Given** a skill with `vskillInstalls`, `uniqueInstalls`, `npmDownloads`, `npmDownloadsWeekly`, `githubStars`, `githubForks`, and `metricsRefreshedAt`
- **When** the compact stats row renders
- **Then** stats appear as inline `label: value` spans in a single flex row, Monthly npm stat is absent when `npmDownloadsWeekly > 0`, Unique stat is absent when `uniqueInstalls === vskillInstalls`, and the `metricsRefreshedAt` timestamp appears as a small note below the row

**Test Cases**:
1. **Unit**: `repositories/anton-abyzov/vskill-platform/src/app/skills/[name]/page.test.tsx`
   - `rendersInlineStatsRow()`: Assert stats container uses `statsRowStyle` (flex, wrap) and contains multiple `InlineStat` children
   - `suppressesMonthlyWhenWeeklyPresent()`: With `npmDownloadsWeekly=100`, assert Monthly stat is not in the DOM
   - `suppressesUniqueWhenEqualToTotal()`: With `uniqueInstalls === vskillInstalls`, assert Unique stat is not in the DOM
   - `rendersRefreshedAtNote()`: Assert `metricsRefreshedAt` timestamp text appears below the stats row
   - **Coverage Target**: 90%

**Implementation**:
1. Delete `SectionDivider title="Popularity"` and all `StatCard` JSX (~30 lines)
2. Add `div[statsRowStyle]` at position 9 in render order with `InlineStat` components
3. Apply deduplication rules: `npmDownloadsWeekly > 0` suppresses Monthly; `uniqueInstalls === vskillInstalls` suppresses Unique
4. Add `metricsRefreshedAt` note `<p>` below stats row
5. Delete `StatCard` component definition (~30 lines at end of file)
6. Run TypeScript check

---

### T-009: Collapse badge embed section in details/summary

**User Story**: US-003
**Satisfies ACs**: AC-US3-02
**Status**: [ ] pending

**Test Plan**:
- **Given** a skill that has a badge embed (markdown badge string)
- **When** the badge section renders
- **Then** the content is wrapped in a native `<details>` element with `<summary>` text "Badge embed", badge image and `TerminalBlock` are only visible when expanded, and no `SectionDivider title="Badge"` is present

**Test Cases**:
1. **Unit**: `repositories/anton-abyzov/vskill-platform/src/app/skills/[name]/page.test.tsx`
   - `badgeEmbedInDetailsElement()`: Assert badge content is a descendant of a `<details>` element
   - `badgeSummaryTextCorrect()`: Assert `<summary>` text equals "Badge embed"
   - `noSectionDividerForBadge()`: Assert no `SectionDivider` with title "Badge" is rendered
   - **Coverage Target**: 85%

**Implementation**:
1. Wrap existing badge embed JSX in:
   `<details><summary style={summaryStyle}>Badge embed</summary><div style={{marginTop:"0.75rem"}}>{...badge content...}</div></details>`
2. Remove `SectionDivider title="Badge"` from above the badge block
3. Run TypeScript check

---

### T-010: Collapse Works With in details/summary for universal skills and verify dead code removal

**User Story**: US-003
**Satisfies ACs**: AC-US3-03
**Status**: [ ] pending

**Test Plan**:
- **Given** a universal skill (`isUniversal === true`) and a specific-compatibility skill (`isUniversal === false`)
- **When** each renders the Works With section
- **Then** the universal skill wraps the agent grid in `<details>` with summary "Works with all agents ({count})", the specific-compatibility skill renders the agent list directly without `<details>`, no `SectionDivider title="Works with"` is present for either, and zero references to dead components (`StatCard`, `MetaRow`, `basePillStyle`, `pillStyle`, `scanRowStyle`, `scanLabelStyle`) remain in the file

**Test Cases**:
1. **Unit**: `repositories/anton-abyzov/vskill-platform/src/app/skills/[name]/page.test.tsx`
   - `universalWorksWithInDetails()`: With `isUniversal=true`, assert agent grid is inside `<details>` and summary contains agent count
   - `specificWorksWithNotInDetails()`: With `isUniversal=false` and `compatibleAgentSlugs`, assert no `<details>` wrapper around agent grid
   - `noSectionDividerForWorksWith()`: Assert no `SectionDivider` with title "Works with" in either case
   - **Coverage Target**: 85%

2. **Dead code verification** (run after implementation):
   - `grep -n "StatCard\|MetaRow\|basePillStyle\|pillStyle\|scanRowStyle\|scanLabelStyle" src/app/skills/[name]/page.tsx` must return zero matches

**Implementation**:
1. For universal skills branch: wrap agent pill grid in `<details><summary style={summaryStyle}>Works with all agents ({visibleAgents.length})</summary><div style={{marginTop:"0.75rem"}}>{...agent grid...}</div></details>`
2. For specific-compatibility branch: remove `SectionDivider title="Works with"`, render small `sectionLabelStyle` label + agent grid directly
3. Verify `SectionDivider` import is still needed (Extension Points + Security retain it) -- do not remove import
4. Run dead code grep to confirm zero references to `StatCard`, `MetaRow`, `basePillStyle`, `pillStyle`, `scanRowStyle`, `scanLabelStyle`
5. Run TypeScript check: `npx tsc --noEmit`
6. Run full test suite: `npx vitest run src/app/skills`
7. Verify page line count is under 700: `wc -l src/app/skills/\[name\]/page.tsx`
