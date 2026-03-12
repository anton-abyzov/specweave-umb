---
id: US-001
feature: FS-497
title: "Actionable comparison results (P1)"
status: completed
priority: P1
created: "2026-03-11T00:00:00.000Z"
tldr: "**As a** skill author."
project: vskill
---

# US-001: Actionable comparison results (P1)

**Feature**: [FS-497](./FEATURE.md)

**As a** skill author
**I want** concrete action items after A/B comparison
**So that** I know exactly what to do: keep, improve, rewrite, or remove my skill

---

## Acceptance Criteria

- [x] **AC-US1-01**: After verdict computation, system generates structured action items via LLM call
- [x] **AC-US1-02**: Action items include recommendation (keep/improve/rewrite/remove), summary, weaknesses, strengths, suggestedFocus
- [x] **AC-US1-03**: Action items are persisted in history alongside verdict and comparison data
- [x] **AC-US1-04**: Action items generation is non-fatal — comparison is still valid without it

---

## Implementation

**Increment**: [0497-comparison-action-items](../../../../../increments/0497-comparison-action-items/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-001**: Add ActionItems types to benchmark.ts and types.ts
- [x] **T-002**: Create action-items.ts engine with LLM prompt
- [x] **T-003**: Wire action items generation into compare endpoint in api-routes.ts
