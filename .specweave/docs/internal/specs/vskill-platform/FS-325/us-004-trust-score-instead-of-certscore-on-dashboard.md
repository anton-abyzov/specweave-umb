---
id: US-004
feature: FS-325
title: Trust Score Instead of certScore on Dashboard
status: complete
priority: P2
created: 2026-02-22
project: vskill-platform
external:
  github:
    issue: 1290
    url: https://github.com/anton-abyzov/specweave/issues/1290
---
# US-004: Trust Score Instead of certScore on Dashboard

**Feature**: [FS-325](./FEATURE.md)

visitor viewing the quality score metric
**I want** the dashboard to show the composite trust score instead of the raw scan score
**So that** I see a more meaningful quality indicator that factors in provenance, community signals, and security history

---

## Acceptance Criteria

- [x] **AC-US4-01**: The fourth metric card title changes from "Avg Quality Score" to "Avg Trust Score"
- [x] **AC-US4-02**: The value is computed from `trustScore` (or computed via `computeTrustScore()` for seed data) instead of `certScore`
- [x] **AC-US4-03**: The ScoreRing component renders the trust score average
- [x] **AC-US4-04**: The subtitle still shows certified/verified counts
- [x] **AC-US4-05**: For seed-data skills that lack `trustScore`, compute it using `computeTrustScore()` with reasonable defaults (tier1=PASS, provenance=unchecked, etc.)

---

## Implementation

**Increment**: [0325-homepage-metrics-accuracy](../../../../../increments/0325-homepage-metrics-accuracy/spec.md)

