---
id: US-002
feature: FS-488
title: "Sidebar Badge Uses Overall Pass Rate"
status: completed
priority: P1
created: "2026-03-11T00:00:00.000Z"
tldr: "**As a** skill author."
project: vskill
---

# US-002: Sidebar Badge Uses Overall Pass Rate

**Feature**: [FS-488](./FEATURE.md)

**As a** skill author
**I want** the sidebar benchmark status badge to reflect the actual `overall_pass_rate` from the latest benchmark
**So that** it never contradicts the header pass-rate display

---

## Acceptance Criteria

- [x] **AC-US2-01**: Given a skill with a latest benchmark where `overall_pass_rate` is 0, when the `/api/skills` endpoint computes `benchmarkStatus`, then the status is `"fail"` (not `"pass"`)
- [x] **AC-US2-02**: Given a skill with a latest benchmark where `overall_pass_rate` is 1.0, when the endpoint computes `benchmarkStatus`, then the status is `"pass"`
- [x] **AC-US2-03**: Given a skill whose latest benchmark references case IDs that no longer exist in `evals.json`, when the endpoint computes `benchmarkStatus`, then the status is `"stale"` to signal outdated results

---

## Implementation

**Increment**: [0488-skill-studio-status-ux](../../../../../increments/0488-skill-studio-status-ux/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-002**: Extract computeBenchmarkStatus helper in api-routes.ts
- [x] **T-003**: Add "stale" status to frontend types and STATUS_CONFIG
