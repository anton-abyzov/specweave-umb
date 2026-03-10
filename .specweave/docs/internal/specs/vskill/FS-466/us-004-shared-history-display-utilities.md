---
id: US-004
feature: FS-466
title: "Shared History Display Utilities"
status: completed
priority: P1
created: 2026-03-09
tldr: "**As a** developer maintaining the eval-ui codebase."
project: vskill
---

# US-004: Shared History Display Utilities

**Feature**: [FS-466](./FEATURE.md)

**As a** developer maintaining the eval-ui codebase
**I want** the history display utilities (passRateColor, shortDate, fmtDuration, MiniTrend) to be shared between HistoryPerEval and the new CaseDetail history section
**So that** there is no code duplication and both views stay visually consistent

---

## Acceptance Criteria

- [x] **AC-US4-01**: Given the shared utilities (passRateColor, shortDate, fmtDuration, MiniTrend), when extracted to a shared module, then both HistoryPerEval.tsx and the CaseDetail history section import from the same source
- [x] **AC-US4-02**: Given the shared utilities are extracted, when HistoryPerEval is rendered, then its visual output is identical to before the extraction (no visual regression)
- [x] **AC-US4-03**: Given the CaseDetail history section and the HistoryPerEval expanded detail, when both display the same run entry, then the visual treatment (colors, formatting, spacing) is consistent between them

---

## Implementation

**Increment**: [0466-skill-builder-preview-history](../../../../../increments/0466-skill-builder-preview-history/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-001**: Create historyUtils.tsx with extracted pure functions
- [x] **T-002**: Add MiniTrend component to historyUtils.tsx
- [x] **T-007**: Update HistoryPerEval to import from historyUtils
- [x] **T-008**: Verify visual consistency between HistoryPerEval and CaseDetail
