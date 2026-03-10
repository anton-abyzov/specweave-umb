---
id: US-005
feature: FS-477
title: "Homepage Simplification"
status: not_started
priority: P1
created: 2026-03-10
tldr: "**As a** visitor."
project: vskill-platform
---

# US-005: Homepage Simplification

**Feature**: [FS-477](./FEATURE.md)

**As a** visitor
**I want** the homepage to lead with a search-first design
**So that** I can find skills immediately without scrolling past marketing sections

---

## Acceptance Criteria

- [ ] **AC-US5-01**: Given the homepage, when rendered, then the top section contains a compact header with the tagline "Install AI skills you can trust" and a key stat (e.g., "90k+ verified")
- [ ] **AC-US5-02**: Given the homepage on a non-touch device (`matchMedia('(hover: hover)')` matches), when the page loads, then the hero search input is auto-focused
- [ ] **AC-US5-03**: Given the homepage on a touch device, when the page loads, then the hero search input is NOT auto-focused (to avoid triggering the virtual keyboard)
- [ ] **AC-US5-04**: Given the hero search input, when rendered, then its placeholder text reads "Search 90,000+ verified skills..." and typing dispatches `openSearch` custom event to the existing SearchPalette
- [ ] **AC-US5-05**: Given the homepage, when rendered below the search, then sections appear in this order: category pills (CategoryNav), trending skills (TrendingSkillsSection), compact agent strip ("Works with 39 agents" + 6 agent icons + "+N more")
- [ ] **AC-US5-06**: Given the homepage, when rendered, then HomepageDemoHero (video hero), role cards, SkillStudioSection, MarketDashboard, verification explainer, and full agent badge grid are NOT present

---

## Implementation

**Increment**: [0477-homepage-studio-nav-redesign](../../../../../increments/0477-homepage-studio-nav-redesign/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
