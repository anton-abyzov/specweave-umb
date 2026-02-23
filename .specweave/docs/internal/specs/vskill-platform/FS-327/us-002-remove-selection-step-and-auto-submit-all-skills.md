---
id: US-002
feature: FS-327
title: Remove selection step and auto-submit all skills
status: complete
priority: P1
created: 2026-02-22
project: vskill-platform
---
# US-002: Remove selection step and auto-submit all skills

**Feature**: [FS-327](./FEATURE.md)

skill author
**I want** discovery to immediately submit all found skills
**So that** the submit flow is faster and requires fewer clicks

---

## Acceptance Criteria

- [x] **AC-US2-01**: The `Phase` type changes from `"input" | "discovering" | "select" | "submitting" | "done"` to `"input" | "discovering" | "submitting" | "done"` (no "select" phase)
- [x] **AC-US2-02**: After successful discovery (skills.length > 0), the page transitions directly from "discovering" to "submitting" -- no user interaction required
- [x] **AC-US2-03**: All discovered skills are submitted (no client-side filtering by status). Already-verified and already-pending skills are submitted and the bulk endpoint's dedup logic handles them.
- [x] **AC-US2-04**: The following state variables are removed: `selected`, `collapsed`
- [x] **AC-US2-05**: The following functions are removed: `toggleSkill`, `toggleAll`, `togglePlugin`, `toggleCollapse`
- [x] **AC-US2-06**: The `StatusBadge` component is removed
- [x] **AC-US2-07**: The `btnSmall` style constant is removed
- [x] **AC-US2-08**: The entire "select" rendering block (previously lines 351-516 in page.tsx) is removed
- [x] **AC-US2-09**: The `reset()` function no longer references `selected`, `collapsed`, or other removed state
- [x] **AC-US2-10**: After cleanup, page.tsx is under 500 lines

---

## Implementation

**Increment**: [0327-submit-page-discovery-fix](../../../../../increments/0327-submit-page-discovery-fix/spec.md)

