# 0243: Skill Detail Page — Extensible Pioneer, Scan Transparency, UX Polish

## Problem

The skill detail page on verified-skill.com has 4 UX issues: "extensible" is a hidden label instead of a first-class feature, popularity stats are buried and ugly, scan scores are opaque (88/100 with no explanation), and "Works with" shows identical agent lists for every skill.

## User Stories

### US-001: Extensible as a pioneering feature
As a visitor, I should immediately see whether a skill supports customization and what extension points it offers.

**Acceptance Criteria:**
- [x] AC-US1-01: Extensible skills show a prominent teal callout banner after the header
- [x] AC-US1-02: Extension Points section lists each point with type and description
- [x] AC-US1-03: "extensible" label filtered from generic badges (replaced by first-class callout)
- [x] AC-US1-04: Non-extensible skills show no callout or extension points section

### US-002: Popularity section redesign
As a visitor, I should see popularity stats prominently with clear visual treatment.

**Acceptance Criteria:**
- [x] AC-US2-01: Popularity section moved above Meta (after Description)
- [x] AC-US2-02: Stats displayed as individual cards (stars, forks, installs, trending)

### US-003: Scan results transparency
As a visitor, I should be able to see WHY a skill scored 88/100 — what checks passed and what failed.

**Acceptance Criteria:**
- [x] AC-US3-01: Expandable "View score breakdown" toggle below scan summary (native `<details>`)
- [x] AC-US3-02: Breakdown shows each check with pass/fail, weight, and failure notes
- [x] AC-US3-03: Skills without breakdown data gracefully hide the toggle

### US-004: Smarter "Works with" agents
As a visitor, I should see relevant agent compatibility, not a blanket list of all 39 agents.

**Acceptance Criteria:**
- [x] AC-US4-01: Universal skills show all agents with "Works with any vskill-compatible agent" subtitle
- [x] AC-US4-02: Tool-specific skills show only their compatible agents with "Verified compatible with:" subtitle
