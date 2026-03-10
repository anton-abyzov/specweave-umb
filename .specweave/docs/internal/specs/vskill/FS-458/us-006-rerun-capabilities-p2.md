---
id: US-006
feature: FS-458
title: "Rerun Capabilities (P2)"
status: not_started
priority: P1
created: 2026-03-09
tldr: "**As a** skill author."
project: vskill
---

# US-006: Rerun Capabilities (P2)

**Feature**: [FS-458](./FEATURE.md)

**As a** skill author
**I want** rerun buttons that let me re-execute a past run as with-skill, baseline-only, or full A/B comparison
**So that** I can quickly re-test after making changes to my skill

---

## Acceptance Criteria

- [ ] **AC-US6-01**: Given the HistoryPage detail view for a selected run, when displayed, then three rerun buttons appear: "Rerun Benchmark" (with-skill), "Run Baseline", and "Run A/B Comparison"
- [ ] **AC-US6-02**: Given the BenchmarkPage, when displayed, then alongside the existing "Run All" button, a "Run Baseline" button and a "Run A/B Comparison" button appear
- [ ] **AC-US6-03**: Given a user clicks any rerun button, when the run starts, then the UI navigates to the appropriate page (BenchmarkPage for benchmark/baseline, ComparisonPage for A/B) and starts the run
- [ ] **AC-US6-04**: Given a baseline rerun completes, when history is refreshed, then the new baseline entry appears in the timeline

---

## Implementation

**Increment**: [0458-eval-run-history](../../../../../increments/0458-eval-run-history/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-010**: Rerun buttons on HistoryPage and BenchmarkPage with autostart support
