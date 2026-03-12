---
id: US-003
feature: FS-513
title: "Dual-line MiniTrend sparkline (P1)"
status: completed
priority: P1
created: 2026-03-12T00:00:00.000Z
tldr: "**As a** skill developer."
project: vskill
---

# US-003: Dual-line MiniTrend sparkline (P1)

**Feature**: [FS-513](./FEATURE.md)

**As a** skill developer
**I want** the MiniTrend sparkline to show two separate polylines -- one for skill runs and one for baseline runs
**So that** I can see at a glance whether the skill is trending up relative to the baseline

---

## Acceptance Criteria

- [x] **AC-US3-01**: Given the `CaseHistoryEntry` type, then it includes an optional `baselinePassRate` field of type `number | undefined`
- [x] **AC-US3-02**: Given the `getCaseHistory` function reads a comparison-type history entry, then it populates `baselinePassRate` by deriving it from the existing `comparisonDetail` rubric scores (average of `baselineContentScore` and `baselineStructureScore`, normalized to 0-1 range)
- [x] **AC-US3-03**: Given the MiniTrend component receives entries, then it renders two SVG polylines: a blue line (`var(--accent)`) for skill pass rates and a gray line (`var(--text-tertiary)`) for baseline pass rates
- [x] **AC-US3-04**: Given a `benchmark`-type entry, then it contributes a point to the skill (blue) line only and does not contribute to the baseline (gray) line
- [x] **AC-US3-05**: Given a `baseline`-type entry, then it contributes a point to the baseline (gray) line only and does not contribute to the skill (blue) line
- [x] **AC-US3-06**: Given a `comparison`-type entry, then it contributes `pass_rate` to the skill (blue) line and `baselinePassRate` to the baseline (gray) line
- [x] **AC-US3-07**: Given entries of types `improve`, `instruct`, `model-compare`, `ai-generate`, or `eval-generate`, then they are excluded from both sparkline polylines entirely

---

## Implementation

**Increment**: [0513-skill-studio-eval-history-redesign](../../../../../increments/0513-skill-studio-eval-history-redesign/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-007**: Add `baselinePassRate` field to `CaseHistoryEntry` types (server + client)
- [x] **T-008**: Derive `baselinePassRate` from `comparisonDetail` rubric scores in `getCaseHistory`
- [x] **T-009**: Rewrite MiniTrend with dual SVG polylines and type-filtered data sources
- [x] **T-010**: Integration test -- history panel renders dual sparkline and split-lane correctly
