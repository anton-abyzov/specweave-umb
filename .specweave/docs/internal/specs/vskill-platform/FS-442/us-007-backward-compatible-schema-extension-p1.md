---
id: US-007
feature: FS-442
title: "Backward-Compatible Schema Extension (P1)"
status: completed
priority: P1
created: 2026-03-06T00:00:00.000Z
tldr: "**As a** developer."
project: vskill-platform
---

# US-007: Backward-Compatible Schema Extension (P1)

**Feature**: [FS-442](./FEATURE.md)

**As a** developer
**I want** the DB schema extended with new nullable columns on EvalRun and EvalCase
**So that** existing V1 data is preserved and new V2 fields coexist without breaking queries

---

## Acceptance Criteria

- [x] **AC-US7-01**: `EvalRun` gains nullable columns: `methodologyVersion` (Int, default null), `assertionPassRate` (Float, nullable), `skillRubricAvg` (Float, nullable), `baselineRubricAvg` (Float, nullable), `varianceData` (Json, nullable), `runCountPerCase` (Int, nullable)
- [x] **AC-US7-02**: `EvalCase` gains nullable columns: `assertionResults` (Json, nullable), `skillContentScore` (Int, nullable), `skillStructureScore` (Int, nullable), `baselineContentScore` (Int, nullable), `baselineStructureScore` (Int, nullable)
- [x] **AC-US7-03**: `EvalTrigger` enum gains the `REVERIFY` value
- [x] **AC-US7-04**: All existing V1 eval data is preserved unchanged after migration -- new columns are null for V1 rows
- [x] **AC-US7-05**: A Prisma migration is created and applied without data loss

---

## Implementation

**Increment**: [0442-eval-system-rework](../../../../../increments/0442-eval-system-rework/spec.md)

**Tasks**: See increment tasks.md for implementation details.


## Tasks

- [x] **T-001**: Extend types.ts with V2 TypeScript types
- [x] **T-002**: Prisma schema extension and migration
