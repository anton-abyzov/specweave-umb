---
id: US-001
feature: FS-426
title: Above-the-fold hero zone
status: complete
priority: P1
created: 2026-03-07
project: vskill-platform
external:
  github:
    issue: 1506
    url: https://github.com/anton-abyzov/specweave/issues/1506
---
# US-001: Above-the-fold hero zone

**Feature**: [FS-426](./FEATURE.md)

developer evaluating a skill
**I want** to see the most important information (name, trust tier, author, install command) immediately
**So that** I can quickly decide whether to install it

**Context**: Currently the page uses `SectionDivider` for the skill name (which renders it as a styled divider, not a semantic heading), places badges in a separate row below, puts meta info (author, repo, version) in a distant table-style section, and buries the install command further down. A developer scanning the page must scroll past popularity stats and meta to reach the install command.

---

## Acceptance Criteria

- [x] **AC-US1-01**: Skill name renders as an `h1` element (not via `SectionDivider`) at the top of the page content, with `TierBadge`, `TrustBadge`, and version string (`v{currentVersion}`) displayed inline on the same row (flex, centered vertically, gap between items). The existing `SectionDivider` call for the header is removed.
- [x] **AC-US1-02**: A byline row appears directly below the h1 row, showing (left to right, separated by a middle-dot or pipe delimiter): author name as a link to `/authors/{author}`, category as plain text from `CATEGORY_LABELS`, repository as a `RepoLink` with adjacent `RepoHealthBadge`, and last-updated date via `formatDate`. All items render inline (flex row, wrapping allowed) in the mono font at the muted/faint color. Source path link (skillPath) also appears in this byline if available.
- [x] **AC-US1-03**: The `TerminalBlock` install section appears immediately after the hero (h1 + byline + description + taint warning if applicable), before any stats or security content. No `SectionDivider` is used for the install heading -- instead a small mono-font label "Install" appears above the terminal block.
- [x] **AC-US1-04**: Security scan summary (Tier 1, Tier 2, and any external scans) renders as a horizontal flex row of compact status chips (label + PASS/FAIL pill) directly adjacent to or immediately below the install section, replacing the current vertical list layout. The "View full security report" link appears inline after the last chip.

---

## Implementation

**Increment**: [0426-skill-page-redesign](../../../../../increments/0426-skill-page-redesign/spec.md)

