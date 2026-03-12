---
id: US-005
feature: FS-465
title: Benchmark Execution Panel (P1)
status: not_started
priority: P1
created: 2026-03-09
tldr: "**As a** skill developer."
project: vskill
external:
  github:
    issue: 45
    url: "https://github.com/anton-abyzov/vskill/issues/45"
---

# US-005: Benchmark Execution Panel (P1)

**Feature**: [FS-465](./FEATURE.md)

**As a** skill developer
**I want** a unified run panel that supports benchmark, baseline, and A/B comparison modes with SSE streaming
**So that** I can execute and monitor all types of evaluation runs from one place

---

## Acceptance Criteria

- [ ] **AC-US5-01**: Given the Run panel is active, when viewing the controls bar, then "Run All", "Run Baseline", and "Run A/B Comparison" buttons are visible
- [ ] **AC-US5-02**: Given the Run panel is active, when a scope selector is present, then the user can choose between "All cases" and "Selected case only" (pre-filled when navigated from Tests panel)
- [ ] **AC-US5-03**: Given a run is in progress, when SSE events stream in, then per-case result cards animate in with fade-in showing pass/fail status and assertion details
- [ ] **AC-US5-04**: Given a run is in progress, when viewing the panel, then a progress bar shows completion count (e.g., "2/5 cases")
- [ ] **AC-US5-05**: Given a run completes, when viewing the panel, then an overall pass rate card and GroupedBarChart render showing results summary
- [ ] **AC-US5-06**: Given a run completes, when switching to the Tests panel, then inline results for each case are updated from the shared workspace state
- [ ] **AC-US5-07**: Given a run is in progress, when clicking another "Run" button, then the action is rejected with message "Benchmark already running -- wait or cancel"

---

## Implementation

**Increment**: [0465-skill-builder-redesign](../../../../../increments/0465-skill-builder-redesign/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

_No tasks defined for this user story_
