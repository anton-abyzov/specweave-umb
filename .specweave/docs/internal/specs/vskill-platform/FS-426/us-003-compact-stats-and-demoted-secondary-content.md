---
id: US-003
feature: FS-426
title: Compact stats and demoted secondary content
status: complete
priority: P2
created: 2026-03-07
project: vskill-platform
---
# US-003: Compact stats and demoted secondary content

**Feature**: [FS-426](./FEATURE.md)

developer browsing skills
**I want** popularity stats displayed compactly and secondary features (badge embed, agent list) demoted
**So that** stats inform without dominating and secondary content is accessible but not distracting

**Context**: Currently 8 `StatCard` box components render in a flex-wrap grid, each with a border, padding, and large font -- taking significant vertical space. Some stats are redundant (Monthly npm downloads alongside Weekly; Unique installs alongside total Installs when counts are equal). The badge embed section takes a full `SectionDivider` + image + code block. The "Works with" agent list for universal skills shows all agents in a pill grid, which is noisy.

---

## Acceptance Criteria

- [x] **AC-US3-01**: The `StatCard` component and its `SectionDivider title="Popularity"` are replaced by inline stat pairs rendered as a single flex row of compact `label: value` spans in mono font (e.g., "Installs 1.2k | Stars 340 | Weekly 890 | 7d Trend 42"). Redundant stats are deduplicated: if `npmDownloadsWeekly > 0`, the Monthly (`npmDownloads`) stat is dropped; if `uniqueInstalls` equals `vskillInstalls`, the Unique stat is dropped. The metrics-refreshed timestamp remains as a small note below the stat row.
- [x] **AC-US3-02**: The badge embed section (current `SectionDivider title="Badge"` block, lines 366-388) is collapsed into a native HTML `details`/`summary` element. The summary text reads "Badge embed". When expanded, it shows the badge image preview and the markdown `TerminalBlock`. No `SectionDivider` is used.
- [x] **AC-US3-03**: The "Works with" section (current `SectionDivider title="Works with"` block, lines 521-582) uses a native HTML `details`/`summary` element for universal skills (when `isUniversal` is true). The summary text reads "Works with all agents ({count})" where count is `visibleAgents.length`. When expanded, the agent pill grid renders as before. For non-universal skills (explicit `compatibleAgentSlugs`), the agent list renders directly without `details`/`summary` since it is a smaller, more relevant set.

---

## Implementation

**Increment**: [0426-skill-page-redesign](../../../../../increments/0426-skill-page-redesign/spec.md)

